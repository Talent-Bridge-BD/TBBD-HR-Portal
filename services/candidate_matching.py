"""Explainable candidate-to-job matching; no database or API dependencies."""

from __future__ import annotations

from typing import Any


WEIGHTS = {
    "skills": 30,
    "experience": 20,
    "qualifications": 15,
    "preferences": 15,
    "languages": 10,
    "readiness": 10,
}


def _normalise(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def _items(value: Any) -> set[str]:
    if not isinstance(value, (list, tuple, set)):
        return set()

    result = set()
    for item in value:
        if isinstance(item, dict):
            item = (
                item.get("name")
                or item.get("skill_name")
                or item.get("title")
                or item.get("language_name")
                or ""
            )
        normalised = _normalise(item)
        if normalised:
            result.add(normalised)
    return result


def _ratio(required: set[str], supplied: set[str]) -> float | None:
    if not required:
        return None
    if not supplied:
        return 0.0
    return len(required & supplied) / len(required)


def score_candidate(candidate: dict, job: dict) -> dict:
    """Return a transparent 0–100 score and warnings for incomplete evidence.

    Expected inputs are plain dictionaries. Missing requirements are not
    silently treated as satisfied. This function does not auto-reject anyone.
    """
    candidate = candidate or {}
    job = job or {}
    factors: dict[str, dict] = {}
    warnings: list[str] = []

    def record(name: str, value: float | None, explanation: str) -> None:
        if value is None:
            warnings.append(f"{name}: insufficient data to assess.")
            factors[name] = {
                "weight": WEIGHTS[name],
                "score": None,
                "points": None,
                "explanation": explanation,
            }
            return

        value = max(0.0, min(1.0, value))
        factors[name] = {
            "weight": WEIGHTS[name],
            "score": round(value * 100, 1),
            "points": round(value * WEIGHTS[name], 2),
            "explanation": explanation,
        }

    # Skills: compare explicitly supplied required skills with candidate skills.
    required_skills = _items(job.get("required_skills"))
    candidate_skills = _items(candidate.get("skills"))
    skill_score = _ratio(required_skills, candidate_skills)
    record(
        "skills",
        skill_score,
        "Required skills matched against the candidate's recorded skills."
        if required_skills else "No required skills were supplied for comparison.",
    )

    # Experience: numeric years only; job titles are not assumed equivalent.
    minimum_years = job.get("minimum_experience_years")
    years = candidate.get("years_experience")
    if minimum_years is None:
        experience_score = None
        experience_note = "The job's minimum experience requirement is missing."
    elif years is None:
        experience_score = None
        experience_note = "The candidate's experience duration is missing."
    else:
        try:
            minimum_years = max(0.0, float(minimum_years))
            years = max(0.0, float(years))
            experience_score = 1.0 if minimum_years == 0 else min(
                years / minimum_years, 1.0
            )
            experience_note = (
                f"Recorded experience: {years:g} years; "
                f"job minimum: {minimum_years:g} years."
            )
        except (TypeError, ValueError):
            experience_score = None
            experience_note = "Experience duration could not be interpreted."
    record("experience", experience_score, experience_note)

    # Qualifications: use explicit qualification/certification names.
    required_qualifications = _items(
        job.get("required_qualifications")
    ) | _items(job.get("required_certifications"))
    candidate_qualifications = _items(
        candidate.get("qualifications")
    ) | _items(candidate.get("certifications"))
    qualification_score = _ratio(
        required_qualifications, candidate_qualifications
    )
    record(
        "qualifications",
        qualification_score,
        "Recorded qualifications and certifications compared with job requirements."
        if required_qualifications
        else "No required qualifications or certifications were supplied.",
    )

    # Preferences: only assess dimensions the job explicitly specifies.
    preference = candidate.get("preferences")
    preference = preference if isinstance(preference, dict) else {}
    preference_checks: list[float] = []

    job_type = _normalise(job.get("employment_type"))
    candidate_type = _normalise(preference.get("preferred_employment_type"))
    if job_type and candidate_type:
        preference_checks.append(float(job_type == candidate_type))

    job_country = _normalise(job.get("country"))
    preferred_location = _normalise(preference.get("preferred_location"))
    if job_country and preferred_location:
        preference_checks.append(float(
            job_country in preferred_location
            or preferred_location in job_country
        ))

    job_currency = _normalise(job.get("salary_currency"))
    candidate_currency = _normalise(preference.get("currency"))
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")
    expected_salary = preference.get("expected_salary")

    if expected_salary is not None and job_currency and candidate_currency:
        if job_currency != candidate_currency:
            warnings.append(
                "preferences: salary comparison skipped because currencies differ."
            )
        elif salary_min is not None or salary_max is not None:
            try:
                expected = float(expected_salary)
                low = float(salary_min) if salary_min is not None else 0.0
                high = float(salary_max) if salary_max is not None else float("inf")
                preference_checks.append(float(low <= expected <= high))
            except (TypeError, ValueError):
                warnings.append("preferences: salary data could not be compared.")

    preference_score = (
        sum(preference_checks) / len(preference_checks)
        if preference_checks else None
    )
    record(
        "preferences",
        preference_score,
        "Assessed the supplied employment, location and comparable salary preferences."
        if preference_checks
        else "No comparable candidate preferences and job conditions were available.",
    )

    # Languages: a language match is not a proficiency certification.
    required_languages = _items(job.get("required_languages"))
    candidate_languages = _items(candidate.get("languages"))
    language_score = _ratio(required_languages, candidate_languages)
    record(
        "languages",
        language_score,
        "Required languages compared with recorded candidate languages."
        if required_languages else "No required languages were supplied.",
    )

    # Readiness is based on an explicit availability flag, not passport nationality.
    availability = preference.get("available_for_recruitment")
    if availability is None:
        readiness_score = None
        readiness_note = "Recruitment availability has not been recorded."
    else:
        readiness_score = 1.0 if availability is True else 0.0
        readiness_note = (
            "Candidate is marked available for recruitment."
            if availability is True
            else "Candidate is not currently marked available for recruitment."
        )
    record("readiness", readiness_score, readiness_note)

    # Keep the weighted score separate from the score among assessed factors.
    total_weight = sum(WEIGHTS.values())
    assessed_weight = sum(
        factor["weight"]
        for factor in factors.values()
        if factor["score"] is not None
    )
    points = sum(
        factor["points"] or 0
        for factor in factors.values()
    )

    score = round(points, 1)
    evidence_coverage_pct = round(
        assessed_weight / total_weight * 100, 1
    ) if total_weight else 0.0
    provisional_score = round(
        points / assessed_weight * 100, 1
    ) if assessed_weight else None

    incomplete = assessed_weight < total_weight

    if incomplete:
        category = "Needs review"
    elif score >= 80:
        category = "Strong"
    elif score >= 65:
        category = "Potential"
    else:
        category = "Needs review"

    return {
        "score": score,
        "provisional_score": provisional_score,
        "evidence_coverage_pct": evidence_coverage_pct,
        "score_type": "provisional" if incomplete else "complete",
        "category": category,
        "factors": factors,
        "warnings": warnings,
        "automatic_rejection": False,
        "scoring_version": "pilot-v1",
    }
