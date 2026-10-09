import json
from pathlib import Path

BASE = Path(__file__).resolve().parent

regions = {
    "upper": [261, 576, 2692, 1427],
    "lower": [256, 2980, 2789, 3776]
}

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def convert_tatr(box):
    x1, y1, x2, y2 = box
    return [3000-y2, x1, 3000-y1, x2]

def inside_center(box, region):
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    x1, y1, x2, y2 = region
    return x1 <= cx <= x2 and y1 <= cy <= y2

pp = load_json(
    BASE.parent / "1_PaddleOCR-PP-Structure"
    / "output" / "sample" / "res_0.txt"
)["res"]["cell_bbox"]

grid = load_json(
    BASE.parent / "2_TATR" / "tatr_result_grid.json"
)

spanning = load_json(
    BASE.parent / "2_TATR" / "tatr_result_spanning.json"
)["reconstructed_cells"]

opencv_grid = load_json(
    BASE / "cells_primitive_original.json"
)["cells"]

opencv_restored = load_json(
    BASE / "cells_original.json"
)["cells"]

models = {
    "PP-Structure": pp,
    "TATR Grid": [convert_tatr(c["bbox"]) for c in grid],
    "TATR Spanning": [
        convert_tatr(c["bbox"]) for c in spanning
    ],
    "OpenCV Primitive": [c["bbox"] for c in opencv_grid],
    "OpenCV Restored": [c["bbox"] for c in opencv_restored]
}

for name, boxes in models.items():
    upper = sum(
        inside_center(b, regions["upper"]) for b in boxes
    )
    lower = sum(
        inside_center(b, regions["lower"]) for b in boxes
    )
    outside = len(boxes) - upper - lower

    print(f"\n{name}")
    print("전체:", len(boxes))
    print("상단 표:", upper)
    print("하단 표:", lower)
    print("표 영역 외부:", outside)
