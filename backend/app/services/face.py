"""
顔認識システムの顔サービスモジュール。

このモジュールは顔検証と埋め込み更新を含む
顔認識操作のビジネスロジックを含みます。
"""

import time
from typing import Any, Dict

import cv2
import numpy as np
from fastapi import HTTPException, UploadFile

from ..core import _CONFIG_
from ..core.config import Config
from ..db import FACE_FEATURES_COLLECTION, get_milvus_client
from ..face_rec import _MODEL_ as model
from ..models import UserModel
from ..utils import (
    create_access_token,
    detect_face,
    image_to_base64,
    inference,
    load_collection,
)


async def verify_face_service(image: UploadFile) -> Dict[str, Any]:
    """
    アップロードされた画像から顔を検証するサービス関数。

    引数:
        image: 顔を含むアップロードされた画像ファイル

    戻り値:
        認識結果と成功時のトークンを含む辞書
    """
    # 画像ファイルを読み込み
    contents = await image.read()

    # numpy配列に変換
    nparr = np.frombuffer(contents, np.uint8)
    # pylint: disable=no-member
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # pylint: enable=no-member

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # 画像内の顔を検出
    detected_faces = detect_face(img)

    if not detected_faces:
        return {
            "recognized": False,
            "message": "No face detected in the image",
            "data": {
                "token": None,
                "token_type": "Bearer",
            },
            "code": 400,
        }

    # 顔から特徴を抽出
    features = [
        inference(model, face_img, device=_CONFIG_.MODEL_DEVICE).reshape(512)
        for face_img in detected_faces
    ]

    # 共有Milvusクライアントを取得
    milvus_client = get_milvus_client()

    await load_collection(FACE_FEATURES_COLLECTION)

    # コレクション内で類似の顔を検索
    search_results = milvus_client.search(
        collection_name=FACE_FEATURES_COLLECTION,
        data=features,
        limit=1,  # 最も近い一致のみ必要
        output_fields=["user_id"],
        search_params={
            "metric_type": "COSINE",
            "params": {"radius": _CONFIG_.MODEL_THRESHOLD},
        },
    )
    if not any(search_results):
        # 一致する顔が見つからない
        return {
            "recognized": False,
            "message": "Face not recognized in the database",
            "data": {
                "token": None,
                "token_type": "Bearer",
            },
            "code": 401,
        }

    # 最良の一致を取得
    # best_match = search_results[0][0]
    best_match = list(filter(lambda l: len(l) > 0, search_results))[0][0]

    # 顔が認識され、ユーザー情報を取得しトークンを作成
    user_id = best_match["entity"]["user_id"]

    # アクセストークンを作成
    access_token = create_access_token(
        data={"sub": str(user_id)},
    )

    return {
        "recognized": True,
        "message": f"Face recognized as user(id={user_id})",
        "user_id": user_id,
        "confidence": 1 - best_match["distance"],  # 距離を類似度に変換
        "data": {
            "token": access_token,
            "token_type": "Bearer",
        },
        "code": 200,
    }


async def update_face_embedding_service(
    user_id: int, image: UploadFile
) -> Dict[str, Any]:
    """
    ユーザーの顔埋め込みを更新するサービス関数。

    引数:
        user_id: 顔埋め込みを更新するユーザーのID
        image: 新しい顔を含むアップロードされた画像ファイル

    戻り値:
        成功メッセージと埋め込みIDを含む辞書
    """
    # 画像ファイルを読み込み
    contents = await image.read()

    # numpy配列に変換
    nparr = np.frombuffer(contents, np.uint8)
    # pylint: disable=no-member
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # pylint: enable=no-member

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # ユーザーオブジェクトを取得
    user = await UserModel.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 画像内の顔を検出
    detected_faces = detect_face(img)

    if not detected_faces:
        raise HTTPException(status_code=400, detail="No face detected in the image")

    if len(detected_faces) > 1:
        raise HTTPException(
            status_code=400,
            detail="Multiple faces detected. Please upload an image with only one face.",
        )

    # 最初に検出された顔を処理
    face_img = detected_faces[0]

    # 顔から特徴を抽出
    features = inference(model, face_img, device=_CONFIG_.MODEL_DEVICE)

    # 共有Milvusクライアントを取得
    milvus_client = get_milvus_client()

    await load_collection(FACE_FEATURES_COLLECTION)

    # コレクション内で類似の顔を検索
    search_results = milvus_client.search(
        collection_name=FACE_FEATURES_COLLECTION,
        data=features,
        limit=1,  # 最も近い一致のみ必要
        output_fields=["user_id"],
        search_params={
            "metric_type": "COSINE",
            "params": {"radius": _CONFIG_.MODEL_THRESHOLD},
        },
    )
    if any(search_results) and not _CONFIG_.ALLOW_FACE_DEDUPICATION:
        raise HTTPException(
            status_code=400,
            detail="Face already exists in the database. Please use a different face or contact the administrator.",
        )

    # 新しい顔特徴をコレクションに挿入
    entities = [
        {
            "user_id": user_id,
            "feature_vector": features[0].tolist(),
            "update_at": int(time.time() * 1000),  # エポックからのミリ秒に変換
        }
    ]

    insert_result = milvus_client.upsert(
        collection_name=FACE_FEATURES_COLLECTION, data=entities
    )

    # Milvusクライアントからの応答の可能性のあるバリエーションを処理
    inserted_id = None
    if isinstance(insert_result, dict):
        # 応答内の異なる可能なキーを確認
        if "insertedIds" in insert_result:
            inserted_id = (
                insert_result["insertedIds"][0]
                if insert_result["insertedIds"]
                else None
            )
        elif "inserted_ids" in insert_result:
            inserted_id = (
                insert_result["inserted_ids"][0]
                if insert_result["inserted_ids"]
                else None
            )
    elif hasattr(insert_result, "inserted_ids"):
        inserted_id = (
            insert_result.inserted_ids[0] if insert_result.inserted_ids else None
        )

    # SQLでバイト単位で画像を更新
    user.head_pic = image_to_base64(img)
    await user.save()

    return {
        "success": True,
        "message": f"Face embedding updated successfully for user ID {user_id}",
        "new_embedding_id": inserted_id,
    }
