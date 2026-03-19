# gui/visualization_page.py
# Placeholder if you want a Tk window to trigger 3D view or embed a static preview.
def open_3d_from_file(ply_path):
    import open3d as o3d
    pcd = o3d.io.read_point_cloud(ply_path)
    o3d.visualization.draw_geometries([pcd])
