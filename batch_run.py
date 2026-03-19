# batch_run.py
import os
from models.damage_segmenter import detect_damage
from models.depth_estimator import estimate_depth
from models.vehicle_classifier import detect_vehicle_type
from utils.mask_to_depth import mask_applied_depth, depth_stats
from utils.color_mapping import depth_to_color
from utils.depth_to_mesh import depth_to_pointcloud
from cost_estimator import estimate_cost_from_masked_depth
from garage_locator import find_nearby_garages
import cv2

INPUT = "data/images"
OUT = "outputs"
os.makedirs(OUT, exist_ok=True)

images = [f for f in os.listdir(INPUT) if f.lower().endswith(('.jpg','.png'))][:15]
for img in images:
    img_path = os.path.join(INPUT,img)
    print("Processing", img)
    vt = detect_vehicle_type(img_path)
    print("Vehicle:", vt)
    mask, mask_path, ann = detect_damage(img_path)
    print("Mask:", mask_path)
    depth, dp = estimate_depth(img_path)
    print("Depth:", dp)
    masked = mask_applied_depth(depth, mask)
    stats = depth_stats(masked)
    colored = depth_to_color(depth, mask=mask)
    cv2.imwrite(os.path.join("outputs","colored_depth",os.path.splitext(img)[0]+"_color.png"), colored)
    pcd = depth_to_pointcloud(masked, color_img=colored, save_path=os.path.join("outputs","meshes",os.path.splitext(img)[0]+"_pc.ply"))
    cost = estimate_cost_from_masked_depth(masked, vehicle_type=vt)
    garages = find_nearby_garages("411001")
    report = os.path.join("outputs","reports",os.path.splitext(img)[0]+"_report.txt")
    os.makedirs(os.path.dirname(report), exist_ok=True)
    with open(report,"w",encoding="utf-8") as f:
        f.write(f"Image: {img}\nVehicle: {vt}\nArea px: {stats['area_pixels']}\nMean depth: {stats['mean_depth']}\nCost: {cost}\nGarages: {garages}\n")
    print("Done:", img)
