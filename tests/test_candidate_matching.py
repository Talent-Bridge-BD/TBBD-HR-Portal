from services.candidate_matching import score_candidate


def test_complete_matching_evidence_returns_explainable_score():
    candidate = {
        "skills": ["Welding", "Blueprint Reading"],
        "years_experience": 5,
        "qualifications": ["Trade Certificate"],
        "certifications": ["Safety Certificate"],
        "preferences": {
            "preferred_employment_type": "Full-time",
            "preferred_location": "Saudi Arabia",
            "expected_salary": 1000,
            "currency": "SAR",
            "available_for_recruitment": True,
        },
        "languages": ["English"],
    }
    job = {
        "required_skills": ["Welding", "Blueprint Reading"],
        "minimum_experience_years": 3,
        "required_qualifications": ["Trade Certificate"],
        "required_certifications": ["Safety Certificate"],
        "employment_type": "Full-time",
        "country": "Saudi Arabia",
        "salary_currency": "SAR",
        "salary_min": 800,
        "salary_max": 1200,
        "required_languages": ["English"],
    }

    result = score_candidate(candidate, job)

    assert result["score"] == 100
    assert result["category"] == "Strong"
    assert result["scoring_version"] == "pilot-v1"
    assert result["automatic_rejection"] is False
    assert set(result["factors"]) == {
        "skills", "experience", "qualifications",
        "preferences", "languages", "readiness",
    }
    assert result["warnings"] == []


def test_missing_requirements_are_not_treated_as_satisfied():
    result = score_candidate(
        {"skills": ["Welding"]},
        {},
    )

    assert result["category"] == "Needs review"
    assert result["automatic_rejection"] is False
    assert result["warnings"]
    assert result["factors"]["skills"]["score"] is None
    assert result["factors"]["experience"]["score"] is None


def test_partial_skill_match_is_explained():
    result = score_candidate(
        {"skills": ["Welding"]},
        {"required_skills": ["Welding", "Blueprint Reading"]},
    )

    assert result["factors"]["skills"]["score"] == 50
    assert result["factors"]["skills"]["points"] == 15
    assert result["automatic_rejection"] is False


def test_salary_comparison_is_skipped_for_different_currencies():
    result = score_candidate(
        {
            "preferences": {
                "expected_salary": 1000,
                "currency": "BDT",
                "available_for_recruitment": True,
            }
        },
        {
            "salary_currency": "SAR",
            "salary_min": 800,
            "salary_max": 1200,
        },
    )

    assert any("currencies differ" in warning for warning in result["warnings"])
    assert result["automatic_rejection"] is False


def test_incomplete_match_reports_evidence_coverage():
    result = score_candidate(
        {"skills": ["Welding"]},
        {"required_skills": ["Welding", "Blueprint Reading"]},
    )

    assert result["score"] == 15
    assert result["category"] == "Needs review"
    assert result["evidence_coverage_pct"] == 30
    assert result["provisional_score"] == 50
    assert result["score_type"] == "provisional"
    assert result["automatic_rejection"] is False


def test_complete_match_reports_full_evidence_coverage():
    candidate = {
        "skills": ["Welding"],
        "years_experience": 3,
        "qualifications": ["Trade Certificate"],
        "preferences": {
            "preferred_employment_type": "Full-time",
            "available_for_recruitment": True,
        },
        "languages": ["English"],
    }
    job = {
        "required_skills": ["Welding"],
        "minimum_experience_years": 2,
        "required_qualifications": ["Trade Certificate"],
        "employment_type": "Full-time",
        "required_languages": ["English"],
    }

    result = score_candidate(candidate, job)

    assert result["evidence_coverage_pct"] == 100
    assert result["provisional_score"] == result["score"] == 100
    assert result["score_type"] == "complete"
    assert result["automatic_rejection"] is False
