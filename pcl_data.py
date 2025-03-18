import struct
from multiprocessing import shared_memory
import time

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

if __name__ == "__main__":
    while True:
        pts = read_pointcloud()
        print("Received {} points".format(len(pts)))
        time.sleep(1)