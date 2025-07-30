# utils/utils.py
import streamlit as st
import os
import pandas as pd # ADDED: Import pandas for pd.isna()

def load_css(css_file_name):
    """Loads a CSS file and applies it to the Streamlit app."""
    try:
        # Construct the full path to the CSS file relative to the script
        script_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(script_dir)
        css_filepath = os.path.join(project_root, css_file_name)

        with open(css_filepath) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: CSS file '{css_file_name}' not found. Please ensure it's in the project root.")
    except Exception as e:
        st.error(f"An error occurred while loading CSS: {e}")

def format_indian_currency(value):
    """Formats a number into Indian Rupees (INR) format (e.g., 1,23,456)."""
    # Handle non-numeric or NaN values
    # Use pandas' is_number check, which is more robust and handles numpy types.
    if not pd.api.types.is_number(value) or pd.isna(value):
        return 'N/A'
        
    s = str(int(value))
    if len(s) <= 3:
        return s
    last_three = s[-3:]
    other_numbers = s[:-3]

    other_numbers_rev = other_numbers[::-1]
    formatted_other_numbers_rev = ''
    for i, char in enumerate(other_numbers_rev):
        formatted_other_numbers_rev += char
        if (i + 1) % 2 == 0 and (i + 1) != len(other_numbers_rev):
            formatted_other_numbers_rev += ','

    return formatted_other_numbers_rev[::-1] + ',' + last_three

# You had a to_csv helper function, but it's not used by the dashboard directly
# and is more relevant for data generation/cleaning if needed.
# @st.cache_data
# def to_csv(df):
#     """Converts a DataFrame to a CSV string for downloading."""
#     return df.to_csv(index=False).encode('utf-8')
