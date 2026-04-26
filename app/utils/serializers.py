def serialize_disease(disease):
    return {
        "id": disease.id,
        "code": disease.code,
        "name": disease.name,
        "description": disease.description,
        "is_active": disease.is_active,
    }


def serialize_symptom(symptom):
    return {
        "id": symptom.id,
        "code": symptom.code,
        "name": symptom.name,
        "description": symptom.description,
        "symptom_type": symptom.symptom_type,
        "is_alarm": symptom.is_alarm,
        "disease_id": symptom.disease_id,
    }


def serialize_risk_factor(risk_factor):
    return {
        "id": risk_factor.id,
        "code": risk_factor.code,
        "name": risk_factor.name,
        "description": risk_factor.description,
        "disease_id": risk_factor.disease_id,
    }


def serialize_evaluation(evaluation):
    return {
        "id": evaluation.id,
        "disease_id": evaluation.disease_id,
        "user_id": evaluation.user_id,
        "systolic": evaluation.systolic,
        "diastolic": evaluation.diastolic,
        "symptoms": evaluation.symptoms_json,
        "risk_factors": evaluation.risk_factors_json,
        "pressure_category": evaluation.pressure_category,
        "risk_level": evaluation.risk_level,
        "prediagnosis": evaluation.prediagnosis,
        "recommendation": evaluation.recommendation,
        "matched_rules": evaluation.matched_rules,
        "created_at": evaluation.created_at.isoformat(),
    }


def serialize_user(user):
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "created_at": user.created_at.isoformat(),
    }


def serialize_profile(profile):
    return {
        "birth_date": profile.birth_date,
        "gender": profile.gender,
        "weight_kg": profile.weight_kg,
        "height_m": profile.height_m,
        "blood_type": profile.blood_type,
        "diagnosis": profile.diagnosis,
        "diagnosis_notes": profile.diagnosis_notes,
    }


def serialize_medication(medication):
    return {
        "id": medication.id,
        "name": medication.name,
        "dose": medication.dose,
        "time": medication.time,
        "frequency": medication.frequency,
        "notes": medication.notes,
        "is_active": medication.is_active,
        "last_taken_at": medication.last_taken_at.isoformat() if medication.last_taken_at else None,
        "created_at": medication.created_at.isoformat(),
    }


def serialize_contact(contact):
    return {
        "id": contact.id,
        "full_name": contact.full_name,
        "relationship": contact.relationship,
        "phone": contact.phone,
    }


def serialize_notification_preferences(pref):
    return {
        "critical_alerts": pref.critical_alerts,
        "ai_trends": pref.ai_trends,
        "medication_reminders": pref.medication_reminders,
        "missed_doses": pref.missed_doses,
        "daily_measurement": pref.daily_measurement,
        "health_tips": pref.health_tips,
    }