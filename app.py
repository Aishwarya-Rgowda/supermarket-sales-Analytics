import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Supermarket Sales Analytics",
    page_icon="🛒",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
.block-container {
    max-width: 100% !important;
    padding: 1rem 2rem !important;
}

.header {
    background: linear-gradient(90deg, #0d47a1, #1976d2);
    padding: 25px;
    border-radius: 15px;
    color: white;
    text-align: center;
}

.kpi {
    background: #e3f2fd;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #90caf9;
}

.kpi h2 {
    color: #0d47a1;
    margin: 0;
}

.section {
    color: #0d47a1;
    font-size: 25px;
    font-weight: bold;
    margin-top: 25px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATA FROM MONGODB
# =========================================================
def load_mongodb_data():

    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)

    # Check connection
    client.admin.command("ping")

    db = client["supermarket_sales"]
    collection = db["sales"]

    records = list(collection.find({}, {"_id": 0}))

    if len(records) == 0:
        return pd.DataFrame()

    return pd.DataFrame(records)


# =========================================================
# TRY MONGODB
# =========================================================
try:

    df = load_mongodb_data()

    if df.empty:

        st.warning(
            "MongoDB is connected, but the sales collection is empty. "
            "Loading data from supermarket_sales.csv..."
        )

        df = pd.read_csv("supermarket_sales.csv")

        data_source = "CSV"

    else:

        data_source = "MongoDB"

except Exception as e:

    st.warning(
        "MongoDB connection failed. Loading data from CSV instead."
    )

    df = pd.read_csv("supermarket_sales.csv")

    data_source = "CSV"


# =========================================================
# CHECK DATA
# =========================================================
if df.empty:

    st.error("No data found.")

    st.stop()


# =========================================================
# CLEAN COLUMN NAMES
# =========================================================
df.columns = df.columns.str.strip()


# =========================================================
# CHECK REQUIRED COLUMNS
# =========================================================
required_columns = [
    "Date",
    "Product",
    "Category",
    "Quantity",
    "Unit_Price",
    "Total_Sales",
    "Customer_Type",
    "Payment",
    "City"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:

    st.error(
        f"Missing columns: {missing_columns}"
    )

    st.write("Columns received:")
    st.write(list(df.columns))

    st.stop()


# =========================================================
# DATA CONVERSION
# =========================================================
df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

df["Quantity"] = pd.to_numeric(
    df["Quantity"],
    errors="coerce"
)

df["Unit_Price"] = pd.to_numeric(
    df["Unit_Price"],
    errors="coerce"
)

df["Total_Sales"] = pd.to_numeric(
    df["Total_Sales"],
    errors="coerce"
)

df = df.dropna()


# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="header">

<h1>🛒 Supermarket Sales Analytics</h1>

<p>
Big Data Analytics Dashboard using Python, MongoDB,
Pandas, Plotly and Streamlit
</p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("📌 Dashboard")

st.sidebar.success(
    f"🟢 Data Source: {data_source}"
)

page = st.sidebar.radio(
    "Select Section",
    [
        "Dashboard",
        "MongoDB & Project",
        "Dataset Explorer"
    ]
)


# =========================================================
# FILTERS
# =========================================================
st.sidebar.markdown("### 🔍 Filters")

city_filter = st.sidebar.multiselect(
    "City",
    sorted(df["City"].unique()),
    default=sorted(df["City"].unique())
)

category_filter = st.sidebar.multiselect(
    "Category",
    sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

customer_filter = st.sidebar.multiselect(
    "Customer Type",
    sorted(df["Customer_Type"].unique()),
    default=sorted(df["Customer_Type"].unique())
)

payment_filter = st.sidebar.multiselect(
    "Payment",
    sorted(df["Payment"].unique()),
    default=sorted(df["Payment"].unique())
)


# =========================================================
# FILTER DATA
# =========================================================
filtered_df = df[
    (df["City"].isin(city_filter)) &
    (df["Category"].isin(category_filter)) &
    (df["Customer_Type"].isin(customer_filter)) &
    (df["Payment"].isin(payment_filter))
]


# =========================================================
# DASHBOARD
# =========================================================
if page == "Dashboard":

    # =====================================================
    # KPI
    # =====================================================

    total_revenue = filtered_df["Total_Sales"].sum()
    total_quantity = filtered_df["Quantity"].sum()
    total_products = filtered_df["Product"].nunique()
    total_cities = filtered_df["City"].nunique()

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(
        f"""
        <div class="kpi">
        <h2>₹{total_revenue:,.0f}</h2>
        <p>Total Revenue</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c2.markdown(
        f"""
        <div class="kpi">
        <h2>{total_quantity:,}</h2>
        <p>Quantity Sold</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c3.markdown(
        f"""
        <div class="kpi">
        <h2>{total_products}</h2>
        <p>Products</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c4.markdown(
        f"""
        <div class="kpi">
        <h2>{total_cities}</h2>
        <p>Cities</p>
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # 1. AREA CHART
    # =====================================================

    st.markdown(
        '<div class="section">📈 Daily Sales Trend</div>',
        unsafe_allow_html=True
    )

    daily_sales = (
        filtered_df
        .groupby("Date")["Total_Sales"]
        .sum()
        .reset_index()
    )

    fig1 = px.area(
        daily_sales,
        x="Date",
        y="Total_Sales",
        title="Daily Revenue Trend"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )


    # =====================================================
    # 2. HEATMAP
    # =====================================================

    st.markdown(
        '<div class="section">🔥 City × Category Heatmap</div>',
        unsafe_allow_html=True
    )

    heatmap_data = pd.pivot_table(
        filtered_df,
        values="Total_Sales",
        index="City",
        columns="Category",
        aggfunc="sum",
        fill_value=0
    )

    fig2 = px.imshow(
        heatmap_data,
        text_auto=True,
        aspect="auto",
        title="Sales by City and Category"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


    # =====================================================
    # 3. TREEMAP
    # =====================================================

    st.markdown(
        '<div class="section">🌳 Product Revenue Treemap</div>',
        unsafe_allow_html=True
    )

    tree_data = (
        filtered_df
        .groupby(
            ["Category", "Product"]
        )["Total_Sales"]
        .sum()
        .reset_index()
    )

    fig3 = px.treemap(
        tree_data,
        path=["Category", "Product"],
        values="Total_Sales",
        title="Revenue Contribution by Product"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )


    # =====================================================
    # 4. STACKED BAR
    # =====================================================

    st.markdown(
        '<div class="section">📊 Category vs Customer Type</div>',
        unsafe_allow_html=True
    )

    category_customer = (
        filtered_df
        .groupby(
            ["Category", "Customer_Type"]
        )["Total_Sales"]
        .sum()
        .reset_index()
    )

    fig4 = px.bar(
        category_customer,
        x="Category",
        y="Total_Sales",
        color="Customer_Type",
        barmode="stack",
        title="Category Sales by Customer Type"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )


    # =====================================================
    # 5. BUBBLE / SCATTER
    # =====================================================

    st.markdown(
        '<div class="section">🫧 Quantity vs Revenue</div>',
        unsafe_allow_html=True
    )

    product_data = (
        filtered_df
        .groupby("Product")
        .agg(
            Quantity=("Quantity", "sum"),
            Revenue=("Total_Sales", "sum"),
            Unit_Price=("Unit_Price", "mean")
        )
        .reset_index()
    )

    fig5 = px.scatter(
        product_data,
        x="Quantity",
        y="Revenue",
        size="Revenue",
        color="Unit_Price",
        hover_name="Product",
        title="Product Quantity vs Revenue",
        size_max=60
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )


    # =====================================================
    # 6. VIOLIN PLOT
    # =====================================================

    st.markdown(
        '<div class="section">🎻 Sales Distribution</div>',
        unsafe_allow_html=True
    )

    fig6 = px.violin(
        filtered_df,
        x="Category",
        y="Total_Sales",
        box=True,
        points="all",
        title="Sales Distribution by Category"
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )


    # =====================================================
    # 7. CUSTOMER TYPE
    # =====================================================

    st.markdown(
        '<div class="section">👥 Customer Analysis</div>',
        unsafe_allow_html=True
    )

    customer_data = (
        filtered_df
        .groupby("Customer_Type")["Total_Sales"]
        .sum()
        .reset_index()
    )

    fig7 = px.pie(
        customer_data,
        names="Customer_Type",
        values="Total_Sales",
        hole=0.45,
        title="Sales by Customer Type"
    )

    st.plotly_chart(
        fig7,
        use_container_width=True
    )


    # =====================================================
    # 8. PAYMENT
    # =====================================================

    st.markdown(
        '<div class="section">💳 Payment Method Analysis</div>',
        unsafe_allow_html=True
    )

    payment_data = (
        filtered_df
        .groupby("Payment")["Total_Sales"]
        .sum()
        .reset_index()
        .sort_values(
            "Total_Sales",
            ascending=False
        )
    )

    fig8 = px.bar(
        payment_data,
        x="Payment",
        y="Total_Sales",
        title="Sales by Payment Method"
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )


    # =====================================================
    # 9. TOP PRODUCTS
    # =====================================================

    st.markdown(
        '<div class="section">🏆 Top Selling Products</div>',
        unsafe_allow_html=True
    )

    top_products = (
        filtered_df
        .groupby("Product")["Total_Sales"]
        .sum()
        .reset_index()
        .sort_values(
            "Total_Sales",
            ascending=False
        )
        .head(10)
    )

    fig9 = px.bar(
        top_products,
        x="Total_Sales",
        y="Product",
        orientation="h",
        title="Top 10 Products by Revenue"
    )

    st.plotly_chart(
        fig9,
        use_container_width=True
    )


    # =====================================================
    # KEY INSIGHTS
    # =====================================================

    st.markdown(
        '<div class="section">💡 Key Insights</div>',
        unsafe_allow_html=True
    )

    best_category = (
        filtered_df
        .groupby("Category")["Total_Sales"]
        .sum()
        .idxmax()
    )

    best_city = (
        filtered_df
        .groupby("City")["Total_Sales"]
        .sum()
        .idxmax()
    )

    best_product = (
        filtered_df
        .groupby("Product")["Total_Sales"]
        .sum()
        .idxmax()
    )

    best_customer = (
        filtered_df
        .groupby("Customer_Type")["Total_Sales"]
        .sum()
        .idxmax()
    )

    st.info(
        f"""
        🔹 Highest Revenue Category: **{best_category}**

        🔹 Best Performing City: **{best_city}**

        🔹 Top Selling Product: **{best_product}**

        🔹 Highest Revenue Customer Type: **{best_customer}**

        🔹 Total Revenue: **₹{total_revenue:,.0f}**
        """
    )


# =========================================================
# MONGODB PAGE
# =========================================================
elif page == "MongoDB & Project":

    st.markdown(
        '<div class="section">🗄️ MongoDB & Project</div>',
        unsafe_allow_html=True
    )

    if data_source == "MongoDB":
        st.success("🟢 MongoDB Connected Successfully")
    else:
        st.warning(
            "🟡 Dashboard is currently using CSV because MongoDB data was not available."
        )

    st.markdown("### 🔄 Project Data Flow")

    st.code("""
Supermarket Sales Dataset
          ↓
      MongoDB
          ↓
      PyMongo
          ↓
       Python
          ↓
       Pandas
          ↓
 Data Cleaning & Analysis
          ↓
       Plotly
          ↓
     Streamlit
          ↓
 Interactive Dashboard
""")

    st.markdown("### 🛠️ Technologies Used")

    tech = pd.DataFrame({
        "Technology": [
            "Python",
            "Pandas",
            "MongoDB",
            "PyMongo",
            "Plotly",
            "Streamlit"
        ],
        "Purpose": [
            "Programming",
            "Data cleaning and analysis",
            "Database storage",
            "MongoDB connection",
            "Data visualization",
            "Dashboard development"
        ]
    })

    st.dataframe(
        tech,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### 📌 Project Details")

    st.write("""
    **Project:** Supermarket Sales Analytics

    **Domain:** Big Data Analytics

    **Database:** MongoDB

    **Programming Language:** Python

    **Data Analysis:** Pandas

    **Visualization:** Plotly

    **Dashboard:** Streamlit

    The project analyzes supermarket sales records and
    presents useful information about products, categories,
    cities, customers, payments and revenue through an
    interactive dashboard.
    """)


# =========================================================
# DATASET PAGE
# =========================================================
elif page == "Dataset Explorer":

    st.markdown(
        '<div class="section">📋 Dataset Explorer</div>',
        unsafe_allow_html=True
    )

    st.write(
        f"**Total Records:** {len(filtered_df):,}"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=600
    )


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown("""
<center>
<b>Supermarket Sales Analytics</b><br>
Big Data Analytics Project | Python | MongoDB | Pandas | Plotly | Streamlit
</center>
""", unsafe_allow_html=True)

