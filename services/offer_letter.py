from io import BytesIO
from datetime import date, datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _format_date(value: Any) -> str:
    if not value:
        return "—"

    if isinstance(value, datetime):
        return value.strftime("%d %B %Y")

    if isinstance(value, date):
        return value.strftime("%d %B %Y")

    return str(value)


def _format_salary(amount: Any, currency: Any) -> str:
    if amount is None:
        return "Not specified"

    try:
        formatted_amount = f"{float(amount):,.2f}"
    except (TypeError, ValueError):
        formatted_amount = str(amount)

    return (
        f"{formatted_amount} {str(currency).strip()}"
        if currency
        else formatted_amount
    )


def _candidate_name(application: Any) -> str:
    first_name = getattr(application, "candidate_first_name", "") or ""
    last_name = getattr(application, "candidate_last_name", "") or ""

    name = " ".join(
        part.strip()
        for part in (first_name, last_name)
        if part and part.strip()
    )

    return name or "Candidate"


def _paragraph(
    text: str,
    style: ParagraphStyle,
) -> Paragraph:
    return Paragraph(str(text), style)


def generate_offer_letter(
    organization_name: str,
    application: Any,
    offer: dict,
) -> bytes:
    """
    Generate an offer-letter PDF from the existing hiring application
    and job offer data.

    This function is intentionally side-effect free:
    it does not write to the database and does not send the offer.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="Employment Offer Letter",
        author=organization_name,
    )

    styles = getSampleStyleSheet()

    organization_style = ParagraphStyle(
        "OfferOrganization",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=5 * mm,
    )

    heading_style = ParagraphStyle(
        "OfferHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0067B8"),
        spaceAfter=9 * mm,
    )

    body_style = ParagraphStyle(
        "OfferBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4 * mm,
    )

    label_style = ParagraphStyle(
        "OfferLabel",
        parent=body_style,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=0,
    )

    value_style = ParagraphStyle(
        "OfferValue",
        parent=body_style,
        spaceAfter=0,
    )

    terms_style = ParagraphStyle(
        "OfferTerms",
        parent=body_style,
        fontSize=9.5,
        leading=14,
    )

    story = []

    story.append(
        _paragraph(
            organization_name or "Organization",
            organization_style,
        )
    )

    story.append(
        _paragraph(
            "EMPLOYMENT OFFER LETTER",
            heading_style,
        )
    )

    story.append(
        _paragraph(
            f"Dear {_candidate_name(application)},",
            body_style,
        )
    )

    story.append(
        _paragraph(
            (
                f"We are pleased to offer you the position of "
                f"<b>{offer.get('offer_title') or getattr(application, 'job_title', 'Employment Position')}</b> "
                f"with {organization_name or 'our organization'}."
            ),
            body_style,
        )
    )

    details = [
        [
            _paragraph("Candidate", label_style),
            _paragraph(_candidate_name(application), value_style),
        ],
        [
            _paragraph("Email", label_style),
            _paragraph(
                getattr(application, "candidate_email", None) or "—",
                value_style,
            ),
        ],
        [
            _paragraph("Position", label_style),
            _paragraph(
                getattr(application, "job_title", None) or "—",
                value_style,
            ),
        ],
        [
            _paragraph("Employment Type", label_style),
            _paragraph(
                offer.get("employment_type") or "—",
                value_style,
            ),
        ],
        [
            _paragraph("Compensation", label_style),
            _paragraph(
                _format_salary(
                    offer.get("salary_amount"),
                    offer.get("salary_currency"),
                ),
                value_style,
            ),
        ],
        [
            _paragraph("Start Date", label_style),
            _paragraph(
                _format_date(offer.get("start_date")),
                value_style,
            ),
        ],
        [
            _paragraph("Offer Expiry", label_style),
            _paragraph(
                _format_date(offer.get("offer_expiry_date")),
                value_style,
            ),
        ],
    ]

    details_table = Table(
        details,
        colWidths=[45 * mm, 105 * mm],
        hAlign="LEFT",
    )

    details_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F8FAFC"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#E2E8F0"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#E2E8F0"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(details_table)
    story.append(Spacer(1, 7 * mm))

    story.append(
        _paragraph(
            "<b>Terms & Conditions</b>",
            body_style,
        )
    )

    terms = offer.get("terms_and_conditions")

    story.append(
        _paragraph(
            terms.strip() if terms and terms.strip() else "No additional terms specified.",
            terms_style,
        )
    )

    story.append(Spacer(1, 9 * mm))

    story.append(
        _paragraph(
            (
                "Please review the terms of this offer carefully. "
                "This offer letter is generated from the employment offer "
                "record maintained in the TBBD HR Portal."
            ),
            body_style,
        )
    )

    story.append(Spacer(1, 14 * mm))

    signature_data = [
        [
            _paragraph("____________________________", body_style),
            _paragraph("____________________________", body_style),
        ],
        [
            _paragraph(
                "Authorized Representative",
                label_style,
            ),
            _paragraph(
                "Candidate",
                label_style,
            ),
        ],
        [
            _paragraph(
                organization_name or "Organization",
                value_style,
            ),
            _paragraph(
                _candidate_name(application),
                value_style,
            ),
        ],
    ]

    signature_table = Table(
        signature_data,
        colWidths=[75 * mm, 75 * mm],
        hAlign="LEFT",
    )

    signature_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    story.append(signature_table)

    document.build(story)

    return buffer.getvalue()
