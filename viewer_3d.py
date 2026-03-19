import open3d as o3d
import numpy as np
import cv2

def show_3d(depth_map_path):
    """Visualize dent in 3D using Open3D mesh reconstruction."""
    depth_img = cv2.imread(depth_map_path, cv2.IMREAD_GRAYSCALE)
    if depth_img is None:
        print("Depth map not found.")
        return

    depth = cv2.resize(depth_img, (480, 360))
    depth = cv2.GaussianBlur(depth, (5, 5), 0)
    h, w = depth.shape

    # Create 3D points
    fx, fy = 500, 500
    cx, cy = w / 2, h / 2
    xs, ys = np.meshgrid(np.arange(w), np.arange(h))
    X = (xs - cx) * depth / fx
    Y = (ys - cy) * depth / fy
    Z = depth

    points = np.stack((X, -Y, Z), axis=-1).reshape(-1, 3)
    colors = cv2.cvtColor(depth_img, cv2.COLOR_GRAY2BGR).reshape(-1, 3) / 255.0

    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.utility.Vector3dVector(points)
    cloud.colors = o3d.utility.Vector3dVector(colors)
    o3d.visualization.draw_geometries([cloud])
