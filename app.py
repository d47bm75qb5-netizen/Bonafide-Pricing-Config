import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

class PricingTool:
    def __init__(self, catalog_file):
        try:
            # This now matches your renamed desktop file
            self.catalog = pd.read_csv(catalog_file)
            
            # --- UPDATED SECTION: FILTERING DATA ---
            # 1. Remove rows where Product/Service is empty (removes 'nan')
            self.catalog = self.catalog.dropna(subset=['Product/Service'])
            
            # 2. Remove the specific "Implementation and Training" row
            self.catalog = self.catalog[self.catalog['Product/Service'] != 'Implementation and Training']
            # ---------------------------------------

            # Clean data: Fix typos (e.g., 'Monthy' -> 'Monthly')
            if 'Term' in self.catalog.columns:
                self.catalog['Term'] = self.catalog['Term'].replace('Monthy', 'Monthly')
            
            # Create a lookup dictionary
            self.prices = self.catalog.set_index('Product/Service')[['List Price', 'Term', 'Quote Name']].to_dict('index')
        except FileNotFoundError:
            st.error(f"Could not find file: {catalog_file}. Please make sure 'price_catalog.csv' is on your Desktop.")
            self.prices = {}

    def get_product_list(self):
        return list(self.prices.keys())

    def calculate_quote(self, selected_items):
        line_items = []
        monthly_total = 0
        onetime_total = 0
        
        for item in selected_items:
            prod_id = item['product']
            qty = item['qty']
            
            if prod_id in self.prices:
                data = self.prices[prod_id]
                unit_price = data['List Price']
                term = data['Term']
                quote_name = data['Quote Name']
                
                line_total = unit_price * qty
                
                if term == 'Monthly':
                    monthly_total += line_total
                elif term == 'One-time':
                    onetime_total += line_total
                
                line_items.append({
                    "Product": quote_name,
                    "Term": term,
                    "Qty": qty,
                    "Unit Price": unit_price,
                    "Total Price": line_total
                })
        
        return line_items, monthly_total, onetime_total

st.title("Bonafide Pricing Calculator")

# --- LOAD DATA ---
# This matches the file you renamed on your desktop
tool = PricingTool('price_catalog.csv')

if not tool.prices:
    st.stop()

# --- SIDEBAR: INPUTS ---
st.sidebar.header("Build Your Quote")

if 'quote_items' not in st.session_state:
    st.session_state['quote_items'] = []

with st
