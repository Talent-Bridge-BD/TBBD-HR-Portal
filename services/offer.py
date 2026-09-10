from repositories.offer import OfferRepository


class OfferService:

    def __init__(self, repository: OfferRepository):
        self.repository = repository

    def list_offers(
        self,
        organization_id: str,
    ):
        return self.repository.list_offers(
            organization_id,
        )

    def get_offer(
        self,
        organization_id: str,
        offer_id: str,
    ):
        return self.repository.get_offer(
            organization_id,
            offer_id,
        )

    def create_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_date,
        expiry_date,
        start_date,
        employment_type: str,
        salary_compensation: str,
        currency: str,
        location: str,
        notes: str,
    ):
        return self.repository.create_offer(
            organization_id,
            application_id,
            offer_date,
            expiry_date,
            start_date,
            employment_type,
            salary_compensation,
            currency,
            location,
            notes,
        )

    def update_offer(
        self,
        organization_id: str,
        offer_id: str,
        offer_date,
        expiry_date,
        start_date,
        employment_type: str,
        salary_compensation: str,
        currency: str,
        location: str,
        notes: str,
        status: str,
    ):
        return self.repository.update_offer(
            organization_id,
            offer_id,
            offer_date,
            expiry_date,
            start_date,
            employment_type,
            salary_compensation,
            currency,
            location,
            notes,
            status,
        )
