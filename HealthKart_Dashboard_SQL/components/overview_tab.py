# components/overview_tab.py
import streamlit as st
from streamlit_echarts import st_echarts
import random
import pandas as pd
from utils.utils import format_indian_currency
from constants import LIGHT_COLORS, PROFIT_MARGIN_FACTOR

def render_overview_tab(kpis, filtered_orders_df, filtered_payment_log_df):
    """
    Renders the content for the 'Overview' tab, including KPI cards and charts.
    """
    st.markdown("<h3 style='text-align: center;'>Overview</h3>", unsafe_allow_html=True)

    # Display KPIs using custom styled cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Total Revenue</h3><p>₹{format_indian_currency(kpis['total_revenue'])}</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Total Orders</h3><p>{kpis['total_orders']}</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Total Payout</h3><p>₹{format_indian_currency(kpis['total_payout'])}</p></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Net Profit</h3><p>₹{format_indian_currency(kpis['net_profit'])}</p></div>", unsafe_allow_html=True)

    col5, col6, col7, col8, col9 = st.columns(5)
    with col5:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Number of Campaigns</h3><p>{kpis['num_campaigns']}</p></div>", unsafe_allow_html=True)
    with col6:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Organic Revenue</h3><p>₹{format_indian_currency(kpis['baseline_revenue'])}</p></div>", unsafe_allow_html=True)
    with col7:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Influenced Revenue</h3><p>₹{format_indian_currency(kpis['influencer_driven_revenue'])}</p></div>", unsafe_allow_html=True)
    with col8:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>ROI</h3><p>{kpis['roi']:.2f}%</p></div>", unsafe_allow_html=True)
    with col9:
        st.markdown(f"<div class='kpi-card' style='background-color: {random.choice(LIGHT_COLORS)};'><h3>Incremental ROAS</h3><p>{kpis['incremental_roas']:.2f}x</p></div>", unsafe_allow_html=True)

    st.markdown("---", unsafe_allow_html=True)

    # --- This is the key change ---
    # Create the columns ONCE in the main overview tab function
    chart_col1, chart_col2, chart_col3 = st.columns(3)

    # Pass these column objects to the respective chart rendering functions
    # The chart functions will then use these provided columns as their context
    render_order_source_pie_chart(chart_col1, filtered_orders_df, kpis) # Pass kpis too for consistency
    render_brand_revenue_pie_chart(chart_col2, filtered_orders_df)
    render_platform_revenue_pie_chart(chart_col3, filtered_orders_df)
    # --- End of key change ---

    st.markdown("<br>", unsafe_allow_html=True)

    # This chart is already in a single column, so it's fine
    render_product_revenue_by_platform_chart(filtered_orders_df)

    render_revenue_payout_profit_time_chart(filtered_orders_df, filtered_payment_log_df)

# --- Updated chart functions to accept a column object ---

def render_order_source_pie_chart(target_column, filtered_orders_df, kpis): # Added target_column and kpis
    """Renders the Influenced vs. Organic Orders Pie Chart."""
    with target_column: # Use the provided column context
        st.markdown("<h4 style='text-align: center;'>Order Source</h4>", unsafe_allow_html=True)
        # Use the KPI counts directly
        influenced_orders = kpis['influenced_orders_count']
        organic_orders = kpis['organic_orders_count']

        pie_chart_options = {
            "tooltip": {"trigger": 'item'},
            "legend": {"orient": 'vertical', "left": 'left', "textStyle": {"fontSize": 10}},
            "series": [
                {
                    "name": 'Order Source',
                    "type": 'pie',
                    "radius": '50%',
                    "data": [
                        {"value": influenced_orders, "name": 'Influenced Orders'},
                        {"value": organic_orders, "name": 'Organic Orders'}
                    ],
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
        st_echarts(options=pie_chart_options, height="250px", width="100%", key="order_source_pie_chart")

def render_brand_revenue_pie_chart(target_column, filtered_orders_df): # Added target_column
    """Renders the Brand Revenue Pie Chart."""
    with target_column: # Use the provided column context
        st.markdown("<h4 style='text-align: center;'>Brand Revenue</h4>", unsafe_allow_html=True)
        brand_revenue = filtered_orders_df.groupby('brand')['revenue_generated'].sum().reset_index()
        brand_revenue_data = [{"value": row['revenue_generated'], "name": row['brand']} for _, row in brand_revenue.iterrows()]

        brand_pie_chart_options = {
            "tooltip": {"trigger": 'item'},
            "legend": {"orient": 'vertical', "left": 'left', "textStyle": {"fontSize": 10}},
            "series": [
                {
                    "name": 'Brand Revenue',
                    "type": 'pie',
                    "radius": '50%',
                    "data": brand_revenue_data,
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
        st_echarts(options=brand_pie_chart_options, height="250px", width="100%", key="brand_revenue_pie_chart")

def render_platform_revenue_pie_chart(target_column, filtered_orders_df): # Added target_column
    """Renders the Platform Revenue Pie Chart."""
    with target_column: # Use the provided column context
        st.markdown("<h4 style='text-align: center;'>Platform Revenue</h4>", unsafe_allow_html=True)
        platform_revenue = filtered_orders_df.copy()
        platform_revenue['platform'] = platform_revenue['platform'].fillna('Organic Sales').replace('', 'Organic Sales')
        platform_revenue = platform_revenue.groupby('platform')['revenue_generated'].sum().reset_index()
        platform_revenue_data = [{"value": row['revenue_generated'], "name": row['platform']} for _, row in platform_revenue.iterrows()]

        platform_pie_chart_options = {
            "tooltip": {"trigger": 'item'},
            "legend": {"orient": 'vertical', "left": 'left', "textStyle": {"fontSize": 10}},
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
        st_echarts(options=platform_pie_chart_options, height="250px", width="100%", key="platform_revenue_pie_chart")

# The rest of the functions (render_product_revenue_by_platform_chart, render_revenue_payout_profit_time_chart)
# remain unchanged as they already correctly use st.columns(1) or no columns within their own scope.
def render_product_revenue_by_platform_chart(filtered_orders_df):
    """Renders the Product Revenue by Platform Stacked Bar Chart."""
    chart_col4_row = st.columns(1) # This is okay, it creates a new full-width row
    with chart_col4_row[0]:
        st.markdown("<h4 style='text-align: center;'>Product Revenue by Platform</h4>", unsafe_allow_html=True)
        product_platform_revenue = filtered_orders_df.copy()
        product_platform_revenue['platform'] = product_platform_revenue['platform'].fillna('Organic Sales').replace('', 'Organic Sales')
        product_platform_revenue = product_platform_revenue.groupby(['product', 'platform'])['revenue_generated'].sum().unstack().fillna(0)

        products = product_platform_revenue.index.tolist()
        platforms = product_platform_revenue.columns.tolist()

        series_data = []
        for platform in platforms:
            series_data.append({
                "name": platform,
                "type": 'bar',
                "stack": 'total',
                "emphasis": {"focus": 'series'},
                "data": product_platform_revenue[platform].tolist(),
                "barWidth": 15
            })

        stacked_bar_options = {
            "tooltip": {"trigger": 'axis', "axisPointer": {"type": 'shadow'}},
            "legend": {"data": platforms, "textStyle": {"fontSize": 10}},
            "grid": {"left": '10%', "right": '4%', "bottom": '3%', "containLabel": True},
            "xAxis": {"type": 'value', "axisLabel": {"textStyle": {"fontSize": 8}}},
            "yAxis": {"type": 'category', "data": products, "axisLabel": {"textStyle": {"fontSize": 10}}},
            "series": series_data
        }
        st_echarts(options=stacked_bar_options, height="400px", width="100%", key="product_revenue_bar_chart")

def render_revenue_payout_profit_time_chart(filtered_orders_df, filtered_payment_log_df):
    """Renders the Revenue, Payout & Net Profit Over Time Chart."""
    st.markdown("<h4 style='text-align: center;'>Revenue, Payout & Net Profit Over Time</h4>", unsafe_allow_html=True)

    revenue_over_time = filtered_orders_df.set_index('order_date').resample('W')['revenue_generated'].sum().rename('Revenue')
    payout_over_time = filtered_payment_log_df.set_index('invoice_date').resample('W')['payment_amount'].sum().rename('Payout')
    chart_data = pd.concat([revenue_over_time, payout_over_time], axis=1).fillna(0)
    chart_data['Net Profit'] = (PROFIT_MARGIN_FACTOR * chart_data['Revenue']) - chart_data['Payout']
    chart_data = chart_data.reset_index()
    chart_data = chart_data.rename(columns={'index': 'date'})

    options = {
        "tooltip": {
            "trigger": 'axis',
            "axisPointer": {"type": 'shadow'},
            "formatter": "function (params) { let tooltipContent = params[0].name + '<br/>'; params.forEach(function (item) { let value = item.value; if (value === 0) value = '0'; let parts = value.toString().split('.'); let integer = parts[0]; let decimal = parts.length > 1 ? '.' + parts[1] : ''; let lastThree = integer.substring(integer.length - 3); let otherNumbers = integer.substring(0, integer.length - 3); if (otherNumbers != '') { lastThree = ',' + lastThree; } let formatted = otherNumbers.replace(/\\B(?=(\\d{2})+(?!\\d))/g, \",\") + lastThree; tooltipContent += item.marker + item.seriesName + ': ₹' + formatted + decimal + '<br/>'; }); return tooltipContent; }"
        },
        "legend": {"data": ['Revenue', 'Payout', 'Net Profit']},
        "xAxis": {
            "type": 'category',
            "data": [d.strftime('%Y-%m-%d') for d in chart_data['date']],
        },
        "yAxis": {"type": 'value'},
        "series": [
            {
                "name": 'Revenue',
                "data": chart_data['Revenue'].tolist(),
                "type": 'line',
                "smooth": True,
            },
            {
                "name": 'Payout',
                "data": chart_data['Payout'].tolist(),
                "type": 'line',
                "smooth": True,
                "itemStyle": {"color": '#FF0000'}
            },
            {
                "name": 'Net Profit',
                "data": chart_data['Net Profit'].tolist(),
                "type": 'line',
                "smooth": True,
                "itemStyle": {"color": '#008000'}
            }
        ],
        "dataZoom": [{
            "type": 'inside',
            "start": 0,
            "end": 100
        }, {
            "start": 0,
            "end": 10,
            "bottom": 0, # Add bottom to the scrollbar to prevent overlap
            "height": 20 # Add height to the scrollbar for better visibility
        }]
    }
    st_echarts(options=options, height="400px", width="100%", key="revenue_payout_net_profit_chart")