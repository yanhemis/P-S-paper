"""
실험 B용 Ground Truth ROI 생성

사용법:
    python make_gt_roi.py <image_path> [<image_path> ...]

양식 PDF를 렌더링한 기준 이미지(gt/template.png) 위에 우선 평가 필드의 칸 좌표를
한 번만 정의해 두고, 각 촬영본과 기준 이미지 사이의 호모그래피(SIFT + RANSAC)로
그 칸을 촬영본 좌표로 옮긴다.

- gt/gt_roi.json            : 이미지별 필드 ROI (4점 quad + 외접 bbox, 원본 이미지 좌표)
- gt/check/<stem>_roi.jpg   : ROI를 원본 위에 그린 확인용 이미지 (육안 검수용)

주의: 이 ROI는 "정답 칸"을 옮긴 것이므로 반드시 check 이미지를 눈으로 검수한 뒤
GT로 사용한다. (ROI 자동 검출 알고리즘이 아니라 GT 라벨링 보조 도구)
"""

import sys
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
GT_DIR = ROOT / "gt"
CHECK_DIR = GT_DIR / "check"
TEMPLATE_PATH = GT_DIR / "template.png"

# 기준 이미지(gt/template.png, 2481x3508, 300dpi) 위의 필드 칸 좌표 [x1, y1, x2, y2].
# 인쇄된 라벨("소재지", "금", "원정 (₩", "성 명" 등)은 제외하고 손글씨가 들어가는 칸만 잡는다.
TEMPLATE_FIELDS = {
    "address": [294, 372, 2418, 434],        # 소재지
    "deposit_kor": [365, 803, 1440, 865],    # 보증금 - 한글 금액 (금 ~ 원정 사이)
    "deposit_num": [1590, 803, 2110, 865],   # 보증금 - 숫자 금액 (₩ ~ ) 사이)
    "down_payment": [365, 865, 1025, 927],   # 계약금 - 한글 금액 (금 ~ 원정은 사이)
    "lessor_name": [1917, 2744, 2215, 2809], # 임대인 성명
    "lessee_name": [1917, 2938, 2215, 3000], # 임차인 성명
}

# 자동 정합이 실패한 칸은 원본 이미지 좌표로 직접 지정한다 (육안 라벨링).
# sample_7(#7 접힘): 인쇄 글자와 표 선이 종이 위에서 한 줄 가까이 어긋나 인쇄돼 있어서
# SIFT 매칭점이 서로 모순되고, 상단 필드의 호모그래피가 크게 틀어진다.
# 하단 성명 칸은 자동 결과가 정확해서 그대로 쓴다.
MANUAL_OVERRIDES = {
    "sample_7.JPG": {
        # 행이 오른쪽으로 갈수록 올라가 있어서 손글씨가 끝나는 지점까지만 잡는다.
        "address": [[630, 530], [1700, 526], [1700, 585], [630, 590]],
        # 이 장은 인쇄 글자 줄이 칸 안을 지나가므로 손글씨가 있는 부분으로 좁힌다.
        "deposit_kor": [[1330, 878], [1700, 878], [1700, 928], [1330, 928]],
        "deposit_num": [[1850, 850], [2330, 850], [2330, 900], [1850, 900]],
        # 계약금은 미기입. "원정은 계약시에" 인쇄 줄 왼쪽 빈칸을 ROI로 둔다.
        "down_payment": [[674, 904], [1283, 904], [1283, 954], [674, 954]],
    },
}

# 매칭용 축소 배율 (원본 4032px 그대로 SIFT를 돌리면 느리고 메모리를 많이 씀)
MATCH_MAX_SIDE = 1600
# 필드별 로컬 호모그래피에 쓸 매칭점 범위(기준 이미지 px)와 최소 개수
LOCAL_BAND = 300
MIN_LOCAL_POINTS = 40


def _resize(img, max_side):
    scale = max_side / max(img.shape[:2])
    if scale >= 1:
        return img, 1.0
    return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA), scale


def find_homography(template_gray, photo_gray):
    """template 좌표 -> photo 좌표 호모그래피와 inlier 수를 반환한다."""
    t_small, t_scale = _resize(template_gray, MATCH_MAX_SIDE)
    p_small, p_scale = _resize(photo_gray, MATCH_MAX_SIDE)

    sift = cv2.SIFT_create(nfeatures=8000)
    kp_t, des_t = sift.detectAndCompute(t_small, None)
    kp_p, des_p = sift.detectAndCompute(p_small, None)

    matcher = cv2.FlannBasedMatcher({"algorithm": 1, "trees": 5}, {"checks": 64})
    good = []
    for pair in matcher.knnMatch(des_t, des_p, k=2):
        if len(pair) == 2 and pair[0].distance < 0.75 * pair[1].distance:
            good.append(pair[0])

    src = np.float32([kp_t[m.queryIdx].pt for m in good]) / t_scale
    dst = np.float32([kp_p[m.trainIdx].pt for m in good]) / p_scale
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 8.0)
    inl = mask.ravel().astype(bool)
    return H, src[inl], dst[inl], len(good)


def local_homography(H_global, src, dst, field_box):
    """필드 주변(세로 ±LOCAL_BAND px)의 inlier 매칭점만으로 호모그래피를 다시 구한다.

    접히거나 구겨진 문서(#7)는 종이가 평면이 아니어서 한 장 전체에 호모그래피 하나를
    쓰면 일부 행이 한 칸 이상 어긋난다. 필드 근처 점만 쓰면 국소적으로 평면에 가까워진다.
    """
    cy = (field_box[1] + field_box[3]) / 2
    near = np.abs(src[:, 1] - cy) < LOCAL_BAND
    if near.sum() < MIN_LOCAL_POINTS:
        return H_global, False
    H, _ = cv2.findHomography(src[near], dst[near], cv2.RANSAC, 5.0)
    return (H, True) if H is not None else (H_global, False)


def project_fields(H_global, src, dst):
    fields = {}
    for name, (x1, y1, x2, y2) in TEMPLATE_FIELDS.items():
        H, is_local = local_homography(H_global, src, dst, (x1, y1, x2, y2))
        quad = np.float32([[x1, y1], [x2, y1], [x2, y2], [x1, y2]]).reshape(-1, 1, 2)
        q = cv2.perspectiveTransform(quad, H).reshape(-1, 2)
        fields[name] = {
            "quad": [[round(float(x)), round(float(y))] for x, y in q],
            "bbox": [
                int(q[:, 0].min()), int(q[:, 1].min()),
                int(q[:, 0].max()), int(q[:, 1].max()),
            ],
            "local_homography": is_local,
        }
    return fields


def draw_check(photo, fields, out_path):
    vis = photo.copy()
    for name, f in fields.items():
        pts = np.int32(f["quad"]).reshape(-1, 1, 2)
        cv2.polylines(vis, [pts], True, (0, 0, 255), 4)
        x, y = f["quad"][0]
        cv2.putText(vis, name, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    cv2.imwrite(str(out_path), vis, [cv2.IMWRITE_JPEG_QUALITY, 80])


def main():
    if len(sys.argv) < 2:
        print("usage: python make_gt_roi.py <image_path> [<image_path> ...]")
        sys.exit(1)

    CHECK_DIR.mkdir(parents=True, exist_ok=True)
    template_gray = cv2.imread(str(TEMPLATE_PATH), cv2.IMREAD_GRAYSCALE)

    out_path = GT_DIR / "gt_roi.json"
    all_rois = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}

    for arg in sys.argv[1:]:
        image_path = Path(arg).resolve()
        photo = cv2.imread(str(image_path))  # EXIF 회전 적용됨 (OCR 결과와 같은 좌표계)
        photo_gray = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)

        H, src, dst, n_good = find_homography(template_gray, photo_gray)
        inliers = len(src)
        fields = project_fields(H, src, dst)
        for name, quad in MANUAL_OVERRIDES.get(image_path.name, {}).items():
            xs = [p[0] for p in quad]
            ys = [p[1] for p in quad]
            fields[name] = {
                "quad": quad,
                "bbox": [min(xs), min(ys), max(xs), max(ys)],
                "local_homography": False,
                "manual": True,
            }
        all_rois[image_path.name] = {
            "image_size": [photo.shape[1], photo.shape[0]],
            "homography_inliers": inliers,
            "homography_matches": n_good,
            "fields": fields,
        }
        draw_check(photo, fields, CHECK_DIR / f"{image_path.stem}_roi.jpg")
        print(f"[ok] {image_path.name}: inliers {inliers}/{n_good}")

    out_path.write_text(json.dumps(all_rois, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
