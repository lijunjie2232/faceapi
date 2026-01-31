import asyncio
from typing import Optional

from ..db import get_milvus_client

# Dictionary to store locks for each collection
_collection_locks = {}


async def load_collection(
    collection_name: str, timeout: Optional[float] = None, **kwargs
):
    """Load the milvus collection."""
    # Get or create a lock for this specific collection
    if collection_name not in _collection_locks:
        _collection_locks[collection_name] = asyncio.Lock()

    # Acquire the lock for this collection to ensure thread safety
    async with _collection_locks[collection_name]:
        milvus_client = get_milvus_client()

        state = milvus_client.get_load_state(collection_name=collection_name)
        if state != "3":
            milvus_client.load_collection(
                collection_name=collection_name, timeout=timeout, **kwargs
            )
