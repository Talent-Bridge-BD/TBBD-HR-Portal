from repositories.medical_examination import SqlMedicalExaminationRepository
from repositories.onboarding import SqlOnboardingRepository
from repositories.ticketing import SqlTicketingRepository
from repositories.visa_processing import SqlVisaProcessingRepository


class DeploymentReadinessService:
    LOCAL_COUNTRY = "bangladesh"

    def __init__(
        self,
        onboarding_repository: SqlOnboardingRepository,
        medical_repository: SqlMedicalExaminationRepository,
        visa_repository: SqlVisaProcessingRepository,
        ticketing_repository: SqlTicketingRepository,
    ):
        self.onboarding_repository = onboarding_repository
        self.medical_repository = medical_repository
        self.visa_repository = visa_repository
        self.ticketing_repository = ticketing_repository

    def check(
        self,
        organization_id: str,
        application_id: str,
        destination_country: str | None,
        target_onboarding_status: str | None = None,
    ) -> dict:
        onboarding_records = self.onboarding_repository.list_by_application(
            application_id,
        )
        medical_records = self.medical_repository.list_by_application(
            organization_id,
            application_id,
        )
        visa_records = self.visa_repository.list_by_application(
            organization_id,
            application_id,
        )
        ticketing_records = self.ticketing_repository.list_by_application(
            application_id,
        )

        overseas = self._is_overseas(destination_country)

        onboarding = onboarding_records[0] if onboarding_records else None
        medical = medical_records[0] if medical_records else None
        visa = visa_records[0] if visa_records else None
        ticketing = ticketing_records[0] if ticketing_records else None

        prerequisites = [
            {
                "name": "Onboarding",
                "status": (
                    "complete"
                    if target_onboarding_status == "Completed"
                    or (onboarding and onboarding.status == "Completed")
                    else "pending"
                    if onboarding
                    else "missing"
                ),
                "required": True,
            }
        ]

        if overseas:
            prerequisites.extend(
                [
                    {
                        "name": "Medical examination",
                        "status": (
                            "complete"
                            if (
                                medical
                                and medical.status == "Completed"
                                and medical.result == "Fit"
                            )
                            else "pending"
                            if medical
                            else "missing"
                        ),
                        "required": True,
                    },
                    {
                        "name": "Visa processing",
                        "status": (
                            "complete"
                            if visa and visa.status == "Approved"
                            else "pending"
                            if visa
                            else "missing"
                        ),
                        "required": True,
                    },
                    {
                        "name": "Ticketing",
                        "status": (
                            "complete"
                            if ticketing and ticketing.status == "Completed"
                            else "pending"
                            if ticketing
                            else "missing"
                        ),
                        "required": True,
                    },
                ]
            )

        incomplete = [
            prerequisite
            for prerequisite in prerequisites
            if prerequisite["required"]
            and prerequisite["status"] != "complete"
        ]

        next_step = (
            incomplete[0]["name"]
            if incomplete
            else None
        )

        return {
            "ready": not incomplete,
            "overseas": overseas,
            "prerequisites": prerequisites,
            "next_step": next_step,
        }

    @classmethod
    def _is_overseas(
        cls,
        destination_country: str | None,
    ) -> bool:
        if not destination_country:
            return False

        return destination_country.strip().lower() != cls.LOCAL_COUNTRY
