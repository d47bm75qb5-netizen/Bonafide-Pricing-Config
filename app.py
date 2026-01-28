import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

class PricingTool:
    def __init__(self, catalog_file):
        try:
            # Load the file
            self.catalog = pd.read_csv(catalog_file)
            
            # --- FILTERING LOGIC ---
            # 1. Remove rows where Product/Service is empty (removes 'nan')
            self.catalog = self.catalog.dropna(subset=['Product/Service'])
            
            # 2. Remove "Implementation and Training"
            self.catalog = self.catalog[self.catalog['Product/Service'] != 'Implementation and Training']
            # -----------------------

            # Clean data: Fix typos (e.g., 'Monthy' -> 'Monthly')
            if 'Term' in self.catalog.columns:
                self.catalog['Term'] = self.catalog['Term'].replace('Monthy', 'Monthly')
            
            # Create a lookup dictionary
            self.prices = self.catalog.set_index('Product/Service')[['List Price', 'Term', 'Quote Name']].to_dict('index')
        except FileNotFoundError:
            st.error(f"Could not find file: {catalog_file}. Please make sure 'price_catalog.csv' is in the repository.")
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
                elif term == 'One
