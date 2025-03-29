from datetime import datetime
from typing import List

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from llms.openai import openai_embeddings
from config.envs import PINECONE_API_KEY, PINECONE_INDEX_NAME

pc = Pinecone(api_key=PINECONE_API_KEY)
pc_index = pc.Index(name=PINECONE_INDEX_NAME)
pc_vector_store = PineconeVectorStore(index=pc_index, embedding=openai_embeddings)


def get_relevant_docs(query: str, k: int = 1) -> List[Document]:
    current_year: int = datetime.now().year
    docs: List[Document] = pc_vector_store.similarity_search(
        query=query,
        k=k,
        filter={
            # Retrieve only data from the past year.
            "lastmod_year": {"$gte": current_year - 1}
        },
    )
    return docs
