# ビルド方法

コードを任意のディレクトリの中に clone します。

```shell
cd ~/your_dir
git clone https://github.com/Mannnenn/Pandar_sharedmemory.git
cd Pandar_sharedmemory
```

HesaiLidar_General_SDK を含む C++ファイルをビルドします。
この際作成される PandarApp が共有メモリに点群データを書き込みます。

```shell
mkdir build
cd build
cmake ..
make
```

main.py を実行し、点群が表示されることを確かめます。
PandarApp が書き込んだデータを Python 側から読み出し、表示するサンプルプログラムになっています。

```
cd ../scripts
uv run main.py
```

LiDAR を接続し,IP アドレスを指定した状態で実行し、エラーがでず描画されれば問題ありません。

# 使用方法

クラス PointCloudReader をインポートして処理を行います。このクラスのインスタンスを作成したときに PandarApp が呼ばれ、LiDAR からのデータが xyzi(i は intensity,反射強度,照射して帰ってきた光線の強度)を示しています。

以下の関数はどちらか片方のみ実行してください。

## `run_visualizer()`

`run_visualizer()`を実行すると読み出したデータを GUI で描画します。

## `run_processor()`

`run_processor()`を実行すると、点群を読み出す度に`processing_callback`で登録した関数を読み出すようになります。この関数で引数`pts`にアクセスすることで取得した点群に処理を行えます。飛行機の検出や検出結果の描画はこの関数の中で行ってください。
