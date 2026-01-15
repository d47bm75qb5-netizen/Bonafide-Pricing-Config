import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

class PricingTool:
    def __init__(self, catalog_file):
        try:
            # This now matches your renamed desktop file
            self.catalog = pd.read_csv(catalog_file)
            
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

with st.sidebar.form("add_item_form"):
    product_choice = st.selectbox("Select Product", tool.get_product_list())
    qty_input = st.number_input("Quantity", min_value=1, value=1)
    add_btn = st.form_submit_button("Add to Quote")

    if add_btn:
        st.session_state['quote_items'].append({
            'product': product_choice,
            'qty': qty_input
        })
        st.success(f"Added {product_choice}")

if st.sidebar.button("Clear Quote"):
    st.session_state['quote_items'] = []
    st.rerun()

# --- MAIN PAGE: DISPLAY QUOTE ---
items, monthly, one_time = tool.calculate_quote(st.session_state['quote_items'])

if items:
    df = pd.DataFrame(items)
    # Format for display
    df_display = df.copy()
    df_display['Unit Price'] = df_display['Unit Price'].apply(lambda x: f"${x:,.2f}")
    df_display['Total Price'] = df_display['Total Price'].apply(lambda x: f"${x:,.2f}")

    st.subheader("Quote Details")
    st.dataframe(df_display, use_container_width=True)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly Recurring", f"${monthly:,.2f}")
    col2.metric("One-Time Fees", f"${one_time:,.2f}")
    col3.metric("Total First Year", f"${(monthly * 12) + one_time:,.2f}")

else:
    st.info("👈 Select products from the sidebar to start building a quote.")