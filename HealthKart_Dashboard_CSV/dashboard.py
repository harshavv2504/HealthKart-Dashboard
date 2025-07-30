# dashboard.py

import streamlit as st
import pandas as pd
import os
from utils.utils import load_css, format_indian_currency # Keep format_indian_currency here or only in utils.utils if needed globally
from utils.data_loader import load_all_data, filter_dataframes
from utils.kpi_calculator import calculate_kpis
from utils.filters import setup_sidebar_filters
from components.overview_tab import render_overview_tab
from components.detailed_analysis_tab import render_detailed_analysis_tab
from components.influencer_analysis_tab import render_influencer_analysis_tab
from constants import PAGE_ICON_PATH, CSS_PATH # Import constants

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
start_date, end_date, brand, product, platform = setup_sidebar_filters(orders_df)

# --- Filter DataFrames based on sidebar selections ---
filtered_performance_df, filtered_orders_df, filtered_payment_log_df = \
    filter_dataframes(performance_df, orders_df, payment_log_df, start_date, end_date, brand, product, platform)

# --- Calculate KPIs (after filtering) ---
kpis = calculate_kpis(filtered_orders_df, filtered_payment_log_df)

# --- Main Dashboard Tabs ---
tab1, tab2, tab3 = st.tabs(["📈 Overview", "📄 Product & Brand Analysis", "🧑‍💻 Influencer Analysis"])

# --- Render Tab Content ---
with tab1:
    render_overview_tab(kpis, filtered_orders_df, filtered_payment_log_df)

with tab2:
    render_detailed_analysis_tab(filtered_orders_df, kpis)

# In dashboard.py, within the tab3 section:
with tab3:
    render_influencer_analysis_tab(filtered_performance_df, filtered_orders_df, filtered_payment_log_df, kpis)