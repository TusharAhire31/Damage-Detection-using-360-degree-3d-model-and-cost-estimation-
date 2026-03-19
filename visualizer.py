# visualizer.py
import open3d as o3d
def view_ply(ply_path):
    pcd = o3d.io.read_point_cloud(ply_path)
    o3d.visualization.draw_geometries([pcd])
