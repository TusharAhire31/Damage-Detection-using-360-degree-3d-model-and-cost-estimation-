import cv2
import numpy as np
import os

def _read_depth(path):
    """Read and normalize a MiDaS-style depth map to [0,1]."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Depth map not found: {path}")

    depth = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if depth is None:
        raise FileNotFoundError("Failed to read depth image")

    if len(depth.shape) == 3:
        depth = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)

    depth = depth.astype(np.float32)
    depth = cv2.normalize(depth, None, 0, 1, cv2.NORM_MINMAX)
    return depth


def estimate_repair_cost(depth_map_path):
    """
    Estimate repair cost from depth map and approximate region location.
    Adds dynamic scaling based on region (bonnet/door/bumper etc.)
    and dent characteristics.
    Returns (total_cost, area_cm2, avg_depth).
    """

    depth = _read_depth(depth_map_path)
    h, w = depth.shape[:2]
    depth_blur = cv2.GaussianBlur(depth, (5, 5), 0)

    # Detect possible dent regions
    median_val = np.median(depth_blur)
    diff = np.abs(depth_blur - median_val)
    _, mask = cv2.threshold(diff, 0.1, 1, cv2.THRESH_BINARY)
    mask = mask.astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

    dent_area_px = cv2.countNonZero(mask)
    if dent_area_px == 0:
        return (0.0, 0.0, 0.0)

    avg_depth = float(np.mean(depth_blur[mask == 1]))
    area_cm2 = dent_area_px / 500.0  # 500 px ≈ 1 cm²

    # Calculate the centroid of the dent region
    moments = cv2.moments(mask)
    cx = int(moments['m10'] / (moments['m00'] + 1e-6))
    cy = int(moments['m01'] / (moments['m00'] + 1e-6))

    region = "unknown"
    region_factor = 1.0

    # top region = bonnet/hood
    if cy < h * 0.35:
        region = "bonnet"
        region_factor = 1.3
    # bottom = bumper area
    elif cy > h * 0.7:
        region = "bumper"
        region_factor = 1.1
    # middle left/right = doors / fender
    elif cx < w * 0.3 or cx > w * 0.7:
        region = "door/fender"
        region_factor = 1.2
    else:
        region = "side_panel"
        region_factor = 1.0

    # deeper dents increase cost more significantly
    depth_factor = 1 + (avg_depth * 2.5)
    area_factor = 1 + (area_cm2 / 800.0)

    base_rate = 150  # ₹/cm² (adjustable)
    base_cost = area_cm2 * base_rate

    total_cost = base_cost * region_factor * depth_factor * area_factor

    total_cost = np.clip(total_cost, 500, 50000)

    total_cost = float(round(total_cost, 2))
    area_cm2 = float(round(area_cm2, 2))
    avg_depth = float(round(avg_depth, 3))

    print(f"[DEBUG] Region: {region}, Area: {area_cm2}cm², Depth: {avg_depth}, Cost: ₹{total_cost}")
    return (total_cost, area_cm2, avg_depth)
