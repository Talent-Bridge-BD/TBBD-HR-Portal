from repositories.candidate import SqlCandidateRepository

class RecruitmentPipelineRepository(SqlCandidateRepository):

    def get_pipeline_counts(self):
        with self._connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    workflow_status,
                    COUNT(*) AS total
                FROM dbo.candidates
                GROUP BY workflow_status
            """)

            rows = cursor.fetchall()

            pipeline = {
                "Applied": 0,
                "Screening": 0,
                "Interview": 0,
                "Trade Test": 0,
                "Medical": 0,
                "Visa Processing": 0,
                "Ticketing": 0,
                "Onboarding": 0,
                "Deployment": 0,
                "Completed": 0,
            }

            for row in rows:
                pipeline[row.workflow_status] = row.total

            return pipeline
