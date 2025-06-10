import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json
from typing import List
from config import Config
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer

load_dotenv()


class ReRanker:
    def __init__(
        self,
        embedding_model_name: str = Config.EMBEDDING_MODEL_NAME,
        top_k: int = Config.TOP_K,
        prompt_path: str = Config.RERANK_PROMPT
    ):
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.top_k = top_k
        self.prompt_template = self._load_prompt(prompt_path)
        self.llm = self._init_llm()

    def _init_llm(self):
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=Config.LLM_MODEL_NAME,
            temperature=0.0,
        )

    def _load_prompt(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def rerank_with_llm(self, query: str, metadatas: List[dict]) -> List[dict]:
        # Convert metadata to JSON string
        formatted_results = json.dumps(metadatas, indent=2, ensure_ascii=False)

        # Insert into the prompt
        prompt = self.prompt_template.format(query=query, results=formatted_results)

        # Get response
        response = self.llm.invoke(prompt)
        output = response.content.strip()

        try:
            # Try parsing the response back to list of dicts
            reranked_metadatas = json.loads(output)
            if isinstance(reranked_metadatas, list):
                return reranked_metadatas
        except json.JSONDecodeError:
            print("❌ Failed to parse LLM output as JSON")

        # Fallback to original results if parsing fails
        return metadatas


if __name__ == "__main__":
    #query = "suggest me some black shoes"
    query = "suggest me some tshirts for summer"
    #query = "suggest me some backpacks and white shoes"

    rerank_prompt = Config.RERANK_PROMPT

    ranker = ReRanker(prompt_path=rerank_prompt)

    search_results = ranker.rerank_with_llm(query=query, metadatas=[])
    print("\n🎯 Search Results:\n")
    print(search_results)
