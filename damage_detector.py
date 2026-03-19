import torch
import cv2
import numpy as np

class DentDetector:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = torch.hub.load("intel-isl/MiDaS", "DPT_Hybrid", trust_repo=True).to(self.device).eval()
        self.transform = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True).dpt_transform

    def detect_dent(self, img_path):
        """Detect dent using MiDaS depth + contour analysis."""
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError("Cannot read image.")

        # Estimate depth
        depth = self.estimate_depth(img)
        depth_norm = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Compute gradients to locate dents (concave regions)
        grad_x = cv2.Sobel(depth_norm, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(depth_norm, cv2.CV_64F, 0, 1, ksize=3)
        gradient_mag = cv2.magnitude(grad_x, grad_y)
        dents = cv2.threshold(gradient_mag, 30, 255, cv2.THRESH_BINARY_INV)[1].astype(np.uint8)

        # Clean up
        dents = cv2.morphologyEx(dents, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        dents = cv2.dilate(dents, np.ones((3, 3), np.uint8), iterations=2)

        mask_rgb = cv2.applyColorMap(dents, cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(img, 0.6, mask_rgb, 0.4, 0)

        return dents, overlay, depth_norm

    def estimate_depth(self, img):
        """Estimate depth using MiDaS DPT-Hybrid."""
        input_batch = self.transform(img).to(self.device)
        with torch.no_grad():
            prediction = self.model(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
        depth = prediction.cpu().numpy()
        return depth
