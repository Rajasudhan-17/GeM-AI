def test_document_upload(client):
    bid_id = "BID-77291"
    file_content = b"%PDF-1.4 Mock PDF upload content for GeM verification test"
    files = {"file": ("new_undertaking.pdf", file_content, "application/pdf")}
    data = {"document_type": "OEM"}

    res = client.post(
        f"/api/v1/bids/{bid_id}/documents/upload",
        files=files,
        data=data,
    )
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["document_id"].startswith("DOC-")
    assert res_data["document_type"] == "OEM"
    assert res_data["status"] == "PROCESSED"

    # Verify document is listed
    res_docs = client.get(f"/api/v1/bids/{bid_id}/documents")
    assert res_docs.status_code == 200
    docs = res_docs.json()
    assert any(d["file_name"] == "new_undertaking.pdf" for d in docs)
