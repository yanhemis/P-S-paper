# OCR Guardrail - validation rules
# OCR 결과의 필드 중요도에 따라 검증 기준을 다르게 적용한다.

# 필드별 위험도
FIELD_RISK = {
    # 낮은 위험도
    "name": "LOW",

    # 중간 위험도
    "address": "MEDIUM",
    "contract_date": "MEDIUM",

    # 높은 위험도
    "deposit": "HIGH",
    "monthly_rent": "HIGH",
}

# 위험도별 OCR confidence 기준
CONFIDENCE_THRESHOLD = {
    "LOW": 0.70,
    "MEDIUM": 0.80,
    "HIGH": 0.90,
}


def get_field_risk(field: str) -> str:
    """
    필드의 위험도를 반환한다.

    정의되지 않은 필드는 안전을 위해
    기본적으로 MEDIUM으로 처리한다.
    """
    return FIELD_RISK.get(field, "MEDIUM")


def get_confidence_threshold(field: str) -> float:
    """
    해당 필드가 통과하기 위해 필요한
    최소 OCR confidence를 반환한다.
    """
    risk = get_field_risk(field)
    return CONFIDENCE_THRESHOLD[risk]