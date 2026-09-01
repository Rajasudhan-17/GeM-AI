def test_list_bidders(client):
    response = client.get("/api/v1/bidders")
    assert response.status_code == 200
    bidders = response.json()
    assert len(bidders) == 4
    bidder_ids = [b["id"] for b in bidders]
    assert "BDR-77291" in bidder_ids
    assert "BDR-51064" in bidder_ids
    assert "BDR-90218" in bidder_ids
    assert "BDR-63357" in bidder_ids


def test_get_bid(client):
    response = client.get("/api/v1/bids/BID-77291")
    assert response.status_code == 200
    bid = response.json()
    assert bid["id"] == "BID-77291"
    assert bid["bidder_id"] == "BDR-77291"
    assert "tender_id" in bid
