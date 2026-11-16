import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

APP = ROOT / "frontend/src/App.jsx"
COMPONENT = ROOT / "frontend/src/components/WorkplaceHub.jsx"
CSS = ROOT / "frontend/src/styles/WorkplaceHub.css"
MAIN = ROOT / "frontend/src/main.jsx"
BANNER = ROOT / "frontend/src/assets/images/banner-hub.jpeg"

APP_SOURCE = APP.read_text(encoding="utf-8")
MAIN_SOURCE = MAIN.read_text(encoding="utf-8")
SOURCE = COMPONENT.read_text(encoding="utf-8")
STYLES = CSS.read_text(encoding="utf-8")


def test_workplace_hub_authentication_urls_are_preserved():
    expected_urls = {
        "STAFF_LOGIN_URL": (
            "/.auth/login/aad?post_login_redirect_uri=%2F%3Fportal%3D1"
        ),
        "CANDIDATE_LOGIN_URL": (
            "/.auth/login/TBBDCandidateExternalID?"
            "post_login_redirect_uri=%2F%3FauthMode%3Dcandidate"
        ),
        "CANDIDATE_REGISTRATION_URL": (
            "/.auth/login/TBBDCandidateExternalID?"
            "prompt=create&post_login_redirect_uri="
            "%2F%3FauthMode%3Dcandidate%26registration%3D1"
        ),
    }

    for name, expected in expected_urls.items():
        match = re.search(
            rf"const\s+{name}\s*=\s*(['\"])(.*?)\1",
            APP_SOURCE,
            re.DOTALL,
        )
        assert match, f"{name} is missing from App.jsx"
        assert match.group(2) == expected, f"{name} has changed"


def test_workplace_hub_has_all_four_approved_access_cards():
    expected_cards = {
        "candidate-access": (
            "Candidate Sign In",
            "For Job Seekers",
            "candidateLoginUrl",
        ),
        "registration-access": (
            "New Candidate Registration",
            "New Candidates",
            "candidateRegistrationUrl",
        ),
        "employer-access": (
            "Employer Access Request",
            "For Employers",
            "'/employer-access-request'",
        ),
        "staff-access": (
            "Staff & Administrator Sign In",
            "Authorized Personnel",
            "staffLoginUrl",
        ),
    }

    for card_id, (title, label, destination) in expected_cards.items():
        match = re.search(
            rf"\{{\s*id:\s*'{re.escape(card_id)}',(.*?)\n\s*\}},",
            SOURCE,
            re.DOTALL,
        )

        assert match, f"Access card {card_id} is missing"

        card = match.group(1)
        assert f"title: '{title}'" in card
        assert f"label: '{label}'" in card
        assert f"href: {destination}" in card


def test_workplace_hub_cards_use_their_configured_destinations():
    assert "hubCards.map((card) =>" in SOURCE
    assert "href={card.href}" in SOURCE
    assert 'className={`workplace-hub-card workplace-hub-card--${card.theme}`}' in SOURCE


def test_workplace_hub_authentication_gate_is_preserved():
    assert "if (!auth?.authenticated && !isCandidateMode)" in APP_SOURCE
    assert "<WorkplaceHub" in APP_SOURCE
    assert "staffLoginUrl={STAFF_LOGIN_URL}" in APP_SOURCE
    assert "candidateLoginUrl={CANDIDATE_LOGIN_URL}" in APP_SOURCE
    assert "candidateRegistrationUrl={CANDIDATE_REGISTRATION_URL}" in APP_SOURCE


def test_workplace_hub_design_assets_and_styles_are_present():
    assert BANNER.is_file(), "Approved Workplace Hub banner is missing"
    assert "workplaceHubBanner" in SOURCE
    assert "import './styles/WorkplaceHub.css'" in MAIN_SOURCE

    assert MAIN_SOURCE.index("import './styles.css'") < MAIN_SOURCE.index(
        "import './styles/WorkplaceHub.css'"
    ) < MAIN_SOURCE.index("import './index.css'")
    assert ".workplace-hub-shell" in STYLES
    assert ".workplace-hub-card" in STYLES
    assert ".workplace-hub-hero" in STYLES
