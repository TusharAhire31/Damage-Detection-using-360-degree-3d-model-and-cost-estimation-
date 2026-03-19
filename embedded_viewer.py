import tkinter as tk
import numpy as np
import open3d as o3d
import cv2


class EmbeddedViewer(tk.Frame):
    """
    A lightweight embedded 3D viewer that displays dent depth maps
    and generates an interactive visualization using Open3D.
    """

    def __init__(self, parent, width=720, height=480, bg="#111111"):
        super().__init__(parent, bg=bg, width=width, height=height)
        self.width = width
        self.height = height
        self.bg = bg
        self.depth_image = None

    def load_depth_image(self, path):
        """
        Load and visualize a processed depth map.
        """
        if not path:
            print("[Error] No depth file path provided.")
            return

        self.depth_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.depth_image is None:
            print(f"[Error] Could not load file: {path}")
            return

        self.show_3d_surface()

    def show_3d_surface(self):
        """
        Display the 3D visualization of the dent depth.
        """
        depth_gray = cv2.cvtColor(self.depth_image, cv2.COLOR_BGR2GRAY)
        depth_gray = cv2.normalize(depth_gray, None, 0, 255, cv2.NORM_MINMAX)
        depth_gray = cv2.GaussianBlur(depth_gray, (5, 5), 0)
        depth_float = depth_gray.astype(np.float32) / 255.0

        h, w = depth_float.shape
        o3d_depth = o3d.geometry.Image(depth_float)
        intrinsic = o3d.camera.PinholeCameraIntrinsic()
        intrinsic.set_intrinsics(w, h, 600, 600, w / 2, h / 2)

        pcd = o3d.geometry.PointCloud.create_from_depth_image(
            o3d_depth, intrinsic, depth_scale=1.0, depth_trunc=3.0, stride=2
        )
        pcd.estimate_normals()
        o3d.visualization.draw_geometries(
            [pcd],
            window_name="3D Dent Visualization",
            width=900,
            height=700,
            left=100,
            top=100,
        )
