import chromadb
import numpy as np
import pandas as pd
from config import Config
from typing import List, Optional


class ChromaDBClient:
    def __init__(self, collection_name: str, persist_directory: str):
        """
        Initializes a native ChromaDB client for storing precomputed embeddings.
        """
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_to_vector_db(
            self,
            ids: List[str],
            embeddings: List[List[float]],
            documents: List[str],
            metadatas: Optional[List[dict]] = None,
    ):
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def get_by_id(self, item_id: str):
        try:
            return self.collection.get(ids=[item_id])
        except Exception:
            return {"ids": []}  # Return empty result if not found or failed

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[dict] = None,
        include: Optional[List[str]] = None
    ):
        """
        Performs similarity search using an embedding, with optional metadata filtering.
        """
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=include
        )

    def export_all_ids_to_csv(self, output_path: str):
        try:
            all_ids = []
            offset = 0
            limit = 500  # Adjustable depending on expected total size

            while True:
                result = self.collection.get(
                    offset=offset,
                    limit=limit
                )
                if not result.get('ids'):
                    break
                all_ids.extend(result['ids'])
                offset += limit

            df = pd.DataFrame({"id": all_ids})
            df.to_csv(output_path, index=False)
            print(f"✅ Exported {len(all_ids)} IDs to {output_path}")
        except Exception as e:
            print(f"❌ Failed to export IDs: {e}")

    def export_all_data_to_txt(self, output_path: str, include_embeddings: bool = False):
        """
        Groups and exports all entries by 'sub_category' into a text file.
        Each group includes ID, document, metadata, and optionally embeddings.
        """
        try:
            offset = 0
            limit = 500
            grouped = {}

            while True:
                result = self.collection.get(
                    offset=offset,
                    limit=limit,
                    include=["documents", "metadatas"] + (["embeddings"] if include_embeddings else [])
                )
                ids = result.get("ids", [])
                if not ids:
                    break

                documents = result.get("documents", [])
                metadatas = result.get("metadatas", [])
                embeddings = result.get("embeddings", []) if include_embeddings else []

                for i, item_id in enumerate(ids):
                    metadata = metadatas[i]
                    sub_category = metadata.get("sub_category", "Unknown")
                    if sub_category not in grouped:
                        grouped[sub_category] = []

                    entry = f"ID: {item_id}\n"
                    entry += f"Document: {documents[i]}\n"
                    entry += f"Metadata: {metadata}\n"
                    if include_embeddings:
                        entry += f"Embedding: {embeddings[i][:5]}... (truncated)\n"
                    entry += "-" * 50 + "\n"
                    grouped[sub_category].append(entry)

                offset += limit

            with open(output_path, "w", encoding="utf-8") as f:
                for sub_category, entries in grouped.items():
                    f.write(f"\n===== Subcategory: {sub_category} =====\n\n")
                    f.writelines(entries)

            print(f"✅ Exported grouped data by sub_category to {output_path}")
        except Exception as e:
            print(f"❌ Failed to export grouped data: {e}")


if __name__ == "__main__":

    client = ChromaDBClient(
        collection_name=Config.VECTOR_COLLECTION_NAME,
        persist_directory=Config.VECTOR_PERSIST_DIRECTORY
    )

    ids = ["img_001", "img_002"]
    embeddings = [np.random.rand(512).tolist(), np.random.rand(512).tolist()]
    metadatas = [{"color": "blue", "category": "tshirt"}, {"color": "red", "category": "dress"}]
    documents = [
        "This is a blue t-shirt made from cotton. Great for summer.",
        "A red evening dress suitable for formal events."
    ]

    client.add_to_vector_db(ids, embeddings, documents, metadatas)

    # Search example
    query_embedding = np.random.rand(512).tolist()
    results = client.query(query_embedding, n_results=2, include=["metadatas", "documents"])

    print("#### result", results)

    client.export_all_ids_to_csv(Config.SAVED_ID_PATH)
    client.export_all_data_to_txt(Config.SAVED_DATA_PATH, include_embeddings=False)


