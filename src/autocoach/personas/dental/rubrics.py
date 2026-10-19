"""Evaluation rubrics for dental front desk & patient coordinator training.

Directly derived from the Dental Clinic Standard Operating Procedures (SOP)
and objection handling playbooks. Used post-call to verify trainee performance.
"""

from typing import Any

# Track 1: Price Shopper & Financial Objections Rubric
DENTAL_PRICE_SHOPPER_RUBRIC: dict[str, Any] = {
    "track": "Track 1: Price Shopper & Financials",
    "required_protocols": [
        {
            "id": "dental_cost_rebuttal",
            "topic": "Procedure Cost Inquiries (Root Canal, Crown, Extraction, Filling)",
            "mandatory_criteria": [
                "Explain that cost cannot be accurately quoted over the phone because it depends on tooth condition, swelling, abscess, and diagnosis.",
                "Emphasize that the doctor must complete an examination and diagnosis first to provide an exact treatment plan and cost.",
                "Offer to verify insurance coverage after the doctor's clinical evaluation.",
            ],
            "prohibited_actions": [
                "Quoting a flat arbitrary procedure cost over the phone without clinical examination.",
                "Promising that insurance will cover 100% before checking benefits.",
            ],
        },
        {
            "id": "dental_prepayment_policy",
            "topic": "Prepayment / $1 Card Hold Objection",
            "mandatory_criteria": [
                "Explain that the card hold policy reserves dedicated time in the doctor's schedule specifically for the patient.",
                "Mention that this policy prevents overbooking and reduces patient wait times.",
                "Clarify that the card is NOT charged unless the appointment is missed without notice, and the patient can still pay cash upon arrival.",
            ],
            "prohibited_actions": [
                "Waiving the prepayment policy without following escalation protocol to the office manager.",
                "Arguing with the caller or hanging up abruptly.",
            ],
        },
        {
            "id": "dental_payment_security",
            "topic": "Payment Link Security Verification",
            "mandatory_criteria": [
                "Reassure the caller that the payment portal is fully HIPAA and PCI compliant and encrypted.",
                "Confirm that no one in the office has access to view full card details.",
            ],
        },
    ],
}

# Track 2: Front Desk Operational Compliance Rubric
DENTAL_FRONTDESK_COMPLIANCE_RUBRIC: dict[str, Any] = {
    "track": "Track 2: Front Desk Operational & Office Compliance",
    "required_protocols": [
        {
            "id": "caller_requesting_doctor",
            "topic": "Caller Demanding to Speak with Doctor Directly",
            "mandatory_criteria": [
                "State that the doctor is currently busy with a patient.",
                "Politely ask how the representative can assist or offer to take a detailed message for a callback.",
                "Explain that more details help arrange a faster, more effective callback from the doctor.",
            ],
            "prohibited_actions": [
                "Putting the caller on hold to search for the doctor.",
                "Interrupting doctor chair-time for non-emergency scheduling inquiries.",
            ],
        },
        {
            "id": "remote_worker_transparency",
            "topic": "Curiosity Regarding Remote / Answering Service Role",
            "mandatory_criteria": [
                "Acknowledge curiosity empathetically and professionally.",
                "Explain working remotely to collect necessary preliminary information so the clinic staff can focus 100% on taking care of the patient in the office.",
            ],
        },
        {
            "id": "patient_balance_due",
            "topic": "Patient Has Outstanding Balance Due",
            "mandatory_criteria": [
                "Politely inform the patient of the outstanding balance.",
                "Explain the clinic protocol requiring collection of pending balance before booking new appointments.",
                "Offer payment options to clear the balance.",
            ],
            "prohibited_actions": [
                "Booking the appointment without addressing or resolving the outstanding balance.",
            ],
        },
        {
            "id": "system_outage_handling",
            "topic": "Computer / PMS System Down Protocol",
            "mandatory_criteria": [
                "Buy time professionally while keeping the caller engaged.",
                "If system remains down, collect preliminary patient information and offer a tentative appointment date with a guaranteed callback once the system is restored.",
            ],
        },
    ],
}

# Track 3: Clinical & Appointment Scheduling Objections Rubric
DENTAL_CLINICAL_OBJECTIONS_RUBRIC: dict[str, Any] = {
    "track": "Track 3: Clinical & Appointment Objections",
    "required_protocols": [
        {
            "id": "existing_xrays_policy",
            "topic": "Patient Brought or Has X-Rays from Another Clinic",
            "mandatory_criteria": [
                "Explain that external X-rays must have been taken within the last 6 months to be clinically valid.",
                "Request that the patient email legible, dated digital images at least 48 hours prior to the appointment.",
                "Clarify that if the external images are clear and condition is unchanged, new full sets may not be needed, saving time and cost.",
            ],
            "prohibited_actions": [
                "Blindly guaranteeing that no new X-rays will be charged without the doctor inspecting the existing ones.",
            ],
        },
        {
            "id": "direct_treatment_without_exam",
            "topic": "Patient Requests Direct Treatment Without Doctor Exam ('My last dentist said...')",
            "mandatory_criteria": [
                "Acknowledge the previous dentist's recommendation respectfully.",
                "Explain that each doctor completes their own independent examination and diagnosis before performing treatment.",
                "Inform the patient that depending on the diagnosis and schedule, same-day treatment may or may not be possible.",
            ],
        },
        {
            "id": "medical_clearance_protocol",
            "topic": "Medical Clearance (Pregnancy / Systemic Health Conditions)",
            "mandatory_criteria": [
                "Identify requirement for medical clearance (e.g. OBGYN clearance for pregnant patients, cardiologist clearance).",
                "Collect medical doctor contact details (name, phone, fax, address) before booking treatment.",
            ],
        },
    ],
}

# Track 4: Urgency & Emergency Triage Rubric
DENTAL_EMERGENCY_TRIAGE_RUBRIC: dict[str, Any] = {
    "track": "Track 4: Urgency & Emergency Triage",
    "required_protocols": [
        {
            "id": "create_urgency_infection",
            "topic": "Creating Urgency for Unscheduled Critical Treatment (Root Canal, Fracture, Crown)",
            "mandatory_criteria": [
                "Explain that dental infections and structural fractures flare up unpredictably, often on weekends, holidays, or during travel.",
                "Advise the patient not to delay treatment to avoid painful emergencies and more costly, invasive procedures.",
                "Give interim care guidance: advise the patient not to chew on the affected side.",
            ],
        },
        {
            "id": "after_hours_emergency",
            "topic": "Severe Pain / Office Closed Triage",
            "mandatory_criteria": [
                "Acknowledge patient discomfort with high empathy.",
                "For severe trauma, excessive bleeding, or major facial swelling, advise emergency room (ER) visitation immediately.",
                "Book the earliest available emergency opening for the next business day and flag the file for clinic follow-up.",
            ],
        },
    ],
}

# Track 5: Insurance & Coverage Confusion Rubric
DENTAL_INSURANCE_COPAY_RUBRIC: dict[str, Any] = {
    "track": "Track 5: Insurance & Coverage Confusion",
    "required_protocols": [
        {
            "id": "out_of_network_rebuttal",
            "topic": "Clinic Does Not Accept Patient's Insurance",
            "mandatory_criteria": [
                "Reassure the patient that many patients with that insurance still choose the office due to high-quality personalized care.",
                "Present alternative savings options: office membership club, in-house discount plans, or new patient specials.",
            ],
        },
        {
            "id": "maxed_out_benefits",
            "topic": "Patient Insurance Benefits Maxed Out",
            "mandatory_criteria": [
                "Acknowledge benefit cap and remind patient that preventive treatment prevents far more expensive procedures down the road.",
                "Highlight that even when benefits are maxed, patients still benefit from in-network discounted fee schedules.",
            ],
        },
        {
            "id": "perio_vs_prophy_copay",
            "topic": "Cleaning Covered 100% vs Periodontal Maintenance Copay",
            "mandatory_criteria": [
                "Explain the clinical distinction: standard cleaning is for healthy gums without active disease.",
                "Clarify that Periodontal Maintenance is specialized medical follow-up for diagnosed gum disease/infection, which insurance codes differently with a copay.",
            ],
        },
    ],
}

# Consolidated Registry of Dental Rubrics
DENTAL_RUBRIC_REGISTRY: dict[str, dict[str, Any]] = {
    "dental_price_shopper": DENTAL_PRICE_SHOPPER_RUBRIC,
    "dental_cost_objection": DENTAL_PRICE_SHOPPER_RUBRIC,
    "dental_frontdesk_compliance": DENTAL_FRONTDESK_COMPLIANCE_RUBRIC,
    "dental_doctor_inquiry": DENTAL_FRONTDESK_COMPLIANCE_RUBRIC,
    "dental_clinical_objections": DENTAL_CLINICAL_OBJECTIONS_RUBRIC,
    "dental_xray_objection": DENTAL_CLINICAL_OBJECTIONS_RUBRIC,
    "dental_emergency_triage": DENTAL_EMERGENCY_TRIAGE_RUBRIC,
    "dental_toothache": DENTAL_EMERGENCY_TRIAGE_RUBRIC,
    "dental_insurance_copay": DENTAL_INSURANCE_COPAY_RUBRIC,
    "dental_perio_copay": DENTAL_INSURANCE_COPAY_RUBRIC,
    "dental_scheduling": DENTAL_PRICE_SHOPPER_RUBRIC,  # Default flagship preset
}
