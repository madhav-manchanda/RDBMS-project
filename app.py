import streamlit as st
from supabase import create_client
import pandas as pd

# ---------------- SUPABASE CONFIG ---------------- #
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="Inventory System", layout="wide")
st.title("📦 Electronic Inventory Management System")

menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Add Category",
        "Add Supplier",
        "Add Product",
        "Update Stock",
        "Delete Product"
    ]
)

# ---------------- DASHBOARD ---------------- #
if menu == "Dashboard":
    st.subheader("📊 Inventory Overview")

    products = supabase.table("product").select("*").execute().data
    categories = supabase.table("category").select("*").execute().data
    stock = supabase.table("stock").select("*").execute().data

    if products:
        cat_map = {c["category_id"]: c["category_name"] for c in categories}
        stock_map = {s["product_id"]: s["quantity"] for s in stock}

        formatted = []

        for p in products:
            formatted.append([
                p["product_id"],
                p["product_name"],
                p["brand"],
                cat_map.get(p["category_id"], None),
                stock_map.get(p["product_id"], 0)
            ])

        df = pd.DataFrame(
            formatted,
            columns=["ID", "Product", "Brand", "Category", "Quantity"]
        )

        st.dataframe(df, use_container_width=True)

        low_stock = df[df["Quantity"] <= 5]
        if not low_stock.empty:
            st.warning("⚠ Low Stock Products")
            st.dataframe(low_stock)
    else:
        st.info("No products available.")

# ---------------- ADD CATEGORY ---------------- #
if menu == "Add Category":
    st.subheader("➕ Add Category")

    name = st.text_input("Category Name")

    if st.button("Add Category"):
        if name:
            supabase.table("category").insert({
                "category_name": name
            }).execute()
            st.success("Category added successfully!")
        else:
            st.warning("Enter category name")

# ---------------- ADD SUPPLIER ---------------- #
if menu == "Add Supplier":
    st.subheader("➕ Add Supplier")

    name = st.text_input("Supplier Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")

    if st.button("Add Supplier"):
        if name:
            supabase.table("supplier").insert({
                "supplier_name": name,
                "phone": phone,
                "email": email
            }).execute()

            st.success("Supplier added successfully!")
        else:
            st.warning("Supplier name required")

# ---------------- ADD PRODUCT ---------------- #
if menu == "Add Product":
    st.subheader("➕ Add Product")

    categories = supabase.table("category").select("*").execute().data
    suppliers = supabase.table("supplier").select("*").execute().data

    if not categories or not suppliers:
        st.warning("Add at least one category and supplier first.")
    else:
        cat_map = {c["category_name"]: c["category_id"] for c in categories}
        sup_map = {s["supplier_name"]: s["supplier_id"] for s in suppliers}

        name = st.text_input("Product Name")
        brand = st.text_input("Brand")
        price = st.number_input("Price", min_value=0.0)
        warranty = st.number_input("Warranty (months)", min_value=0)

        category = st.selectbox("Category", list(cat_map.keys()))
        supplier = st.selectbox("Supplier", list(sup_map.keys()))

        if st.button("Add Product"):
            if name:
                result = supabase.table("product").insert({
                    "product_name": name,
                    "brand": brand,
                    "price": price,
                    "warranty": warranty,
                    "category_id": cat_map[category],
                    "supplier_id": sup_map[supplier]
                }).execute()

                product_id = result.data[0]["product_id"]

                supabase.table("stock").insert({
                    "product_id": product_id,
                    "quantity": 0
                }).execute()

                st.success("Product added successfully!")
            else:
                st.warning("Product name required")

# ---------------- UPDATE STOCK ---------------- #
if menu == "Update Stock":
    st.subheader("🔁 Update Stock")

    products = supabase.table("product").select("product_id, product_name").execute().data

    if not products:
        st.warning("No products found.")
    else:
        prod_map = {p["product_name"]: p["product_id"] for p in products}

        product = st.selectbox("Select Product", list(prod_map.keys()))
        qty = st.number_input("Quantity to Add", min_value=1)

        if st.button("Update Stock"):
            current = supabase.table("stock") \
                .select("quantity") \
                .eq("product_id", prod_map[product]) \
                .execute().data

            if current:
                new_qty = current[0]["quantity"] + qty

                supabase.table("stock") \
                    .update({"quantity": new_qty}) \
                    .eq("product_id", prod_map[product]) \
                    .execute()

                st.success("Stock updated successfully!")

# ---------------- DELETE PRODUCT ---------------- #
if menu == "Delete Product":
    st.subheader("❌ Delete Product")

    products = supabase.table("product").select("product_id, product_name").execute().data

    if not products:
        st.warning("No products available.")
    else:
        prod_map = {p["product_name"]: p["product_id"] for p in products}

        product = st.selectbox("Select Product to Delete", list(prod_map.keys()))

        if st.button("Delete"):
            supabase.table("product") \
                .delete() \
                .eq("product_id", prod_map[product]) \
                .execute()

            st.success("Product deleted successfully!")
