from app.system.knowledge_base import RECOMMENDATIONS


def classify_blood_pressure(systolic: int, diastolic: int) -> str:
    if systolic > 180 or diastolic > 120:
        return "crisis"
    if systolic >= 140 or diastolic >= 90:
        return "stage_2"
    if 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return "stage_1"
    if 120 <= systolic <= 129 and diastolic < 80:
        return "elevated"
    return "normal"


def evaluate_case(systolic: int, diastolic: int, symptoms: list[str], risk_factors: list[str]) -> dict:
    symptom_set = set(symptoms)
    risk_factor_count = len(risk_factors)

    pressure_category = classify_blood_pressure(systolic, diastolic)
    matched_rules = [f"pressure_{pressure_category}"]

    cardiac_alarm = bool({"chest_pain", "shortness_of_breath"} & symptom_set)
    neuro_alarm = bool({"confusion", "trouble_speaking", "one_sided_weakness"} & symptom_set)
    warning_symptoms = bool({
        "palpitations",
        "blurred_vision",
        "severe_headache",
        "dizziness",
        "fatigue",
        "leg_swelling"
    } & symptom_set)

    if cardiac_alarm:
        matched_rules.append("cardiac_alarm_present")

    if neuro_alarm:
        matched_rules.append("neuro_alarm_present")

    if warning_symptoms:
        matched_rules.append("warning_symptoms_present")

    if risk_factor_count >= 2:
        matched_rules.append("multiple_risk_factors")

    if pressure_category == "crisis" and (cardiac_alarm or neuro_alarm or "blurred_vision" in symptom_set):
        return {
            "pressure_category": pressure_category,
            "risk_level": "urgent",
            "prediagnosis": "Posible crisis hipertensiva o complicación cardiovascular aguda.",
            "recommendation": RECOMMENDATIONS["urgent"],
            "matched_rules": matched_rules,
        }

    if neuro_alarm:
        return {
            "pressure_category": pressure_category,
            "risk_level": "urgent",
            "prediagnosis": "Posibles signos neurológicos de alarma asociados a riesgo cardiovascular.",
            "recommendation": RECOMMENDATIONS["urgent"],
            "matched_rules": matched_rules,
        }

    if pressure_category == "stage_2":
        return {
            "pressure_category": pressure_category,
            "risk_level": "high",
            "prediagnosis": "Alto riesgo cardiovascular asociado a hipertensión.",
            "recommendation": RECOMMENDATIONS["high"],
            "matched_rules": matched_rules,
        }

    if pressure_category == "stage_1" and risk_factor_count >= 2:
        return {
            "pressure_category": pressure_category,
            "risk_level": "high",
            "prediagnosis": "Riesgo cardiovascular elevado debido a hipertensión y múltiples factores de riesgo.",
            "recommendation": RECOMMENDATIONS["high"],
            "matched_rules": matched_rules,
        }

    if pressure_category in {"stage_1", "elevated"} or risk_factor_count >= 2 or warning_symptoms:
        return {
            "pressure_category": pressure_category,
            "risk_level": "moderate",
            "prediagnosis": "Riesgo cardiovascular moderado. Se recomienda monitoreo y seguimiento médico.",
            "recommendation": RECOMMENDATIONS["moderate"],
            "matched_rules": matched_rules,
        }

    return {
        "pressure_category": pressure_category,
        "risk_level": "low",
        "prediagnosis": "No se detectaron signos fuertes de riesgo cardiovascular inmediato.",
        "recommendation": RECOMMENDATIONS["low"],
        "matched_rules": matched_rules,
    }