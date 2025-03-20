import open3d as o3d
import numpy as np
from multiprocessing import shared_memory
import time
from datetime import datetime
import subprocess  # 追加

def read_pointcloud():
    # 共有メモリ "PointCloudSharedMemory" をオープン
    shm = shared_memory.SharedMemory(name="PointCloudSharedMemory")
    buffer = shm.buf

    # 先頭4バイトから点の数を取得
    count = np.frombuffer(buffer, dtype=np.int32, count=1)[0]
    if count == 0:
        return np.empty((0, 4), dtype=np.float32)

    # 共有メモリ内のデータをfloat32として読み込み、(count,4)に変換（x,y,z,intensity）
    pts_np = np.frombuffer(buffer, dtype=np.float32, offset=4, count=count * 4).reshape((count, 4)).copy()
    return pts_np

def get_point_cloud():
    pts_np = read_pointcloud()
    if pts_np.size == 0:
        return None
    pcd = o3d.geometry.PointCloud()
    # 点の座標は最初の3列
    points = pts_np[:, :3]
    pcd.points = o3d.utility.Vector3dVector(points)

    # # 点の色は4列目をグレースケールに変換してRGBにする
    # intensities = pts_np[:, 3]
    # # 0~255範囲の値をグレースケールのRGB ([0,0,0]~[255,255,255]) に変換するため、連続した配列を確保
    # colors = np.empty((intensities.shape[0], 3), dtype=np.float32)
    # colors[:] = intensities[:, None]
    # pcd.colors = o3d.utility.Vector3dVector(colors)

    return pcd

if __name__ == "__main__":
    # build ディレクトリ内の PandarApp 実行ファイルを呼び出す
    pandar_app_path = "../build/PandarApp"
    try:
        pandar_process = subprocess.Popen([pandar_app_path])
    except Exception as e:
        print("Failed to start PandarApp:", e)

    vis = o3d.visualization.VisualizerWithKeyCallback()
    vis.create_window("Open3D PointCloud Viewer")

    init_pcd = get_point_cloud()
    if init_pcd is None:
        init_pcd = o3d.geometry.PointCloud()
    vis.add_geometry(init_pcd)

    running = True
    def exit_callback(vis):
        global running
        running = False
        return False

    vis.register_key_callback(ord("Q"), exit_callback)
    vis.register_key_callback(ord("q"), exit_callback)

    while running:
        cycle_start = time.time()
        
        new_pcd = get_point_cloud()
        if new_pcd is None or len(new_pcd.points) == 0:
            print("Received no point cloud data.")
        else:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            # print("Timestamp {} Received {} points.".format(timestamp, len(new_pcd.points)))
            init_pcd.points = new_pcd.points
            vis.update_geometry(init_pcd)

        vis.poll_events()
        vis.update_renderer()
        
        elapsed = time.time() - cycle_start
        sleep_time = max(0, 0.1 - elapsed) #0.1s->10Hz
        time.sleep(sleep_time)

    vis.destroy_window()