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
    parser.add_argument('--windows_base', type=str, default=r"C:\Users\tomoki\workspace",
                        help='Windows baase path.')
    parser.add_argument('--wsl_base', type=str, default="/workspaces",
                        help='WSL base path.')

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
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_duration = total_frames / fps  # 動画の総時間（秒）
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    relative_path = absolute_video_path[len(args.wsl_base):]
    windows_path = args.windows_base + \
        relative_path.replace('/', '\\')  # Replace "/" with "\\"
    # JSONデータの雛形
    json_data = {
        "version": "1.0",
        "videoPath": windows_path,
        "masks": []
    }

    # マスクグループを生成
    for _ in range(mask_groups):
        masks_list = []
        begin_time = 0.0
        while begin_time < total_duration:
            end_time = min(begin_time + random.randint(1, 10),
                           total_duration)

            # ランダムな頂点を生成
            vertices = []
            for _ in range(random.randint(3, 10)):
                x = random.randint(0, width)
                y = random.randint(0, height)
                vertices.append([x, y])

            hull = ConvexHull(vertices)

            # 凸包の頂点を取得
            hull_vertices = [vertices[vertex] for vertex in hull.vertices]
            mask = {
                "begin": round(begin_time, 2),
                "end": round(end_time, 2),
                "vertice": hull_vertices
            }

            masks_list.append(mask)
            begin_time = end_time + random.randint(0, 2)
        json_data["masks"].append(masks_list)

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
    output_json_path = args.input.replace("mp4", "json")       # 出力JSONファイルパス
    create_test_json(video_path, output_json_path)
