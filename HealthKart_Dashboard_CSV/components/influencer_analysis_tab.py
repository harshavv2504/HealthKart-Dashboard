# components/influencer_analysis_tab.py
import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts, JsCode
from utils.utils import format_indian_currency
from constants import PROFIT_MARGIN_FACTOR, CHART_COLORS, LIGHT_COLORS
import random

# --- Helper function for Platform Revenue Pie Chart (adapted for this tab) ---
def render_platform_revenue_pie_chart_influencer_tab(filtered_orders_df):
    """Renders the Platform Revenue Pie Chart for the Influencer Analysis tab."""

    
    # Ensure platform column is clean for grouping
    platform_revenue = filtered_orders_df.copy()
    platform_revenue['platform'] = platform_revenue['platform'].fillna('Organic Sales').replace('', 'Organic Sales')
    platform_revenue = platform_revenue.groupby('platform')['revenue_generated'].sum().reset_index()
    
    platform_revenue_data = [
        {"value": row['revenue_generated'], "name": row['platform']}
        for index, row in platform_revenue.iterrows()
    ]

    if not platform_revenue_data:
        st.info("No platform revenue data available for the selected filters.")
        return

    platform_pie_chart_options = {
        "tooltip": {"trigger": 'item', "formatter": "{a} <br/>{b} : ₹{c} ({d}%)"},

        "series": [
            {
                "name": 'Platform Revenue',
                "type": 'pie',
                "radius": '50%',
                "data": platform_revenue_data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    }
    st_echarts(options=platform_pie_chart_options, height="400px", width="100%", key="platform_revenue_pie_chart_influencer_tab")


# --- NEW FUNCTION: Top N Influencers by Revenue Generated Bar Chart ---
def render_top_influencers_by_revenue_chart(filtered_performance_df):
    """Renders a horizontal bar chart for Top N Influencers by Revenue Generated."""
    st.markdown("<h3 style='text-align: center;'>Top Influencers by Revenue Generated</h3>", unsafe_allow_html=True)

    filtered_performance_df['Revenue'] = pd.to_numeric(filtered_performance_df['Revenue'], errors='coerce').fillna(0)
    top_influencers = filtered_performance_df[filtered_performance_df['Revenue'] > 0].sort_values(by='Revenue', ascending=False).head(10).copy()

    if top_influencers.empty:
        st.info("No influencers with positive Revenue in the selected period.")
    else:
        chart_data = top_influencers[['Influencer', 'Revenue']].copy()
        chart_data['revenue_formatted'] = chart_data['Revenue'].apply(lambda x: f"₹{format_indian_currency(x)}")

        bar_chart_options = {
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {"type": 'shadow'},
                "formatter": JsCode("function (params) { return params[0].name + '<br/>Revenue: ' + params[0].data.revenue_formatted; }").js_code
            },
            "grid": {"left": '3%', "right": '4%', "bottom": '3%', "containLabel": True},
            "xAxis": {
                "type": 'value',
                "axisLabel": {
                    "formatter": JsCode("function (value) { return '₹' + new Intl.NumberFormat('en-IN').format(value); }").js_code
                }
            },
            "yAxis": {
                "type": 'category',
                "data": chart_data['Influencer'].tolist(),
                "axisLabel": {"interval": 0, "rotate": 0}
            },
            "series": [
                {
                    "name": 'Revenue',
                    "type": 'bar',
                    "encode": {"x": 'Revenue', "y": 'Influencer'},
                    "data": [
                        {"value": row['Revenue'], "revenue_formatted": row['revenue_formatted']}
                        for _, row in chart_data.iterrows()
                    ],
                    "itemStyle": {
                        "color": CHART_COLORS[2]
                    },
                    "barWidth": "20%"
                }
            ]
        }
        st_echarts(options=bar_chart_options, height="400px", width="100%", key="top_influencers_revenue_chart")


# --- NEW FUNCTION: Worst 10 Influencers by ROI Chart ---
def render_worst_influencers_by_roi_chart(filtered_performance_df):
    """Renders a horizontal bar chart for Worst 10 Influencers by ROI (only negative ROI)."""
    st.subheader("Worst 10 Influencers by ROI")

    # Ensure 'ROI' column is numeric before filtering and sorting
    filtered_performance_df['ROI'] = pd.to_numeric(filtered_performance_df['ROI'], errors='coerce').fillna(0)
    
    # Filter for influencers with NEGATIVE ROI only
    worst_influencers = filtered_performance_df[filtered_performance_df['ROI'] < 0].sort_values(by='ROI', ascending=True).head(10).copy()

    if worst_influencers.empty:
        st.info("No influencers with negative ROI in the selected period.")
    else:
        chart_data = worst_influencers[['Influencer', 'ROI']].copy()
        # Format for tooltip display
        chart_data['roi_formatted'] = chart_data['ROI'].apply(lambda x: f"{x:.2f}%")

        min_roi = chart_data['ROI'].min()
        max_roi = chart_data['ROI'].max() # This will still be negative, but closer to 0

        bar_chart_options = {
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {"type": 'shadow'},
                "formatter": JsCode("function (params) { return params[0].name + '<br/>ROI: ' + params[0].data.roi_formatted; }").js_code
            },
            "grid": {"left": '3%', "right": '4%', "bottom": '3%', "containLabel": True},
            "xAxis": {
                "type": 'value',
                "axisLabel": {
                    "formatter": JsCode("function (value) { return value.toFixed(2) + '%'; }").js_code
                }
            },
            "yAxis": {
                "type": 'category',
                "data": chart_data['Influencer'].tolist(),
                "axisLabel": {"interval": 0, "rotate": 0}
            },
            "visualMap": { # Visual map for color gradient
                "orient": 'horizontal',
                "left": 'center',
                "bottom": '0',
                "min": min_roi,
                "max": max_roi,
                "text": ['High Negative ROI', 'Low Negative ROI'], # Labels for the gradient
                "inRange": {
                    "color": ['#FF0000', "#FFB09D"] # Red to DarkOrange gradient (adjust as needed)
                }
            },
            "series": [
                {
                    "name": 'ROI',
                    "type": 'bar',
                    "encode": {"x": 'ROI', "y": 'Influencer'},
                    "data": [
                        {"value": row['ROI'], "roi_formatted": row['roi_formatted']}
                        for _, row in chart_data.iterrows()
                    ],
                    "itemStyle": {
                        # Color will be determined by visualMap, but setting a default here won't hurt
                        "color": '#FF0000'
                    },
                    "barWidth": "20%"
                }
            ]
        }
        st_echarts(options=bar_chart_options, height="250px", width="100%", key="worst_influencers_roi_chart")


# --- Main tab rendering function ---
def render_influencer_analysis_tab(filtered_performance_df, filtered_orders_df, filtered_payment_log_df, kpis):
    """
    Renders the content for the 'Influencer Analysis' tab,
    showing detailed metrics directly from influencer_performance.csv.
    """


    if filtered_performance_df.empty:
        st.info("No influencer performance data available for the selected filters.")
        return

    # --- Specific KPI Cards for Influencer Analysis ---

    
    # Ensure columns are numeric for aggregation
    temp_perf_df = filtered_performance_df.copy()
    temp_perf_df['Revenue'] = pd.to_numeric(temp_perf_df['Revenue'], errors='coerce').fillna(0)
    temp_perf_df['Payout'] = pd.to_numeric(temp_perf_df['Payout'], errors='coerce').fillna(0)
    temp_perf_df['Posts'] = pd.to_numeric(temp_perf_df['Posts'], errors='coerce').fillna(0)
    temp_perf_df['Engagement Rate'] = pd.to_numeric(temp_perf_df['Engagement Rate'], errors='coerce').fillna(0)
    temp_perf_df['Reach'] = pd.to_numeric(temp_perf_df['Reach'], errors='coerce').fillna(0)


    # Calculate the 7 selected KPIs
    total_unique_influencers = temp_perf_df['influencer_id'].nunique()
    total_posts_generated = temp_perf_df['Posts'].sum()
    avg_posts_per_influencer = temp_perf_df['Posts'].mean()
    avg_revenue_per_influencer = temp_perf_df['Revenue'].mean()
    avg_payout_per_influencer = temp_perf_df['Payout'].mean()
    avg_engagement_rate = temp_perf_df['Engagement Rate'].mean()
    total_reach = temp_perf_df['Reach'].sum()

    # --- Row 1: 4 KPI Cards, centered ---
    spacer_kpi_row1_left, col_kpi1, col_kpi2, col_kpi3, col_kpi4, spacer_kpi_row1_right = st.columns([1, 1, 1, 1, 1, 1])

    with col_kpi1:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Total Active Influencers</h3><p>{total_unique_influencers}</p></div>", unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Total Generated Posts</h3><p>{int(total_posts_generated):,}</p></div>", unsafe_allow_html=True)
    with col_kpi3:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Avg. Posts per Influencer</h3><p>{avg_posts_per_influencer:.1f}</p></div>", unsafe_allow_html=True)
    with col_kpi4:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Avg. Revenue per Influencer</h3><p>₹{format_indian_currency(avg_revenue_per_influencer)}</p></div>", unsafe_allow_html=True)

    # --- Row 2: 3 KPI Cards, centered ---
    spacer_kpi_row2_left, col_kpi5, col_kpi6, col_kpi7, spacer_kpi_row2_right = st.columns([1.5, 1, 1, 1, 1.5])

    with col_kpi5:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Avg. Payout per Influencer</h3><p>₹{format_indian_currency(avg_payout_per_influencer)}</p></div>", unsafe_allow_html=True)
    with col_kpi6:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Avg. Engagement Rate</h3><p>{avg_engagement_rate:.2f}%</p></div>", unsafe_allow_html=True)
    with col_kpi7:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Total Reach</h3><p>{int(total_reach):,}</p></div>", unsafe_allow_html=True)
    
    st.write("")
    st.write("")

    # --- Platform Analysis Section (Pie Chart + 4 Blank KPIs) ---
    st.markdown("<h3 style='text-align: center;'>Platform Analysis</h3>", unsafe_allow_html=True)
    st.write("")
    
    col_platform_chart, col_platform_kpis = st.columns(2)

    with col_platform_chart:
        render_platform_revenue_pie_chart_influencer_tab(filtered_orders_df) # Use filtered_orders_df for platform revenue

    with col_platform_kpis:
        
        # 4 Blank KPI Cards
        col_blank_kpi1, col_blank_kpi2 = st.columns(2)

        with col_blank_kpi1:

            st.write("")
            st.write("")
            st.write("")

            st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>1. Blank KPI</h3><p>---</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>3. Blank KPI</h3><p>---</p></div>", unsafe_allow_html=True)
        
        with col_blank_kpi2:

            st.write("")
            st.write("")
            st.write("")

            st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>2. Blank KPI</h3><p>---</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>4. Blank KPI</h3><p>---</p></div>", unsafe_allow_html=True)
        

    # --- Top N Influencers by Revenue Generated Bar Chart ---
    render_top_influencers_by_revenue_chart(filtered_performance_df)


    # --- NEW: Worst 10 Influencers by ROI Chart & 2 Blank KPIs ---
    col_roi_chart, col_roi_kpis = st.columns([2, 1])

    with col_roi_chart:
        render_worst_influencers_by_roi_chart(filtered_performance_df)

    with col_roi_kpis:
        st.markdown("<h4 style='text-align: center;'>ROI Insights</h4>", unsafe_allow_html=True)
        # The <br> tag was causing the issue. Replaced with an empty st.write()
        st.write("") # Add a little vertical space to align with chart title
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>5. Blank KPI</h3><p>---</p></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>6. Blank KPI</h3><p>---</p></div>", unsafe_allow_html=True)
    

    # --- MOVED: Detailed Influencer Metrics Table ---
    st.subheader("Detailed Influencer Metrics")

    display_df = filtered_performance_df.copy()

    # --- Ensure numerical columns are truly numerical FIRST ---
    numeric_cols_for_table = [
        'Revenue', 'Gross Profit', 'Net Profit', 'Payout',
        'Engagement Rate', 'ROAS', 'ROI',
        'Posts', 'Orders', 'Reach', 'Likes', 'Comments'
    ]
    for col in numeric_cols_for_table:
        if col in display_df.columns:
            display_df[col] = pd.to_numeric(display_df[col], errors='coerce')


    # --- REMOVED MANUAL STRING FORMATTING FOR TABLE ---
    # We are now relying on st.column_config for formatting, which keeps data numerical.
    # The format_indian_currency will NOT be used for the table.

    # Rename columns for user-friendly display (these are now NUMERICAL again)
    display_df = display_df.rename(columns={
        'Influencer': 'Influencer Name',
        'Payout Type': 'Payment Basis',
        'Posts': 'Total Posts',
        'Orders': 'Total Orders',
        'Reach': 'Total Reach',
        'Likes': 'Total Likes',
        'Comments': 'Total Comments',
        'Engagement Rate': 'Engagement Rate', # Keep as original for numerical sort
        'Revenue': 'Total Revenue', # Keep as original for numerical sort
        'Gross Profit': 'Gross Profit', # Keep as original for numerical sort
        'Net Profit': 'Net Profit', # Keep as original for numerical sort
        'Payout': 'Total Payout', # Keep as original for numerical sort
        'ROAS': 'ROAS', # Keep as original for numerical sort
        'ROI': 'ROI' # Keep as original for numerical sort
    })

    cols_to_drop_from_display = ['influencer_id', 'Gross Profit', 'ROAS', 'ROI']
    for col in cols_to_drop_from_display:
        if col in display_df.columns:
            display_df = display_df.drop(columns=[col])

    # --- Define column_config using basic 'format' parameter ---
    column_configuration = {
        "Influencer Name": st.column_config.TextColumn("Influencer Name"),
        "Payment Basis": st.column_config.TextColumn("Payment Basis"),

        "Total Revenue": st.column_config.NumberColumn(
            "Total Revenue (₹)",
            format="%.2f", # Basic float format with 2 decimal places
        ),
        "Net Profit": st.column_config.NumberColumn(
            "Net Profit (₹)",
            format="%.2f",
        ),
        "Total Payout": st.column_config.NumberColumn(
            "Total Payout (₹)",
            format="%.2f",
        ),
        "Total Posts": st.column_config.NumberColumn(
            "Total Posts",
            format="%d", # Basic integer format
        ),
        "Total Orders": st.column_config.NumberColumn(
            "Total Orders",
            format="%d",
        ),
        "Total Reach": st.column_config.NumberColumn(
            "Total Reach",
            format="%d",
        ),
        "Total Likes": st.column_config.NumberColumn(
            "Total Likes",
            format="%d",
        ),
        "Total Comments": st.column_config.NumberColumn(
            "Total Comments",
            format="%d",
        ),
        "Engagement Rate": st.column_config.NumberColumn(
            "Engagement Rate (%)",
            format="%.2f", # Basic float format for percentage
        )
    }

    st.dataframe(display_df, use_container_width=True, height=300, column_config=column_configuration)