import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from src.model.model_run import UniqueIdentifier
from src.connectors.redshift_connector import RedshiftConnector

# Load environment variables
load_dotenv()

def init_connection(credentials):
    """Initialize database connection"""
    try:
        connector = RedshiftConnector()
        connector.connect(**credentials)
        return connector
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="Data Matching Tool", layout="wide")
    
    # Sidebar for database connection
    with st.sidebar:
        st.title("Database Connection")
        
        # Receive database connection details from user input
        host = st.text_input("Host")
        database = st.text_input("Database")
        user = st.text_input("User")
        password = st.text_input("Password", type="password")
        port = st.number_input("Port", value=5439)
        
        connect_button = st.button("Connect to Database")
        
        if connect_button:
            credentials = {
                'host': host,
                'database': database,
                'user': user,
                'password': password,
                'port': int(port)
            }
            connector = init_connection(credentials)
            if connector:
                st.session_state['connector'] = connector
                st.success("Connected successfully!")

    # Main content
    st.title("Unique - Data Matching Tool")
    
    if 'connector' in st.session_state:
        connector = st.session_state['connector']
        
        # Create two columns for table selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("First Table")
            schemas = connector.get_schemas()
            schema1 = st.selectbox("Select Schema 1", schemas, key="schema1")
            
            if schema1:
                tables = connector.get_tables(schema1)
                table1 = st.selectbox("Select Table 1", tables, key="table1")
                
                if table1:
                    columns = connector.get_columns(schema1, table1)
                    columns1 = st.multiselect(
                        "Select Columns 1",
                        [col["name"] for col in columns],
                        key="columns1"
                    )
        
        with col2:
            st.header("Second Table")
            schema2 = st.selectbox("Select Schema 2", schemas, key="schema2")
            
            if schema2:
                tables = connector.get_tables(schema2)
                table2 = st.selectbox("Select Table 2", tables, key="table2")
                
                if table2:
                    columns = connector.get_columns(schema2, table2)
                    columns2 = st.multiselect(
                        "Select Columns 2",
                        [col["name"] for col in columns],
                        key="columns2"
                    )
        
        # Run matching button in the center
        if schema1 and table1 and columns1 and schema2 and table2 and columns2:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                run_button = st.button("🔍 Run Matching Analysis", use_container_width=True)
                
                if run_button:
                    with st.spinner("Analyzing tables for matching users..."):
                        try:
                            unique_identifier = UniqueIdentifier(connector)
                            results = unique_identifier.find_unique_users(
                                schema1=schema1,
                                table1=table1,
                                columns1=columns1,
                                schema2=schema2,
                                table2=table2,
                                columns2=columns2
                            )
                            
                            if not results.empty:
                                st.success(f"Found {len(results)} potential matches!")
                                
                                # Create tabs for different views
                                tab1, tab2 = st.tabs(["Detailed Results", "Summary Statistics"])
                                
                                with tab1:
                                    st.dataframe(
                                        results.style.background_gradient(
                                            subset=['similarity_score'],
                                            cmap='RdYlGn'
                                        ),
                                        use_container_width=True
                                    )
                                    
                                    # Download button
                                    csv = results.to_csv(index=False)
                                    st.download_button(
                                        "📥 Download Results",
                                        csv,
                                        "matching_results.csv",
                                        "text/csv",
                                        key='download-csv'
                                    )
                                
                                with tab2:
                                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                                    with metric_col1:
                                        st.metric("Total Matches", len(results))
                                    with metric_col2:
                                        st.metric("Average Similarity", f"{results['similarity_score'].mean():.2f}%")
                                    with metric_col3:
                                        st.metric("Max Similarity", f"{results['similarity_score'].max():.2f}%")
                                    
                                    # Add a histogram of similarity scores
                                    st.subheader("Similarity Score Distribution")
                                    hist_data = results['similarity_score']
                                    st.bar_chart(hist_data.value_counts(bins=10).sort_index())
                            else:
                                st.info("No matches found between the selected tables.")
                                
                        except Exception as e:
                            st.error(f"Error during matching: {str(e)}")
    else:
        st.info("👈 Please connect to your database using the sidebar")

if __name__ == "__main__":
    main() 
