import time


def test_e2e_vikram_traders_pipeline(client):
    # Step 1: Select Bid
    bid_id = "BID-51064"
    res_bid = client.get(f"/api/v1/bids/{bid_id}")
    assert res_bid.status_code == 200
    assert res_bid.json()["bidder_id"] == "BDR-51064"

    # Step 2: Start Verification
    res_start = client.post(f"/api/v1/bids/{bid_id}/verify")
    assert res_start.status_code == 200
    start_data = res_start.json()
    run_id = start_data["run_id"]
    assert run_id.startswith("VR-")

    # Await pipeline completion (polling)
    run_data = None
    for _ in range(40):
        res_run = client.get(f"/api/v1/verification-runs/{run_id}")
        assert res_run.status_code == 200
        run_data = res_run.json()
        if run_data["status"] == "COMPLETED":
            break
        time.sleep(0.05)

    assert run_data["status"] == "COMPLETED"
    assert run_data["current_stage"] == "COMPLETED"
    assert run_data["progress_pct"] == 100

    # Step 3-9: Inspect GST check
    gst_check = next((c for c in run_data["checks"] if c["rule_code"] == "GST-001"), None)
    assert gst_check is not None
    assert gst_check["status"] == "FAIL"
    assert "07AACPV9821K1Z2" in gst_check["reason"]
    assert "07AACPV9821K1ZP" in gst_check["reason"]

    # ESIC check
    esic_check = next((c for c in run_data["checks"] if c["rule_code"] == "ESIC-001"), None)
    assert esic_check is not None
    assert esic_check["status"] == "FAIL"

    # Step 10: Calculate Score (~74-75%)
    assert run_data["score"] is not None
    total_score = run_data["score"]["total_score"]
    assert 70.0 <= total_score <= 78.0

    # Step 11: Calculate Risk (MEDIUM)
    assert run_data["risk_assessment"] is not None
    assert run_data["risk_assessment"]["risk_level"] == "MEDIUM"

    # Step 12: AI Explanation
    assert run_data["ai_recommendation"] is not None
    assert "GST" in run_data["ai_recommendation"]["summary"]
    assert "discrepancies" in run_data["ai_recommendation"]["risk_explanation"].lower() or "statutory" in run_data["ai_recommendation"]["risk_explanation"].lower()

    # Step 13: AI Chat
    res_chat = client.post(
        f"/api/v1/bids/{bid_id}/ai/chat",
        json={"message": "Why is GST flagged?"},
    )
    assert res_chat.status_code == 200
    chat_data = res_chat.json()
    assert "07AACPV9821K1Z2" in chat_data["answer"]
    assert "07AACPV9821K1ZP" in chat_data["answer"]

    # Step 14: Generate Decision Reason
    res_reason = client.post(f"/api/v1/bids/{bid_id}/ai/generate-reason")
    assert res_reason.status_code == 200
    reason_data = res_reason.json()
    assert len(reason_data["reason"]) > 20
    assert reason_data["suggested_decision"] == "REJECTED"

    # Step 15: Submit REJECTED Decision
    res_dec = client.post(
        f"/api/v1/bids/{bid_id}/decision",
        json={
            "decision": "REJECTED",
            "reason": reason_data["reason"],
            "officer_name": "Senior Evaluation Officer",
        },
    )
    assert res_dec.status_code == 200
    dec_data = res_dec.json()
    assert dec_data["decision"] == "REJECTED"
    assert dec_data["bid_id"] == bid_id

    # Step 16: Verify Decision Exists in History
    res_dec_hist = client.get(f"/api/v1/bids/{bid_id}/decision")
    assert res_dec_hist.status_code == 200
    hist_data = res_dec_hist.json()
    assert hist_data["current_decision"]["decision"] == "REJECTED"
    assert len(hist_data["history"]) >= 1

    # Step 17: Verify Audit Trail Exists and is Chained
    res_audit = client.get(f"/api/v1/bids/{bid_id}/audit")
    assert res_audit.status_code == 200
    audit_events = res_audit.json()
    assert len(audit_events) > 5

    actions = [e["action"] for e in audit_events]
    assert "DOCUMENT_PROCESSING_STARTED" in actions
    assert "DECISION_SUBMITTED" in actions
