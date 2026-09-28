"""
계약서 표 셀 검출 + 병합 셀 복원 파이프라인  (method: opencv_grid_merge)
담당 범위: OpenCV 표선/셀 검출 → merged reconstruction → 표준 cells.json

흐름
  이미지 로드(EXIF 방향 보정) → 기울기 보정(HoughLinesP) → 이진화
  → 수평/수직선 추출(짧은 open → close) → 표 영역 분리(긴 선이 있는 선 묶음)
  → 표별 grid 좌표 → shared boundary 판정 → Union-Find 병합
  → 비직사각형 component 복구 → 검증·실패 분류 → cells.json + 시각화 + 리포트

사용법
  run_pipeline(IMAGE_PATH)            한 장 처리 + 그림 확인
  compare_line_settings(IMAGE_PATH)   선 추출 커널 0.4(이전 코드) vs 작은 값 비교 → 짧은 내부 경계 누락 확인
  run_batch(INPUT_DIR)                폴더 일괄 처리 → output/summary.csv, output/failure_cases.csv

출력 (이미지 1장당 output/<이미지 이름>/)
  cells.json            전달용 prediction. 형식 고정 (아래)
  cells_primitive.json  병합 전 primitive grid. 같은 형식 → 'primitive vs merged' 평가 비교용
  <이름>_aligned.png    bbox 기준 이미지 (기울기/EXIF 보정이 있었을 때만 저장)
  report.json           검증 결과, 실패 사례, 경계 점수, 파라미터, 처리 시간
  vis/0_lines.png       초록=grid 에 쓰인 선 / 주황=표 선에 안 붙어 grid 에서 빠진 선 / 파랑=표 영역
  vis/1_primitive.png   primitive grid
  vis/2_boundary.png    빨강=경계 없음(병합) / 주황=끊긴 선 의심 / 노랑=약한 경계 / 자홍=비직사각형 복구 / 파랑=외곽 손상
  vis/3_final.png       하늘=general / 빨강=merged / 주황=검토 필요 / 자홍=비직사각형 복구
  vis/4_compare.png     1 → 2 → 3 단계 비교 (표 영역만 확대)
  roi/                  셀 이미지 (SAVE_ROI=True 일 때)

[cells.json 형식 — 고정, 이후 변경하지 않음]
{
  "image": "sample_01_aligned.png",
  "source_image": "sample_01.jpg",
  "method": "opencv_grid_merge",
  "rotation_deg": 1.52,
  "cells": [
    {"id": 0, "table": 0, "bbox": [x1, y1, x2, y2], "type": "general", "primitive_cells": [[0, 0]]},
    {"id": 1, "table": 0, "bbox": [x1, y1, x2, y2], "type": "merged", "primitive_cells": [[0, 1], [0, 2]]}
  ]
}
- image  : bbox 좌표가 맞는 이미지. 보정이 있으면 cells.json 옆의 <이름>_aligned.png, 없으면 원본 파일명.
           받는 쪽은 이 이미지에서 img[y1:y2, x1:x2] 로 자른다. GT 도 이 이미지 기준으로 만들어야 IoU 가 맞는다.
- type   : "general"(primitive 1칸) | "merged"(primitive 2칸 이상)
- table  : 페이지 안 표 번호(위→아래). primitive_cells 의 [row, col] 은 그 표 안의 좌표
- 정렬   : 표 순서 → 표 안에서 위→아래, 왼→오른쪽. id 는 그 순서대로 0부터
- 셀끼리 겹치지 않는다 (비직사각형 병합은 직사각형으로 복구해서 저장하고 report 에 기록)
"""
import csv
import json
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


# ==============================================================
# 설정 — 실험할 때는 여기만 바꾸면 된다
# ==============================================================
def _code_dir():
    """이 코드 파일이 있는 폴더 (주피터 노트북에서는 노트북이 있는 폴더)"""
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()


INPUT_DIR = _code_dir() / "Test_image_file"  # 계약서 이미지 폴더 (일괄 처리)
IMAGE_PATH = INPUT_DIR / "sample.jpg"        # 한 장씩 확인할 이미지
OUTPUT_DIR = _code_dir() / "output"          # 결과 폴더
SHOW_PLOTS = True                            # run_pipeline / compare 에서 그림을 화면에 띄울지
SAVE_ROI = False                             # 셀 이미지를 roi/ 에 잘라 저장할지
METHOD = "opencv_grid_merge"
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

PARAMS = {
    # 해상도 스케일: 이미지 대각선이 ref_diag px 일 때 scale = 1.0 (A4 300dpi ≈ 2.15)
    "ref_diag": 2000,
    # 기울기 보정
    "deskew_angle_limit": 10.0,     # 수평/수직에서 이 각도 이내인 선만 각도 추정에 사용
    "deskew_min_angle": 0.3,        # 이보다 작은 기울기는 보정하지 않음
    "deskew_residual_max": 0.3,     # 보정 후에도 이만큼 기울어 있으면 deskew 실패로 기록
    # 이진화
    "block_size_base": 15,
    "binarize_C": 10,
    # 선 추출
    #   open 커널이 한 행 높이보다 길면 한 행짜리 세로 경계가 통째로 지워진다(→ 오병합).
    #   30px(scale 1) ≈ A4 300dpi 에서 5.4mm: 인쇄 글자 획은 지우고 7mm 행의 경계는 남긴다.
    "line_open_base": 30,
    "line_open_ratio": None,        # 숫자를 넣으면 open 커널 = 이미지 폭/높이 × 비율 (이전 코드 0.4 재현용)
    "close_ratio": 0.01,            # 끊어진 선 잇기 (폭/높이 대비). 크면 행 하나를 건너 세로선을 이어버림
    # 표 영역 분리
    #   선 조각들을 연결 성분으로 묶고, 그중 이 길이 이상인 선(anchor)이 하나라도 있는 묶음만 표로 본다.
    #   짧은 내부 경계·끊긴 테두리 조각도 표 선에 붙어 있으면 grid/경계 판정에 그대로 들어가고,
    #   표 선에 안 붙은 선(표 밖 서명 밑줄, 셀 안 기입용 밑줄·필기 획)은 빠진다.
    "anchor_h_ratio": 0.15,         # 이미지 폭 대비
    "anchor_v_ratio": 0.03,         # 이미지 높이 대비
    "table_min_w_ratio": 0.10,
    "table_min_h_ratio": 0.02,
    "table_join_base": 3,           # 선 끝끼리 이만큼(scale 1 기준 px) 떨어져 있어도 같은 표로 묶음
    # grid / shared boundary
    "gap_thresh_base": 10,
    "strip_half_width_base": 2,
    "corner_margin_base": 2,
    "presence_ratio": 0.5,          # 경계 길이의 50% 넘게 선이 이어져 있으면 '경계 있음'
    # 검증
    "suspicious_score_min": 0.15,   # '경계 없음'인데 선이 이만큼 남아 있으면 경계 누락 오판 의심
    "weak_score_max": 0.8,          # '경계 있음'인데 선이 이만큼도 안 되면 미병합 의심
    "max_merged_area_ratio": 0.3,   # 병합 셀 하나가 표 면적의 30% 초과면 과다 병합 의심
    "hidden_line_ratio": 0.8,       # 셀 안을 폭(높이)의 80% 이상 가로지르는 선이 있으면 선 검출 실패
}

# compare_line_settings 기본 비교 대상 — open 커널만 바꾼다 (이전 코드 0.4 와 더 작은 값들)
LINE_SETTINGS = {
    "legacy_0.4": {"line_open_ratio": 0.4},
    "open_0.2": {"line_open_ratio": 0.2},
    "open_0.1": {"line_open_ratio": 0.1},
    "open_0.05": {"line_open_ratio": 0.05},
    "current": {},
}

FAIL_LABEL = {   # 실패 유형 (피드백 4.C 분류)
    "line_detection_failure": "선 검출 실패",
    "missing_boundary_misjudge": "경계 누락 오판 의심",
    "over_merge": "과다 병합 의심",
    "under_merge": "미병합 의심",
    "irregular_component": "비직사각형 component",
    "deskew_failure": "기울기 보정 실패",
    "validation_error": "형식/겹침 오류",
}


# ==============================================================
# 0. 입출력 유틸 (한글 경로, EXIF 방향)
# ==============================================================
def load_image(path):
    """반환: (BGR 이미지, EXIF 방향 보정 여부)"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {path}")
    try:
        with Image.open(path) as im:
            orient = im.getexif().get(0x0112, 1)     # 휴대폰 촬영본의 회전 정보
            if orient != 1:
                im = ImageOps.exif_transpose(im)
            img = cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)
        return img, orient != 1
    except Exception:
        img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise IOError(f"이미지를 읽을 수 없습니다: {path}")
        return img, False


def save_image(path, img):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, buf = cv2.imencode(path.suffix.lower() or ".png", img)
    if not ok:
        raise IOError(f"이미지 저장 실패: {path}")
    buf.tofile(str(path))


def get_scale_factor(img_w, img_h, ref_diag):
    """기준 대각선 대비 현재 이미지 배율. 픽셀 단위 파라미터를 해상도에 비례시키는 데 사용."""
    return max((img_w ** 2 + img_h ** 2) ** 0.5 / ref_diag, 0.3)


def _to_py(o):
    return o.item() if hasattr(o, "item") else str(o)


# ==============================================================
# 1. 기울기 보정
# ==============================================================
def estimate_skew(gray, p, max_side=1600):
    """HoughLinesP 선분 각도의 중앙값(도). 선이 없으면 None.
    축소본(긴 변 1600px)에서 0.1도 해상도로 추정 — 원본에서 1도 해상도로 하면 1.5도 같은 각도가 틀어지고,
    1000px 까지 줄이면 1도 미만 기울기가 0.1도 이상 틀어진다."""
    f = min(1.0, max_side / max(gray.shape))
    small = cv2.resize(gray, None, fx=f, fy=f, interpolation=cv2.INTER_AREA) if f < 1 else gray
    edges = cv2.Canny(small, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 1800, threshold=100,
                            minLineLength=min(small.shape) * 0.2, maxLineGap=10)
    if lines is None:
        return None
    limit = p["deskew_angle_limit"]
    angles = []
    for x1, y1, x2, y2 in np.asarray(lines).reshape(-1, 4):
        a = (np.degrees(np.arctan2(y2 - y1, x2 - x1)) + 90) % 180 - 90   # [-90, 90)
        if abs(a) < limit:                    # 수평선
            angles.append(a)
        elif abs(a) > 90 - limit:             # 수직선 → 수평 기준 편차로 변환
            angles.append(a - 90 if a > 0 else a + 90)
    return float(np.median(angles)) if angles else None


def rotate_expand(img, angle):
    """모서리가 잘리지 않도록 캔버스를 키워서 회전. 빈 곳은 테두리 중앙값 색으로 채운다."""
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    cos, sin = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(np.ceil(h * sin + w * cos)), int(np.ceil(h * cos + w * sin))
    M[0, 2] += nw / 2 - w / 2
    M[1, 2] += nh / 2 - h / 2
    edge = np.concatenate([img[0], img[-1], img[:, 0], img[:, -1]])
    fill = tuple(float(v) for v in np.median(edge, axis=0))
    out = cv2.warpAffine(img, M, (nw, nh), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=fill)
    return out, M


def deskew(img, p):
    """반환: (보정 이미지, gray, 회전 각도, 정보). 정보의 affine 은 원본 → 보정본 좌표 변환 행렬."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    angle = estimate_skew(gray, p)
    info = {"estimated_deg": angle, "residual_deg": None, "affine": None}
    if angle is None or abs(angle) < p["deskew_min_angle"]:
        return img, gray, 0.0, info
    rotated, M = rotate_expand(img, angle)
    rgray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
    info["residual_deg"] = estimate_skew(rgray, p, max_side=1200)   # 확인용이라 조금 작게
    info["affine"] = M.round(6).tolist()
    return rotated, rgray, angle, info


# ==============================================================
# 2. 전처리 + 이진화 (blockSize 해상도 비례)
# ==============================================================
def binarize(gray, scale, p):
    enhanced = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)
    block = int(p["block_size_base"] * scale)
    block = max(3, block if block % 2 == 1 else block + 1)
    return cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY_INV, block, p["binarize_C"])


# ==============================================================
# 3. 수평/수직선 추출 → 끊어진 선 잇기
# ==============================================================
def filter_short_components(mask, axis, min_len):
    """가로(세로) 길이가 min_len 미만인 연결 성분 제거"""
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    length = stats[:, cv2.CC_STAT_WIDTH if axis == "h" else cv2.CC_STAT_HEIGHT]
    keep = length >= min_len
    keep[0] = False
    return np.where(keep[labels], 255, 0).astype(np.uint8)


def extract_lines(bin_img, scale, p):
    """
    1) MORPH_OPEN(짧은 커널): 글자 획을 지우되 끊긴 선 조각과 짧은 내부 경계는 남긴다
       (긴 커널로 open 을 먼저 하면 끊긴 조각·한 행짜리 경계가 이어붙이기 전에 사라진다)
    2) MORPH_CLOSE: 끊긴 선 조각을 잇는다 (수평선은 폭, 수직선은 높이 기준)
    반환: (가로선 조각, 세로선 조각, 가로 anchor, 세로 anchor) — anchor 는 표를 찾는 기준인 긴 선
    """
    h, w = bin_img.shape
    rect = cv2.getStructuringElement
    r = p["line_open_ratio"]
    if r:
        kh, kv = max(10, int(w * r)), max(10, int(h * r))
    else:
        kh = kv = max(10, int(p["line_open_base"] * scale))
    h_all = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, rect(cv2.MORPH_RECT, (kh, 1)))
    v_all = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, rect(cv2.MORPH_RECT, (1, kv)))

    hc, vc = max(5, int(w * p["close_ratio"])), max(5, int(h * p["close_ratio"]))
    h_all = cv2.morphologyEx(h_all, cv2.MORPH_CLOSE, rect(cv2.MORPH_RECT, (hc, 1)))
    v_all = cv2.morphologyEx(v_all, cv2.MORPH_CLOSE, rect(cv2.MORPH_RECT, (1, vc)))

    h_anchor = filter_short_components(h_all, "h", w * p["anchor_h_ratio"])
    v_anchor = filter_short_components(v_all, "v", h * p["anchor_v_ratio"])
    return h_all, v_all, h_anchor, v_anchor


# ==============================================================
# 4. 표 영역 분리 — 서로 연결된 선 묶음 하나 = 표 하나
# ==============================================================
def find_tables(h_all, v_all, h_anchor, v_anchor, scale, p):
    """
    한 페이지에 표가 여러 개면 표 사이 본문 영역이 거대한 병합 셀로 잡히므로 표별로 나눠 처리한다.
    긴 선(anchor)이 들어 있는 선 묶음만 표로 보고, 그 묶음에 붙은 짧은 조각까지 표 선으로 쓴다.
    반환: [{"offset": (x0, y0), "h": 표 가로선(crop), "v": 표 세로선(crop)}] 위→아래 순
    """
    H, W = h_all.shape
    k = 2 * max(1, int(p["table_join_base"] * scale)) + 1
    joined = cv2.dilate(cv2.bitwise_or(h_all, v_all), np.ones((k, k), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(joined, connectivity=8)
    has_anchor = np.zeros(n, bool)
    has_anchor[np.unique(labels[(h_anchor > 0) | (v_anchor > 0)])] = True
    out = []
    for i in range(1, n):
        x, y, w, h = (int(v) for v in stats[i, :4])
        if not has_anchor[i] or w < W * p["table_min_w_ratio"] or h < H * p["table_min_h_ratio"]:
            continue
        region = labels[y:y + h, x:x + w] == i
        out.append({"offset": (x, y),
                    "h": np.where(region, h_all[y:y + h, x:x + w], 0).astype(np.uint8),
                    "v": np.where(region, v_all[y:y + h, x:x + w], 0).astype(np.uint8)})
    out.sort(key=lambda t: (t["offset"][1], t["offset"][0]))
    return out


# ==============================================================
# 5. grid 좌표
# ==============================================================
def cluster_positions(mask, axis, scale, p):
    """
    선 마스크를 투영해 가까운 좌표끼리 묶는다. 반환: ([grid 좌표], [(band 시작, band 끝)])
    - grid 좌표: 묶음 안에서 가장 진한 선의 중심 (묶음 중간값을 쓰면 이중선·밑줄 때문에 선이 없는 위치가 될 수 있다)
    - band: 그 묶음이 실제로 퍼져 있는 범위. 촬영본처럼 선이 비스듬하거나 구역마다 몇 px 어긋나 있어도
            경계 판정은 band 전체에서 하므로 놓치지 않는다.
    """
    gap = max(3, int(p["gap_thresh_base"] * scale))
    proj = (mask > 0).sum(axis=1 if axis == "h" else 0)
    idx = np.flatnonzero(proj)
    if idx.size == 0:
        return [], []
    pos, bands = [], []
    for g in np.split(idx, np.where(np.diff(idx) > gap)[0] + 1):
        strong = g[proj[g] >= proj[g].max() * 0.5]
        runs = np.split(strong, np.where(np.diff(strong) > 1)[0] + 1)
        best = max(runs, key=lambda r: proj[r].sum())
        pos.append(int((best[0] + best[-1]) // 2))
        bands.append((int(g[0]), int(g[-1])))
    return pos, bands


# ==============================================================
# 6. shared boundary 판정
# ==============================================================
def _line_coverage(mask, band, start, end, axis, strip_half, corner_margin):
    """band 위치의 경계선이 [start, end) 구간에서 몇 % 이어져 있는지 (0~1). 선 두께·기울기와 무관."""
    s, e = start + corner_margin, end - corner_margin
    if e <= s:
        s, e = start, end
    lo, hi = max(0, band[0] - strip_half), band[1] + strip_half + 1
    if axis == "v":
        covered = np.any(mask[s:e, lo:hi] > 0, axis=1)
    else:
        covered = np.any(mask[lo:hi, s:e] > 0, axis=0)
    return float(covered.mean()) if covered.size else 0.0


def detect_boundaries(h_lines, v_lines, rows, cols, row_bands, col_bands, scale, p):
    """각 primitive cell 의 right/bottom, 0열 left, 0행 top 경계 판정.
    반환: {(row, col, side): {"ok": bool, "score": float}}"""
    half = max(1, int(p["strip_half_width_base"] * scale))
    margin = max(1, int(p["corner_margin_base"] * scale))
    result = {}

    def judge(key, mask, band, start, end, axis):
        score = _line_coverage(mask, band, start, end, axis, half, margin)
        result[key] = {"ok": score > p["presence_ratio"], "score": score}

    for i in range(len(rows) - 1):
        y1, y2 = rows[i], rows[i + 1]
        for j in range(len(cols) - 1):
            x1, x2 = cols[j], cols[j + 1]
            judge((i, j, "right"), v_lines, col_bands[j + 1], y1, y2, "v")
            judge((i, j, "bottom"), h_lines, row_bands[i + 1], x1, x2, "h")
            if j == 0:
                judge((i, j, "left"), v_lines, col_bands[0], y1, y2, "v")
            if i == 0:
                judge((i, j, "top"), h_lines, row_bands[0], x1, x2, "h")
    return result


def is_internal(i, j, side, n_rows, n_cols):
    """표 내부 경계인지 (아니면 표 바깥 테두리)"""
    return (side == "right" and j + 1 < n_cols) or (side == "bottom" and i + 1 < n_rows)


def _neighbor(i, j, side):
    return (i, j + 1) if side == "right" else (i + 1, j)


# ==============================================================
# 7. Union-Find 병합 + 비직사각형 component 복구
# ==============================================================
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def _groups(n_rows, n_cols, edges, restored):
    uf = UnionFind(n_rows * n_cols)
    for a, b, _, key in edges:
        if key not in restored:
            uf.union(a[0] * n_cols + a[1], b[0] * n_cols + b[1])
    groups = {}
    for i in range(n_rows):
        for j in range(n_cols):
            groups.setdefault(uf.find(i * n_cols + j), []).append((i, j))
    return list(groups.values())


def _is_rect(members):
    rs = [r for r, _ in members]
    cs = [c for _, c in members]
    return len(members) == (max(rs) - min(rs) + 1) * (max(cs) - min(cs) + 1)


def reconstruct_cells(rows, cols, boundaries):
    """
    내부 경계가 없는 인접 primitive cell 을 Union-Find 로 묶어 general/merged bbox 생성.
    바깥 테두리 누락은 병합이 아니라 border_damage 로 기록.

    L자처럼 비직사각형으로 묶이면 bbox 가 다른 셀을 덮으므로 정상 병합으로 확정하지 않는다.
    그 component 안의 '경계 없음' 판정 중 선이 가장 많이 남아 있던(score 최대) 경계부터
    '경계 있음'으로 되돌려, 모든 component 가 직사각형이 될 때까지 반복한다.
    반환: (cells, border_damage, 비직사각형 component 목록, 되돌린 경계 목록)
    """
    n_rows, n_cols = len(rows) - 1, len(cols) - 1
    edges, border_damage = [], []
    for (i, j, side), b in boundaries.items():
        if b["ok"]:
            continue
        if not is_internal(i, j, side, n_rows, n_cols):
            border_damage.append({"row": i, "col": j, "side": side, "score": round(b["score"], 3)})
        else:
            edges.append(((i, j), _neighbor(i, j, side), b["score"], (i, j, side)))

    groups = _groups(n_rows, n_cols, edges, set())
    irregular = [sorted(g) for g in groups if not _is_rect(g)]
    restored = set()
    while True:
        bad = {m for g in groups if not _is_rect(g) for m in g}
        if not bad:
            break
        cand = [e for e in edges if e[3] not in restored and e[0] in bad]
        restored.add(max(cand, key=lambda e: e[2])[3])
        groups = _groups(n_rows, n_cols, edges, restored)

    irregular_members = {m for g in irregular for m in g}
    cells = []
    for g in groups:
        rs = [r for r, _ in g]
        cs = [c for _, c in g]
        i0, i1, j0, j1 = min(rs), max(rs), min(cs), max(cs)
        cells.append({
            "bbox": [cols[j0], rows[i0], cols[j1 + 1], rows[i1 + 1]],
            "type": "merged" if len(g) > 1 else "general",
            "primitive_cells": sorted([r, c] for r, c in g),
            "irregular": any(m in irregular_members for m in g),
        })
    cells.sort(key=lambda c: (c["bbox"][1], c["bbox"][0]))   # 읽는 순서
    return cells, border_damage, irregular, sorted(restored)


def merge_types(cells):
    """병합 형태별 개수: h=가로 병합(한 행, 여러 열) / v=세로 병합(한 열, 여러 행) / block=다중"""
    mt = {"h": 0, "v": 0, "block": 0}
    for c in cells:
        if c["type"] == "merged":
            nr = len({r for r, _ in c["primitive_cells"]})
            nc = len({col for _, col in c["primitive_cells"]})
            mt["h" if nr == 1 else "v" if nc == 1 else "block"] += 1
    return mt


# ==============================================================
# 8. 검증 + 실패 유형 분류
#    line_detection_failure     : 선이 이미지에는 있는데 grid 에 못 들어감 → 원인은 '선 추출'
#    missing_boundary_misjudge  : 선이 일부 남았는데 '경계 없음' 판정 → 원인은 '경계 판정'
#    over_merge / under_merge   : 결과 기준 의심 (원인 확인 필요)
#    irregular_component        : 비직사각형 연결 → 복구 후 기록
# ==============================================================
def check_table(t, cells, rows, cols, row_bands, col_bands, boundaries, restored, irregular,
                h_all, v_all, scale, p):
    n_rows, n_cols = len(rows) - 1, len(cols) - 1
    cell_of = {tuple(pc): c["id"] for c in cells for pc in c["primitive_cells"]}
    restored = set(restored)
    fails = []

    def add(kind, ids, detail):
        fails.append({"type": kind, "table": t, "cell_ids": sorted(set(ids)), "detail": detail})

    # (1) 내부 경계 판정 점검
    for (i, j, side), b in boundaries.items():
        if not is_internal(i, j, side, n_rows, n_cols) or (i, j, side) in restored:
            continue
        a, nb = cell_of[(i, j)], cell_of[_neighbor(i, j, side)]
        where = f"primitive ({i},{j}) {side}"
        if not b["ok"] and b["score"] >= p["suspicious_score_min"]:
            add("missing_boundary_misjudge", [a],
                f"{where} 선 커버리지 {b['score']:.2f} (기준 {p['presence_ratio']}) → 경계 없음 판정으로 병합됨")
        elif b["ok"] and a == nb:
            add("over_merge", [a], f"{where} 경계선(커버리지 {b['score']:.2f})이 병합 셀 안에 있음")
        elif b["ok"] and b["score"] < p["weak_score_max"]:
            add("under_merge", [a, nb], f"{where} 선 커버리지 {b['score']:.2f} 인 약한 경계로 분리됨")

    # (2) 결과 기준 과다 병합
    table_area = (cols[-1] - cols[0]) * (rows[-1] - rows[0])
    if len(cells) == 1 and n_rows * n_cols > 1:
        add("over_merge", [cells[0]["id"]], "표 전체가 셀 1개로 합쳐짐")
    elif table_area > 0:
        for c in cells:
            x1, y1, x2, y2 = c["bbox"]
            ratio = (x2 - x1) * (y2 - y1) / table_area
            if c["type"] == "merged" and ratio > p["max_merged_area_ratio"]:
                add("over_merge", [c["id"]], f"병합 셀이 표 면적의 {ratio:.0%}")

    # (3) 셀 안을 가로지르는 선 = 이미지에는 있는데 표 선과 끊겨 있어 grid 에 못 들어간 선
    #     셀 테두리 선이 퍼져 있는 band 바깥(셀 안쪽)만 본다
    m = max(2, int(3 * scale))
    for c in cells:
        rs = [r for r, _ in c["primitive_cells"]]
        cs = [col for _, col in c["primitive_cells"]]
        x1, x2 = col_bands[min(cs)][1] + m, col_bands[max(cs) + 1][0] - m
        y1, y2 = row_bands[min(rs)][1] + m, row_bands[max(rs) + 1][0] - m
        if x2 <= x1 or y2 <= y1:
            continue
        hs = h_all[y1:y2, x1:x2] > 0
        vs = v_all[y1:y2, x1:x2] > 0
        if hs.size == 0:
            continue
        for axis, cov in (("h", hs.mean(axis=1).max()), ("v", vs.mean(axis=0).max())):
            if cov >= p["hidden_line_ratio"]:
                add("line_detection_failure", [c["id"]],
                    f"셀 안에 {'가로선' if axis == 'h' else '세로선'}"
                    f"(셀 {'폭' if axis == 'h' else '높이'}의 {cov:.0%})이 있는데 grid 에서 빠짐")

    # (4) 비직사각형 component
    for g in irregular:
        gs = {tuple(x) for x in g}
        fixed = [f"({i},{j}) {s}" for i, j, s in restored if (i, j) in gs]
        add("irregular_component", [cell_of[x] for x in gs],
            f"primitive {[list(x) for x in g]} 가 비직사각형으로 연결 → 경계 {fixed} 를 되살려 직사각형으로 복구")
    return fails


def validate_cells(cells, img_w, img_h):
    """형식 오류는 예외, 셀 겹침은 목록으로 반환"""
    for k, c in enumerate(cells):
        x1, y1, x2, y2 = c["bbox"]
        if c["id"] != k or c["type"] not in ("general", "merged") \
                or not (0 <= x1 < x2 <= img_w and 0 <= y1 < y2 <= img_h):
            raise ValueError(f"cells.json 형식 오류: {c}")
    overlaps = []
    for a in range(len(cells)):
        ax1, ay1, ax2, ay2 = cells[a]["bbox"]
        for b in range(a + 1, len(cells)):
            bx1, by1, bx2, by2 = cells[b]["bbox"]
            if min(ax2, bx2) > max(ax1, bx1) and min(ay2, by2) > max(ay1, by1):
                overlaps.append((a, b))
    return overlaps


# ==============================================================
# 9. 핵심 처리 (입출력 없음)
# ==============================================================
def process(img, p):
    t0 = time.time()
    img, gray, angle, skew = deskew(img, p)
    H, W = gray.shape
    scale = get_scale_factor(W, H, p["ref_diag"])
    bin_img = binarize(gray, scale, p)
    h_all, v_all, h_anchor, v_anchor = extract_lines(bin_img, scale, p)

    tables, cells, prims, fails = [], [], [], []
    kept = np.zeros((H, W), bool)
    for comp in find_tables(h_all, v_all, h_anchor, v_anchor, scale, p):
        x0, y0 = comp["offset"]
        rows, row_bands = cluster_positions(comp["h"], "h", scale, p)
        cols, col_bands = cluster_positions(comp["v"], "v", scale, p)
        if len(rows) < 2 or len(cols) < 2:
            continue                       # 한 방향 선뿐인 성분 (밑줄 묶음, 페이지 가장자리 등) — 표가 아님
        t = len(tables)
        bnd = detect_boundaries(comp["h"], comp["v"], rows, cols, row_bands, col_bands, scale, p)
        rows, cols = [r + y0 for r in rows], [c + x0 for c in cols]
        row_bands = [(a + y0, b + y0) for a, b in row_bands]
        col_bands = [(a + x0, b + x0) for a, b in col_bands]
        tcells, damage, irregular, restored = reconstruct_cells(rows, cols, bnd)
        for c in tcells:
            c["id"], c["table"] = len(cells), t
            cells.append(c)
        for i in range(len(rows) - 1):
            for j in range(len(cols) - 1):
                prims.append({"id": len(prims), "table": t, "type": "general",
                              "bbox": [cols[j], rows[i], cols[j + 1], rows[i + 1]],
                              "primitive_cells": [[i, j]]})
        fails += check_table(t, tcells, rows, cols, row_bands, col_bands, bnd, restored, irregular,
                             h_all, v_all, scale, p)
        ch, cw = comp["h"].shape
        kept[y0:y0 + ch, x0:x0 + cw] |= (comp["h"] > 0) | (comp["v"] > 0)
        tables.append({"table": t, "bbox": [cols[0], rows[0], cols[-1], rows[-1]],
                       "rows": rows, "cols": cols, "boundaries": bnd, "restored": restored,
                       "border_damage": damage, "merge_types": merge_types(tcells)})

    res = skew["residual_deg"]
    if angle and res is not None and abs(res) > p["deskew_residual_max"]:
        fails.append({"type": "deskew_failure", "table": None, "cell_ids": [],
                      "detail": f"{angle:.2f}도 보정 후에도 {res:.2f}도 기울어 있음"})
    if not tables:
        fails.append({"type": "line_detection_failure", "table": None, "cell_ids": [],
                      "detail": "표 영역/grid 를 만들지 못함 — vis/0_lines.png 에서 선이 남는지 확인"})
    for a, b in validate_cells(cells, W, H):
        fails.append({"type": "validation_error", "table": None, "cell_ids": [a, b],
                      "detail": f"셀 {a}, {b} bbox 겹침 (표 안에 다른 표가 있는 경우)"})

    return {"img": img, "rotation_deg": float(angle), "skew": skew, "scale": scale,
            "h_all": h_all, "v_all": v_all, "kept": kept, "tables": tables,
            "cells": cells, "prims": prims, "fails": fails,
            "process_sec": time.time() - t0}


# ==============================================================
# 10. cells.json 저장 (형식 고정)
# ==============================================================
def save_cells_json(path, image_name, source_name, rotation_deg, cells):
    out = [{"id": int(c["id"]), "table": int(c["table"]),
            "bbox": [int(v) for v in c["bbox"]], "type": c["type"],
            "primitive_cells": [[int(r), int(col)] for r, col in c["primitive_cells"]]}
           for c in cells]
    head = {"image": image_name, "source_image": source_name,
            "method": METHOD, "rotation_deg": round(float(rotation_deg), 3)}
    body = ",\n".join("    " + json.dumps(c, ensure_ascii=False) for c in out)   # 셀 하나당 한 줄
    text = ("{\n" + "".join(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},\n"
                            for k, v in head.items())
            + '  "cells": [\n' + body + ("\n" if body else "") + "  ]\n}\n")
    json.loads(text)   # 표준 JSON 인지 확인
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ==============================================================
# 11. 시각화
# ==============================================================
FONT = cv2.FONT_HERSHEY_SIMPLEX
COLOR = {   # BGR
    "kept": (0, 170, 0), "dropped": (0, 140, 255), "table": (255, 90, 0), "grid": (0, 170, 0),
    "missing": (0, 0, 255), "suspicious": (0, 140, 255), "weak": (0, 215, 255),
    "border": (255, 0, 0), "general": (255, 160, 0), "merged": (0, 0, 230),
    "flagged": (0, 140, 255), "irregular": (255, 0, 255),
}


def _thick(mask, t):
    return cv2.dilate(mask.astype(np.uint8), np.ones((2 * t - 1, 2 * t - 1), np.uint8)) > 0 if t > 1 else mask


def draw_lines(r, t):
    out = cv2.addWeighted(r["img"], 0.45, np.full_like(r["img"], 255), 0.55, 0)
    all_ = _thick((r["h_all"] > 0) | (r["v_all"] > 0), t)
    kept = _thick(r["kept"], t)
    out[all_ & ~kept] = COLOR["dropped"]
    out[kept] = COLOR["kept"]
    for tb in r["tables"]:
        x1, y1, x2, y2 = tb["bbox"]
        d = 8 * t
        cv2.rectangle(out, (x1 - d, y1 - d), (x2 + d, y2 + d), COLOR["table"], 2 * t)
        cv2.putText(out, f"table {tb['table']}", (x1 - d, y1 - d - 6 * t), FONT, 0.6 * t, COLOR["table"], t + 1)
    return out


def draw_primitive_grid(r, t):
    out = r["img"].copy()
    for tb in r["tables"]:
        rows, cols = tb["rows"], tb["cols"]
        for y in rows:
            cv2.line(out, (cols[0], y), (cols[-1], y), COLOR["grid"], t)
        for x in cols:
            cv2.line(out, (x, rows[0]), (x, rows[-1]), COLOR["grid"], t)
    return out


def _edge(rows, cols, i, j, side):
    if side == "right":
        return (cols[j + 1], rows[i]), (cols[j + 1], rows[i + 1])
    if side == "left":
        return (cols[j], rows[i]), (cols[j], rows[i + 1])
    if side == "bottom":
        return (cols[j], rows[i + 1]), (cols[j + 1], rows[i + 1])
    return (cols[j], rows[i]), (cols[j + 1], rows[i])


def draw_boundaries(r, p, t):
    out = r["img"].copy()
    for tb in r["tables"]:
        rows, cols = tb["rows"], tb["cols"]
        nr, nc = len(rows) - 1, len(cols) - 1
        for y in rows:
            cv2.line(out, (cols[0], y), (cols[-1], y), (190, 190, 190), 1)
        for x in cols:
            cv2.line(out, (x, rows[0]), (x, rows[-1]), (190, 190, 190), 1)
        restored = set(tb["restored"])
        for (i, j, side), b in tb["boundaries"].items():
            internal = is_internal(i, j, side, nr, nc)
            if not b["ok"]:
                if not internal:
                    color = COLOR["border"]
                elif (i, j, side) in restored:
                    color = COLOR["irregular"]
                elif b["score"] >= p["suspicious_score_min"]:
                    color = COLOR["suspicious"]
                else:
                    color = COLOR["missing"]
            elif internal and b["score"] < p["weak_score_max"]:
                color = COLOR["weak"]
            else:
                continue
            p1, p2 = _edge(rows, cols, i, j, side)
            cv2.line(out, p1, p2, color, 3 * t)
    return out


def draw_final(img, cells, flagged, t):
    out = img.copy()
    for c in cells:
        x1, y1, x2, y2 = c["bbox"]
        if c.get("irregular"):
            color = COLOR["irregular"]
        elif c["id"] in flagged:
            color = COLOR["flagged"]
        else:
            color = COLOR["merged"] if c["type"] == "merged" else COLOR["general"]
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2 * t)
        cv2.putText(out, str(c["id"]), (x1 + 5 * t, y1 + 20 * t), FONT, 0.6 * t, color, t + 1)
    return out


def _tables_crop(r, t):
    if not r["tables"]:
        return 0, 0, r["img"].shape[1], r["img"].shape[0]
    b = np.array([tb["bbox"] for tb in r["tables"]])
    d = 30 * t
    H, W = r["img"].shape[:2]
    return max(0, b[:, 0].min() - d), max(0, b[:, 1].min() - d), min(W, b[:, 2].max() + d), min(H, b[:, 3].max() + d)


def compare_panel(items, crop, height=1400):
    x1, y1, x2, y2 = crop
    panels = []
    for title, im in items:
        im = im[y1:y2, x1:x2]
        f = height / im.shape[0]
        im = cv2.resize(im, (max(1, int(im.shape[1] * f)), height), interpolation=cv2.INTER_AREA)
        bar = np.full((60, im.shape[1], 3), 255, np.uint8)
        cv2.putText(bar, title, (10, 42), FONT, 1.0, (0, 0, 0), 2)
        panels += [np.vstack([bar, im]), np.full((height + 60, 20, 3), 255, np.uint8)]
    return np.hstack(panels[:-1])


def show_images(items):
    import matplotlib.pyplot as plt
    for title, im in items:
        plt.figure(figsize=(12, 12))
        plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
        plt.title(title)   # 한글 폰트 깨짐 방지를 위해 영문
        plt.axis("off")
    plt.show()


# ==============================================================
# 12. 실행: 한 장
# ==============================================================
def _clean_outputs(folder):
    """재실행 시 이전 결과가 섞이지 않도록 이 코드가 만드는 파일만 지운다"""
    if folder.exists():
        for pat in ("cells.json", "cells_primitive.json", "report.json",
                    "*_aligned.png", "vis/*.png", "roi/*.png"):
            for f in folder.glob(pat):
                f.unlink()


def run_pipeline(image_path=IMAGE_PATH, out_dir=OUTPUT_DIR, params=None, show=SHOW_PLOTS,
                 save_roi=SAVE_ROI, folder_name=None, verbose=True):
    p = {**PARAMS, **(params or {})}
    image_path = Path(image_path)
    stem = image_path.stem
    folder = Path(out_dir) / (folder_name or stem)
    _clean_outputs(folder)
    t0 = time.time()

    # 1) 처리
    src, exif_fixed = load_image(image_path)
    r = process(src, p)
    img, cells, fails = r["img"], r["cells"], r["fails"]
    H, W = img.shape[:2]

    # 2) bbox 기준 이미지 — 회전/EXIF 보정이 있으면 보정본을 cells.json 옆에 저장
    corrected = exif_fixed or r["rotation_deg"] != 0.0
    ref_name = f"{stem}_aligned.png" if corrected else image_path.name
    if corrected:
        save_image(folder / ref_name, img)

    # 3) 전달용 cells.json + primitive baseline
    save_cells_json(folder / "cells.json", ref_name, image_path.name, r["rotation_deg"], cells)
    save_cells_json(folder / "cells_primitive.json", ref_name, image_path.name, r["rotation_deg"], r["prims"])

    # 4) 시각화
    t = max(1, int(round(r["scale"])))
    flagged = {i for f in fails for i in f["cell_ids"]}
    vis = [("0_lines", "0. Lines (green=used, orange=dropped, blue=table)", draw_lines(r, t))]
    if r["tables"]:
        vis += [
            ("1_primitive", f"1. Primitive grid ({len(r['prims'])} cells)", draw_primitive_grid(r, t)),
            ("2_boundary", "2. Boundary (red=missing, orange=suspicious, yellow=weak, magenta=irregular fix, blue=border)",
             draw_boundaries(r, p, t)),
            ("3_final", f"3. Final cells {len(cells)} (sky=general, red=merged, orange=check, magenta=irregular)",
             draw_final(img, cells, flagged, t)),
        ]
    for name, _, im in vis:
        save_image(folder / "vis" / f"{name}.png", im)
    if r["tables"]:
        save_image(folder / "vis" / "4_compare.png",
                   compare_panel([("1. primitive", vis[1][2]), ("2. boundary", vis[2][2]),
                                  ("3. final", vis[3][2])], _tables_crop(r, t)))
    if save_roi:
        for c in cells:
            x1, y1, x2, y2 = c["bbox"]
            save_image(folder / "roi" / f"{c['id']:03d}_{c['type']}.png", img[y1:y2, x1:x2])

    # 5) 리포트
    n_merged = sum(c["type"] == "merged" for c in cells)
    mt = {k: sum(tb["merge_types"][k] for tb in r["tables"]) for k in ("h", "v", "block")}
    damage = sum(len(tb["border_damage"]) for tb in r["tables"])
    status = "grid_fail" if not r["tables"] else ("check" if fails else "ok")
    fail_count = {k: sum(f["type"] == k for f in fails) for k in FAIL_LABEL}
    total = time.time() - t0
    report = {
        "source_image": image_path.name, "image": ref_name, "method": METHOD, "status": status,
        "source_size": [src.shape[1], src.shape[0]], "image_size": [W, H],
        "scale": round(r["scale"], 3), "exif_transposed": exif_fixed,
        "rotation_deg": round(r["rotation_deg"], 3), "deskew": r["skew"],
        "counts": {"tables": len(r["tables"]), "primitive_cells": len(r["prims"]), "cells": len(cells),
                   "general": len(cells) - n_merged, "merged": n_merged,
                   "merge_h": mt["h"], "merge_v": mt["v"], "merge_block": mt["block"],
                   "border_damage": damage, **fail_count},
        "tables": [{"table": tb["table"], "bbox": tb["bbox"],
                    "grid": [len(tb["rows"]) - 1, len(tb["cols"]) - 1],
                    "rows": tb["rows"], "cols": tb["cols"], "merge_types": tb["merge_types"],
                    "border_damage": tb["border_damage"],
                    "restored_boundaries": [list(x) for x in tb["restored"]]} for tb in r["tables"]],
        "failures": fails,
        "cells_detail": [{k: c[k] for k in ("id", "table", "bbox", "type", "primitive_cells", "irregular")}
                         for c in cells],
        "boundaries": [{"table": tb["table"], "row": i, "col": j, "side": s,
                        "ok": b["ok"], "score": round(b["score"], 3)}
                       for tb in r["tables"] for (i, j, s), b in tb["boundaries"].items()],
        "params": p,
        "process_sec": round(r["process_sec"], 3),
        "total_sec": round(total, 3),
    }
    (folder / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=_to_py),
                                        encoding="utf-8")

    if show:
        show_images([(title, im) for _, title, im in vis])

    # 6) 요약 출력
    if verbose:
        sk = r["skew"]
        print(f"이미지: {image_path.name}  ({src.shape[1]} x {src.shape[0]}"
              + (f" → 보정본 {W} x {H}" if corrected else "") + f", 스케일 {r['scale']:.2f})")
        if r["rotation_deg"]:
            print(f"기울기 보정: {r['rotation_deg']:.2f}도 (보정 후 잔여 {sk['residual_deg'] or 0:.2f}도)"
                  f" → bbox 기준 이미지 {ref_name}")
        else:
            est = sk["estimated_deg"]
            print("기울기 보정: 없음" + (f" (추정 {est:.2f}도)" if est is not None else " (각도 추정용 선 없음)"))
        print(f"표 {len(r['tables'])}개: " + ", ".join(
            f"표{tb['table']} {len(tb['rows']) - 1}행 x {len(tb['cols']) - 1}열" for tb in r["tables"]))
        print(f"최종 셀 {len(cells)}개 (primitive {len(r['prims'])}) — general {len(cells) - n_merged}, "
              f"merged {n_merged} [가로 {mt['h']} / 세로 {mt['v']} / 다중 {mt['block']}]")
        print(f"표 바깥 테두리 손상 후보: {damage}건")
        print("-- 검증 --")
        for kind, label in FAIL_LABEL.items():
            items = [f for f in fails if f["type"] == kind]
            print(f"{'[OK]   ' if not items else '[CHECK]'} {label}: {len(items)}건")
            for f in items[:10]:
                print(f"          - 셀 {f['cell_ids']}: {f['detail']}")
            if len(items) > 10:
                print(f"          ... 외 {len(items) - 10}건 (report.json 참고)")
        print(f"처리 시간 {r['process_sec']:.2f}초 (저장 포함 {total:.2f}초) | 결과: {folder}")

    return {"image": image_path.name, "folder": folder.name, "status": status,
            "rotation_deg": round(r["rotation_deg"], 2), "tables": len(r["tables"]),
            "grid": " / ".join(f"{len(tb['rows']) - 1}x{len(tb['cols']) - 1}" for tb in r["tables"]),
            **{k: v for k, v in report["counts"].items() if k != "tables"},
            "process_sec": round(r["process_sec"], 3), "failures": fails}


# ==============================================================
# 13. 실행: 폴더 일괄
# ==============================================================
def _write_csv(path, rows):
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:   # 엑셀에서 한글 안 깨짐
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def run_batch(input_dir=INPUT_DIR, out_dir=OUTPUT_DIR, params=None, save_roi=SAVE_ROI):
    input_dir, out_dir = Path(input_dir), Path(out_dir)
    paths = sorted(q for q in input_dir.iterdir() if q.suffix.lower() in IMG_EXTS) if input_dir.is_dir() else []
    if not paths:
        print(f"이미지가 없습니다: {input_dir}")
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    stems = [q.stem for q in paths]
    dup = {s for s in stems if stems.count(s) > 1}   # a.jpg / a.png 처럼 이름이 겹치면 폴더명에 확장자 추가

    summary, fail_rows = [], []
    for q in paths:
        name = f"{q.stem}_{q.suffix[1:].lower()}" if q.stem in dup else q.stem
        try:
            s = run_pipeline(q, out_dir, params, show=False, save_roi=save_roi, folder_name=name, verbose=False)
        except Exception as e:
            s = {"image": q.name, "folder": name, "status": "error", "message": f"{type(e).__name__}: {e}"}
        fails = s.pop("failures", [])
        fail_rows += [{"image": q.name, "type": f["type"], "label": FAIL_LABEL[f["type"]], "table": f["table"],
                       "cell_ids": " ".join(map(str, f["cell_ids"])), "detail": f["detail"]} for f in fails]
        summary.append(s)
        if s["status"] == "error":
            print(f"[error] {q.name}: {s['message']}")
        else:
            issues = ", ".join(f"{FAIL_LABEL[k]} {s[k]}" for k in FAIL_LABEL if s.get(k))
            print(f"[{s['status']:>9}] {q.name}: 셀 {s['cells']} (merged {s['merged']}) | "
                  f"{issues or '문제 없음'} | {s['process_sec']:.2f}s")

    _write_csv(out_dir / "summary.csv", summary)
    if fail_rows:
        _write_csv(out_dir / "failure_cases.csv", fail_rows)
    n_ok = sum(s["status"] == "ok" for s in summary)
    print(f"\n총 {len(summary)}장 | ok {n_ok} | 확인 필요 {len(summary) - n_ok}")
    print(f"요약: {out_dir / 'summary.csv'}" + (f" | 실패 사례: {out_dir / 'failure_cases.csv'}" if fail_rows else ""))
    return summary


# ==============================================================
# 14. 선 추출 설정 비교 — 오병합 원인이 '선 추출'인지 '경계 판정'인지 분리
# ==============================================================
def _iou(a, b):
    iw = min(a[2], b[2]) - max(a[0], b[0])
    ih = min(a[3], b[3]) - max(a[1], b[1])
    if iw <= 0 or ih <= 0:
        return 0.0
    inter = iw * ih
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter)


def compare_line_settings(image_path=IMAGE_PATH, out_dir=OUTPUT_DIR, settings=None, params=None,
                          reference="current", show=SHOW_PLOTS):
    """
    같은 이미지를 선 추출 설정만 바꿔 돌리고, 기준 설정(reference)과 bbox 가 다른 셀을 주황으로 표시한다.
    - 작은 커널에서만 나뉘는 셀 = 큰 커널이 짧은 내부 경계를 지워 오병합된 것 (선 추출 원인)
    - 모든 설정에서 똑같이 병합되는 셀 = 선 추출과 무관 → 실제 병합이거나 경계 판정 문제
    결과: output/_line_compare/<이름>/compare.csv, <설정>_0_lines.png, <설정>_3_final.png
    """
    settings = settings or LINE_SETTINGS
    p_base = {**PARAMS, **(params or {})}
    image_path = Path(image_path)
    folder = Path(out_dir) / "_line_compare" / image_path.stem
    src, _ = load_image(image_path)
    results = {name: process(src, {**p_base, **ov}) for name, ov in settings.items()}
    ref = results.get(reference) or next(iter(results.values()))

    rows, shows = [], []
    for name, r in results.items():
        changed = {c["id"] for c in r["cells"]
                   if not any(_iou(c["bbox"], d["bbox"]) >= 0.9 for d in ref["cells"])}
        lost = sum(not any(_iou(d["bbox"], c["bbox"]) >= 0.9 for c in r["cells"]) for d in ref["cells"])
        t = max(1, int(round(r["scale"])))
        lines_im, final_im = draw_lines(r, t), draw_final(r["img"], r["cells"], changed, t)
        save_image(folder / f"{name}_0_lines.png", lines_im)
        save_image(folder / f"{name}_3_final.png", final_im)
        shows.append((f"{name}: final (orange = differs from '{reference}')", final_im))
        ov = settings[name]
        rows.append({
            "setting": name,
            "open": ov.get("line_open_ratio") or f"{p_base['line_open_base']}px*scale",
            "tables": len(r["tables"]),
            "grid": " / ".join(f"{len(tb['rows']) - 1}x{len(tb['cols']) - 1}" for tb in r["tables"]) or "-",
            "primitive": len(r["prims"]), "cells": len(r["cells"]),
            "merged": sum(c["type"] == "merged" for c in r["cells"]),
            "diff_vs_ref": len(changed), "lost_vs_ref": lost,
            **{k: sum(f["type"] == k for f in r["fails"])
               for k in ("line_detection_failure", "missing_boundary_misjudge", "over_merge")},
        })

    folder.mkdir(parents=True, exist_ok=True)
    _write_csv(folder / "compare.csv", rows)
    head = (f"{'setting':<12}{'open':>12}{'grid':>20}{'prim':>6}{'cells':>7}{'merged':>8}"
            f"{'diff':>6}{'lost':>6}{'line_fail':>10}{'misjudge':>9}")
    print(head)
    print("-" * len(head))
    for x in rows:
        print(f"{x['setting']:<12}{str(x['open']):>12}{x['grid']:>20}{x['primitive']:>6}{x['cells']:>7}"
              f"{x['merged']:>8}{x['diff_vs_ref']:>6}{x['lost_vs_ref']:>6}{x['line_detection_failure']:>10}"
              f"{x['missing_boundary_misjudge']:>9}")
    print(f"\ndiff = 이 설정에만 있는 셀 수(주황), lost = '{reference}' 에는 있는데 이 설정에서 사라진 셀 수")
    print(f"저장: {folder}")
    if show:
        show_images(shows)
    return rows


if __name__ == "__main__":
    # 1) 한 장 확인 (그림 띄움) — Test_image_file/sample.jpg
    run_pipeline(IMAGE_PATH, show=True)

    # 2) 짧은 내부 경계 누락 확인 — 이전 코드(open 0.4) vs 작은 값
    # compare_line_settings(IMAGE_PATH)

    # 3) 폴더 일괄 처리 → output/summary.csv, output/failure_cases.csv
    # run_batch(INPUT_DIR)
