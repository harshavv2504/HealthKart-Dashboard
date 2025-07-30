# utils/data_loader.py
import streamlit as st
import pandas as pd
import os
import sqlite3 # NEW: Import sqlite3 for database connection

# --- Database Configuration (from constants.py) ---
from constants import DB_NAME 

@st.cache_data
def load_all_data():
    """
    Loads performance, orders, and payment log data from SQLite database views.
    Caches the data to avoid reloading on every rerun.
    """
    print(f"Attempting to load data from SQLite database: {DB_NAME}")
    try:
        with sqlite3.connect(DB_NAME) as conn:
            # Load influencer_performance data from SQL view
            performance_df = pd.read_sql_query("SELECT * FROM influencer_performance", conn)
            
            # Load enriched_orders data from SQL view
            orders_df = pd.read_sql_query("SELECT * FROM enriched_orders", conn)
            # Convert order_date to datetime objects after loading, as SQLite stores dates as TEXT
            orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
            # CRITICAL: Force revenue column to be numeric to prevent downstream errors.
            orders_df['revenue_generated'] = pd.to_numeric(orders_df['revenue_generated'], errors='coerce').fillna(0) 
            
            # Load payments_log data from SQL view
            payment_log_df = pd.read_sql_query("SELECT * FROM payments_log", conn)
            # Convert invoice_date to datetime objects, as SQLite stores dates as TEXT
            payment_log_df['invoice_date'] = pd.to_datetime(payment_log_df['invoice_date']) 

            return performance_df, orders_df, payment_log_df
    except FileNotFoundError:
        st.error(f"Error: Database file '{DB_NAME}' not found. Please run generate_data.py and create_sql_marts.py.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred while loading data from SQL: {e}")
        st.stop()

def filter_dataframes(performance_df, orders_df, payment_log_df, start_date, end_date, brand, product, platform):
    """
    Filters the DataFrames based on the provided sidebar selections.
    Returns filtered performance_df, orders_df, and payment_log_df.
    """
    # Platform filter logic
    if 'Organic' in platform:
        platform_mask = orders_df['platform'].isin([p for p in platform if p != 'Organic']) | \
                        orders_df['platform'].isna() | (orders_df['platform'] == '')
    else:
        platform_mask = orders_df['platform'].isin(platform)

    # Filter orders_df
    filtered_orders_df = orders_df[
        (orders_df['order_date'].dt.date >= start_date) &
        (orders_df['order_date'].dt.date <= end_date) &
        (orders_df['brand'].isin(brand)) &
        (orders_df['product'].isin(product)) &
        platform_mask
    ].copy()

    # Get the list of influencers who match the order filters
    filtered_influencers = filtered_orders_df['influencer_id'].unique()

    # Filter performance_df
    filtered_performance_df = performance_df[
        (performance_df['influencer_id'].isin(filtered_influencers))
    ].copy()

    # Filter payment_log_df by date range and influencer_id
    filtered_payment_log_df = payment_log_df[
        (payment_log_df['invoice_date'].dt.date >= start_date) &
        (payment_log_df['invoice_date'].dt.date <= end_date) &
        (payment_log_df['influencer_id'].isin(filtered_influencers))
    ].copy()

    return filtered_performance_df, filtered_orders_df, filtered_payment_log_df

