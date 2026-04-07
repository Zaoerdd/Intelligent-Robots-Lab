import math
from pathlib import Path

import cv2
import numpy as np


OUT_DIR = Path(".")
IMG_W = 640
IMG_H = 480
PATTERN_SIZE = (6, 4)  # inner corners
SQUARE_SIZE_M = 0.024
BOARD_SQUARES = (PATTERN_SIZE[0] + 1, PATTERN_SIZE[1] + 1)
BOARD_PX = (700, 500)


def build_board_image():
    w_squares, h_squares = BOARD_SQUARES
    cell_w = BOARD_PX[0] // w_squares
    cell_h = BOARD_PX[1] // h_squares
    board = np.full((BOARD_PX[1], BOARD_PX[0]), 255, dtype=np.uint8)
    for y in range(h_squares):
        for x in range(w_squares):
            if (x + y) % 2 == 0:
                x0 = x * cell_w
                y0 = y * cell_h
                board[y0 : y0 + cell_h, x0 : x0 + cell_w] = 0
    return board, cell_w, cell_h


def object_points():
    objp = np.zeros((PATTERN_SIZE[0] * PATTERN_SIZE[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0 : PATTERN_SIZE[0], 0 : PATTERN_SIZE[1]].T.reshape(-1, 2)
    objp *= SQUARE_SIZE_M
    return objp


def render_view(board_img, k_true, pose_idx):
    board_w_m = BOARD_SQUARES[0] * SQUARE_SIZE_M
    board_h_m = BOARD_SQUARES[1] * SQUARE_SIZE_M
    outer = np.array(
        [
            [0.0, 0.0, 0.0],
            [board_w_m, 0.0, 0.0],
            [board_w_m, board_h_m, 0.0],
            [0.0, board_h_m, 0.0],
        ],
        dtype=np.float32,
    )

    yaw = np.deg2rad(np.random.uniform(-35, 35))
    pitch = np.deg2rad(np.random.uniform(-25, 25))
    roll = np.deg2rad(np.random.uniform(-15, 15))
    rvec = np.array([roll, pitch, yaw], dtype=np.float32)
    tvec = np.array(
        [
            np.random.uniform(-0.06, 0.06),
            np.random.uniform(-0.05, 0.05),
            np.random.uniform(0.45, 0.85),
        ],
        dtype=np.float32,
    )

    img_outer, _ = cv2.projectPoints(outer, rvec, tvec, k_true, np.zeros((5, 1), np.float32))
    img_outer = img_outer.reshape(-1, 2).astype(np.float32)

    src = np.array(
        [
            [0, 0],
            [board_img.shape[1] - 1, 0],
            [board_img.shape[1] - 1, board_img.shape[0] - 1],
            [0, board_img.shape[0] - 1],
        ],
        dtype=np.float32,
    )
    h, _ = cv2.findHomography(src, img_outer)
    canvas = np.full((IMG_H, IMG_W), 180, dtype=np.uint8)
    warped = cv2.warpPerspective(board_img, h, (IMG_W, IMG_H), borderValue=180)

    mask = warped != 180
    canvas[mask] = warped[mask]

    noise = np.random.normal(0, 4, canvas.shape).astype(np.int16)
    canvas = np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    canvas = cv2.GaussianBlur(canvas, (5, 5), 0)
    return canvas


def main():
    np.random.seed(7)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    board_img, _, _ = build_board_image()
    objp = object_points()
    k_true = np.array([[640.0, 0.0, 320.0], [0.0, 635.0, 240.0], [0.0, 0.0, 1.0]], dtype=np.float32)

    objpoints = []
    imgpoints = []
    sample_drawn = None

    for idx in range(80):
        gray = render_view(board_img, k_true, idx)
        found, corners = cv2.findChessboardCornersSB(gray, PATTERN_SIZE)
        if not found:
            continue
        objpoints.append(objp.copy())
        imgpoints.append(corners.astype(np.float32))

        if sample_drawn is None:
            drawn = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            cv2.drawChessboardCorners(drawn, PATTERN_SIZE, corners, found)
            sample_drawn = drawn

        if len(objpoints) >= 16:
            break

    if len(objpoints) < 8:
        raise RuntimeError(f"not enough valid calibration views: {len(objpoints)}")

    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, (IMG_W, IMG_H), None, None
    )

    rectification = np.eye(3, dtype=np.float64)
    projection = np.hstack([camera_matrix, np.zeros((3, 1), dtype=np.float64)])

    if sample_drawn is not None:
        cv2.imwrite(str(OUT_DIR / "part4_calibration_corners.png"), sample_drawn)

    yaml_text = f"""image_width: {IMG_W}
image_height: {IMG_H}
camera_name: synthetic_usb_cam
camera_matrix:
  rows: 3
  cols: 3
  data: [{", ".join(f"{v:.6f}" for v in camera_matrix.reshape(-1))}]
distortion_model: plumb_bob
distortion_coefficients:
  rows: 1
  cols: {dist_coeffs.size}
  data: [{", ".join(f"{v:.6f}" for v in dist_coeffs.reshape(-1))}]
rectification_matrix:
  rows: 3
  cols: 3
  data: [{", ".join(f"{v:.6f}" for v in rectification.reshape(-1))}]
projection_matrix:
  rows: 3
  cols: 4
  data: [{", ".join(f"{v:.6f}" for v in projection.reshape(-1))}]
reprojection_error: {ret:.6f}
valid_views: {len(objpoints)}
"""

    (OUT_DIR / "part4_camera_parameters.yaml").write_text(yaml_text, encoding="utf-8")
    print("generated")
    print(f"valid_views={len(objpoints)}")
    print(f"reprojection_error={ret:.6f}")


if __name__ == "__main__":
    main()
