import time


def test_accept_decision_suresh(client):
    bid_id = "BID-77291"
    
    # Run verification first
    client.post(f"/api/v1/bids/{bid_id}/verify")
    time.sleep(0.5)

    # Submit accept decision
    res = client.post(
        f"/api/v1/bids/{bid_id}/decision",
        json={
            "decision": "ACCEPTED",
            "reason": "All statutory documents verified authentic and compliant.",
            "officer_name": "Evaluation Officer A",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "ACCEPTED"
    assert data["score_at_decision"] >= 95.0
    assert data["risk_at_decision"] == "LOW"


def test_decision_history_immutable(client):
    bid_id = "BID-77291"
    
    # First decision
    client.post(
        f"/api/v1/bids/{bid_id}/decision",
        json={"decision": "ACCEPTED", "reason": "Initial approval"},
    )
    # Second decision (e.g. revision)
    client.post(
        f"/api/v1/bids/{bid_id}/decision",
        json={"decision": "REJECTED", "reason": "Revised upon administrative order"},
    )

    res = client.get(f"/api/v1/bids/{bid_id}/decision")
    assert res.status_code == 200
    data = res.json()
    assert data["current_decision"]["decision"] == "REJECTED"
    assert len(data["history"]) >= 2
