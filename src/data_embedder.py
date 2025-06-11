import os
from tqdm import tqdm
from typing import List
from config import Config
from vector_db import ChromaDBClient
from metadata_extractor import MetadataExtractor
from sentence_transformers import SentenceTransformer


class DataEmbedder:
    def __init__(
        self,
        metadata_dir: str,
        metadata_extractor: MetadataExtractor,
        vector_db_client: ChromaDBClient,
        embedding_model_name: str = Config.EMBEDDING_MODEL_NAME
    ):
        self.metadata_dir = metadata_dir
        self.metadata_extractor = metadata_extractor
        self.vector_db_client = vector_db_client
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.batch_size = Config.EMBEDDING_BATCH_SIZE

    def _get_metadata_paths(self) -> List[str]:
        return [
            os.path.join(self.metadata_dir, fname)
            for fname in os.listdir(self.metadata_dir)
            if fname.lower().endswith(".json")
        ]

    def process_and_store(self):
        metadata_paths = self._get_metadata_paths()
        ids, embeddings, documents, metadatas = [], [], [], []

        for metadata_path in tqdm(metadata_paths, desc="🔄 Processing metadata", unit="file"):
            try:
                base_filename = os.path.splitext(os.path.basename(metadata_path))[0]

                # ✨ Skip if ID already exists in ChromaDB
                existing = self.vector_db_client.get_by_id(base_filename)
                if existing and existing.get("ids"):
                    continue

                # 1. Extract metadata
                metadata = self.metadata_extractor.extract_from_file(metadata_path)
                if not metadata:
                    continue

                # 2. Convert metadata to paragraph
                paragraph = self.metadata_extractor.convert_to_paragraph(metadata)

                # 3. Encode paragraph
                embedding = self.embedding_model.encode(paragraph).tolist()

                # 4. Prepare for vector DB
                ids.append(base_filename)
                embeddings.append(embedding)
                documents.append(paragraph)
                metadatas.append(metadata)

                # 5. Add to DB in batches
                if len(ids) >= self.batch_size:
                    try:
                        self.vector_db_client.add_to_vector_db(
                            ids=ids,
                            embeddings=embeddings,
                            documents=documents,
                            metadatas=metadatas
                        )
                        ids, embeddings, documents, metadatas = [], [], [], []
                    except Exception as e:
                        print(f"❌ Failed to save batch of {len(ids)} items: {e}")
                        break  # Terminate on vector DB error too

            except Exception as e:
                print(f"❌ Embedding failed (possible token limit): {e}")
                break  # Stop entire loop if embedding fails

        # Flush remaining items, if any
        if ids:
            try:
                self.vector_db_client.add_to_vector_db(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
                print(f"📦 Added {len(ids)} remaining items to vector DB.")
            except Exception as e:
                print(f"❌ Failed to save final batch of {len(ids)} items: {e}")


if __name__ == '__main__':

    # File paths
    metadata_dir = Config.METADATA_DIR
    html_prompt = Config.HTML_PROMPT
    paragraph_prompt = Config.PARAGRAPH_PROMPT
    style_csv = Config.STYLE_CSV
    image_csv = Config.IMAGE_CSV
    persist_directory = Config.VECTOR_PERSIST_DIRECTORY
    collection_name = Config.VECTOR_COLLECTION_NAME

    # Components
    extractor = MetadataExtractor(html_prompt, paragraph_prompt, style_csv, image_csv)
    vector_client = ChromaDBClient(collection_name=collection_name, persist_directory=persist_directory)

    # Run pipeline
    embedder = DataEmbedder(
        metadata_dir=metadata_dir,
        metadata_extractor=extractor,
        vector_db_client=vector_client
    )
    embedder.process_and_store()

    vector_client.export_all_ids_to_csv(Config.SAVED_ID_PATH)
