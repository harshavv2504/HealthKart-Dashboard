# utils/filters.py
import streamlit as st

def setup_sidebar_filters(orders_df):
    """
    Sets up the sidebar filters for date range, brand, product, and platform.
    Returns the selected filter values.
    """
    st.sidebar.header("Dashboard Filters")

    min_date = orders_df['order_date'].min().date()
    max_date = orders_df['order_date'].max().date()
    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    brand_options = orders_df['brand'].unique()
    brand = st.sidebar.multiselect(
        "Select Brand",
        options=brand_options,
        default=brand_options
    )

    product_options = orders_df['product'].unique()
    product = st.sidebar.multiselect(
        "Select Product",
        options=product_options,
        default=product_options
    )

    platform_options = orders_df['platform'].fillna('Organic').unique()
    platform = st.sidebar.multiselect(
        "Select Platform",
        options=platform_options,
        default=platform_options
    )

    return start_date, end_date, brand, product, platform