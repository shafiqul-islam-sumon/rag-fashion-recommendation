import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from config import Config
from re_ranker import ReRanker
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from vector_db import ChromaDBClient
from sentence_transformers import SentenceTransformer

load_dotenv()


class DataRetriever:
    def __init__(
        self,
        vector_db_client: ChromaDBClient,
        embedding_model_name: str = Config.EMBEDDING_MODEL_NAME,
        top_k: int = Config.TOP_K,
    ):
        self.ranker = ReRanker()
        self.vector_db_client = vector_db_client
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.top_k = top_k
        self.llm = self._init_llm()

    def _init_llm(self):
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=Config.LLM_MODEL_NAME,
            temperature=0.0,
        )

    def search(self, query: str):
        query_embedding = self.embedding_model.encode(query).tolist()

        results = self.vector_db_client.query(
            query_embedding=query_embedding,
            n_results=self.top_k,
            include=["metadatas"]
        )

        if not results or not results["metadatas"] or not results["metadatas"][0]:
            print("❌ No results found.")
            return

        top_matches = results["metadatas"][0]

        final_output = self.ranker.rerank_with_llm(query, top_matches)

        return final_output


if __name__ == "__main__":
    #query = "suggest me some black shoes"
    query = "suggest me some tshirts for summer"
    #query = "suggest me some backpacks and white shoes"

    vector_client = ChromaDBClient(
        collection_name=Config.VECTOR_COLLECTION_NAME,
        persist_directory=Config.VECTOR_PERSIST_DIRECTORY
    )

    retriever = DataRetriever(
        vector_db_client=vector_client,
    )

    search_results = retriever.search(query)
    print("\n🎯 Search Results:\n")
    print(search_results)
