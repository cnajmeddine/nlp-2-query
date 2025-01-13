# main.py
import streamlit as st
import json
from database.connector import DatabaseConnector
from nlp.text_to_sql import TextToSQL
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def save_query(query, filename):
    with open(filename, 'w') as f:
        f.write(query)

def main():
    st.title("Natural Language to SQL Query")
    
    # Database connection section
    st.sidebar.header("Database Connection")
    db_host = st.sidebar.text_input("Host", "localhost")
    db_name = st.sidebar.text_input("Database", "postgres")
    db_user = st.sidebar.text_input("Username", "postgres")
    db_pass = st.sidebar.text_input("Password", type="password")
    
    # OpenRouter API Key input
    openrouter_api_key = st.sidebar.text_input(
        "OpenRouter API Key", 
        type="password",
        value=os.getenv('OPENROUTER_API_KEY', '')
    )
    
    # Initialize components
    if 'db_connector' not in st.session_state:
        st.session_state.db_connector = None
    if 'text_to_sql' not in st.session_state:
        st.session_state.text_to_sql = None
    
    # Connect button
    if st.sidebar.button("Connect"):
        try:
            st.session_state.db_connector = DatabaseConnector(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_pass
            )
            st.session_state.text_to_sql = TextToSQL(
                st.session_state.db_connector,
                openrouter_api_key
            )
            st.sidebar.success("Connected successfully!")
        except Exception as e:
            st.sidebar.error(f"Connection failed: {str(e)}")
    
    # Main query interface
    user_input = st.text_area("Enter your question:", "What were the sales in the last year?")
    
    if st.button("Generate Query"):
        if st.session_state.db_connector and st.session_state.text_to_sql:
            try:
                generated_query = st.session_state.text_to_sql.generate_query(user_input)
                st.session_state['current_query'] = generated_query
                
                # Display the generated query
                st.subheader("Generated SQL Query")
                st.code(generated_query, language="sql")
                
                # Query modification
                modified_query = st.text_area("Modify Query:", generated_query)
                
                # Execute and save options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Execute Query"):
                        results = st.session_state.db_connector.execute_query(modified_query)
                        st.subheader("Results")
                        st.dataframe(results)
                
                with col2:
                    save_filename = st.text_input("Save as:", "query.sql")
                    if st.button("Save Query"):
                        save_query(modified_query, save_filename)
                        st.success(f"Query saved to {save_filename}")
                        
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please connect to a database first.")

if __name__ == "__main__":
    main()