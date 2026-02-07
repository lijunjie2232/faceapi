import asyncio
from typing import Optional

from ..db import get_milvus_client

# 各コレクションのロックを格納する辞書
_collection_locks = {}


async def load_collection(
    collection_name: str, timeout: Optional[float] = None, **kwargs
):
    """milvusコレクションをロード。"""
    # この特定のコレクションのロックを取得または作成
    if collection_name not in _collection_locks:
        _collection_locks[collection_name] = asyncio.Lock()

    # スレッドセーフを確保するためにこのコレクションのロックを取得
    async with _collection_locks[collection_name]:
        milvus_client = get_milvus_client()

        state = milvus_client.get_load_state(collection_name=collection_name)
        if state != "3":
            milvus_client.load_collection(
                collection_name=collection_name, timeout=timeout, **kwargs
            )
    # 成功した完了を示すためにTrueを返す
    return True
