from app.system.knowledge_base import RECOMMENDATIONS


def classify_blood_pressure(systolic: int, diastolic: int) -> dict:
    is_isolated_systolic = systolic >= 140 and diastolic < 90

    if systolic >= 180 or diastolic >= 110:
        return {
            "pressure_category_code": "grade_3_hypertension",
            "pressure_category_label": "Hipertensión grado III",
            "is_isolated_systolic": is_isolated_systolic,
        }

    if 160 <= systolic <= 179 or 100 <= diastolic <= 109:
        return {
            "pressure_category_code": "grade_2_hypertension",
            "pressure_category_label": "Hipertensión grado II",
            "is_isolated_systolic": is_isolated_systolic,
        }

    if 140 <= systolic <= 159 or 90 <= diastolic <= 99:
        return {
            "pressure_category_code": "grade_1_hypertension",
            "pressure_category_label": "Hipertensión grado I",
            "is_isolated_systolic": is_isolated_systolic,
        }

    if 130 <= systolic <= 139 or 85 <= diastolic <= 89:
        return {
            "pressure_category_code": "high_normal",
            "pressure_category_label": "Alta normal",
            "is_isolated_systolic": False,
        }

    if 120 <= systolic <= 129 or 80 <= diastolic <= 84:
        return {
            "pressure_category_code": "normal",
            "pressure_category_label": "Normal",
            "is_isolated_systolic": False,
        }

    return {
        "pressure_category_code": "optimal",
        "pressure_category_label": "Óptima",
        "is_isolated_systolic": False,
    }


def evaluate_case(systolic: int, diastolic: int, symptoms: list[str], risk_factors: list[str]) -> dict:
    symptom_set = set(symptoms)
    risk_factor_count = len(risk_factors)

    pressure_data = classify_blood_pressure(systolic, diastolic)
    pressure_category = pressure_data["pressure_category_code"]
    matched_rules = [f"pressure_{pressure_category}"]

    if pressure_data["is_isolated_systolic"]:
        matched_rules.append("isolated_systolic_pattern")

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
            "pressure_category": pressure_data["pressure_category_code"],
            "pressure_category_label": pressure_data["pressure_category_label"],
            "is_isolated_systolic": pressure_data["is_isolated_systolic"],
            "risk_level": "urgent",
            "prediagnosis": "Posible crisis hipertensiva o complicación cardiovascular aguda.",
            "recommendation": RECOMMENDATIONS["urgent"],
            "matched_rules": matched_rules,
        }

    if neuro_alarm:
        return {
            "pressure_category": pressure_data["pressure_category_code"],
            "pressure_category_label": pressure_data["pressure_category_label"],
            "is_isolated_systolic": pressure_data["is_isolated_systolic"],
            "risk_level": "urgent",
            "prediagnosis": "Posibles signos neurológicos de alarma asociados a riesgo cardiovascular.",
            "recommendation": RECOMMENDATIONS["urgent"],
            "matched_rules": matched_rules,
        }

    if pressure_category == "stage_2":
        return {
            "pressure_category": pressure_data["pressure_category_code"],
            "pressure_category_label": pressure_data["pressure_category_label"],
            "is_isolated_systolic": pressure_data["is_isolated_systolic"],
            "risk_level": "high",
            "prediagnosis": "Alto riesgo cardiovascular asociado a hipertensión.",
            "recommendation": RECOMMENDATIONS["high"],
            "matched_rules": matched_rules,
        }

    if pressure_category == "stage_1" and risk_factor_count >= 2:
        return {
            "pressure_category": pressure_data["pressure_category_code"],
            "pressure_category_label": pressure_data["pressure_category_label"],
            "is_isolated_systolic": pressure_data["is_isolated_systolic"],
            "risk_level": "high",
            "prediagnosis": "Riesgo cardiovascular elevado debido a hipertensión y múltiples factores de riesgo.",
            "recommendation": RECOMMENDATIONS["high"],
            "matched_rules": matched_rules,
        }

    if pressure_category in {"stage_1", "elevated"} or risk_factor_count >= 2 or warning_symptoms:
        return {
            "pressure_category": pressure_data["pressure_category_code"],
            "pressure_category_label": pressure_data["pressure_category_label"],
            "is_isolated_systolic": pressure_data["is_isolated_systolic"],
            "risk_level": "moderate",
            "prediagnosis": "Riesgo cardiovascular moderado. Se recomienda monitoreo y seguimiento médico.",
            "recommendation": RECOMMENDATIONS["moderate"],
            "matched_rules": matched_rules,
        }

    return {
        "pressure_category": pressure_data["pressure_category_code"],
        "pressure_category_label": pressure_data["pressure_category_label"],
        "is_isolated_systolic": pressure_data["is_isolated_systolic"],
        "risk_level": "low",
        "prediagnosis": "No se detectaron signos fuertes de riesgo cardiovascular inmediato.",
        "recommendation": RECOMMENDATIONS["low"],
        "matched_rules": matched_rules,
    }