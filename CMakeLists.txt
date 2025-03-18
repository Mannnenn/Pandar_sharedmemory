cmake_minimum_required(VERSION 3.10)
project(PandarPythonInterface C CXX)

# Boostの設定（必要なコンポーネントがあれば追加してください）
find_package(Boost REQUIRED COMPONENTS system thread)
find_package( PCL REQUIRED COMPONENTS common )

find_package(Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

# set (CMAKE_CXX_FLAGS "-fPIC --std=c++11")
ADD_COMPILE_OPTIONS(-std=c++11 )
ADD_COMPILE_OPTIONS(-std=c++14 )

# HesaiLidarのSDKをサブディレクトリとして追加
add_subdirectory(HesaiLidar_General_SDK)

# インクルードディレクトリの追加
include_directories(
    HesaiLidar_General_SDK/include
    HesaiLidar_General_SDK/src/PandarGeneralRaw/include
    ${Boost_INCLUDE_DIRS}
    ${PCL_INCLUDE_DIRS}

)

# 実行ファイルの定義（ファイル名やソースは必要に応じて変更してください）
add_executable(PandarApp
    lidar_callback.cpp
)

# 必要なライブラリのリンク
target_link_libraries(PandarApp
    PandarGeneralSDK
    ${Boost_LIBRARIES}
)