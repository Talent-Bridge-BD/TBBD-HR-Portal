from services.authorization import AuthorizationContext
from repositories.candidate import SqlCandidateRepository


class RecruitmentPipelineRepository(SqlCandidateRepository):

    PIPELINE_STAGES = (
        "Applied",
        "Screening",
        "Interview",
        "Trade Test",
        "Medical",
        "Visa Processing",
        "Ticketing",
        "Onboarding",
        "Deployment",
        "Completed",
    )

    def get_pipeline_counts(self, context: AuthorizationContext):
        pipeline = {stage: 0 for stage in self.PIPELINE_STAGES}

        if not context.is_global_administrator and not context.organization_ids:
            return pipeline

        with self._connection() as connection:
            cursor = connection.cursor()

            if context.is_global_administrator:
                cursor.execute("""
                    SELECT
                        workflow_status,
                        COUNT(*) AS total
                    FROM dbo.candidates
                    GROUP BY workflow_status
                """)
            else:
                organization_ids = tuple(context.organization_ids)

                if not organization_ids:
                    return pipeline

                placeholders = ", ".join("?" for _ in organization_ids)

                cursor.execute(
                    f"""
                        SELECT
                            c.workflow_status,
                            COUNT(*) AS total
                        FROM dbo.candidates AS c
                        WHERE EXISTS (
                            SELECT 1
                            FROM dbo.applications AS a
                            INNER JOIN dbo.jobs AS j
                                ON j.id = a.job_id
                            WHERE a.candidate_id = c.id
                              AND j.organization_id IN ({placeholders})
                        )
                        GROUP BY c.workflow_status
                    """,
                    organization_ids,
                )

            rows = cursor.fetchall()

            for row in rows:
                if row.workflow_status in pipeline:
                    pipeline[row.workflow_status] = row.total

        return pipeline
