---
title: RAG Fashion Recommendation
emoji: 👗
colorFrom: green
colorTo: pink
sdk: docker
app_port: 8501
tags:
- streamlit
- fashion
- recommendation
- chromadb
- rag
- LLM
- ai
license: mit
pinned: false
short_description: A fashion recommendation system powered by RAG and ChromaDB.
---

## 🖼️ Fashion Recommender System Preview

![App Preview](figure/thumbnail.png)


# 👗 RAG Fashion Recommendation

This is a smart **fashion product recommendation system** built using **Retrieval-Augmented Generation (RAG)**. It combines:

- 🧠 Natural language understanding (via LLMs)
- 🛍️ Fashion metadata & embeddings stored in **ChromaDB**
- ⚡ A responsive UI powered by **Streamlit**

## 🛠 Features

- Search fashion items with natural language queries
- Category-based product browsing
- Product detail views with image, brand, price, and more
- Embedded metadata for personalized recommendations

## 📦 Stack

- **Frontend:** Streamlit
- **Backend:** Python + Docker
- **Vector DB:** ChromaDB
- **LLM:** Groq (LLAMA3)
- **Embedding Model:** BAAI/bge-base-en-v1.5

## 🔎 How to Search Products

You can search for fashion products using **natural language queries** — just type what you're looking for in the chat input, and the app will retrieve the most relevant items from the fashion catalog.

Here are some example queries:

1. **Can you show me some simple and comfortable t-shirts for men and women that are good for both daily wear and light exercise during the fall season? I like colors like blue, white, or red, and something from Nike or similar brands would be great.**

2. **I’m looking for affordable t-shirts under ¥1000 for men, something I can wear casually with jeans or shorts. It should be soft and easy to maintain, and I prefer basic colors like navy or grey with maybe a small design.**

3. **Suggest a few t-shirts for women that are stylish but not too flashy, something good for daily walks or casual outings in cool weather. I like black, white, or pink, and a comfortable fit is important.**

🎯 You can be specific about:
- Gender
- Season
- Style
- Color
- Brand
- Price range
- Usage (casual, workout, outdoor, etc.)

Let the AI assistant take care of the rest!


## 🚀 Try It Live

> Click **Open in Spaces** to launch the app  
Or visit: [https://huggingface.co/spaces/shafiqul1357/rag-fashion-recommendation](https://huggingface.co/spaces/shafiqul1357/rag-fashion-recommendation)