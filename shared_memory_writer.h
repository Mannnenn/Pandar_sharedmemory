#ifndef SHARED_MEMORY_WRITER_H
#define SHARED_MEMORY_WRITER_H

#include <boost/interprocess/shared_memory_object.hpp>
#include <boost/interprocess/mapped_region.hpp>
#include <cstring>
#include <vector>
#include <string>

struct Point
{
    float x, y, z;
};

class SharedMemoryWriter
{
public:
    SharedMemoryWriter(const std::string &shm_name, std::size_t size)
        : shm_name_(shm_name), size_(size)
    {
        using namespace boost::interprocess;
        // 以前の共有メモリを削除（必要に応じて）
        shared_memory_object::remove(shm_name_.c_str());
        // 読み書き可能な共有メモリを生成
        shm_ = shared_memory_object(boost::interprocess::create_only, shm_name_.c_str(), boost::interprocess::read_write);
        shm_.truncate(size_);
        region_ = mapped_region(shm_, boost::interprocess::read_write);
    }

    ~SharedMemoryWriter()
    {
        using namespace boost::interprocess;
        shared_memory_object::remove(shm_name_.c_str());
    }

    // 点群データを共有メモリに書き込みます。
    void writeData(const std::vector<Point> &points)
    {
        std::size_t data_size = sizeof(int) + points.size() * sizeof(Point);
        if (data_size > size_)
        {
            // データサイズが領域サイズを超える場合のエラーハンドリング
            return;
        }
        void *addr = region_.get_address();
        int num_points = static_cast<int>(points.size());
        std::memcpy(addr, &num_points, sizeof(num_points));
        std::memcpy(static_cast<char *>(addr) + sizeof(int), points.data(), points.size() * sizeof(Point));
    }

private:
    std::string shm_name_;
    std::size_t size_;
    boost::interprocess::shared_memory_object shm_;
    boost::interprocess::mapped_region region_;
};

#endif // SHARED_MEMORY_WRITER_H