from run import app

def test_endpoints():
    client = app.test_client()
    
    # 1. Test Homepage
    resp = client.get("/")
    assert resp.status_code == 200, f"Expected 200 on /, got {resp.status_code}"
    print("PASS: GET /")

    # 2. Test Sample Scam
    resp = client.get("/sample/internshala_scam", follow_redirects=True)
    assert resp.status_code == 200, f"Expected 200 on sample, got {resp.status_code}"
    assert b"LIKELY FAKE / SCAM" in resp.data, "Expected LIKELY FAKE / SCAM in result"
    print("PASS: GET /sample/internshala_scam (Scam correctly detected)")

    # 3. Test Sample Genuine
    resp = client.get("/sample/linkedin_genuine", follow_redirects=True)
    assert resp.status_code == 200, f"Expected 200 on genuine sample, got {resp.status_code}"
    assert b"GENUINE / SAFE" in resp.data, "Expected GENUINE / SAFE in result"
    print("PASS: GET /sample/linkedin_genuine (Genuine correctly verified)")

    # 4. Test History
    resp = client.get("/history")
    assert resp.status_code == 200, f"Expected 200 on /history, got {resp.status_code}"
    print("PASS: GET /history")

    # 5. Test Batch Check
    resp = client.get("/batch")
    assert resp.status_code == 200, f"Expected 200 on /batch, got {resp.status_code}"
    print("PASS: GET /batch")

    # 6. Test Academic Report
    resp = client.get("/project-report")
    assert resp.status_code == 200, f"Expected 200 on /project-report, got {resp.status_code}"
    assert b"AJAY KUMAR GARG ENGINEERING COLLEGE" in resp.data
    print("PASS: GET /project-report (AKGEC College Template Loaded)")

    # 7. Test Export Certificate
    resp = client.get("/export-report/1")
    assert resp.status_code == 200, f"Expected 200 on /export-report/1, got {resp.status_code}"
    print("PASS: GET /export-report/1")

    # 8. Test JSON REST API
    api_resp = client.post("/api/analyze", json={
        "title": "Data Entry Typist",
        "text": "Earn 50000 daily typing books. Pay refundable security deposit 1200 via Paytm and join Telegram."
    })
    assert api_resp.status_code == 200
    json_data = api_resp.get_json()
    assert json_data["status"] == "success"
    assert json_data["analysis"]["verdict"] == "LIKELY FAKE / SCAM"
    print(f"PASS: POST /api/analyze (Score: {json_data['analysis']['scam_score']}%, Verdict: {json_data['analysis']['verdict']})")

    print("\nALL 8 SYSTEM INTEGRATION TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_endpoints()
