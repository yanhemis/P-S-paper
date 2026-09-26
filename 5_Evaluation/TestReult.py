import json
import time
import warnings

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


# ==============================================================
# 0. 유틸 함수
# ==============================================================
def show(img, title="", cmap=None):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(10, 10))
    plt.imshow(img, cmap=cmap)
    plt.title(title)
    plt.axis('off')
    plt.show()


def load_image(path):
    # cv2로 먼저 시도, 실패하면(jpg 등 비표준 포맷) PIL로 변환해서 재시도
    img = cv2.imread(path)
    if img is None:
        pil_img = Image.open(path).convert("RGB")
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img, gray


def get_scale_factor(img_w, img_h, ref_diag=2000):
    """
    기준 대각선 길이(ref_diag px) 대비 현재 이미지의 상대 배율.
    gap_thresh, boundary strip 폭처럼 절대 픽셀로 고정돼 있던 값들을
    해상도에 비례하도록 만드는 데 사용한다. 
    """
    diag = (img_w ** 2 + img_h ** 2) ** 0.5
    return max(diag / ref_diag, 0.3)


# ==============================================================
# 1. 기울기 보정 (신규 - 추가 피드백 #10)
# ==============================================================
def deskew(img, gray, angle_limit=10.0):
    """
    HoughLinesP로 검출된 선분들의 각도 중앙값만큼 이미지를 회전시켜
    이후 단계의 '완전한 수평/수직' 가정이 깨지지 않도록 사전 보정한다.
    선이 검출되지 않으면 회전 없이 원본을 그대로 반환한다.
    """
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, threshold=100,
        minLineLength=min(gray.shape) * 0.2, maxLineGap=10
    )
    if lines is None:
        return img, gray, 0.0

    angles = []
    for x1, y1, x2, y2 in lines[:, 0]:
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if abs(angle) < angle_limit:
            angles.append(angle)
        elif abs(abs(angle) - 90) < angle_limit:
            angles.append(angle - 90 if angle > 0 else angle + 90)

    if not angles:
        return img, gray, 0.0

    rot_angle = float(np.median(angles))
    if abs(rot_angle) < 0.3:  # 무시할 수준의 미세한 기울기
        return img, gray, 0.0

    h, w = gray.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, rot_angle, 1.0)
    rotated_img = cv2.warpAffine(
        img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    rotated_gray = cv2.cvtColor(rotated_img, cv2.COLOR_BGR2GRAY)
    return rotated_img, rotated_gray, rot_angle


# ==============================================================
# 2. 전처리 + 이진화 (blockSize 해상도 비례 - 추가 피드백 #11)
# ==============================================================
def enhance_and_binarize(gray, scale=1.0, base_block_size=15, C=10):
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    block_size = int(base_block_size * scale)
    if block_size % 2 == 0:
        block_size += 1
    block_size = max(block_size, 3)

    bin_img = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, block_size, C
    )
    return bin_img


# ==============================================================
# 3. 수평/수직 선 추출 + 끊어진 선 보정 (h/v 축 분리 - 피드백 문서 2.3)
# ==============================================================
def extract_hv_lines(bin_img, img_w, img_h, h_ratio=0.4, v_ratio=0.4):
    h_len = max(10, int(img_w * h_ratio))
    v_len = max(10, int(img_h * v_ratio))
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_len, 1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_len))
    h_lines = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, h_kernel, iterations=1)
    v_lines = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, v_kernel, iterations=1)
    return h_lines, v_lines


def close_gaps(h_lines, v_lines, img_w, img_h, close_ratio=0.02):
    # 수정: 수평선은 img_w, 수직선은 img_h 기준으로 각각 계산 (기존엔 둘 다 img_w 사용)
    h_close_len = max(5, int(img_w * close_ratio))
    v_close_len = max(5, int(img_h * close_ratio))
    h_close = cv2.getStructuringElement(cv2.MORPH_RECT, (h_close_len, 1))
    v_close = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_close_len))
    h_out = cv2.morphologyEx(h_lines, cv2.MORPH_CLOSE, h_close)
    v_out = cv2.morphologyEx(v_lines, cv2.MORPH_CLOSE, v_close)
    return h_out, v_out


# ==============================================================
# 4. 문자 획('ㅣ','ㅡ') 오검출 제거 (기존 로직 유지)
# ==============================================================
def filter_short_components(mask, axis, min_len):
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    clean = np.zeros_like(mask)
    for i in range(1, n):
        length = stats[i, cv2.CC_STAT_WIDTH] if axis == 'h' else stats[i, cv2.CC_STAT_HEIGHT]
        if length >= min_len:
            clean[labels == i] = 255
    return clean


# ==============================================================
# 5. grid 좌표 추출 (gap_thresh 해상도 비례)
# ==============================================================
def cluster_positions(mask, axis, scale=1.0, gap_thresh_base=10):
    gap_thresh = max(3, int(gap_thresh_base * scale))
    proj = np.sum(mask, axis=1 if axis == 'h' else 0)
    idx = np.where(proj > 0)[0]
    if len(idx) == 0:
        return []
    clusters, start, prev = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - prev > gap_thresh:
            clusters.append((start + prev) // 2)
            start = i
        prev = i
    clusters.append((start + prev) // 2)
    return sorted(clusters)


# ==============================================================
# 6. shared boundary 판정 (외곽 top/left 포함, 해상도 비례 strip)
# ==============================================================
def _boundary_ok(mask, y1, y2, x1, x2, axis, corner_margin, presence_ratio):
    if axis == 'v':
        y1c, y2c = y1 + corner_margin, y2 - corner_margin
        if y2c <= y1c:
            y1c, y2c = y1, y2
        strip = mask[y1c:y2c, x1:x2]
    else:
        x1c, x2c = x1 + corner_margin, x2 - corner_margin
        if x2c <= x1c:
            x1c, x2c = x1, x2
        strip = mask[y1:y2, x1c:x2c]

    if strip.size == 0:
        return False, 0.0
    score = float(np.mean(strip > 0))
    return score > presence_ratio, score


def detect_boundaries(h_lines, v_lines, rows, cols, scale=1.0,
                       presence_ratio=0.5, strip_half_width_base=2,
                       corner_margin_base=2):
    """
    각 primitive cell의 오른쪽/아래쪽 shared boundary를 판정하고,
    0행의 위쪽 외곽선, 0열의 왼쪽 외곽선도 별도로 판정한다.
    strip 폭과 모서리 마진은 해상도(scale)에 비례해서 계산한다.

    반환: {(row, col, 'right'|'bottom'|'left'|'top'): {'ok': bool, 'score': float}}
    """
    strip_half = max(1, int(strip_half_width_base * scale))
    corner_margin = max(1, int(corner_margin_base * scale))
    result = {}

    n_rows, n_cols = len(rows) - 1, len(cols) - 1

    for i in range(n_rows):
        for j in range(n_cols):
            y1, y2 = rows[i], rows[i + 1]
            x1, x2 = cols[j], cols[j + 1]

            # 오른쪽 경계
            xr = cols[j + 1]
            ok, score = _boundary_ok(
                v_lines, y1, y2, max(0, xr - strip_half), xr + strip_half,
                axis='v', corner_margin=corner_margin, presence_ratio=presence_ratio
            )
            result[(i, j, 'right')] = {'ok': ok, 'score': score}

            # 아래쪽 경계
            yb = rows[i + 1]
            ok, score = _boundary_ok(
                h_lines, max(0, yb - strip_half), yb + strip_half, x1, x2,
                axis='h', corner_margin=corner_margin, presence_ratio=presence_ratio
            )
            result[(i, j, 'bottom')] = {'ok': ok, 'score': score}

            # 신규: 표 왼쪽 외곽선(0열)
            if j == 0:
                xl = cols[0]
                ok, score = _boundary_ok(
                    v_lines, y1, y2, max(0, xl - strip_half), xl + strip_half,
                    axis='v', corner_margin=corner_margin, presence_ratio=presence_ratio
                )
                result[(i, j, 'left')] = {'ok': ok, 'score': score}

            # 신규: 표 위쪽 외곽선(0행)
            if i == 0:
                yt = rows[0]
                ok, score = _boundary_ok(
                    h_lines, max(0, yt - strip_half), yt + strip_half, x1, x2,
                    axis='h', corner_margin=corner_margin, presence_ratio=presence_ratio
                )
                result[(i, j, 'top')] = {'ok': ok, 'score': score}

    return result


# ==============================================================
# 7. Union-Find 기반 병합 셀 재구성 
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


def reconstruct_cells(rows, cols, boundaries):
    """
    boundary가 없는(ok=False) 인접 primitive cell끼리 Union-Find로 묶어
    최종 general/merged bbox를 만든다.
    표 왼쪽/위쪽 외곽선 손상은 '병합'이 아니라 별도의 border_damage로 기록한다.
    (외곽 테두리와 내부 shared boundary를 구분 )
    """
    n_rows, n_cols = len(rows) - 1, len(cols) - 1
    if n_rows <= 0 or n_cols <= 0:
        return [], []

    def idx(i, j):
        return i * n_cols + j

    uf = UnionFind(n_rows * n_cols)
    border_damage = []

    for i in range(n_rows):
        for j in range(n_cols):
            if j + 1 < n_cols and not boundaries[(i, j, 'right')]['ok']:
                uf.union(idx(i, j), idx(i, j + 1))
            if i + 1 < n_rows and not boundaries[(i, j, 'bottom')]['ok']:
                uf.union(idx(i, j), idx(i + 1, j))
            if j == 0 and not boundaries[(i, j, 'left')]['ok']:
                border_damage.append({
                    'row': i, 'col': j, 'side': 'left',
                    'score': boundaries[(i, j, 'left')]['score']
                })
            if i == 0 and not boundaries[(i, j, 'top')]['ok']:
                border_damage.append({
                    'row': i, 'col': j, 'side': 'top',
                    'score': boundaries[(i, j, 'top')]['score']
                })

    groups = {}
    for i in range(n_rows):
        for j in range(n_cols):
            root = uf.find(idx(i, j))
            groups.setdefault(root, []).append((i, j))

    cells = []
    for cid, members in enumerate(groups.values()):
        rs = [m[0] for m in members]
        cs = [m[1] for m in members]
        i_min, i_max = min(rs), max(rs)
        j_min, j_max = min(cs), max(cs)
        x1, y1 = cols[j_min], rows[i_min]
        x2, y2 = cols[j_max + 1], rows[i_max + 1]
        cells.append({
            "id": cid,
            "bbox": [int(x1), int(y1), int(x2), int(y2)],
            "type": "merged" if len(members) > 1 else "general",
            "primitive_cells": [[int(r), int(c)] for r, c in members]
        })

    return cells, border_damage


# ==============================================================
# 8. 시각화 (3종 - 피드백 문서 7번 "기능 검증" 요구사항 반영)
# ==============================================================
def draw_primitive_grid(img, rows, cols, color=(0, 200, 0)):
    out = img.copy()
    for i in range(len(rows) - 1):
        for j in range(len(cols) - 1):
            x1, y1 = cols[j], rows[i]
            x2, y2 = cols[j + 1], rows[i + 1]
            cv2.rectangle(out, (x1, y1), (x2, y2), color, 1)
    return out


def draw_missing_boundaries(img, rows, cols, boundaries):
    """
    빨강: 내부 shared boundary(오른쪽/아래쪽) 누락
    파랑: 표 왼쪽/위쪽 외곽선 손상
    """
    out = img.copy()
    for (i, j, side), info in boundaries.items():
        if info['ok']:
            continue
        if side == 'right':
            x, y1, y2 = cols[j + 1], rows[i], rows[i + 1]
            cv2.line(out, (x, y1), (x, y2), (0, 0, 255), 3)
        elif side == 'bottom':
            y, x1, x2 = rows[i + 1], cols[j], cols[j + 1]
            cv2.line(out, (x1, y), (x2, y), (0, 0, 255), 3)
        elif side == 'left':
            x, y1, y2 = cols[0], rows[i], rows[i + 1]
            cv2.line(out, (x, y1), (x, y2), (255, 0, 0), 3)
        elif side == 'top':
            y, x1, x2 = rows[0], cols[j], cols[j + 1]
            cv2.line(out, (x1, y), (x2, y), (255, 0, 0), 3)
    return out


def draw_final_cells(img, cells):
    out = img.copy()
    for c in cells:
        x1, y1, x2, y2 = c["bbox"]
        color = (0, 0, 255) if c["type"] == "merged" else (0, 150, 255)
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
    return out


# ==============================================================
# 실행 파이프라인
# ==============================================================
def run_pipeline(path="sample.jpg", save_json_path="cells.json", visualize=True):
    t0 = time.time()

    # 1) 이미지 로드
    img, gray = load_image(path)
    img_h, img_w = gray.shape
    scale = get_scale_factor(img_w, img_h)

    # 2) 기울기 보정 (신규)
    img, gray, rot_angle = deskew(img, gray)
    img_h, img_w = gray.shape

    # 3) 전처리 + 이진화 (해상도 비례 파라미터)
    bin_img = enhance_and_binarize(gray, scale=scale)

    # 4) 선 추출 + 끊어진 선 보정 (h/v 축 분리 수정)
    h_lines, v_lines = extract_hv_lines(bin_img, img_w, img_h)
    h_lines, v_lines = close_gaps(h_lines, v_lines, img_w, img_h)

    # 5) 문자 오검출 제거
    h_clean = filter_short_components(h_lines, 'h', img_w * 0.15)
    v_clean = filter_short_components(v_lines, 'v', img_h * 0.15)

    # 6) grid 좌표 (gap_thresh 해상도 비례)
    rows = cluster_positions(h_clean, 'h', scale=scale)
    cols = cluster_positions(v_clean, 'v', scale=scale)

    if len(rows) < 2 or len(cols) < 2:
        warnings.warn(
            f"표선 검출 실패로 grid를 만들 수 없습니다 "
            f"(검출된 행 경계 {len(rows)}개, 열 경계 {len(cols)}개). "
            f"이진화/기울기/전처리 파라미터를 먼저 점검하세요."
        )
        return None

    # 7) shared boundary 판정 (외곽 top/left 포함, 해상도 비례 strip)
    boundaries = detect_boundaries(h_clean, v_clean, rows, cols, scale=scale)

    # 8) Union-Find 기반 병합 셀 재구성
    cells, border_damage = reconstruct_cells(rows, cols, boundaries)

    # 9) 표준 cells.json 저장
    output = {
        "image": path,
        "method": "opencv_grid_merge",
        "rotation_deg": rot_angle,
        "cells": cells,
        "border_damage": border_damage
    }
    with open(save_json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - t0

    # ------------------------------------------------------------
    # 결과 확인 (3종 시각화)
    # ------------------------------------------------------------
    if visualize:
        show(cv2.bitwise_or(h_clean, v_clean), title="검출된 표선(정제 후)", cmap='gray')
        show(draw_primitive_grid(img, rows, cols), title="1. Primitive Grid")
        show(draw_missing_boundaries(img, rows, cols, boundaries),
             title="2. Missing Boundary 판정 결과 (빨강=내부, 파랑=외곽 top/left)")
        show(draw_final_cells(img, cells),
             title=f"3. 최종 General/Merged Cell 결과 (총 {len(cells)}개)")

    n_general = sum(1 for c in cells if c["type"] == "general")
    n_merged = sum(1 for c in cells if c["type"] == "merged")

    print(f"이미지 크기: {img_w} x {img_h} (스케일 팩터: {scale:.2f})")
    print(f"기울기 보정 각도: {rot_angle:.2f}도")
    print(f"검출된 행 개수: {len(rows) - 1}, 열 개수: {len(cols) - 1}")
    print(f"최종 셀 개수: {len(cells)} (general: {n_general}, merged: {n_merged})")
    print(f"표 왼쪽/위쪽 외곽선 손상 후보: {len(border_damage)}건")
    if border_damage:
        print("외곽선 손상 상세:", border_damage)
    print(f"처리 시간: {elapsed:.3f}초")
    print(f"cells.json 저장 완료: {save_json_path}")

    return output


if __name__ == "__main__":
    run_pipeline("../sample.jpg")