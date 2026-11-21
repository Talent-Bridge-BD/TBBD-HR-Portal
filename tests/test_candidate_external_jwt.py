from types import SimpleNamespace

from starlette.requests import Request

from services import local_auth


def make_bearer_request(token="test-candidate-token"):
    return Request({
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [
            (b"authorization", f"Bearer {token}".encode("ascii")),
        ],
        "query_string": b"",
    })


def install_candidate_jwt_stubs(monkeypatch, verified_claims):
    decode_calls = []

    def fake_decode(token, *args, **kwargs):
        decode_calls.append((token, args, kwargs))

        # The first decode selects the fixed validator using the
        # unverified issuer. The second performs verified decoding.
        if kwargs.get("options", {}).get("verify_signature") is False:
            return {"iss": local_auth.CANDIDATE_EXTERNAL_ISSUER}

        return verified_claims

    class FakeJWKClient:
        def __init__(self, url):
            self.url = url

        def get_signing_key_from_jwt(self, token):
            return SimpleNamespace(key="test-signing-key")

    monkeypatch.setattr(local_auth.jwt, "decode", fake_decode)
    monkeypatch.setattr(local_auth.jwt, "PyJWKClient", FakeJWKClient)

    return decode_calls


def base_verified_claims(**overrides):
    claims = {
        "iss": local_auth.CANDIDATE_EXTERNAL_ISSUER,
        "aud": local_auth.CANDIDATE_EXTERNAL_CLIENT_ID,
        "scp": local_auth.CANDIDATE_EXTERNAL_SCOPE,
        "oid": "candidate-object-001",
        "preferred_username": "candidate@example.test",
    }
    claims.update(overrides)
    return claims


def test_candidate_jwt_preserves_verified_candidate_role(monkeypatch):
    claims = base_verified_claims(roles=["Candidate"])
    install_candidate_jwt_stubs(monkeypatch, claims)

    principal = local_auth._get_candidate_external_id_principal(
        make_bearer_request()
    )

    assert principal is not None
    assert principal["id"] == "candidate-object-001"
    assert principal["roles"] == ["Candidate"]
    assert {
        "typ": "roles",
        "val": "Candidate",
    } in principal["claims"]
    assert {
        "typ": "tid",
        "val": local_auth.CANDIDATE_EXTERNAL_TENANT_ID,
    } in principal["claims"]


def test_candidate_jwt_without_roles_does_not_synthesize_candidate(monkeypatch):
    claims = base_verified_claims()
    install_candidate_jwt_stubs(monkeypatch, claims)

    principal = local_auth._get_candidate_external_id_principal(
        make_bearer_request()
    )

    assert principal is not None
    assert principal["roles"] == []
    assert not any(
        claim.get("typ") == "roles"
        for claim in principal["claims"]
    )


def test_candidate_jwt_ignores_invalid_role_values(monkeypatch):
    claims = base_verified_claims(
        roles=[
            "Candidate",
            "",
            "   ",
            None,
            123,
            {},
        ]
    )
    install_candidate_jwt_stubs(monkeypatch, claims)

    principal = local_auth._get_candidate_external_id_principal(
        make_bearer_request()
    )

    assert principal is not None
    assert principal["roles"] == ["Candidate"]
    assert [
        claim["val"]
        for claim in principal["claims"]
        if claim.get("typ") == "roles"
    ] == ["Candidate"]


def test_candidate_jwt_ignores_non_list_roles_claim(monkeypatch):
    claims = base_verified_claims(roles="Candidate")
    install_candidate_jwt_stubs(monkeypatch, claims)

    principal = local_auth._get_candidate_external_id_principal(
        make_bearer_request()
    )

    assert principal is not None
    assert principal["roles"] == []
    assert not any(
        claim.get("typ") == "roles"
        for claim in principal["claims"]
    )


def test_candidate_jwt_rejects_token_without_required_scope(monkeypatch):
    claims = base_verified_claims(scp="profile openid")
    install_candidate_jwt_stubs(monkeypatch, claims)

    principal = local_auth._get_candidate_external_id_principal(
        make_bearer_request()
    )

    assert principal is None


def test_candidate_jwt_uses_expected_signature_issuer_and_audience(monkeypatch):
    claims = base_verified_claims(roles=["Candidate"])
    decode_calls = install_candidate_jwt_stubs(monkeypatch, claims)

    principal = local_auth._get_candidate_external_id_principal(
        make_bearer_request()
    )

    assert principal is not None

    verified_calls = [
        call for call in decode_calls
        if call[2].get("algorithms") is not None
    ]

    assert len(verified_calls) == 1

    _, args, kwargs = verified_calls[0]

    assert args == ("test-signing-key",)
    assert kwargs["algorithms"] == ["RS256"]
    assert kwargs["audience"] == local_auth.CANDIDATE_EXTERNAL_AUDIENCES
    assert kwargs["issuer"] == local_auth.CANDIDATE_EXTERNAL_ISSUER


def test_candidate_jwt_uses_configured_jwks_endpoint(monkeypatch):
    claims = base_verified_claims()
    captured_urls = []

    def fake_decode(token, *args, **kwargs):
        if kwargs.get("options", {}).get("verify_signature") is False:
            return {"iss": local_auth.CANDIDATE_EXTERNAL_ISSUER}
        return claims

    class FakeJWKClient:
        def __init__(self, url):
            captured_urls.append(url)

        def get_signing_key_from_jwt(self, token):
            return SimpleNamespace(key="test-signing-key")

    monkeypatch.setattr(local_auth.jwt, "decode", fake_decode)
    monkeypatch.setattr(local_auth.jwt, "PyJWKClient", FakeJWKClient)

    principal = local_auth._get_candidate_external_id_principal(
        make_bearer_request()
    )

    assert principal is not None
    assert captured_urls == [local_auth.CANDIDATE_EXTERNAL_JWKS_URL]