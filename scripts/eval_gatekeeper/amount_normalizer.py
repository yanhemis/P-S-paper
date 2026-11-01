import re

DIGITS = {
    "일": 1, "이": 2, "삼": 3, "사": 4, "오": 5,
    "육": 6, "칠": 7, "팔": 8, "구": 9,
}
SMALL_UNITS = {"십": 10, "백": 100, "천": 1000}
BIG_UNITS = {"만": 10000, "억": 100000000, "조": 1000000000000}


def normalize_amount(text):
    """금액을 원 단위 숫자 문자열로 변환한다. 해석 불가 시 None."""
    if text is None:
        return None

    s = re.sub(r"\s+", "", str(text)).replace(",", "")

    if s.startswith("금"):
        s = s[1:]

    if s.endswith("원정"):
        s = s[:-2]
    elif s.endswith("원"):
        s = s[:-1]

    if not s:
        return None

    if re.fullmatch(r"\d+", s):
        return str(int(s))

    tokens = re.findall(r"\d+|[일이삼사오육칠팔구십백천만억조]", s)

    # 금액 이외 문장이나 알 수 없는 글자가 있으면 변환하지 않는다.
    if "".join(tokens) != s:
        return None

    total = 0
    section = 0
    pending = None
    last_small = 10000
    last_big = 10000000000000000

    for token in tokens:
        if token.isdigit() or token in DIGITS:
            if pending is not None:
                return None
            pending = int(token) if token.isdigit() else DIGITS[token]

        elif token in SMALL_UNITS:
            unit = SMALL_UNITS[token]
            if unit >= last_small:
                return None
            section += (pending if pending is not None else 1) * unit
            pending = None
            last_small = unit

        elif token in BIG_UNITS:
            unit = BIG_UNITS[token]
            if unit >= last_big:
                return None
            chunk = section + (pending if pending is not None else 0)
            total += (chunk if chunk else 1) * unit
            section = 0
            pending = None
            last_small = 10000
            last_big = unit

    total += section + (pending if pending is not None else 0)
    return str(total)


if __name__ == "__main__":
    cases = {
        "일천팔백만": "18000000",
        "일백만": "1000000",
        "이천오백만": "25000000",
        "오십만": "500000",
        "삼천이백만": "32000000",
        "사천일백만": "41000000",
        "1백만": "1000000",
        "금 오백만원정": "5000000",
        "1,800만원": "18000000",
        "소십만": None,
        "일벽만": None,
        "이전오백만": None,
        "일천팔백만계약시에지급하고영수함": None,
        "": None,
    }

    for raw, expected in cases.items():
        actual = normalize_amount(raw)
        assert actual == expected, (raw, expected, actual)

    print(f"금액 정규화 테스트 {len(cases)}개 통과")
