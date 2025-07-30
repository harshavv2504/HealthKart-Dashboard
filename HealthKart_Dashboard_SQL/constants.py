# constants.py
import os

# --- UI Colors for KPI Cards and Charts ---
# Define a list of light colors for KPI cards
LIGHT_COLORS = [
    "#E3F2FD",  # Light Blue (similar to powder blue)
    "#E8F5E9",  # Mint Green (existing, good)
    "#FFFDE7",  # Pale Yellow (very light cream)
    "#F3E5F5",  # Soft Lavender (existing, good)
    "#FFEBEE",  # Blush Pink (existing, good)
    "#F5F5F5",  # Very Light Grey (neutral base)
    "#DDF9F8"   # Light Aqua
]

# Define a color palette for ECharts visualizations
# These colors will be used for different series/segments in charts.
CHART_COLORS = [
    '#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3', '#8C96C6', '#8C628C',
    '#D0D1E6', '#A1D99B', '#43A2CA', '#FED98E', '#C7E9B4', '#7FCDSA', '#FDBB84', '#FDD49E', '#E0F3DB', '#CCEBC5',
    '#A8DDB5', '#7BCCC4', '#4EB3D3', '#2B8CBE', '#08589E', '#F7FCFD', '#E0ECF4', '#BFD3E6', '#9EBCDA', '#8C96C6'
]

# --- Business Logic Constants ---
# Percentage used for calculating Cost of Goods and Gross Profit.
PROFIT_MARGIN_FACTOR = 0.45 # Assumes 45% of total revenue is gross profit (1 - 0.55 COGS)

# --- File Paths & Database Configuration ---
# Name of the SQLite database file. It will be created in the project root.
DB_NAME = 'data.db' 

# Paths for static assets and CSS file.
PAGE_ICON_PATH = "static/New Project.png" # Make sure you have this image in a 'static' folder
CSS_PATH = "style.css"

# --- Table Styling (for Streamlit's st.dataframe if custom HTML styling is needed) ---
# These are general CSS styles that can be applied to tables.
# Note: With st.column_config, much of this styling is handled natively.
TABLE_BASE_STYLES = [
    {'selector': 'th, td', 'props': [('padding', '0.2rem 0.4rem'), ('font-size', '0.85rem'), ('text-align', 'left')]},
    {'selector': 'th', 'props': [('font-weight', 'bold')]}
]
TABLE_HEADER_CENTER_STYLE = [{'selector': 'th', 'props': [('text-align', 'center')]}]
