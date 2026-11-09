import json
import time

OCR_PATH = "full_ocr_result.json"
OUTPUT_PATH = "field_mapping_result.json"

with open(OCR_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


def normalize(text):
    return "".join(text.split())


def find_exact_anchor(target):
    for item in data:
        if normalize(item["text"]) == normalize(target):
            return item
    return None


def find_split_anchor(target):
    chars = []

    for item in data:
        text = normalize(item["text"])

        if len(text) == 1 and text in target:
            chars.append(item)

    for start in chars:
        if normalize(start["text"]) != target[0]:
            continue

        sequence = [start]
        current = start
        success = True

        for expected_char in target[1:]:
            _, cy1, cx2, cy2 = current["bbox"]

            current_center_y = (cy1 + cy2) / 2
            current_h = cy2 - cy1

            candidates = []

            for item in chars:
                if normalize(item["text"]) != expected_char:
                    continue

                x1, y1, _, y2 = item["bbox"]
                center_y = (y1 + y2) / 2

                if x1 < cx2 - current_h * 0.3:
                    continue

                if abs(center_y - current_center_y) > current_h:
                    continue

                gap = x1 - cx2

                if gap > current_h * 1.5:
                    continue

                candidates.append(item)

            if not candidates:
                success = False
                break

            current = min(
                candidates,
                key=lambda x: x["bbox"][0]
            )

            sequence.append(current)

        if success:
            combined = "".join(
                normalize(x["text"]) for x in sequence
            )

            if combined != target:
                continue

            x1 = min(x["bbox"][0] for x in sequence)
            y1 = min(x["bbox"][1] for x in sequence)
            x2 = max(x["bbox"][2] for x in sequence)
            y2 = max(x["bbox"][3] for x in sequence)

            return {
                "text": target,
                "bbox": [x1, y1, x2, y2],
                "method": "split_anchor"
            }

    if target == "보증금":
        for item in data:
            if normalize(item["text"]) != "보증":
                continue
            x1,y1,x2,y2 = item["bbox"]
            h = max(y2-y1,1)
            for other in data:
                if normalize(other["text"]) != "금":
                    continue
                nx1,ny1,nx2,ny2 = other["bbox"]
                if -0.2*h <= nx1-x2 <= 2*h and abs((ny1+ny2-y1-y2)/2) <= h:
                    return {"text":target,"bbox":[x1,min(y1,ny1),nx2,max(y2,ny2)],"method":"split_anchor"}
    if target == "보증금":
        starts = [item for item in data if normalize(item["text"]) in ("보", "보중", "보통")]
        ends = [item for item in data if normalize(item["text"]) == "금"]
        for first in starts:
            x1,y1,x2,y2 = first["bbox"]
            h = max(y2-y1,1)
            matches = []
            for last in ends:
                nx1,ny1,nx2,ny2 = last["bbox"]
                gap = nx1-x2
                cy_diff = abs((ny1+ny2-y1-y2)/2)
                if -0.3*h <= gap <= 4*h and cy_diff <= h:
                    matches.append((abs(gap-h),last))
            if matches:
                last = min(matches,key=lambda v:v[0])[1]
                nx1,ny1,nx2,ny2 = last["bbox"]
                return {"text":target,"bbox":[x1,min(y1,ny1),nx2,max(y2,ny2)],"method":"partial_anchor"}
    return None


# --------------------------------------------------
# 소재지
# --------------------------------------------------
def extract_address():
    anchor = find_exact_anchor("소재지")

    if anchor is None:
        return {
            "value": None,
            "anchor_found": False,
            "anchor_bbox": None,
            "value_roi": None
        }

    ax1, ay1, ax2, ay2 = anchor["bbox"]

    anchor_w = ax2 - ax1
    anchor_h = ay2 - ay1

    # 주소는 길이가 다양하므로 짧은 라벨 너비의 6배로 제한하지 않는다.
    # 페이지 너비를 추정할 수 없는 1차 OCR만 있으므로 충분히 넓은
    # 상대 ROI를 만들고 실제 이미지 경계는 파이프라인에서 자른다.
    roi = [
        int(ax2),
        int(ay1 - anchor_h * 1.2),
        int(ax2 + anchor_w * 16.0),
        int(ay2 + anchor_h * 0.5)
    ]

    candidates = []

    for item in data:
        if item is anchor:
            continue

        x1, y1, x2, y2 = item["bbox"]
        cx = (x1 + x2) / 2

        overlap_y = max(
            0,
            min(ay2, y2) - max(ay1, y1)
        )

        candidate_h = y2 - y1

        overlap_ratio = (
            overlap_y / candidate_h
            if candidate_h > 0
            else 0
        )

        if (
            roi[0] <= cx <= roi[2]
            and overlap_ratio >= 0.5
        ):
            candidates.append(item)

    candidates.sort(key=lambda x: x["bbox"][0])

    value = (
        " ".join(item["text"] for item in candidates)
        if candidates else None
    )

    return {
        "value": value,
        "anchor_found": True,
        "anchor_bbox": anchor["bbox"],
        "value_roi": roi
    }


# --------------------------------------------------
# 임대인 / 임차인 성명
# --------------------------------------------------
def extract_party_name(party):
    party_anchor = find_exact_anchor(party)

    if party_anchor is None:
        return {
            "value": None,
            "anchor_found": False,
            "anchor_bbox": None,
            "value_roi": None
        }

    _, py1, _, py2 = party_anchor["bbox"]

    name_anchors = []

    for item in data:
        if normalize(item["text"]) != "성명":
            continue

        _, y1, _, y2 = item["bbox"]
        cy = (y1 + y2) / 2

        if py1 <= cy <= py2 + (py2 - py1) * 0.5:
            name_anchors.append(item)

    if not name_anchors:
        return {
            "value": None,
            "anchor_found": False,
            "anchor_bbox": party_anchor["bbox"],
            "value_roi": None
        }

    name_anchor = min(
        name_anchors,
        key=lambda x: abs(
            (x["bbox"][1] + x["bbox"][3]) / 2 - py2
        )
    )

    nx1, ny1, nx2, ny2 = name_anchor["bbox"]
    name_w = nx2 - nx1
    name_h = ny2 - ny1

    # 이름 칸이 OCR의 '성명' 라벨보다 훨씬 넓을 수 있으므로
    # 수평 범위를 확장한다. 세로는 인접 행 유입을 피하도록 유지한다.
    roi = [
        int(nx2),
        int(ny1 - name_h * 2.0),
        int(nx2 + name_w * 7.0),
        int(ny2 + name_h * 0.5)
    ]

    candidates = []

    for item in data:
        if item is name_anchor:
            continue

        x1, y1, x2, y2 = item["bbox"]

        if x1 <= nx2:
            continue

        overlap_y = max(
            0,
            min(ny2, y2) - max(ny1, y1)
        )

        candidate_h = y2 - y1

        overlap_ratio = (
            overlap_y / candidate_h
            if candidate_h > 0
            else 0
        )

        if (
            overlap_ratio >= 0.5
            and x1 <= roi[2]
        ):
            candidates.append(item)

    candidates.sort(key=lambda x: x["bbox"][0])

    candidates = [
        item for item in candidates
        if normalize(item["text"]) not in ["(인)", "인)"]
    ]

    value = candidates[0]["text"] if candidates else None

    return {
        "value": value,
        "anchor_found": True,
        "anchor_bbox": name_anchor["bbox"],
        "value_roi": roi
    }


# --------------------------------------------------
# 보증금 / 계약금
# --------------------------------------------------
def extract_amount(target):
    anchor = find_exact_anchor(target)
    method = "exact_anchor"

    if anchor is None:
        anchor = find_split_anchor(target)
        method = "split_anchor"

    if anchor is None:
        return {
            "value": None,
            "anchor_found": False,
            "anchor_bbox": None,
            "value_roi": None,
            "anchor_method": None
        }

    ax1, ay1, ax2, ay2 = anchor["bbox"]

    anchor_h = ay2 - ay1
    anchor_w = ax2 - ax1
    anchor_center_y = (ay1 + ay2) / 2

    # 1차 OCR 값 bbox로 ROI를 축소하면 누락된 글자가 영구히 잘린다.
    # Anchor 기준 행 전체를 유지하고, 2차 OCR에서 값을 선택한다.
    roi = [
        int(ax2),
        int(ay1 - anchor_h * 0.8),
        int(ax2 + anchor_w * 6.5),
        int(ay2 + anchor_h * 0.8)
    ]

    candidates = []

    for item in data:
        x1, y1, x2, y2 = item["bbox"]

        if x1 <= ax2:
            continue

        center_y = (y1 + y2) / 2

        if abs(center_y - anchor_center_y) > anchor_h:
            continue

        if x1 > roi[2]:
            continue

        text = normalize(item["text"])

        if text == "금":
            continue

        candidates.append(item)

    def candidate_score(item):
        x1, y1, x2, y2 = item["bbox"]
        overlap = max(0, min(ay2, y2) - max(ay1, y1))
        overlap_ratio = overlap / max(1, min(anchor_h, y2-y1))
        text = normalize(item["text"])
        amount_like = any(ch in text for ch in "억천백십만")
        return (amount_like, overlap_ratio, -abs((y1+y2)/2-anchor_center_y), -x1)

    candidates = [item for item in candidates if any(ch in normalize(item["text"]) for ch in "억천백십만")]
    candidates.sort(key=candidate_score, reverse=True)
    value = candidates[0]["text"] if candidates else None

    return {
        "value": value,
        "anchor_found": True,
        "anchor_bbox": anchor["bbox"],
        "value_roi": roi,
        "anchor_method": method
    }


# --------------------------------------------------
# 실행
# --------------------------------------------------
start_time = time.perf_counter()

results = {
    "소재지": extract_address(),
    "임대인_성명": extract_party_name("임대인"),
    "임차인_성명": extract_party_name("임차인"),
    "보증금": extract_amount("보증금"),
    "계약금": extract_amount("계약금")
}

elapsed = time.perf_counter() - start_time


print("\n===== Anchor-ROI Field Mapping =====")

for field, result in results.items():
    print(f"\n[{field}]")
    print("Value:", result["value"])
    print("Anchor:", result["anchor_bbox"])
    print("Value ROI:", result["value_roi"])

print(f"\n처리시간: {elapsed:.6f} sec")


output = {
    "image": "sample.jpg",
    "fields": results,
    "processing_time_sec": elapsed
}

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        output,
        f,
        ensure_ascii=False,
        indent=2
    )

print(f"\n저장 완료: {OUTPUT_PATH}")
