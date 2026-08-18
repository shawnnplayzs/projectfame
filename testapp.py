import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "inventory.json"


def load_inventory() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_inventory(inventory: dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(inventory, f, indent=2)


if "inventory" not in st.session_state:
    st.session_state.inventory = load_inventory()

st.set_page_config(page_title="Inventory Manager", page_icon="📦", layout="wide")
st.title("📦 Inventory Manager")

tab_add, tab_view, tab_update, tab_delete = st.tabs(["Add", "View", "Update", "Delete"])

with tab_add:
    st.subheader("Add Product")
    with st.form("add_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        name = col1.text_input("Product Name")
        quantity = col2.number_input("Quantity", min_value=0, step=1, value=0)
        price = col3.number_input("Price", min_value=0.0, step=0.01, format="%.2f", value=0.0)
        submitted = st.form_submit_button("Add Product")
        if submitted:
            if not name.strip():
                st.error("Product name cannot be empty.")
            elif name in st.session_state.inventory:
                st.warning(f'"{name}" already exists. Use the Update tab to modify it.')
            else:
                st.session_state.inventory[name.strip()] = {"quantity": quantity, "price": price}
                save_inventory(st.session_state.inventory)
                st.success(f'Added "{name}" successfully!')
                st.rerun()

with tab_view:
    st.subheader("All Products")
    inv = st.session_state.inventory
    if not inv:
        st.info("No products yet. Add one in the Add tab.")
    else:
        df = pd.DataFrame(
            [{"Name": name, "Quantity": d["quantity"], "Price": d["price"]} for name, d in inv.items()]
        )
        df["Price"] = df["Price"].map("${:.2f}".format)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Total products: {len(inv)}")

with tab_update:
    st.subheader("Update Product")
    inv = st.session_state.inventory
    if not inv:
        st.info("No products to update.")
    else:
        name = st.selectbox("Select product", list(inv.keys()), key="update_select")
        if name:
            current = inv[name]
            with st.form("update_form"):
                col1, col2 = st.columns(2)
                quantity = col1.number_input("Quantity", min_value=0, step=1, value=current["quantity"])
                price = col2.number_input("Price", min_value=0.0, step=0.01, format="%.2f", value=current["price"])
                if st.form_submit_button("Update Product"):
                    st.session_state.inventory[name] = {"quantity": quantity, "price": price}
                    save_inventory(st.session_state.inventory)
                    st.success(f'Updated "{name}" successfully!')
                    st.rerun()

with tab_delete:
    st.subheader("Delete Product")
    inv = st.session_state.inventory
    if not inv:
        st.info("No products to delete.")
    else:
        name = st.selectbox("Select product to delete", list(inv.keys()), key="delete_select")
        if name and st.button("Delete Product", type="primary"):
            del st.session_state.inventory[name]
            save_inventory(st.session_state.inventory)
            st.success(f'Deleted "{name}" successfully!')
            st.rerun()
