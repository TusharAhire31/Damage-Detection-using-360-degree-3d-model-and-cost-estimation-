import torch
import cv2
import numpy as np
from PIL import Image

def estimate_depth(image_path, save_path="depth_output.png"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    midas = torch.hub.load("intel-isl/MiDaS", "DPT_Hybrid").to(device)
    midas.eval()
    transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    transform = transforms.dpt_transform

    img = Image.open(image_path).convert("RGB")
    input_batch = transform(img).to(device)

    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.size[::-1],
            mode="bicubic",
            align_corners=False,
        ).squeeze().cpu().numpy()

    depth_min, depth_max = np.min(prediction), np.max(prediction)
    depth_img = (255 * (prediction - depth_min) / (depth_max - depth_min)).astype(np.uint8)
    color_map = cv2.applyColorMap(depth_img, cv2.COLORMAP_INFERNO)
    cv2.imwrite(save_path, color_map)
    return prediction, save_path
