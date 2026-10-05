"""HL7 FHIR R4 and Jeevandata Clinical Intake Interoperability Adapter.

Enables bidirectional synchronization between Jeevandata AI Kiosk intake sessions
(FHIR R4 Bundles / SOAP Briefs) and the WellCare Hospital System patient and
consultation records.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.wellcare.database import Database
from src.wellcare.logger import logger


@dataclass
class IngestionResult:
    """Outcome of a FHIR or Jeevandata intake ingestion transaction."""

    success: bool
    patient_id: int | None = None
    record_id: int | None = None
    appointment_id: int | None = None
    message: str = ""
    errors: list[str] = field(default_factory=list)


class FHIRAdapter:
    """Bidirectional interoperability adapter for FHIR R4 and Jeevandata intake data."""

    @staticmethod
    def _parse_input(data: dict[str, Any] | str) -> dict[str, Any]:
        """Normalize JSON string or dictionary into a parsed dictionary."""
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                if not isinstance(parsed, dict):
                    raise ValueError("Payload must be a JSON object")
                return parsed
            except Exception as e:
                raise ValueError(f"Invalid JSON string: {e}") from e
        elif isinstance(data, dict):
            return data
        raise TypeError(f"Expected dict or JSON str, got {type(data).__name__}")

    @classmethod
    def ingest_bundle(
        cls,
        bundle_data: dict[str, Any] | str,
        db: Database | None = None,
    ) -> IngestionResult:
        """Ingest a standard FHIR R4 Bundle into WellCare records.

        Parses Patient, Encounter, and Observation resources, creating or updating
        the patient and generating a clinical consultation medical record.
        """
        try:
            bundle = cls._parse_input(bundle_data)
        except Exception as e:
            return IngestionResult(success=False, message=str(e), errors=[str(e)])

        if bundle.get("resourceType") != "Bundle":
            return IngestionResult(
                success=False,
                message="Resource is not a FHIR Bundle",
                errors=["Expected resourceType='Bundle'"],
            )

        entries = bundle.get("entry", [])
        if not isinstance(entries, list) or not entries:
            return IngestionResult(
                success=False,
                message="FHIR Bundle contains no entries",
                errors=["Bundle.entry must be a non-empty list"],
            )

        patient_res: dict[str, Any] | None = None
        encounter_res: dict[str, Any] | None = None
        observations: list[dict[str, Any]] = []

        for entry in entries:
            resource = entry.get("resource", {}) if isinstance(entry, dict) else {}
            res_type = resource.get("resourceType")
            if res_type == "Patient" and patient_res is None:
                patient_res = resource
            elif res_type == "Encounter" and encounter_res is None:
                encounter_res = resource
            elif res_type == "Observation":
                observations.append(resource)

        if not patient_res:
            return IngestionResult(
                success=False,
                message="Missing Patient resource in FHIR Bundle",
                errors=["No resource with resourceType='Patient' found"],
            )

        # Extract Demographics
        demographics = cls._extract_demographics_from_fhir_patient(patient_res)

        # Extract Clinical Findings
        clinical_data = cls._extract_clinical_from_encounter_and_obs(encounter_res, observations)

        return cls._persist_intake_to_db(
            demographics=demographics,
            clinical_data=clinical_data,
            source="FHIR R4 Bundle",
            db=db,
        )

    @classmethod
    def ingest_jeevandata_brief(
        cls,
        brief_data: dict[str, Any] | str,
        db: Database | None = None,
    ) -> IngestionResult:
        """Ingest a native Jeevandata SOAP intake brief or sync payload."""
        try:
            payload = cls._parse_input(brief_data)
        except Exception as e:
            return IngestionResult(success=False, message=str(e), errors=[str(e)])

        # Support both raw sync input and dashboard SOAP brief formats
        demos = payload.get("patientDemographics", {})
        intake = payload.get("intakeData", {})
        soap = payload.get("soapBrief", payload.get("brief", {}))

        # Handle demographic extraction
        raw_name = str(demos.get("name") or payload.get("patientName") or "Intake Patient").strip()
        name_parts = raw_name.split()
        first_name = name_parts[0] if name_parts else "Intake"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        age = str(demos.get("age") or payload.get("age") or "0")
        gender = str(demos.get("gender") or payload.get("gender") or "Other")
        mobile = str(demos.get("mobile") or payload.get("mobile") or "")
        email = str(demos.get("email") or payload.get("email") or "")
        address = str(demos.get("address") or payload.get("address") or "")
        pincode = str(demos.get("pincode") or payload.get("pincode") or "")

        # Symptoms
        symptoms_list = intake.get("symptoms", [])
        if isinstance(symptoms_list, list) and symptoms_list:
            formatted_syms = ", ".join(
                f"{s.get('name', 'Symptom')} (Sev: {s.get('severity', 'N/A')}/10)"
                if isinstance(s, dict)
                else str(s)
                for s in symptoms_list
            )
        else:
            formatted_syms = str(
                intake.get("chiefComplaint") or payload.get("chiefComplaint") or ""
            )

        demographics = {
            "first_name": first_name,
            "last_name": last_name,
            "age": age,
            "gender": gender,
            "blood_group": str(demos.get("blood_group") or "O+"),
            "weight": str(demos.get("weight") or "0.0"),
            "mobile": mobile,
            "email": email,
            "address": address,
            "pincode": pincode,
            "symptoms": formatted_syms,
        }

        # Build consultation record fields
        subjective = soap.get("subjective", "") if isinstance(soap, dict) else ""
        objective = soap.get("objective", "") if isinstance(soap, dict) else ""
        assessment = soap.get("assessment", "") if isinstance(soap, dict) else ""
        plan = soap.get("plan", "") if isinstance(soap, dict) else ""

        chief = intake.get("chiefComplaint") or formatted_syms or "Clinical Intake"
        diagnosis = assessment or f"Triage Assessment: {chief}"
        treatment = plan or "Awaiting physician consultation"
        notes = (
            f"Jeevandata Kiosk Intake\n"
            f"Subjective: {subjective or 'N/A'}\n"
            f"Objective: {objective or 'N/A'}\n"
            f"Chief Complaint: {chief}"
        )

        clinical_data = {
            "doctor_name": "Jeevandata AI Triage",
            "diagnosis": diagnosis,
            "treatment": treatment,
            "notes": notes,
        }

        return cls._persist_intake_to_db(
            demographics=demographics,
            clinical_data=clinical_data,
            source="Jeevandata SOAP Brief",
            db=db,
        )

    @classmethod
    def export_patient_to_fhir(
        cls,
        patient_id: int,
        db: Database | None = None,
    ) -> dict[str, Any]:
        """Export a WellCare patient record and consultation history as a FHIR R4 Bundle."""
        should_close = False
        if db is None:
            db = Database()
            should_close = True

        try:
            patient = db.get_patient_by_id(patient_id)
            if not patient:
                raise ValueError(f"Patient #{patient_id} not found")

            records = db.get_patient_medical_history(patient_id)

            bundle_id = f"bundle-patient-{patient_id}-{int(datetime.now().timestamp())}"
            entries: list[dict[str, Any]] = []

            # 1. Patient Resource
            patient_entry = {
                "resource": {
                    "resourceType": "Patient",
                    "id": str(patient.id),
                    "identifier": [
                        {"system": "https://wellcare.hospital/patients", "value": str(patient.id)}
                    ],
                    "name": [
                        {
                            "use": "official",
                            "family": patient.last_name or "",
                            "given": [patient.first_name] if patient.first_name else [],
                        }
                    ],
                    "telecom": [{"system": "phone", "value": patient.mobile, "use": "mobile"}]
                    if patient.mobile
                    else [],
                    "gender": (patient.gender or "other").lower(),
                    "address": [
                        {
                            "text": patient.address or "",
                            "postalCode": patient.pincode or "",
                        }
                    ]
                    if patient.address or patient.pincode
                    else [],
                },
                "request": {"method": "PUT", "url": f"Patient/{patient.id}"},
            }
            entries.append(patient_entry)

            # 2. Medical Records -> Encounter & Observation Resources
            for rec in records:
                # rec format: (id, patient_id, patient_name, doctor_name,
                #              diagnosis, treatment, notes, visit_date)
                rec_id = rec[0]
                doc_name = rec[3] or "Attending Physician"
                diagnosis = rec[4] or ""
                treatment = rec[5] or ""
                notes = rec[6] or ""
                visit_date = str(rec[7] or datetime.now().isoformat())

                encounter_entry = {
                    "resource": {
                        "resourceType": "Encounter",
                        "id": f"encounter-{rec_id}",
                        "status": "finished",
                        "subject": {"reference": f"Patient/{patient.id}"},
                        "participant": [{"individual": {"display": doc_name}}],
                        "period": {"start": visit_date},
                        "reasonCode": [{"text": diagnosis}],
                    },
                    "request": {"method": "PUT", "url": f"Encounter/encounter-{rec_id}"},
                }
                entries.append(encounter_entry)

                if notes or treatment:
                    obs_entry = {
                        "resource": {
                            "resourceType": "Observation",
                            "id": f"obs-{rec_id}",
                            "status": "final",
                            "subject": {"reference": f"Patient/{patient.id}"},
                            "effectiveDateTime": visit_date,
                            "code": {"text": "Clinical Consultation Notes & Treatment"},
                            "valueString": f"Treatment: {treatment}\nNotes: {notes}".strip(),
                        },
                        "request": {"method": "PUT", "url": f"Observation/obs-{rec_id}"},
                    }
                    entries.append(obs_entry)

            return {
                "resourceType": "Bundle",
                "id": bundle_id,
                "type": "transaction",
                "entry": entries,
            }
        finally:
            if should_close:
                db.close()

    # ── Private Helpers ────────────────────────────────────────────────────────

    @classmethod
    def _extract_demographics_from_fhir_patient(cls, patient_res: dict[str, Any]) -> dict[str, str]:
        """Extract WellCare demographic dictionary from FHIR Patient resource."""
        names = patient_res.get("name", [])
        first_name = "Patient"
        last_name = ""

        if isinstance(names, list) and names:
            name_obj = names[0] if isinstance(names[0], dict) else {}
            given_list = name_obj.get("given", [])
            if isinstance(given_list, list) and given_list:
                first_name = str(given_list[0])
            last_name = str(name_obj.get("family", ""))

        mobile = ""
        telecoms = patient_res.get("telecom", [])
        if isinstance(telecoms, list):
            for tel in telecoms:
                if isinstance(tel, dict) and tel.get("system") == "phone":
                    mobile = str(tel.get("value", ""))
                    break

        address = ""
        pincode = ""
        addr_list = patient_res.get("address", [])
        if isinstance(addr_list, list) and addr_list:
            addr_obj = addr_list[0] if isinstance(addr_list[0], dict) else {}
            address = str(addr_obj.get("text", ""))
            pincode = str(addr_obj.get("postalCode", ""))

        raw_gender = str(patient_res.get("gender", "")).capitalize()
        gender = raw_gender if raw_gender in ("Male", "Female") else "Other"

        # Calculate or extract age
        age = "0"
        birth_date_str = str(patient_res.get("birthDate", ""))
        if birth_date_str:
            try:
                b_year = int(birth_date_str.split("-")[0])
                age = str(max(0, datetime.now().year - b_year))
            except Exception:
                age = "0"

        return {
            "first_name": first_name,
            "last_name": last_name,
            "age": age,
            "gender": gender,
            "blood_group": "O+",
            "weight": "0.0",
            "mobile": mobile,
            "email": "",
            "address": address,
            "pincode": pincode,
            "symptoms": "",
        }

    @classmethod
    def _extract_clinical_from_encounter_and_obs(
        cls,
        encounter: dict[str, Any] | None,
        observations: list[dict[str, Any]],
    ) -> dict[str, str]:
        """Aggregate Encounter reason and Observations into diagnostic history."""
        diagnosis = "Clinical Intake"
        if encounter:
            reasons = encounter.get("reasonCode", [])
            if isinstance(reasons, list) and reasons:
                first_reason = reasons[0] if isinstance(reasons[0], dict) else {}
                diagnosis = str(first_reason.get("text") or diagnosis)

        obs_findings: list[str] = []
        for obs in observations:
            if not isinstance(obs, dict):
                continue
            code_text = obs.get("code", {}).get("text", "Finding")
            val = obs.get("valueString") or obs.get("valueQuantity", {}).get("value") or ""
            obs_findings.append(f"{code_text}: {val}" if val else code_text)

        symptoms_str = "; ".join(obs_findings) if obs_findings else "General Consultation"
        treatment = "Initial triage completed via Jeevandata FHIR bridge"
        notes = f"FHIR Ingestion Findings:\n{symptoms_str}"

        return {
            "doctor_name": "Jeevandata Kiosk Ingestion",
            "diagnosis": diagnosis,
            "treatment": treatment,
            "notes": notes,
        }

    @classmethod
    def _persist_intake_to_db(
        cls,
        demographics: dict[str, str],
        clinical_data: dict[str, str],
        source: str,
        db: Database | None = None,
    ) -> IngestionResult:
        """Helper to create patient and medical record in database."""
        should_close = False
        if db is None:
            db = Database()
            should_close = True

        try:
            # Check if patient already exists by phone or name
            mobile = demographics.get("mobile", "").strip()
            first_name = demographics.get("first_name", "").strip()
            last_name = demographics.get("last_name", "").strip()

            existing_patient_id: int | None = None
            if mobile and db.cur:
                db.cur.execute("SELECT id FROM patients WHERE mobile = ?", (mobile,))
                row = db.cur.fetchone()
                if row:
                    existing_patient_id = int(row[0])

            if existing_patient_id is None:
                # Insert new patient
                data_tuple = (
                    first_name,
                    last_name,
                    demographics.get("age", "0"),
                    demographics.get("gender", "Other"),
                    demographics.get("blood_group", "O+"),
                    demographics.get("weight", "0.0"),
                    mobile,
                    demographics.get("email", ""),
                    demographics.get("address", ""),
                    demographics.get("pincode", ""),
                    demographics.get("symptoms", clinical_data.get("diagnosis", "")),
                )
                success = db.add_patient(data_tuple)
                if not success or db.cur is None:
                    return IngestionResult(
                        success=False,
                        message="Failed to insert patient into database",
                        errors=["Database insertion error"],
                    )
                patient_id = int(db.cur.lastrowid or 0)
            else:
                patient_id = existing_patient_id

            # Add Medical Record
            record_id = db.add_medical_record(
                patient_id=patient_id,
                doctor_name=clinical_data.get("doctor_name", "Jeevandata AI Triage"),
                diagnosis=clinical_data.get("diagnosis", "Intake Consultation"),
                treatment=clinical_data.get("treatment", "Triage Completed"),
                notes=clinical_data.get("notes", f"Imported from {source}"),
            )

            db.log_action(
                "system",
                "FHIR_INTAKE_INGESTED",
                f"Ingested {source} for patient #{patient_id} (MedicalRecord #{record_id})",
            )

            logger.info("Successfully ingested %s for patient #%d", source, patient_id)
            return IngestionResult(
                success=True,
                patient_id=patient_id,
                record_id=record_id,
                message=f"Successfully ingested {source} for patient #{patient_id}",
            )
        except Exception as e:
            logger.error("Error during intake persistence: %s", e)
            return IngestionResult(
                success=False,
                message=f"Persistence error: {e}",
                errors=[str(e)],
            )
        finally:
            if should_close:
                db.close()
