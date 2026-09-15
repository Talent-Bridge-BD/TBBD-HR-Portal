from repositories.visa_processing import SqlVisaProcessingRepository


class VisaProcessingService:
    def __init__(
        self,
        repository: SqlVisaProcessingRepository,
    ):
        self.repository = repository

    def list_by_application(
        self,
        application_id: str,
    ):
        return self.repository.list_by_application(
            application_id,
        )

    def create(
        self,
        application_id: str,
        test_type: str | None = None,
        scheduled_at=None,
        location: str | None = None,
        assessor_name: str | None = None,
    ):
        return self.repository.create(
            application_id=application_id,
            test_type=test_type,
            scheduled_at=scheduled_at,
            location=location,
            assessor_name=assessor_name,
        )

    def get(
        self,
        visa_processing_id: str,
    ):
        return self.repository.get(
            visa_processing_id,
        )

    PASSING_SCORE = 70

    def update_assessment(
        self,
        visa_processing_id: str,
        technical_knowledge_score: int,
        trade_skills_score: int,
        safety_awareness_score: int,
        tool_handling_score: int,
        communication_score: int,
        problem_solving_score: int,
        teamwork_score: int,
        assessment_notes: str | None = None,
    ):
        scores = {
            "technical_knowledge_score": technical_knowledge_score,
            "trade_skills_score": trade_skills_score,
            "safety_awareness_score": safety_awareness_score,
            "tool_handling_score": tool_handling_score,
            "communication_score": communication_score,
            "problem_solving_score": problem_solving_score,
            "teamwork_score": teamwork_score,
        }

        for field, score in scores.items():
            if not isinstance(score, int) or isinstance(score, bool):
                raise ValueError(f"{field} must be an integer")

            if score < 0 or score > 100:
                raise ValueError(f"{field} must be between 0 and 100")

        total_score = round(sum(scores.values()) / len(scores))

        result = (
            "Pass"
            if total_score >= self.PASSING_SCORE
            else "Fail"
        )

        return self.repository.update_assessment(
            visa_processing_id=visa_processing_id,
            technical_knowledge_score=technical_knowledge_score,
            trade_skills_score=trade_skills_score,
            safety_awareness_score=safety_awareness_score,
            tool_handling_score=tool_handling_score,
            communication_score=communication_score,
            problem_solving_score=problem_solving_score,
            teamwork_score=teamwork_score,
            total_score=total_score,
            result=result,
            status="Completed",
            assessment_notes=assessment_notes,
        )

