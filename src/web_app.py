import torch
torch.classes.__path__ = []

import re
import pandas as pd
import streamlit as st
from config import Config
from vector_db import ChromaDBClient
from data_retriever import DataRetriever
from utils import category, metadata_fields

st.set_page_config(page_title="Fashion Recommender", layout="wide")


class WebApp:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.img_count = Config.PER_CATEGORY_IMAGE
        self.df = pd.read_csv(self.csv_path, dtype=str)
        self.category_tree = category.get_category_tree()
        self.chroma_client = ChromaDBClient(
            collection_name=Config.VECTOR_COLLECTION_NAME,
            persist_directory=Config.VECTOR_PERSIST_DIRECTORY
        )
        self.retriever = DataRetriever(
            vector_db_client=self.chroma_client,
        )

        if "selected_product_id" not in st.session_state:
            st.session_state["selected_product_id"] = None
        if "subcategory_products" not in st.session_state:
            st.session_state["subcategory_products"] = []
        if "subcategory_page" not in st.session_state:
            st.session_state["subcategory_page"] = 0
        if "search_results" not in st.session_state:
            st.session_state["search_results"] = []
        if "search_page" not in st.session_state:
            st.session_state["search_page"] = 0

    def handle_category_selection(self, master_category, sub_category):
        clean_master = self.clean_label(master_category)
        clean_sub = self.clean_label(sub_category)

        filtered_df = self.df[
            (self.df["master_category"] == clean_master) &
            (self.df["sub_category"] == clean_sub)
        ]
        product_ids = sorted(filtered_df["product_id"].unique())

        results = self.chroma_client.collection.get(
            ids=[str(pid) for pid in product_ids],
            include=["metadatas"]
        )
        metadatas = results.get("metadatas", [])

        st.session_state["subcategory_products"] = metadatas
        st.session_state["subcategory_page"] = 0
        st.session_state["search_results"] = []

    def render_sidebar(self, col):
        with col:
            st.markdown("<h2 style='margin-bottom: 20px;'>🛍️ Categories</h2>", unsafe_allow_html=True)

            if "selected_master" not in st.session_state:
                st.session_state["selected_master"] = None
            if "selected_sub" not in st.session_state:
                st.session_state["selected_sub"] = None
            if "expanded_master" not in st.session_state:
                st.session_state["expanded_master"] = None

            st.markdown("""
                <style>
                div.stButton > button {
                    width: 100% !important;
                    text-align: left !important;
                    justify-content: flex-start !important;
                    padding: 0.5em 1em;
                    margin-bottom: 0.25em;
                    border-radius: 6px;
                }
                </style>
            """, unsafe_allow_html=True)

            for master_with_icon, sub_dict in self.category_tree.items():
                expanded = st.session_state["expanded_master"] == master_with_icon
                with st.expander(master_with_icon, expanded=expanded):
                    for sub, icon in sub_dict.items():
                        label = f"{icon} {sub}"
                        key = f"{master_with_icon}-{sub}"

                        if st.button(label, key=key):
                            st.session_state["selected_master"] = master_with_icon
                            st.session_state["selected_sub"] = sub
                            st.session_state["expanded_master"] = master_with_icon
                            self.handle_category_selection(master_with_icon, sub)

    def clean_label(self, text):
        return re.sub(r"[^\w\s&]+", "", text).strip()

    def render_main_gallery(self, col):
        with col:
            st.markdown("<h2 style='margin-bottom: 20px;'>🖼️ Product Gallery</h2>", unsafe_allow_html=True)

            for master, sub_dict in self.category_tree.items():
                clean_master = self.clean_label(master)

                st.markdown(f"""
                    <div style="background-color:#f7e9e3;padding:10px;border-radius:8px;margin-top:20px;margin-bottom:10px">
                        <h3 style="margin:0">{master}</h3>
                    </div>
                """, unsafe_allow_html=True)

                for sub, _ in sub_dict.items():
                    clean_sub = self.clean_label(sub)

                    filtered_df = self.df[
                        (self.df["master_category"] == clean_master) &
                        (self.df["sub_category"] == clean_sub)
                    ]

                    product_ids = sorted(filtered_df["product_id"].unique())

                    if not product_ids:
                        continue

                    results = self.chroma_client.collection.get(
                        ids=[str(pid) for pid in product_ids],
                        include=["metadatas"]
                    )
                    metadatas = results.get("metadatas", [])[:self.img_count]

                    if metadatas:
                        st.markdown(f"""
                            <div style="background-color:#e2f0f7;padding:6px 12px;border-radius:5px;margin-top:10px;margin-bottom:8px">
                                <strong>{sub}</strong>
                            </div>
                        """, unsafe_allow_html=True)

                        cols = st.columns(4)
                        for i, metadata in enumerate(metadatas):
                            product_id = metadata.get("product_id")
                            product_name = metadata.get("product_name", "N/A")
                            brand = metadata.get("brand", "Unknown")
                            price = metadata.get("price", "N/A")
                            image_url = metadata.get("image_url")

                            with cols[i % 4]:
                                st.markdown(f"""
                                    <div style="display: flex; flex-direction: column; height: 320px; justify-content: space-between;">
                                        <img src="{image_url}" style="width: 100%; border-radius: 6px" />
                                        <div style="margin-top: 10px; flex-grow: 1;">
                                            <strong>{product_name}</strong><br/>
                                            <span style="font-size: 12px;">Brand: {brand} | Price: ¥{price}</span>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)

                                if st.button("🔍 View Details", key=f"view-{product_id}"):
                                    st.session_state["selected_product_id"] = product_id

    def render_subcategory_gallery(self, col):
        with col:
            sub_title = st.session_state.get("selected_sub", "Subcategory")
            st.markdown(f"<h2 style='margin-bottom: 20px;'>🖼️ {sub_title}</h2>", unsafe_allow_html=True)

            if st.button("🔙 Back to All Categories"):
                st.session_state["subcategory_products"] = []
                st.session_state["subcategory_page"] = 0
                st.session_state["selected_product_id"] = None
                st.rerun()

            metadatas = st.session_state.get("subcategory_products", [])
            if not metadatas:
                st.info("No products to display.")
                return

            if "subcategory_page" not in st.session_state:
                st.session_state["subcategory_page"] = 0

            items_per_page = Config.PAGINATION_IMAGE
            total_items = len(metadatas)
            total_pages = (total_items + items_per_page - 1) // items_per_page

            page = st.session_state["subcategory_page"]
            page = max(0, min(page, total_pages - 1))
            st.session_state["subcategory_page"] = page

            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if page > 0 and st.button("⬅️ Prev Page"):
                    st.session_state["subcategory_page"] -= 1
                    st.session_state["selected_product_id"] = None
                    st.rerun()

            with col3:
                if page < total_pages - 1 and st.button("➡️ Next Page"):
                    st.session_state["subcategory_page"] += 1
                    st.session_state["selected_product_id"] = None
                    st.rerun()

            # Refresh page after possible rerun
            page = st.session_state["subcategory_page"]
            start = page * items_per_page
            end = min(start + items_per_page, total_items)
            paged_items = metadatas[start:end]

            st.markdown(f"<div style='text-align:center; color:gray;'>Page {page + 1} of {total_pages}</div>",
                        unsafe_allow_html=True)

            cols = st.columns(4)
            for i, metadata in enumerate(paged_items):
                product_id = metadata.get("product_id")
                product_name = metadata.get("product_name", "N/A")
                brand = metadata.get("brand", "Unknown")
                price = metadata.get("price", "N/A")
                image_url = metadata.get("image_url")

                with cols[i % 4]:
                    st.markdown(f"""
                        <div style="display: flex; flex-direction: column; height: 320px; justify-content: space-between;">
                            <img src="{image_url}" style="width: 100%; border-radius: 6px;" />
                            <div style="margin-top: 10px; flex-grow: 1;">
                                <strong>{product_name}</strong><br/>
                                <span style="font-size: 12px;">Brand: {brand} | Price: ¥{price}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    if st.button("🔍 View Details", key=f"view-details-{product_id}-{page}"):
                        st.session_state["selected_product_id"] = product_id

    def render_search_result_gallery(self, col):
        with col:
            st.markdown(f"<h2 style='margin-bottom: 20px;'>🔍 Search Results</h2>", unsafe_allow_html=True)

            if st.button("🔙 Back to All Categories"):
                st.session_state["search_results"] = []
                st.session_state["search_page"] = 0
                st.session_state["selected_product_id"] = None
                st.rerun()

            metadatas = st.session_state.get("search_results", [])
            if not metadatas:
                st.info("No matching products found.")
                return

            items_per_page = Config.PAGINATION_IMAGE
            total_items = len(metadatas)
            total_pages = (total_items + items_per_page - 1) // items_per_page

            page = st.session_state["search_page"]
            page = max(0, min(page, total_pages - 1))
            st.session_state["search_page"] = page

            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if page > 0 and st.button("⬅️ Prev Page", key="search_prev"):
                    st.session_state["search_page"] -= 1
                    st.session_state["selected_product_id"] = None
                    st.rerun()

            with col3:
                if page < total_pages - 1 and st.button("➡️ Next Page", key="search_next"):
                    st.session_state["search_page"] += 1
                    st.session_state["selected_product_id"] = None
                    st.rerun()

            page = st.session_state["search_page"]
            start = page * items_per_page
            end = min(start + items_per_page, total_items)
            paged_items = metadatas[start:end]

            st.markdown(f"<div style='text-align:center; color:gray;'>Page {page + 1} of {total_pages}</div>", unsafe_allow_html=True)

            cols = st.columns(4)
            for i, metadata in enumerate(paged_items):
                product_id = metadata.get("product_id")
                product_name = metadata.get("product_name", "N/A")
                brand = metadata.get("brand", "Unknown")
                price = metadata.get("price", "N/A")
                image_url = metadata.get("image_url")

                with cols[i % 4]:
                    st.markdown(f"""
                        <div style="display: flex; flex-direction: column; height: 320px; justify-content: space-between;">
                            <img src="{image_url}" style="width: 100%; border-radius: 6px;" />
                            <div style="margin-top: 10px; flex-grow: 1;">
                                <strong>{product_name}</strong><br/>
                                <span style="font-size: 12px;">Brand: {brand} | Price: ¥{price}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    if st.button("🔍 View Details", key=f"search-view-details-{product_id}-{page}"):
                        st.session_state["selected_product_id"] = product_id

    def render_product_detail(self, col):
        with col:
            st.markdown("<h2 style='margin-bottom: 20px;'>📋 Product Details</h2>", unsafe_allow_html=True)

            product_id = st.session_state.get("selected_product_id")
            detail_placeholder = st.empty()

            if not product_id:
                detail_placeholder.info("Click Details button to see details of product here.")
                return

            metadata = self.chroma_client.collection.get(
                ids=[str(product_id)],
                include=["metadatas"]
            ).get("metadatas", [None])[0]

            if not metadata:
                detail_placeholder.warning("Product not found.")
                return

            with detail_placeholder.container():
                image_url = metadata.get("image_url")
                if image_url:
                    st.image(image_url, use_container_width=True)

                fields_to_display = metadata_fields.get_metadata_display_fields()
                for key, label in fields_to_display:
                    value = metadata.get(key)
                    if value:
                        st.markdown(f"**{label}:** {value}")

                if st.button("🔙 Clear", key="clear_button"):
                    st.session_state["clear_detail"] = True

            if st.session_state.get("clear_detail"):
                st.session_state["selected_product_id"] = None
                st.session_state["clear_detail"] = False
                detail_placeholder.empty()
                detail_placeholder.info("Click Details button to see details of product here.")

    def render_chat_input(self):
        user_query = st.chat_input("💬 search fashion products...")
        if user_query:
            st.session_state["user_query"] = user_query
            search_results = self.retriever.search(user_query)
            st.session_state["search_results"] = search_results
            st.session_state["search_page"] = 0
            st.session_state["selected_product_id"] = None
            st.rerun()

    def render(self):
        col_sidebar, col_main, col_detail = st.columns([2, 5, 3])
        self.render_sidebar(col_sidebar)

        if st.session_state.get("search_results"):
            self.render_search_result_gallery(col_main)
        elif st.session_state.get("subcategory_products"):
            self.render_subcategory_gallery(col_main)
        else:
            self.render_main_gallery(col_main)

        self.render_product_detail(col_detail)
        self.render_chat_input()


if __name__ == "__main__":
    
    style_csv = Config.STYLE_CSV
    app = WebApp(csv_path=style_csv)
    app.render()

    # Huggingface App: https://huggingface.co/spaces/shafiqul1357/rag-fashion-recommendation