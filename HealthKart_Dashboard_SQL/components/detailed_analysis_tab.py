# components/detailed_analysis_tab.py
import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd
from utils.utils import format_indian_currency
from constants import CHART_COLORS

def render_detailed_analysis_tab(filtered_orders_df, kpis):
    """
    Renders the content for the 'Detailed Analysis' tab.
    """
    st.markdown("<h3 style='text-align: center;'>Product Analysis</h3>", unsafe_allow_html=True)

    # --- Product Analysis Alignment ---
    spacer_left_prod, col1, col2, col3, spacer_right_prod = st.columns([0.5, 3, 3, 3, 0.5]) # Adjust spacer ratios as needed

    with col1:
        render_product_revenue_donut_chart(filtered_orders_df)

    with col2:
        
        # Add spacing to push the table down to align its center with the donut chart
        for _ in range(3): # Start with a guess, then adjust this number
            st.write("")
        render_product_revenue_table(filtered_orders_df, kpis['overall_net_profit_percentage'])

    with col3:
        # Add even more spacing for the shorter summary text
        for _ in range(7): # Adjust this number as needed
            st.write("")
        st.markdown("<h4 style='text-align: center;'>Summary</h4>", unsafe_allow_html=True)
        st.write("")
        st.write("This is a dummy paragraph for the summary column. You can edit this later with your desired content.")
    # --- End Product Analysis Alignment ---



    st.markdown("<h3 style='text-align: center;'>Brand Analysis</h3>", unsafe_allow_html=True)

    # --- Brand Analysis Alignment ---
    spacer_left_brand, col_brand1, col_brand2, col_brand3, spacer_right_brand = st.columns([0.5, 3, 3, 3, 0.5]) # Adjust spacer ratios as needed

    with col_brand1:
        render_brand_revenue_donut_chart(filtered_orders_df)

    with col_brand2:
        # Add spacing to push the table down
        for _ in range(11): # Start with a guess, then adjust
            st.write("")
        render_brand_revenue_table(filtered_orders_df, kpis['overall_net_profit_percentage'])

    with col_brand3:
        # Add even more spacing for the shorter summary text
        for _ in range(10): # Adjust this number as needed
            st.write("")
        st.markdown("<h4 style='text-align: center;'>Brand Summary</h4>", unsafe_allow_html=True)
        st.write("")
        st.write("This is a dummy paragraph for the brand summary column. You can edit this later with your desired content.")
    # --- End Brand Analysis Alignment ---



    st.markdown("<h3 style='text-align: center;'>Campaign Analysis</h3>", unsafe_allow_html=True)

    # --- Campaign Analysis Alignment ---
    spacer_left_campaign, col_campaign1, col_campaign2, col_campaign3, spacer_right_campaign = st.columns([0.5, 3, 3, 3, 0.5]) # Adjust spacer ratios as needed

    with col_campaign1:
        render_campaign_revenue_donut_chart(filtered_orders_df)

    with col_campaign2:
        # Add spacing to push the table down (adjust numbers based on visual alignment)
        for _ in range(8): # Example number, tune this
            st.write("")
        render_campaign_revenue_table(filtered_orders_df, kpis['overall_net_profit_percentage'])

    with col_campaign3:
        # Add even more spacing for the shorter summary text (adjust numbers based on visual alignment)
        for _ in range(10): # Example number, tune this
            st.write("")
        st.markdown("<h4 style='text-align: center;'>Campaign Summary</h4>", unsafe_allow_html=True)
        st.write("")
        st.write("This is a dummy paragraph for the campaign summary column. You can edit this later with your desired content.")
    # --- End Campaign Analysis Alignment ---


# --- Existing Chart and Table Rendering Functions (remain unchanged) ---

def render_product_revenue_donut_chart(filtered_orders_df):
    """Renders the Product Revenue Donut Chart."""
    product_revenue = filtered_orders_df.groupby('product')['revenue_generated'].sum().reset_index()
    product_revenue = product_revenue.sort_values(by='revenue_generated', ascending=False)

    donut_data = []
    for _, row in product_revenue.iterrows():
        donut_data.append({
            "value": round(row['revenue_generated'], 2),
            "name": row['product']
        })

    if not donut_data:
        st.info("No product revenue data available for the selected filters.")
        return

    donut_options = {
        "tooltip": {"trigger": 'item', "formatter": "{a} <br/>{b} : ₹{c} ({d}%)"},
        "toolbox": {
            "show": True,
            "feature": {
                "mark": {"show": True},
                "dataView": {"show": True, "readOnly": False},
                "restore": {"show": True},
                "saveAsImage": {"show": True}
            }
        },
        "color": CHART_COLORS,
        "series": [
            {
                "name": 'Revenue',
                "type": 'pie',
                "radius": ['35%', '60%'],
                "center": ['50%', '50%'],
                "avoidLabelOverlap": True,
                "borderRadius": 10,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": '#fff',
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "position": 'outside',
                    "formatter": '{b}: {d}%',
                    "fontSize": 11
                },
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": 14,
                        "fontWeight": 'bold'
                    }
                },
                "labelLine": {
                    "show": True
                },
                "data": donut_data
            }
        ]
    }
    st_echarts(options=donut_options, height="500px", key="product_revenue_donut_chart")

def render_product_revenue_table(filtered_orders_df, overall_net_profit_percentage):
    """Renders the Product Revenue Table using Streamlit's default dataframe."""
    product_revenue = filtered_orders_df.groupby('product')['revenue_generated'].sum().reset_index()
    product_revenue = product_revenue.sort_values(by='revenue_generated', ascending=False)

    product_table_data = product_revenue.copy()
    product_table_data['net_profit'] = product_table_data['revenue_generated'] * overall_net_profit_percentage

    product_table_data['revenue_generated'] = product_table_data['revenue_generated'].apply(lambda x: f"₹{format_indian_currency(x)}")
    product_table_data['net_profit'] = product_table_data['net_profit'].apply(lambda x: f"₹{format_indian_currency(x)}")
    
    product_table_data = product_table_data.rename(columns={
        'product': 'Product',
        'revenue_generated': 'Revenue',
        'net_profit': 'Net Profit'
    })

    st.dataframe(product_table_data, use_container_width=True)


def render_brand_revenue_donut_chart(filtered_orders_df):
    """Renders the Brand Revenue Donut Chart."""
    brand_revenue = filtered_orders_df.groupby('brand')['revenue_generated'].sum().reset_index()
    brand_revenue = brand_revenue.sort_values(by='revenue_generated', ascending=False)

    brand_donut_data = [
        {"value": row['revenue_generated'], "name": row['brand']}
        for _, row in brand_revenue.iterrows()
    ]

    brand_donut_options = {
        "tooltip": {"trigger": 'item', "formatter": "{a} <br/>{b} : ₹{c} ({d}%)"},
        "series": [
            {
                "name": 'Brand Revenue',
                "type": 'pie',
                "radius": ['35%', '60%'],
                "center": ['50%', '50%'],
                "avoidLabelOverlap": True,
                "borderRadius": 10,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": '#fff',
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "position": 'outside',
                    "formatter": '{b}: {d}%',
                    "fontSize": 11
                },
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": 14,
                        "fontWeight": 'bold'
                    }
                },
                "labelLine": {
                    "show": True
                },
                "data": brand_donut_data
            }
        ]
    }
    st_echarts(options=brand_donut_options, height="500px", key="brand_revenue_donut_chart")

def render_brand_revenue_table(filtered_orders_df, overall_net_profit_percentage):
    """Renders the Brand Revenue Table using Streamlit's default dataframe."""
    brand_revenue = filtered_orders_df.groupby('brand')['revenue_generated'].sum().reset_index()
    brand_table_data = brand_revenue.copy()
    brand_table_data['net_profit'] = brand_table_data['revenue_generated'] * overall_net_profit_percentage
    
    brand_table_data['revenue_generated'] = brand_table_data['revenue_generated'].apply(lambda x: f"₹{format_indian_currency(x)}")
    brand_table_data['net_profit'] = brand_table_data['net_profit'].apply(lambda x: f"₹{format_indian_currency(x)}")

    order_counts = filtered_orders_df['brand'].value_counts().reset_index()
    order_counts.columns = ['brand', 'Number of Orders']
    brand_table_data = pd.merge(brand_table_data, order_counts, on='brand', how='left')
    
    brand_table_data = brand_table_data.rename(columns={
        'brand': 'Brand',
        'revenue_generated': 'Revenue',
        'net_profit': 'Net Profit',
        'Number of Orders': 'No. of Orders'
    })

    st.dataframe(brand_table_data, use_container_width=True)


# --- NEW FUNCTIONS FOR CAMPAIGN ANALYSIS ---

def render_campaign_revenue_donut_chart(filtered_orders_df):
    """Renders the Campaign Revenue Donut Chart."""
    # Group by 'campaign', sum revenue. Fill NaN campaigns for consistent display.
    campaign_revenue = filtered_orders_df.groupby('campaign')['revenue_generated'].sum().reset_index()
    campaign_revenue['campaign'] = campaign_revenue['campaign'].fillna('No Campaign')
    campaign_revenue = campaign_revenue.sort_values(by='revenue_generated', ascending=False)

    campaign_donut_data = [
        {"value": row['revenue_generated'], "name": row['campaign']}
        for _, row in campaign_revenue.iterrows()
    ]

    if not campaign_donut_data:
        st.info("No campaign revenue data available for the selected filters.")
        return

    campaign_donut_options = {
        "tooltip": {"trigger": 'item', "formatter": "{a} <br/>{b} : ₹{c} ({d}%)"},
        "series": [
            {
                "name": 'Campaign Revenue',
                "type": 'pie',
                "radius": ['35%', '60%'],
                "center": ['50%', '50%'],
                "avoidLabelOverlap": True,
                "borderRadius": 10,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": '#fff',
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "position": 'outside',
                    "formatter": '{b}: {d}%',
                    "fontSize": 11
                },
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": 14,
                        "fontWeight": 'bold'
                    }
                },
                "labelLine": {
                    "show": True
                },
                "data": campaign_donut_data
            }
        ]
    }
    st_echarts(options=campaign_donut_options, height="500px", key="campaign_revenue_donut_chart")


def render_campaign_revenue_table(filtered_orders_df, overall_net_profit_percentage):
    """Renders the Campaign Revenue Table using Streamlit's default dataframe."""
    # Group by 'campaign', sum revenue. Fill NaN campaigns for consistent display.
    campaign_revenue = filtered_orders_df.groupby('campaign')['revenue_generated'].sum().reset_index()
    campaign_table_data = campaign_revenue.copy()
    campaign_table_data['net_profit'] = campaign_table_data['revenue_generated'] * overall_net_profit_percentage

    # Fill NaN campaigns in the table data itself
    campaign_table_data['campaign'] = campaign_table_data['campaign'].fillna('No Campaign')

    # Format for display
    campaign_table_data['revenue_generated'] = campaign_table_data['revenue_generated'].apply(lambda x: f"₹{format_indian_currency(x)}")
    campaign_table_data['net_profit'] = campaign_table_data['net_profit'].apply(lambda x: f"₹{format_indian_currency(x)}")

    # Calculate order counts for each campaign
    campaign_order_counts = filtered_orders_df['campaign'].value_counts().reset_index()
    campaign_order_counts.columns = ['campaign', 'Number of Orders']
    # Ensure 'campaign' column in order counts is also filled for merging
    campaign_order_counts['campaign'] = campaign_order_counts['campaign'].fillna('No Campaign')


    # Merge order counts into the campaign table data
    campaign_table_data = pd.merge(campaign_table_data, campaign_order_counts, on='campaign', how='left')
    # Fill any NaN in 'Number of Orders' after merge with 0, and convert to int
    campaign_table_data['Number of Orders'] = campaign_table_data['Number of Orders'].fillna(0).astype(int)

    campaign_table_data = campaign_table_data.rename(columns={
        'campaign': 'Campaign',
        'revenue_generated': 'Revenue',
        'net_profit': 'Net Profit',
        'Number of Orders': 'No. of Orders'
    })

    st.dataframe(campaign_table_data, use_container_width=True)