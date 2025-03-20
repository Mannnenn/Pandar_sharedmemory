import open3d as o3d
import numpy as np
from multiprocessing import shared_memory
import time
from datetime import datetime
import subprocess
import threading

class PointCloudReader:
    def __init__(self,
                 shared_memory_name="PointCloudSharedMemory",
                 pandar_app_path="../build/PandarApp",
                 window_name="Open3D PointCloud Viewer",
                 update_rate=10,
                 processing_callback=None):
        """
        Args:
            shared_memory_name (str): 共有メモリの名前
            pandar_app_path (str): PandarApp 実行ファイルのパス
            window_name (str): Open3D ウィンドウの名前
            update_rate (int): 更新レート(Hz)
            processing_callback (callable): 点群データを受け取った際に呼び出すコールバック関数。
                引数としてnumpy.ndarray形式の点群データ (N x 4) が渡される。
                Noneの場合はコールバック処理は行われません。
        """
        self.shared_memory_name = shared_memory_name
        self.pandar_app_path = pandar_app_path
        self.window_name = window_name
        self.update_interval = 1.0 / update_rate
        self.vis = None
        self.running = False
        self.pcd = o3d.geometry.PointCloud()
        self.pandar_process = None
        self.processing_callback = processing_callback
        self.latest_pointcloud = None

    def read_pointcloud(self):
        try:
            shm = shared_memory.SharedMemory(name=self.shared_memory_name)
        except Exception as e:
            print("共有メモリオープン失敗:", e)
            return np.empty((0, 4), dtype=np.float32)

        buffer = shm.buf
        count = np.frombuffer(buffer, dtype=np.int32, count=1)[0]
        if count == 0:
            return np.empty((0, 4), dtype=np.float32)
        pts_np = np.frombuffer(buffer, dtype=np.float32, offset=4, count=count * 4)
        pts_np = pts_np.reshape((count, 4)).copy()
        return pts_np

    def get_point_cloud(self):
        pts_np = self.read_pointcloud()
        if pts_np.size == 0:
            return None
        pcd = o3d.geometry.PointCloud()
        points = pts_np[:, :3]
        pcd.points = o3d.utility.Vector3dVector(points)
        return pcd

    def start_pandar_app(self):
        try:
            self.pandar_process = subprocess.Popen([self.pandar_app_path])
        except Exception as e:
            print("PandarApp の起動失敗:", e)

    def exit_callback(self, vis):
        self.running = False
        return False

    def run_visualizer(self):
        """Visualizerを使った表示モード"""
        
        self.start_pandar_app()
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        self.vis.create_window(self.window_name)
        init_pcd = self.get_point_cloud() or o3d.geometry.PointCloud()
        self.pcd = init_pcd
        self.vis.add_geometry(self.pcd)
        self.vis.register_key_callback(ord("Q"), self.exit_callback)
        self.vis.register_key_callback(ord("q"), self.exit_callback)

        self.running = True
        while self.running:
            cycle_start = time.time()
            new_pcd = self.get_point_cloud()
            if new_pcd is None or len(new_pcd.points) == 0:
                print("点群データを受信できませんでした。")
            else:
                # ビジュアライザーの表示用に更新
                self.pcd.points = new_pcd.points
                self.vis.update_geometry(self.pcd)
            self.vis.poll_events()
            self.vis.update_renderer()
            elapsed = time.time() - cycle_start
            time.sleep(max(0, self.update_interval - elapsed))
        self.vis.destroy_window()

    def run_processor(self):
        """高速な後処理用モード。Visualizerを起動せず、点群をコールバック関数によって利用可能にする"""
        self.start_pandar_app()
        self.running = True
        while self.running:
            cycle_start = time.time()
            pts_np = self.read_pointcloud()
            if pts_np.size == 0:
                # 点群データが存在しない場合の処理
                print("点群データを受信できませんでした。")
            else:
                self.latest_pointcloud = pts_np
                if self.processing_callback is not None:
                    # コールバックにnumpy配列の点群データを渡す
                    self.processing_callback(pts_np)
            elapsed = time.time() - cycle_start
            time.sleep(max(0, self.update_interval - elapsed))
    
    def stop(self):
        self.running = False

    def __del__(self):
        if self.pandar_process is not None:
            try:
                self.pandar_process.terminate()
                self.pandar_process.wait()
                print("PandarAppをクラス破棄時に終了しました。")
            except Exception as e:
                print("PandarApp終了時にエラーが発生しました:", e)