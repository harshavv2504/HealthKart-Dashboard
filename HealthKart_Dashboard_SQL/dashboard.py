# dashboard.py

import streamlit as st
import pandas as pd
import os

from utils.utils import load_css, format_indian_currency
from utils.data_loader import load_all_data, filter_dataframes # filter_dataframes is still used here

# REMOVED: from utils.kpi_calculator import calculate_kpis # No longer needed
# REMOVED: from utils.filters import setup_sidebar_filters # No longer needed

from components.overview_tab import render_overview_tab
from components.detailed_analysis_tab import render_detailed_analysis_tab
from components.influencer_analysis_tab import render_influencer_analysis_tab
from constants import PAGE_ICON_PATH, CSS_PATH, PROFIT_MARGIN_FACTOR # Import constants

# --- Page Configuration and Styling ---
st.set_page_config(
    page_title="HealthKart",
    page_icon=PAGE_ICON_PATH,
    layout="wide"
)
load_css(CSS_PATH)

# --- Load Data ---
performance_df, orders_df, payment_log_df = load_all_data()

# --- Sidebar Filters ---
st.sidebar.header("Dashboard Filters") # Moved directly into dashboard.py

# Date Range Filter
min_date = orders_df['order_date'].min().date()
max_date = orders_df['order_date'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Categorical Filters
brand = st.sidebar.multiselect(
    "Select Brand",
    options=orders_df['brand'].unique(),
    default=orders_df['brand'].unique()
)

product = st.sidebar.multiselect(
    "Select Product",
    options=orders_df['product'].unique(),
    default=orders_df['product'].unique()
)

platform_options = orders_df['platform'].fillna('Organic').unique()
platform = st.sidebar.multiselect(
    "Select Platform",
    options=platform_options,
    default=platform_options
)

# --- Filter DataFrames based on sidebar selections ---
filtered_performance_df, filtered_orders_df, filtered_payment_log_df = \
    filter_dataframes(performance_df, orders_df, payment_log_df, start_date, end_date, brand, product, platform)

# --- Data Cleaning (Post-Filtering) ---
# Force-fill any potential NaN values in revenue to prevent KPI calculation errors.
filtered_orders_df['revenue_generated'] = filtered_orders_df['revenue_generated'].fillna(0)

# --- Calculate KPIs (after filtering) ---
# KPIs are now directly available in filtered_performance_df from SQL marts
# We need to extract them or pass filtered_performance_df directly to tabs
# For overview tab, we need specific aggregated KPIs. Let's calculate them here.

# Calculate KPIs from filtered data for Overview Tab
total_revenue = filtered_orders_df['revenue_generated'].sum()
total_payout = filtered_payment_log_df['payment_amount'].sum()
net_profit = (total_revenue * PROFIT_MARGIN_FACTOR) - total_payout

# Calculate Baseline Revenue (Organic Sales) - Corrected Logic
baseline_revenue = filtered_orders_df[filtered_orders_df['attribution_type'] != 'Influenced']['revenue_generated'].sum()

# Calculate Influencer-Driven Revenue - Corrected Logic
influencer_driven_revenue = filtered_orders_df[filtered_orders_df['attribution_type'] == 'Influenced']['revenue_generated'].sum()

# Calculate Incremental ROAS
incremental_roas = influencer_driven_revenue / total_payout if total_payout > 0 else 0

# Calculate new KPIs
roi = (net_profit / total_payout) * 100 if total_payout > 0 else 0
num_campaigns = filtered_orders_df['campaign'].dropna().nunique()
total_orders = len(filtered_orders_df)

# Orders by Attribution Type
influenced_orders_count = filtered_orders_df[filtered_orders_df['attribution_type'] == 'Influenced'].shape[0]
organic_orders_count = filtered_orders_df[filtered_orders_df['attribution_type'] != 'Influenced'].shape[0] # Changed from platform.isna() to attribution_type

# Package KPIs for Overview tab
kpis_for_overview = {
    "total_revenue": total_revenue,
    "total_payout": total_payout,
    "net_profit": net_profit,
    "baseline_revenue": baseline_revenue,
    "influencer_driven_revenue": influencer_driven_revenue,
    "incremental_roas": incremental_roas,
    "roi": roi,
    "num_campaigns": num_campaigns,
    "total_orders": total_orders,
    "influenced_orders_count": influenced_orders_count,
    "organic_orders_count": organic_orders_count,
    "overall_net_profit_percentage": (net_profit / total_revenue) if total_revenue > 0 else 0
}


# --- Main Dashboard Tabs ---
tab1, tab2, tab3 = st.tabs(["📈 Overview", "📄 Detailed Analysis", "🧑‍💻 Influencer Analysis"])

# --- Render Tab Content ---
with tab1:
    render_overview_tab(kpis_for_overview, filtered_orders_df, filtered_payment_log_df)

with tab2:
    render_detailed_analysis_tab(filtered_orders_df, kpis_for_overview) # Pass kpis_for_overview for overall_net_profit_percentage

with tab3:
    # Pass all filtered DFs as component tabs might need them for various charts/tables
    render_influencer_analysis_tab(filtered_performance_df, filtered_orders_df, filtered_payment_log_df, kpis_for_overview)