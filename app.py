import streamlit as st
import pandas as pd
from src.connectors.redshift_connector import RedshiftConnector

st.set_page_config(page_title="Data Source Connector", layout="wide")

def main():
    st.title("Data Source Connector")
    
    # Initialize connector
    if 'connector' not in st.session_state:
        st.session_state.connector = RedshiftConnector()
    
    # Sidebar for connector selection
    with st.sidebar:
        st.header("Data Source")
        connector_type = st.selectbox(
            "Select Connector",
            ["Amazon Redshift"],  # We'll add more connectors later
            index=0
        )
    
    # Main content area for credentials
    st.header("Connection Settings")
    
    # Create columns for a better layout
    col1, col2 = st.columns(2)
    
    with col1:
        host = st.text_input("Host")
        database = st.text_input("Database")
        port = st.number_input("Port", value=5439)
    
    with col2:
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
    
    if st.button("Connect", type="primary"):
        try:
            st.session_state.connector.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )
            st.success("Connected successfully!")
            st.session_state.connected = True
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")
            st.session_state.connected = False
    
    # Table and column selection (only shown when connected)
    if st.session_state.get('connected', False):
        st.divider()
        try:
            # Get tables
            tables = st.session_state.connector.get_tables()
            selected_table = st.selectbox("Select a table", tables)
            
            if selected_table:
                # Get columns
                columns = st.session_state.connector.get_columns(selected_table)
                column_names = [col["name"] for col in columns]
                selected_columns = st.multiselect("Select columns", column_names)
                
                if selected_columns:
                    st.write(f"Selected columns from table '{selected_table}':")
                    st.write(selected_columns)
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 