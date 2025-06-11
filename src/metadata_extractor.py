import os
import json
import pandas as pd
from config import Config
from dotenv import load_dotenv
from typing import Dict, Optional
from langchain_groq import ChatGroq

load_dotenv()


class MetadataExtractor:
    def __init__(self, html_prompt_path: str, paragraph_prompt_path: str, style_csv_path: str, images_csv_path: str):
        self.llm = self._init_llm()
        self.html_prompt_template = self._load_prompt(html_prompt_path)
        self.paragraph_prompt_template = self._load_prompt(paragraph_prompt_path)
        self.images_df = self._load_csv(images_csv_path)
        self.style_df = self._load_csv(style_csv_path)

    def _init_llm(self):
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=Config.LLM_MODEL_NAME,
            temperature=0.0,
        )

    def _load_prompt(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(f"System prompt file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_csv(self, path: str) -> pd.DataFrame:
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV file not found: {path}")
        return pd.read_csv(path)

    def _clean_html_with_llm(self, html_content: str) -> str:
        if not html_content.strip():
            return ""

        prompt = self.html_prompt_template.format(html_text=html_content)

        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"⚠️ Failed to clean HTML: {e}")
            raise e  # 🚨 Re-raise to allow outer loop to break

    def _lookup_csv_metadata(self, product_id: int) -> Dict[str, str]:
        row = self.style_df[self.style_df["product_id"] == product_id]
        if row.empty:
            return {}
        return row.iloc[0].to_dict()

    def _lookup_image_url(self, product_id: int) -> Optional[str]:
        filename = f"{product_id}.jpg"
        row = self.images_df[self.images_df["file_name"] == filename]
        if not row.empty:
            return row.iloc[0]["link"]
        return None

    def convert_to_paragraph(self, metadata: dict) -> str:
        ignore_keys = ["product_id", "image_url"]
        label_string = ". ".join(f"{k}: {v}" for k, v in metadata.items() if k not in ignore_keys and v)
        prompt = self.paragraph_prompt_template.format(label_string=label_string)

        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"❌ LLM invocation failed: {e}")
            raise e  # 🚨 Let the outer process_and_store() handle it

    def extract_from_file(self, json_path: str) -> Optional[Dict[str, str]]:
        if not os.path.exists(json_path):
            print(f"❌ File not found: {json_path}")
            return None

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw_json = json.load(f)
        except Exception as e:
            print(f"❌ JSON loading error: {e}")
            return None

        try:
            data = raw_json.get("data", {})
            descriptors = data.get("productDescriptors", {})

            product_id = int(data.get("id", 0))
            brand = data.get("brandName", "")

            description_paragraph = self._clean_html_with_llm(descriptors.get("description", {}).get("value", ""))
            style_note_paragraph = self._clean_html_with_llm(descriptors.get("style_note", {}).get("value", ""))
            materials_care_paragraph = self._clean_html_with_llm(descriptors.get("materials_care_desc", {}).get("value", ""))

            # Final cleaned metadata
            cleaned_metadata = {
                "brand": brand,
                "description": description_paragraph,
                "style_note": style_note_paragraph,
                "materials_care": materials_care_paragraph,
                "price": str(data.get("price", 0)),
            }

            # Lookup from CSV
            csv_data = self._lookup_csv_metadata(product_id)

            # Merge CSV attributes
            for key, value in csv_data.items():
                if key not in cleaned_metadata and pd.notna(value):
                    cleaned_metadata[key] = str(value)

            # Add image URL if available
            image_url = self._lookup_image_url(product_id)
            if image_url:
                cleaned_metadata["image_url"] = image_url

            return cleaned_metadata

        except Exception as e:
            print(f"❌ Metadata extraction error from {json_path}: {e}")
            raise e  # 🚨 allow outer logic to detect and break the loop


if __name__ == "__main__":

    json_file = Config.METADATA_DIR / "1551.json"
    html_prompt = Config.HTML_PROMPT
    paragraph_prompt = Config.PARAGRAPH_PROMPT
    style_csv = Config.STYLE_CSV
    image_csv = Config.IMAGE_CSV

    extractor = MetadataExtractor(html_prompt, paragraph_prompt, style_csv, image_csv)
    metadata = extractor.extract_from_file(json_file)
    paragraph = extractor.convert_to_paragraph(metadata)

    print("✅ paragraph:\n", paragraph)
    if metadata:
        print("✅ Metadata:\n")
        for k, v in metadata.items():
            print(f"{k}: {v}\n")
    else:
        print("❌ Failed to extract metadata.")
