import argparse
import re
from pathlib import Path
from typing import Callable

import numpy as np
import torch
import yaml
from pymilvus import DataType, MilvusClient
from StarNet import faceDetector, get_s3, inference

# デフォルトのデバイスとモデル設定
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
MODEL_PATH = "g_m3.pt"


def load_milvus_config(config_path="milvus_config.yaml"):
    """
    YAMLファイルからMilvus設定を読み込み
    """
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config["milvus"]


def load_model(get_sn: Callable, model_path: Path, device: str | torch.device):
    """
    顔認識モデルを読み込み、Milvusクライアントを初期化
    """
    # モデルを読み込み
    return get_sn(model_path).eval().to(device)


def init_milvus(client):
    """
    Milvusを初期化
    """
    # YAMLからMilvus設定を読み込み
    config = load_milvus_config()

    # Milvusクライアントを初期化
    client = MilvusClient(
        uri=config["uri"],
        token=config["token"],
    )

    if "test" not in client.list_databases():
        client.create_database("test")

    client.use_database("test")

    # コレクションが存在するか確認し、存在しない場合は作成
    if not client.has_collection("experiment"):
        create_collection(client)

    # コレクションをロード
    client.load_collection("experiment")

    # スキーマを作成
    schema = MilvusClient.create_schema()
    schema.add_field("id", DataType.INT64, is_primary=True, auto_id=True)
    schema.add_field("vector", DataType.FLOAT_VECTOR, dim=512)
    schema.add_field("user_id", DataType.INT64)
    schema.add_field("user_name", DataType.VARCHAR, max_length=200)

    # コレクションを作成
    client.create_collection(
        collection_name="experiment",
        dimension=512,
        metric_type="COSINE",
        schema=schema,
    )

    # インデックスパラメータを設定
    index_params = MilvusClient.prepare_index_params()

    # ベクトルフィールドにインデックスを追加
    index_params.add_index(
        field_name="vector",
        metric_type="COSINE",
        index_type="IVF_FLAT",
        index_name="vector_index",
    )

    # インデックスファイルを作成
    client.create_index(
        collection_name="experiment",
        index_params=index_params,
        sync=False,
    )

    client.flush("experiment")
    print("顔認識用の新しいコレクションを作成しました")


def add_user_to_database(image_path, user_name, user_id, model, client, device):
    """
    顔認識データベースに新しいユーザーを追加。

    引数:
        image_path: ユーザーの画像ファイルへのパス
        user_name: ユーザー名
        user_id: ユーザーの一意のID
        model: 読み込まれた顔認識モデル
        client: Milvusクライアントインスタンス
        device: 計算デバイス

    戻り値:
        bool: ユーザーが正常に追加された場合はTrue、それ以外はFalse
    """
    face_detector = faceDetector()

    # 画像内の顔を検出
    detected_faces = face_detector(image_path)

    if not detected_faces:
        print(f"エラー: 画像内に顔が検出されませんでした: {image_path}")
        return False

    # 検出された顔から特徴を抽出
    face_img = detected_faces[0]
    features = inference(model, face_img, device=device)

    # データベースに挿入
    entities = [
        {
            "vector": features[0].tolist(),
            "user_id": int(user_id),
            "user_name": user_name,
        }
    ]

    try:
        insert_result = client.insert(collection_name="experiment", data=entities)
        client.flush("experiment")
        print(f"ユーザー '{user_name}' (ID: {user_id}) をデータベースに正常に追加しました")
        return True
    except Exception as e:
        print(f"データベースへのユーザー挿入エラー: {e}")
        return False


def predict_face_identity(
    image_path, model, client: MilvusClient, device, threshold=0.7
):
    """
    画像から特徴を抽出し、Milvusデータベース内で類似の顔を検索することで顔の身元を予測。

    引数:
        image_path: 画像ファイルへのパス
        model: 読み込まれた顔認識モデル
        client: Milvusクライアントインスタンス
        device: 計算デバイス
        threshold: 顔認識の信頼度閾値

    戻り値:
        dict: 顔が見つかったかどうか、身元、信頼度スコアを含む
    """
    face_detector = faceDetector()

    # 画像内の顔を検出
    detected_faces = face_detector(image_path)

    if not detected_faces:
        return {
            "success": False,
            "found": False,
            "identity": None,
            "confidence": 0.0,
            "message": "画像内に顔が検出されませんでした",
        }

    # 検出された顔から特徴を抽出
    from StarNet import inference

    face_img = detected_faces[0]
    features = inference(model, face_img, device=device)

    # Milvusデータベース内で類似の顔を検索
    search_result = client.search(
        collection_name="experiment",
        anns_field="vector",
        data=[features[0]],
        limit=3,
        output_fields=["user_id", "user_name"],
        search_params={
            "params": {
                "radius": threshold,  # 検索の半径として閾値を使用
            },
        },
    )

    if not search_result or len(search_result[0]) == 0:
        return {
            "success": True,
            "found": False,
            "identity": None,
            "confidence": 0.0,
            "message": "データベース内に類似の顔が見つかりませんでした",
        }

    # 最上位の一致を取得
    top_match = search_result[0][0]
    similarity_score = top_match.distance  # 距離を類似度に変換
    user_id = top_match.entity.get("user_id")
    user_name = top_match.entity.get("user_name")
    return {
        "success": True,
        "found": True,
        "identity": {"user_id": user_id, "user_name": user_name},
        "confidence": similarity_score,
        "message": f"データベース内で顔が見つかりました。身元: {user_name} (ID: {user_id})",
    }


def main():
    parser = argparse.ArgumentParser(
        description="データベースにユーザーを追加するか、画像から顔の身元を予測"
    )
    parser.add_argument("image_path", type=str, help="画像ファイルへのパス")

    # アクションの相互排他的グループ
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--predict",
        action="store_true",
        help="顔認識予測を実行（デフォルト動作）",
    )
    action_group.add_argument(
        "--add-user",
        nargs=2,
        metavar=("USER_NAME", "USER_ID"),
        help="データベースに新しいユーザーを追加（ユーザー名とユーザーIDが必要）",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.2285,
        help="認識の信頼度閾値（デフォルト: 0.2285）",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=DEVICE,
        help=f"計算デバイス（デフォルト: {DEVICE}）",
    )

    args = parser.parse_args()

    # 画像パスを検証
    img_path = Path(args.image_path)
    if not img_path.exists():
        print(f"エラー: 画像ファイルが存在しません: {args.image_path}")
        return

    # モデルとクライアントを読み込み
    print("モデルを読み込み、データベースに接続しています...")
    try:
        model, client = load_model_and_client()
    except Exception as e:
        print(f"モデル読み込みまたはデータベース接続エラー: {e}")
        return

    if args.add_user:
        # データベースにユーザーを追加
        user_name, user_id_str = args.add_user

        # ユーザーIDが数値であることを検証
        try:
            user_id = int(user_id_str)
        except ValueError:
            print(f"エラー: ユーザーIDは数値である必要があります、入力: {user_id_str}")
            return

        # ユーザー名の形式を検証
        if not re.match(r"^[A-Za-z0-9 _-]+$", user_name):
            print(f"エラー: ユーザー名に無効な文字が含まれています: {user_name}")
            print(
                "英数字、スペース、ハイフン、アンダースコアのみが許可されています"
            )
            return

        success = add_user_to_database(
            image_path=args.image_path,
            user_name=user_name,
            user_id=user_id,
            model=model,
            client=client,
            device=args.device,
        )

        if success:
            print(
                f"ユーザー '{user_name}' (ID: {user_id}) がデータベースに正常に追加されました！"
            )
        else:
            print("データベースへのユーザー追加に失敗しました。")

    elif args.predict or not (args.add_user):  # デフォルト動作は予測
        # 予測を実行
        print(f"画像内の顔を分析しています: {args.image_path}")
        result = predict_face_identity(
            image_path=args.image_path,
            model=model,
            client=client,
            device=args.device,
            threshold=args.threshold,
        )

        # 結果を出力
        print("\n予測結果:")
        print(f"成功: {result['success']}")
        print(f"データベース内に見つかりました: {result['found']}")
        print(f"信頼度: {result['confidence']:.3f}")
        print(f"メッセージ: {result['message']}")

        if result["identity"]:
            identity = result["identity"]
            print(f"身元: {identity['user_name']} (ID: {identity['user_id']})")


if __name__ == "__main__":
    main()
