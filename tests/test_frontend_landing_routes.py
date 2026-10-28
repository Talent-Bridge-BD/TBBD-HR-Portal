from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def assert_workplace_hub(response):
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Candidate Sign In" in response.text
    assert "New Candidate Registration" in response.text
    assert "Employer Access Request" in response.text
    assert "Staff &amp; Administrator Sign In" in response.text
    assert "/assets/talent-bridge-bd-logo.png" in response.text
    assert "Sign in with Microsoft" in response.text


def test_public_homepage_serves_workplace_hub():
    response = client.get("/")
    assert_workplace_hub(response)


def test_workplace_hub_html_route_serves_landing_page():
    response = client.get("/workplace-hub.html")
    assert_workplace_hub(response)
