# utils/utils.py
import streamlit as st
import os

def load_css(css_file_name):
    """Loads a CSS file and applies it to the Streamlit app."""
    try:
        with open(css_file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: CSS file '{css_file_name}' not found.")

def format_indian_currency(value):
    """Formats a number into Indian Rupees (INR) format (e.g., 1,23,456)."""
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

@st.cache_data
def to_csv(df):
    """Converts a DataFrame to a CSV string for downloading."""
    return df.to_csv(index=False).encode('utf-8')