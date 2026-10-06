import re

from .rules import get_field_risk, get_confidence_threshold


def check_format(field: str, text: str) -> bool:
    """
    필드별 기본 형식을 검사한다.
    """

    text = text.strip()

    # 빈 문자열
    if not text:
        return False

    # 금액 필드
    if field in ["deposit", "monthly_rent"]:
        # OCR에서 숫자와 혼동하기 쉬운 문자 검사
        suspicious_chars = ["O", "o", "I", "l"]

        if any(char in text for char in suspicious_chars):
            return False

        # 금액 표현에서 허용할 문자 제거
        cleaned = (
            text.replace("원", "")
            .replace(",", "")
            .replace(" ", "")
        )

        # 나머지가 숫자로만 구성되어 있어야 함
        return cleaned.isdigit()

    # 날짜 필드
    if field == "contract_date":
        date_pattern = r"^\d{4}[-./]\d{1,2}[-./]\d{1,2}$"
        return bool(re.match(date_pattern, text))

    # 이름, 주소 등은 비어있지 않으면 통과
    return True


def validate_ocr(field: str, text: str, confidence: float) -> dict:
    """
    OCR 결과를 검증하고
    PASS / RECHECK / BLOCK 상태를 반환한다.
    """

    risk = get_field_risk(field)
    threshold = get_confidence_threshold(field)

    reasons = []

    # 1. OCR confidence 검사
    if confidence < threshold:
        reasons.append(
            f"Low OCR confidence ({confidence:.2f} < {threshold:.2f})"
        )

    # 2. 필드 형식 검사
    format_valid = check_format(field, text)

    if not format_valid:
        reasons.append("Invalid field format")

    # 3. 최종 상태 결정
    if confidence < 0.50 or not text.strip():
        status = "BLOCK"
    elif reasons:
        status = "RECHECK"
    else:
        status = "PASS"

    return {
        "field": field,
        "text": text,
        "confidence": confidence,
        "risk_level": risk,
        "threshold": threshold,
        "format_valid": format_valid,
        "status": status,
        "reasons": reasons,
    }