def get_age_band(age_years: int) -> str | None:
    if 40 <= age_years <= 44:
        return "40_44"
    if 45 <= age_years <= 49:
        return "45_49"
    if 50 <= age_years <= 54:
        return "50_54"
    if 55 <= age_years <= 59:
        return "55_59"
    if 60 <= age_years <= 64:
        return "60_64"
    if 65 <= age_years <= 69:
        return "65_69"
    if 70 <= age_years <= 74:
        return "70_74"
    return None


def get_systolic_band(systolic_bp: int) -> str:
    if systolic_bp < 120:
        return "lt_120"
    if systolic_bp < 140:
        return "120_139"
    if systolic_bp < 160:
        return "140_159"
    if systolic_bp < 180:
        return "160_179"
    return "gte_180"


def get_total_cholesterol_band(total_cholesterol_mg_dl: int) -> str:
    mmol = total_cholesterol_mg_dl / 38.67

    if mmol < 4:
        return "lt_4"
    if mmol < 5:
        return "4_4_9"
    if mmol < 6:
        return "5_5_9"
    if mmol < 7:
        return "6_6_9"
    return "gte_7"


def lookup_who_hearts_central_latam_risk(
    *,
    sex: str,
    age_band: str,
    systolic_band: str,
    cholesterol_band: str,
    is_smoker: bool,
    has_diabetes: bool,
) -> dict:
    # TODO: aquí va la tabla completa WHO/HEARTS
    # Placeholder temporal mientras cargamos el lookup real
    score = 0

    if sex == "male":
        score += 1
    if has_diabetes:
        score += 2
    if is_smoker:
        score += 2
    if age_band in {"60_64", "65_69", "70_74"}:
        score += 2
    elif age_band in {"50_54", "55_59"}:
        score += 1

    if systolic_band == "gte_180":
        score += 3
    elif systolic_band == "160_179":
        score += 2
    elif systolic_band == "140_159":
        score += 1

    if cholesterol_band in {"6_6_9", "gte_7"}:
        score += 2
    elif cholesterol_band == "5_5_9":
        score += 1

    if score <= 1:
        return {
            "risk_band_code": "lt_5",
            "risk_band_label": "Riesgo menor a 5% a 10 años",
            "risk_percent_min": 0,
            "risk_percent_max": 5,
        }
    if score <= 3:
        return {
            "risk_band_code": "btw_5_10",
            "risk_band_label": "Riesgo de 5% a menos de 10% a 10 años",
            "risk_percent_min": 5,
            "risk_percent_max": 10,
        }
    if score <= 5:
        return {
            "risk_band_code": "btw_10_20",
            "risk_band_label": "Riesgo de 10% a menos de 20% a 10 años",
            "risk_percent_min": 10,
            "risk_percent_max": 20,
        }
    if score <= 7:
        return {
            "risk_band_code": "btw_20_30",
            "risk_band_label": "Riesgo de 20% a menos de 30% a 10 años",
            "risk_percent_min": 20,
            "risk_percent_max": 30,
        }

    return {
        "risk_band_code": "gte_30",
        "risk_band_label": "Riesgo mayor o igual a 30% a 10 años",
        "risk_percent_min": 30,
        "risk_percent_max": None,
    }


def calculate_10y_cvd_risk_card(
    *,
    sex: str,
    age_years: int,
    systolic_bp: int,
    total_cholesterol_mg_dl: int,
    is_smoker: bool,
    has_diabetes: bool,
) -> dict:
    age_band = get_age_band(age_years)

    if age_band is None:
        return {
            "risk_band_code": "not_available",
            "risk_band_label": "No calculable con esta metodología para esta edad",
            "risk_percent_min": None,
            "risk_percent_max": None,
            "chart_region": "central_latin_america",
            "risk_model": "who_hearts_laboratory_2019",
        }

    systolic_band = get_systolic_band(systolic_bp)
    cholesterol_band = get_total_cholesterol_band(total_cholesterol_mg_dl)

    band = lookup_who_hearts_central_latam_risk(
        sex=sex,
        age_band=age_band,
        systolic_band=systolic_band,
        cholesterol_band=cholesterol_band,
        is_smoker=is_smoker,
        has_diabetes=has_diabetes,
    )

    return {
        **band,
        "chart_region": "central_latin_america",
        "risk_model": "who_hearts_laboratory_2019",
    }