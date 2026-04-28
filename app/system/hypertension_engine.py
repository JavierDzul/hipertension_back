# app/system/hypertension_engine.py

from typing import Any


SYMPTOMS = {
    "headache": "Dolor de cabeza",
    "severe_headache": "Dolor de cabeza intenso",
    "dizziness": "Mareo",
    "blurred_vision": "Visión borrosa",
    "chest_pain": "Dolor en el pecho",
    "shortness_of_breath": "Falta de aire",
    "palpitations": "Palpitaciones",
    "nosebleed": "Sangrado nasal",
    "confusion": "Confusión",
    "fatigue": "Fatiga",
    "nausea": "Náusea",
    "weakness": "Debilidad",
    "anxiety": "Ansiedad",
    "sweating": "Sudoración",
    "edema": "Hinchazón",
}

ALARM_SYMPTOMS = {
    "chest_pain",
    "shortness_of_breath",
    "confusion",
    "weakness",
    "blurred_vision",
    "severe_headache",
}

CATEGORY_SEVERITY = {
    "optimal": 0,
    "normal": 1,
    "high_normal": 2,
    "grade_1": 3,
    "isolated_systolic_hypertension": 3,
    "grade_2": 4,
    "grade_3": 5,
}

CATEGORY_LABELS = {
    "optimal": "Óptima",
    "normal": "Normal",
    "high_normal": "Normal alta",
    "grade_1": "Hipertensión grado I",
    "grade_2": "Hipertensión grado II",
    "grade_3": "Hipertensión grado III",
    "isolated_systolic_hypertension": "Hipertensión sistólica aislada",
}


def classify_systolic(systolic_bp: int) -> str:
    if systolic_bp < 120:
        return "optimal"
    if systolic_bp <= 129:
        return "normal"
    if systolic_bp <= 139:
        return "high_normal"
    if systolic_bp <= 159:
        return "grade_1"
    if systolic_bp <= 179:
        return "grade_2"

    return "grade_3"


def classify_diastolic(diastolic_bp: int) -> str:
    if diastolic_bp < 80:
        return "optimal"
    if diastolic_bp <= 84:
        return "normal"
    if diastolic_bp <= 89:
        return "high_normal"
    if diastolic_bp <= 99:
        return "grade_1"
    if diastolic_bp <= 109:
        return "grade_2"

    return "grade_3"


def get_most_severe_category(systolic_category: str, diastolic_category: str) -> str:
    if CATEGORY_SEVERITY[systolic_category] >= CATEGORY_SEVERITY[diastolic_category]:
        return systolic_category

    return diastolic_category


def normalize_symptoms(symptoms: list[str] | None) -> list[str]:
    if symptoms is None:
        return []

    valid_symptoms = []

    for symptom in symptoms:
        if symptom in SYMPTOMS and symptom not in valid_symptoms:
            valid_symptoms.append(symptom)

    return valid_symptoms


def get_symptom_labels(symptoms: list[str]) -> list[str]:
    return [SYMPTOMS[symptom] for symptom in symptoms if symptom in SYMPTOMS]


def has_alarm_symptoms(symptoms: list[str]) -> bool:
    return bool(set(symptoms).intersection(ALARM_SYMPTOMS))


def build_recommendations(
    category: str,
    symptoms: list[str],
    heart_rate_bpm: int,
) -> list[str]:
    recommendations = [
        "Registre nuevas mediciones en reposo.",
        "Evite automedicarse.",
    ]

    alarm_symptoms_found = has_alarm_symptoms(symptoms)

    if category in {"high_normal", "grade_1"}:
        recommendations.append("Consulte a un profesional de salud para seguimiento.")

    if category in {"grade_2", "grade_3", "isolated_systolic_hypertension"}:
        recommendations.append("Consulte a un profesional de salud lo antes posible.")

    if category == "grade_3":
        recommendations.append(
            "Busque atención médica inmediata si la presión se mantiene elevada o presenta síntomas de alarma."
        )

    if alarm_symptoms_found:
        recommendations.append(
            "Busque atención médica inmediata si presenta dolor en el pecho, falta de aire, confusión, debilidad, visión borrosa o dolor de cabeza intenso."
        )

    if heart_rate_bpm > 100:
        recommendations.append(
            "Los latidos se encuentran elevados; registre el dato en reposo y consulte si se repite."
        )

    if heart_rate_bpm < 50:
        recommendations.append(
            "Los latidos se encuentran bajos; consulte a un profesional de salud si presenta mareo, debilidad o desmayo."
        )

    return recommendations


def evaluate_hypertension_case(
    systolic_bp: int,
    diastolic_bp: int,
    heart_rate_bpm: int,
    symptoms: list[str] | None = None,
) -> dict[str, Any]:
    normalized_symptoms = normalize_symptoms(symptoms)

    systolic_category = classify_systolic(systolic_bp)
    diastolic_category = classify_diastolic(diastolic_bp)
    final_category = get_most_severe_category(systolic_category, diastolic_category)

    is_isolated_systolic = systolic_bp >= 140 and diastolic_bp < 90

    if is_isolated_systolic:
        final_category = "isolated_systolic_hypertension"

    category_label = CATEGORY_LABELS[final_category]

    alarm_symptoms_found = has_alarm_symptoms(normalized_symptoms)

    if alarm_symptoms_found and final_category in {
        "grade_1",
        "grade_2",
        "grade_3",
        "isolated_systolic_hypertension",
    }:
        urgency_level = "high"
    elif final_category == "grade_3":
        urgency_level = "critical"
    elif final_category in {"grade_2", "isolated_systolic_hypertension"}:
        urgency_level = "medium"
    else:
        urgency_level = "low"

    initial_assessment = (
        f"La evaluación inicial sugiere: {category_label}. "
        "Este resultado no sustituye una valoración médica profesional."
    )

    return {
        "bp_category": final_category,
        "bp_category_label": category_label,
        "systolic_category": systolic_category,
        "diastolic_category": diastolic_category,
        "systolic_category_label": CATEGORY_LABELS[systolic_category],
        "diastolic_category_label": CATEGORY_LABELS[diastolic_category],
        "is_isolated_systolic": is_isolated_systolic,
        "has_alarm_symptoms": alarm_symptoms_found,
        "symptoms": normalized_symptoms,
        "symptom_labels": get_symptom_labels(normalized_symptoms),
        "urgency_level": urgency_level,
        "initial_assessment": initial_assessment,
        "recommendations": build_recommendations(
            category=final_category,
            symptoms=normalized_symptoms,
            heart_rate_bpm=heart_rate_bpm,
        ),
    }