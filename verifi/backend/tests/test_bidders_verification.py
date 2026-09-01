import time
from app.core.enums import VerificationStatus, RiskLevel


def test_correct_document_suresh_enterprises(client):
    bid_id = "BID-77291"
    res_start = client.post(f"/api/v1/bids/{bid_id}/verify")
    assert res_start.status_code == 200
    run_id = res_start.json()["run_id"]

    for _ in range(40):
        res_run = client.get(f"/api/v1/verification-runs/{run_id}")
        run_data = res_run.json()
        if run_data["status"] == "COMPLETED":
            break
        time.sleep(0.05)

    assert run_data["status"] == "COMPLETED"
    assert run_data["score"]["total_score"] >= 95.0
    assert run_data["risk_assessment"]["risk_level"] == "LOW"
    assert run_data["score"]["failed_count"] == 0
    assert all(c["status"] == "PASS" for c in run_data["checks"])


def test_high_risk_novatech_systems(client):
    bid_id = "BID-90218"
    res_start = client.post(f"/api/v1/bids/{bid_id}/verify")
    assert res_start.status_code == 200
    run_id = res_start.json()["run_id"]

    for _ in range(40):
        res_run = client.get(f"/api/v1/verification-runs/{run_id}")
        run_data = res_run.json()
        if run_data["status"] == "COMPLETED":
            break
        time.sleep(0.05)

    assert run_data["status"] == "COMPLETED"
    assert run_data["risk_assessment"]["risk_level"] == "HIGH"
    assert run_data["score"]["failed_count"] >= 3

    # Check DigiLocker is REVIEW due to provider outage
    dgl_check = next((c for c in run_data["checks"] if c["rule_code"] == "DGL-001"), None)
    assert dgl_check is not None
    assert dgl_check["status"] == "REVIEW"

    # Check Blacklist is FAIL
    bl_check = next((c for c in run_data["checks"] if c["rule_code"] == "BL-001"), None)
    assert bl_check is not None
    assert bl_check["status"] == "FAIL"


def test_green_fields_oem_review(client):
    bid_id = "BID-63357"
    res_start = client.post(f"/api/v1/bids/{bid_id}/verify")
    assert res_start.status_code == 200
    run_id = res_start.json()["run_id"]

    for _ in range(40):
        res_run = client.get(f"/api/v1/verification-runs/{run_id}")
        run_data = res_run.json()
        if run_data["status"] == "COMPLETED":
            break
        time.sleep(0.05)

    assert run_data["status"] == "COMPLETED"
    # OEM check must be REVIEW (near expiry), all others PASS
    oem_check = next((c for c in run_data["checks"] if c["rule_code"] == "OEM-001"), None)
    assert oem_check is not None
    assert oem_check["status"] == "REVIEW"
    assert "expires soon" in oem_check["reason"].lower() or "2026-09-15" in oem_check["reason"]

    # Score should be ~88-95%, and Risk remains LOW! (Demonstrates REVIEW != automatic rejection)
    assert run_data["risk_assessment"]["risk_level"] == "LOW"
    assert 85.0 <= run_data["score"]["total_score"] <= 95.0


def test_ai_chat_and_generate_reason(client):
    bid_id = "BID-77291"
    # Query AI chat for low risk reason
    res_chat = client.post(
        f"/api/v1/bids/{bid_id}/ai/chat",
        json={"message": "Why is this bidder low risk?"},
    )
    assert res_chat.status_code == 200
    chat_data = res_chat.json()
    assert "LOW RISK" in chat_data["answer"] or "compliant" in chat_data["answer"].lower()

    # Generate decision reason
    res_reason = client.post(f"/api/v1/bids/{bid_id}/ai/generate-reason")
    assert res_reason.status_code == 200
    reason_data = res_reason.json()
    assert reason_data["suggested_decision"] == "ACCEPTED"
    assert "ACCEPTED" in reason_data["reason"]
