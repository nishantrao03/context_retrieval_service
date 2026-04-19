# updation/archive_chunks.py

from vectorstore.pinecone_client import get_pinecone_index


INDEX_NAME = "slack-bot-context"
EMBEDDING_DIMENSION = 384


async def archive_chunks(retrieved_update_chunks, project_id, index_name=INDEX_NAME):
    """
    Updates retrieved chunk metadata by setting update_status to archived.
    """

    index = get_pinecone_index(index_name, EMBEDDING_DIMENSION)

    for chunk_group in retrieved_update_chunks.get("retrieved_update_chunks", []):
        for chunk in chunk_group:
            chunk_id = chunk.get("chunk_id")

            if chunk_id:
                index.update(
                    id=chunk_id,
                    set_metadata={
                        "update_status": "archived"
                    },
                    namespace=project_id
                )

# # updation/archive_chunks.py

# import asyncio
# from vectorstore.pinecone_client import get_pinecone_index


# INDEX_NAME = "slack-bot-context"
# EMBEDDING_DIMENSION = 384


# async def archive_chunks(retrieved_update_chunks):
#     """
#     Updates retrieved chunk metadata by setting update_status to archived.
#     """

#     index = get_pinecone_index(INDEX_NAME, EMBEDDING_DIMENSION)

#     async def update_chunk(chunk_id):
#         index.update(
#             id=chunk_id,
#             set_metadata={
#                 "update_status": "archived"
#             }
#         )

#     tasks = []

#     for chunk_group in retrieved_update_chunks.get("retrieved_update_chunks", []):
#         for chunk in chunk_group:
#             chunk_id = chunk.get("chunk_id")

#             if chunk_id:
#                 tasks.append(update_chunk(chunk_id))

#     if tasks:
#         await asyncio.gather(*tasks)                