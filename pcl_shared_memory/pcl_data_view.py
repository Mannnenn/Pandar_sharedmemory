import open3d as o3d
import numpy as np
import time
import struct
from multiprocessing import shared_memory

def read_pointcloud():
    # 共有メモリ "PointCloudSharedMemory" をオープン
    shm = shared_memory.SharedMemory(name="PointCloudSharedMemory")
    buffer = shm.buf

    # 先頭4バイトから点の数を取得
    count = struct.unpack("i", buffer[:4])[0]
    points = []
    offset = 4
    for _ in range(count):
        if offset + 12 > len(buffer):
            break
        x, y, z = struct.unpack("fff", buffer[offset:offset+12])
        points.append((x, y, z))
        offset += 12
    return points

def get_point_cloud():
    pts = read_pointcloud()
    if not pts:
        return None
    pts_np = np.array(pts, dtype=np.float32)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts_np)
    return pcd

if __name__ == "__main__":
    # VisualizerWithKeyCallback を初期化してウィンドウを作成
    vis = o3d.visualization.VisualizerWithKeyCallback()
    vis.create_window("Open3D PointCloud Viewer")
    
    # 初回の点群取得
    init_pcd = get_point_cloud()
    if init_pcd is None:
        init_pcd = o3d.geometry.PointCloud()
    vis.add_geometry(init_pcd)
    
    running = True
    def exit_callback(vis):
        global running
        running = False
        return False

    # 'q' または 'Q' キーで終了できるように登録
    vis.register_key_callback(ord("Q"), exit_callback)
    vis.register_key_callback(ord("q"), exit_callback)
    
    while running:
        new_pcd = get_point_cloud()
        if new_pcd is None or len(new_pcd.points) == 0:
            print("Received no point cloud data.")
        else:
            print("Received {} points.".format(len(new_pcd.points)))
            # 既存の点群データを更新
            init_pcd.points = new_pcd.points
            vis.update_geometry(init_pcd)
        vis.poll_events()
        vis.update_renderer()
        
    vis.destroy_window()