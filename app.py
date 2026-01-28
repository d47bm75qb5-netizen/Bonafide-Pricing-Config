import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

class PricingTool:
    def __init__(self, catalog_file):
        try:
            self.catalog = pd.read_csv(catalog_file)
            
            # 1. Clean Data
            self.catalog = self.catalog.dropna(subset=['Product/Service'])
            # Remove Implementation and Training if it exists
            self.catalog = self.catalog[self.catalog['Product/Service'] != 'Implementation and Training']
            
            if 'Term' in self.catalog.columns:
                self.catalog['Term'] = self.catalog['Term'].replace('Monthy', 'Monthly')
            
            # 2. Create Lookup Dictionary
            self.prices = self.catalog.set_index('Product/Service')[['List Price', 'Term', 'Quote Name']].to_dict('index')
        except FileNotFoundError:
            st.error(f"Could not find file: {catalog_file}. Please make sure 'price_catalog.csv' is in the repository.")
            self.prices = {}

    def get_product_list(self):
        return list(self.prices.keys())

    # Helper to get default item details when adding to list
    def get_item_details(self, product_name, qty=1, is_service=False):
        if is_service:
            return {
                "Product": product_name,
                "Term": "One-time",
                "Qty": float(qty),
                "Unit Price": 205.00
            }
        elif product_name in self.prices:
            data = self.prices[product_name]
            return {
                "Product": product_name, # Use the selected name from dropdown
                "Term": data['Term'],
                "Qty": float(qty),
                "Unit Price": float(data['List Price'])
            }
        return None

st.title("Bonafide Pricing Calculator")

# --- LOAD DATA ---
tool = PricingTool('price_catalog.csv')

# --- INITIALIZE SESSION STATE ---
if 'quote_data' not in st.session_state:
    st.session_state['quote_data'] = []

# --- SIDEBAR: ADD ITEMS ---
st.sidebar.header("Build Your Quote")

# 1. STANDARD PRODUCTS
with st.sidebar.form("add_item_form"):
    st.markdown("### Standard Products")
    product_choice = st.selectbox("Select Product", tool.get_product_list())
    qty_input = st.number_input("Quantity", min_value=1, value=1)
    add_btn = st.form_submit_button("Add Product")

    if add_btn:
        new_item = tool.get_item_details(product_choice, qty_input)
        if new_item:
            st.session_state['quote_data'].append(new_item)
            st.success(f"Added {product_choice}")

# 2. SERVICES
st.sidebar.markdown("---")
with st.sidebar.form("add_service_form"):
    st.markdown("### Add Hourly Services")
    service_choice = st.selectbox("Select Service", ["Professional Services", "Migration"])
    hours_input = st.number_input("Hours", min_value=1, value=1)
    add_svc_btn = st.form_submit_button("Add Service Fee")

    if add_svc_btn:
        new_item = tool.get_item_details(service_choice, hours_input, is_service=True)
        if new_item:
            st.session_state['quote_data'].append(new_item)
            st.success(f"Added {service_choice}")

if st.sidebar.button("Clear Quote"):
    st.session_state['quote_data'] = []
    st.rerun()

# --- MAIN PAGE: EDITABLE DATA TABLE ---
if st.session_state['quote_data']:
    st.subheader("Quote Details")
    st.caption("📝 You can edit 'Qty' and 'Unit Price' directly in the table below. Select a row and press Delete to remove it.")

    # Convert list to DataFrame
    df = pd.DataFrame(st.session_state['quote_data'])

    # Calculate Total Price (Dynamic)
    df['Total Price'] = df['Qty'] * df['Unit Price']

    # Configure the Data Editor
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic", # Allows adding/deleting rows
        column_config={
            "Unit Price": st.column_config.NumberColumn(format="$%.2f"),
            "Total Price": st.column_config.NumberColumn(format="$%.2f", disabled=True), # Read-only
            "Term": st.column_config.TextColumn(disabled=True),
            "Product": st.column_config.TextColumn(disabled=True),
        },
        key="editor"
    )

    # --- SYNC CHANGES & CALCULATE TOTALS ---
    # Update session state with changes from the editor (excluding the calculated total column)
    if not edited_df.equals(df):
        # We drop 'Total Price' before saving back to state so it recalculates correctly next time
        st.session_state['quote_data'] = edited_df.drop(columns=['Total Price']).to_dict('records')
        st.rerun()

    # Calculate Totals for Metrics
    monthly_total = edited_df[edited_df['Term'] == 'Monthly']['Total Price'].sum()
    onetime_total = edited_df[edited_df['Term'] == 'One-time']['Total Price'].sum()

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly Recurring", f"${monthly_total:,.2f}")
    col2.metric("One-Time Fees", f"${onetime_total:,.2f}")
    col3.metric("Total First Year", f"${(monthly_total * 12) + onetime_total:,.2f}")

else:
    st.info("👈 Select products or services from the sidebar to start building a quote.")
