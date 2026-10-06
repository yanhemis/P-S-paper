from ocr_guardrail.guardrail import validate_ocr


test_cases = [
    {
        "field": "deposit",
        "text": "50,000,000원",
        "confidence": 0.96,
    },
    {
        "field": "deposit",
        "text": "5O,OOO,OOO원",
        "confidence": 0.76,
    },
    {
        "field": "contract_date",
        "text": "2026.10.06",
        "confidence": 0.87,
    },
    {
        "field": "address",
        "text": "서울특별시 노원구",
        "confidence": 0.84,
    },
    {
        "field": "monthly_rent",
        "text": "",
        "confidence": 0.32,
    },
]


for case in test_cases:
    result = validate_ocr(
        field=case["field"],
        text=case["text"],
        confidence=case["confidence"],
    )

    print("=" * 50)
    print(f"Field      : {result['field']}")
    print(f"Text       : {result['text']}")
    print(f"Confidence : {result['confidence']}")
    print(f"Risk       : {result['risk_level']}")
    print(f"Threshold  : {result['threshold']}")
    print(f"Format     : {result['format_valid']}")
    print(f"Status     : {result['status']}")
    print(f"Reasons    : {result['reasons']}")