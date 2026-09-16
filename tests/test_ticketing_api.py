from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import api.ticketing as ticketing_api
from models.ticketing import Ticketing


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(ticketing_api.router)

    ticketing_api._repository = MagicMock()
    ticketing_api._service = ticketing_api.TicketingService(
        ticketing_api._repository
    )

    return TestClient(app)


def sample_ticketing():
    return Ticketing(
        id="ticket-001",
        application_id="application-001",
        airline_name="Qatar Airways",
        flight_number="QR641",
        booking_reference="ABC123",
        ticket_number="1571234567890",
        departure_airport="DAC",
        arrival_airport="DOH",
        departure_datetime=datetime(2026, 10, 1, 10, 30),
        arrival_datetime=datetime(2026, 10, 1, 13, 45),
        status="Issued",
        ticket_document_reference="tickets/QR641.pdf",
        notes="Confirmed travel itinerary",
    )


def test_list_ticketing(client):
    ticket = sample_ticketing()

    ticketing_api._repository.list_by_application.return_value = [
        ticket
    ]

    response = client.get(
        "/api/ticketing",
        params={"application_id": "application-001"},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["application_id"] == "application-001"
    assert data[0]["airline_name"] == "Qatar Airways"
    assert data[0]["status"] == "Issued"


def test_create_ticketing(client):
    ticket = sample_ticketing()

    ticketing_api._repository.create.return_value = ticket

    response = client.post(
        "/api/ticketing",
        json={
            "application_id": "application-001",
            "airline_name": "Qatar Airways",
            "flight_number": "QR641",
            "booking_reference": "ABC123",
            "ticket_number": "1571234567890",
            "departure_airport": "DAC",
            "arrival_airport": "DOH",
            "departure_datetime": "2026-10-01T10:30:00",
            "arrival_datetime": "2026-10-01T13:45:00",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["airline_name"] == "Qatar Airways"
    assert data["flight_number"] == "QR641"
    assert data["status"] == "Issued"

    ticketing_api._repository.create.assert_called_once()


def test_get_ticketing(client):
    ticket = sample_ticketing()

    ticketing_api._repository.get.return_value = ticket

    response = client.get("/api/ticketing/ticket-001")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "ticket-001"
    assert data["booking_reference"] == "ABC123"


def test_get_ticketing_not_found(client):
    ticketing_api._repository.get.return_value = None

    response = client.get("/api/ticketing/missing-ticket")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticketing record not found"


def test_update_ticketing(client):
    ticket = sample_ticketing()

    ticketing_api._repository.update.return_value = ticket

    response = client.put(
        "/api/ticketing/ticket-001",
        json={
            "airline_name": "Qatar Airways",
            "flight_number": "QR641",
            "booking_reference": "ABC123",
            "ticket_number": "1571234567890",
            "departure_airport": "DAC",
            "arrival_airport": "DOH",
            "departure_datetime": "2026-10-01T10:30:00",
            "arrival_datetime": "2026-10-01T13:45:00",
            "status": "Issued",
            "ticket_document_reference": "tickets/QR641.pdf",
            "notes": "Confirmed travel itinerary",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "Issued"
    assert data["ticket_document_reference"] == "tickets/QR641.pdf"

    ticketing_api._repository.update.assert_called_once()


def test_update_ticketing_invalid_status(client):
    response = client.put(
        "/api/ticketing/ticket-001",
        json={
            "status": "Invalid Status",
        },
    )

    assert response.status_code == 400
    assert "Invalid ticketing status" in response.json()["detail"]


def test_update_ticketing_not_found(client):
    ticketing_api._repository.update.side_effect = ValueError(
        "Ticketing record not found"
    )

    response = client.put(
        "/api/ticketing/missing-ticket",
        json={
            "status": "Completed",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticketing record not found"
