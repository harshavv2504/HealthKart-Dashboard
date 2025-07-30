# utils/data_loader.py
import streamlit as st
import pandas as pd
import os
from constants import PERFORMANCE_DATA_PATH, ORDERS_DATA_PATH, PAYMENT_LOG_DATA_PATH

@st.cache_data
def load_all_data():
    """
    Loads performance, orders, and payment log data.
    Caches the data to avoid reloading on every rerun.
    """
    try:
        performance_df = pd.read_csv(PERFORMANCE_DATA_PATH)
        orders_df = pd.read_csv(ORDERS_DATA_PATH)
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        payment_log_df = pd.read_csv(PAYMENT_LOG_DATA_PATH)
        payment_log_df['invoice_date'] = pd.to_datetime(payment_log_df['invoice_date'])
        return performance_df, orders_df, payment_log_df
    except FileNotFoundError as e:
        st.error(f"Error: Could not find data files. {e}")
        st.error("Please ensure the 'cleaned_data' folder exists and contains all required CSVs.")
        st.stop() # Stop the app if data files are missing
    except Exception as e:
        st.error(f"An unexpected error occurred while loading data: {e}")
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
    # ADD .copy() HERE
    filtered_orders_df = orders_df[
        (orders_df['order_date'].dt.date >= start_date) &
        (orders_df['order_date'].dt.date <= end_date) &
        (orders_df['brand'].isin(brand)) &
        (orders_df['product'].isin(product)) &
        platform_mask
    ].copy() # <--- ADDED .copy() HERE

    # Get the list of influencers who match the order filters
    filtered_influencers = filtered_orders_df['influencer_id'].unique()

    # Filter performance_df
    # ADD .copy() HERE
    filtered_performance_df = performance_df[
        (performance_df['influencer_id'].isin(filtered_influencers))
    ].copy() # <--- ADDED .copy() HERE

    # Filter payment_log_df
    # ADD .copy() HERE
    filtered_payment_log_df = payment_log_df[
        (payment_log_df['invoice_date'].dt.date >= start_date) &
        (payment_log_df['invoice_date'].dt.date <= end_date) &
        (payment_log_df['influencer_id'].isin(filtered_influencers))
    ].copy() # <--- ADDED .copy() HERE

    return filtered_performance_df, filtered_orders_df, filtered_payment_log_df