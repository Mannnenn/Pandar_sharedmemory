from datetime import datetime
from pointcloud_reader import PointCloudReader


if __name__ == "__main__":
    # 使用例: コールバック関数を定義して後処理を実行する例
    def process_pointcloud(pts):
        # ptsはnumpy.ndarray形式 (N x 4)
        print(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]}: 点群サイズ = {pts.shape[0]}")
        # ...ここに後処理のコードを追加...

    viewer = PointCloudReader(
        shared_memory_name="PointCloudSharedMemory",
        pandar_app_path="../build/PandarApp",
        window_name="My PointCloud Viewer",
        update_rate=10,
        processing_callback=process_pointcloud  # コールバック関数を登録
    )

    try:
        # 以下のrun_processor()かrun_visualizer()のどちらかを実行する.

        # こっちを実行するとコールバック関数が呼ばれるようになる.
        # 実処理を行うときはこちらを使って、process_pointcloudの中に処理を追加

        # viewer.run_processor()

        # こっちを実行するとコールバック関数は呼ばれない.
        # 点群データを表示するだけの処理

        viewer.run_visualizer()
    except KeyboardInterrupt:
        viewer.stop()