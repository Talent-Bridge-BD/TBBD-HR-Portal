from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def assert_workplace_hub(response):
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Welcome to Talent Bridge BD" in response.text
    assert "Candidate Sign In" in response.text
    assert "New Candidate Registration" in response.text
    assert "Employer Access Request" in response.text
    assert "Staff &amp; Administrator Sign In" in response.text
    assert response.text.count('src="/assets/talent-bridge-bd-logo.png"') == 2
    assert 'url("/assets/tbbd-workplace-hub.jpg")' in response.text
    assert 'id="copyright-year"' in response.text
    assert "new Date().getFullYear()" in response.text
    assert "@media (max-width: 760px)" in response.text
    assert "@media (max-width: 520px)" in response.text
    assert "grid-auto-rows: 1fr" in response.text
    assert ".workspace.registration" in response.text
    assert "place-items: center" in response.text
    assert "min-height: 46px" in response.text

    candidate_sign_in = (
        'href="/.auth/login/TBBDCandidateExternalID?'
        'post_login_redirect_uri=%2F%3FauthMode%3Dcandidate"'
    )
    candidate_registration = (
        'href="/.auth/login/TBBDCandidateExternalID?'
        'post_login_redirect_uri=%2F%3FauthMode%3Dcandidate&amp;prompt=create"'
    )
    assert candidate_sign_in in response.text
    assert candidate_registration in response.text
    assert 'href="/employer-access-request"' in response.text
    assert (
        'href="/.auth/login/aad?'
        'post_login_redirect_uri=%2F%3Fportal%3D1"'
    ) in response.text
    assert 'href="#page-title"' in response.text
    assert 'href="#access-options"' in response.text


def test_public_homepage_serves_workplace_hub():
    response = client.get("/")
    assert_workplace_hub(response)


def test_workplace_hub_html_route_serves_landing_page():
    response = client.get("/workplace-hub.html")
    assert_workplace_hub(response)
