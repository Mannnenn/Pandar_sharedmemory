#include "pandarGeneral_sdk/pandarGeneral_sdk.h"
#include "shared_memory_writer.h"
#define PRINT_FLAG
// #define PCD_FILE_WRITE_FLAG

int frameItem = 0;

void gpsCallback(int timestamp)
{
#ifdef PRINT_FLAG
    printf("gps: %d\n", timestamp);
#endif
}

void lidarCallback(boost::shared_ptr<PPointCloud> cld, double timestamp)
{
#ifdef PRINT_FLAG
    printf("timestamp: %lf, point_size: %ld\n", timestamp, cld->points.size());
#endif

    // SDK の点群データ構造体から点群データを変換
    std::vector<Point> points;
    for (const auto &pt : cld->points)
    {
        Point p;
        p.x = pt.x;
        p.y = pt.y;
        p.z = pt.z;
        points.push_back(p);
    }

    // 共有メモリにデータを書き込み
    static SharedMemoryWriter shmWriter("PointCloudSharedMemory", 10 * 1024 * 1024); // 10MB領域を確保
    shmWriter.writeData(points);

#ifdef PCD_FILE_WRITE_FLAG
    frameItem++;
    pcl::PCDWriter writer;
    std::string fileName = "PointCloudFrame" + std::to_string(frameItem) + ".pcd";
    writer.write(fileName, *cld);
    printf("save frame %d\n", frameItem);
#endif
}

void lidarAlgorithmCallback(HS_Object3D_Object_List *object_t)
{
    HS_Object3D_Object *object;
#ifdef PRINT_FLAG
    printf("----------------------\n");
    printf("total objects: %d\n", object_t->valid_size);
    for (size_t i = 0; i < object_t->valid_size; i++)
    {
        object = &object_t->data[i];
        printf("id: %u, type: %u\n", object->data.id, object->type);
    }
    printf("----------------------\n");
#endif
}

int main(int argc, char **argv)
{
    PandarGeneralSDK pandarGeneral(std::string("192.168.1.201"), 2368, 0, 10110,
                                   lidarCallback, lidarAlgorithmCallback, gpsCallback, 0, 0, 0,
                                   std::string("Pandar40P"), std::string("frame_id"),
                                   "", "", "", false);
    pandarGeneral.Start();

    while (true)
    {
        sleep(100);
    }

    return 0;
}