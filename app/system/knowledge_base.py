DISEASE_CODE = "HTN_CARDIO"

SYMPTOMS = {
    "chest_pain": {
        "name": "Dolor en el pecho",
        "description": "Dolor o presión en el pecho",
        "type": "alarma_cardiaca",
        "is_alarm": True,
    },
    "shortness_of_breath": {
        "name": "Falta de aire",
        "description": "Dificultad para respirar",
        "type": "alarma_cardiaca",
        "is_alarm": True,
    },
    "palpitations": {
        "name": "Palpitaciones",
        "description": "Latidos rápidos o irregulares",
        "type": "alerta_cardiaca",
        "is_alarm": False,
    },
    "blurred_vision": {
        "name": "Visión borrosa",
        "description": "Dificultad para ver con claridad",
        "type": "alerta_hipertensiva",
        "is_alarm": False,
    },
    "severe_headache": {
        "name": "Dolor de cabeza intenso",
        "description": "Cefalea fuerte o repentina",
        "type": "alerta_hipertensiva",
        "is_alarm": False,
    },
    "dizziness": {
        "name": "Mareo",
        "description": "Sensación de inestabilidad o desmayo",
        "type": "alerta_general",
        "is_alarm": False,
    },
    "fatigue": {
        "name": "Fatiga",
        "description": "Cansancio inusual o excesivo",
        "type": "alerta_general",
        "is_alarm": False,
    },
    "leg_swelling": {
        "name": "Hinchazón en piernas",
        "description": "Inflamación en piernas o tobillos",
        "type": "alerta_cardiaca",
        "is_alarm": False,
    },
    "confusion": {
        "name": "Confusión",
        "description": "Dificultad para pensar o responder con claridad",
        "type": "alarma_neurologica",
        "is_alarm": True,
    },
    "trouble_speaking": {
        "name": "Dificultad para hablar",
        "description": "Problemas para hablar o pronunciar palabras",
        "type": "alarma_neurologica",
        "is_alarm": True,
    },
    "one_sided_weakness": {
        "name": "Debilidad en un lado del cuerpo",
        "description": "Pérdida de fuerza en un lado del cuerpo",
        "type": "alarma_neurologica",
        "is_alarm": True,
    },
}

RISK_FACTORS = {
    "obesity": {
        "name": "Obesidad",
        "description": "Exceso de peso corporal que aumenta el riesgo cardiovascular",
    },
    "smoking": {
        "name": "Tabaquismo",
        "description": "Consumo habitual de tabaco",
    },
    "diabetes": {
        "name": "Diabetes",
        "description": "Antecedente de diabetes mellitus",
    },
    "sedentary_lifestyle": {
        "name": "Sedentarismo",
        "description": "Poca o nula actividad física regular",
    },
    "family_history": {
        "name": "Antecedentes familiares",
        "description": "Antecedentes familiares de hipertensión o enfermedad cardiovascular",
    },
}

RECOMMENDATIONS = {
    "low": "Mantenga hábitos saludables y continúe con chequeos médicos regulares.",
    "moderate": "Monitoree su presión arterial y programe una valoración médica.",
    "high": "Acuda pronto a valoración médica para confirmar la presión arterial y el riesgo cardiovascular.",
    "urgent": "Busque atención médica inmediata.",
}