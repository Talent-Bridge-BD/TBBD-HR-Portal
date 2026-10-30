from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def assert_workplace_hub(response):
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Talent Bridge BD Workplace Hub" in response.text
    assert "SECURE WORKPLACE ACCESS" in response.text
    assert "Connecting Bangladeshi Talent With Global Employment Opportunities." in response.text
    assert "Candidate Sign In" in response.text
    assert "New Candidate Registration" in response.text
    assert "Employer Access Request" in response.text
    assert "Staff &amp; Administrator Sign In" in response.text
    assert response.text.count('src="/assets/talent-bridge-bd-logo.png"') == 1
    assert 'id="copyright-year"' in response.text
    assert "new Date().getFullYear()" in response.text
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in response.text
    assert "grid-template-rows: repeat(2, minmax(220px, 1fr))" in response.text
    assert "grid-template-columns: minmax(0, 1fr)" in response.text
    assert "@media (max-height: 820px)" in response.text
    assert "@media (max-width: 640px)" in response.text
    assert "--accent: #356FC1" in response.text
    assert "--accent: #278B77" in response.text
    assert "--accent: #805CC0" in response.text
    assert "--accent: #B87535" in response.text
    assert "width: 220px" in response.text
    assert "align-self: center" in response.text
    assert "Access is subject to account verification, approval status and assigned permissions." in response.text
    assert "prefers-reduced-motion: reduce" in response.text
    assert 'url("/assets/tbbd-workplace-hub.jpg")' not in response.text

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
