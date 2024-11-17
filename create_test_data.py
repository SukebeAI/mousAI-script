import cv2
import json
import random
import argparse
import os
from scipy.spatial import ConvexHull


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Process images and detect sensitive areas.')
    parser.add_argument('--input', type=str, default='test',
                        help='Input directory containing images.')
    parser.add_argument('--version', type=str, default='1.0',
                        help='JSON format version.')

    return parser.parse_args()


def create_test_json(video_path, output_json_path, mask_groups=2):
    # 動画の絶対パスを取得
    absolute_video_path = os.path.abspath(video_path)

    # 動画を開く
    cap = cv2.VideoCapture(absolute_video_path)
    if not cap.isOpened():
        raise FileNotFoundError(
            f"Could not open the video file: {absolute_video_path}")

    # 動画の情報を取得
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # JSONデータの雛形
    json_data = {
        "version": "1.0",
        "videoPath": absolute_video_path,
        "masks": []
    }

    # マスクグループを生成
    for _ in range(mask_groups):
        mask_group = []

        for frame_idx in range(total_frames):
            vertices = []
            num_vertices = random.randint(3, 10)
            for _ in range(num_vertices):
                x = random.randint(0, width)
                y = random.randint(0, height)
                vertices.append([x, y])

            hull = ConvexHull(vertices)

            # 凸包の頂点を取得
            hull_vertices = [vertices[vertex] for vertex in hull.vertices]
            # マスク情報
            mask = {
                "frame": frame_idx,
                "vertices": hull_vertices
            }
            mask_group.append(mask)

        # マスクグループを追加
        json_data["masks"].append(mask_group)

    # 動画を閉じる
    cap.release()

    # JSONファイルを書き出す
    with open(output_json_path, "w") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"JSON file has been saved to {output_json_path}")


if __name__ == '__main__':
    args = parse_arguments()

    # 実行例
    video_path = args.input  # 入力動画ファイルパス
    output_json_path = "output.json"       # 出力JSONファイルパス
    create_test_json(video_path, output_json_path)
