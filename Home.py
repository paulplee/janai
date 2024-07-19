import streamlit as st
import warnings
import os
from dotenv import load_dotenv
from janai import JanAI
from utils import JanAIUtils as utils

# Assuming janai is already imported or defined somewhere in your code
import janai

load_dotenv()

# Suppress future warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Set Streamlit page to wide mode
st.set_page_config(layout="wide")

def main(): 
    utils.init_session_state()

    st.write("# JanAI")

    projects = {key: value for key, value in os.environ.items() if key.startswith('PROJECT_')}

    # Initialize selected_project in session state if not present
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = list(projects.keys())[0]

    col_projects, _, col_clear_project = st.columns([3, 5, 2])
    with col_projects:

        selected_project = st.selectbox(
            "Select a Project",
            options=list(projects.keys()),
            format_func=lambda x: x[8:],
            index=list(projects.keys()).index(st.session_state.selected_project) if st.session_state.selected_project in projects else 0,
            on_change=lambda: st.session_state.janai.set_project(projects[st.session_state.selected_project])
        )
    
    with col_clear_project:
        if st.button('⚠️ ☢️ Clear Project ☢️⚠️'):
            # Set a flag in session_state to show the confirmation buttons
            st.session_state.show_confirm = True

        if 'show_confirm' in st.session_state and st.session_state.show_confirm:
            st.write("Are you sure you want to clear all resources? This action cannot be undone.")
            if st.button("Yes, I'm sure"):
                utils.delete_all_resources()
                # Reset the flag to hide confirmation buttons
                st.session_state.show_confirm = False
            if st.button("No, cancel"):
                # Reset the flag to hide confirmation buttons
                st.session_state.show_confirm = False    
                
    # Update session state and call janai.set_project if the selection changes
    if selected_project != st.session_state.selected_project:
        st.session_state.janai.set_project(projects[selected_project])
        st.session_state.selected_project = selected_project
        st.session_state.vector_stores = st.session_state.janai.list_vector_stores()
        st.session_state.files = st.session_state.janai.list_files()
        st.session_state.assistants = st.session_state.janai.list_assistants()
        st.session_state.update_grid = True
        
        
    assistant_grid, vector_store_grid, file_grid = st.columns(3)
    
    with assistant_grid:
        st.write("### Assistants")

        st.session_state.grid_response = utils.display_assistants()
    
        num_assistants = len(st.session_state.assistants)
        st.write(f"Number of assistants: {num_assistants}")
    
        button_col1, button_col2, _ = st.columns([1.2, 1.2,1])
        with button_col1:
            if st.button('Delete Assistant(s)'):
                if 'selected_rows' in st.session_state.grid_response and st.session_state.grid_response['selected_rows'] is not None:
                    selected_rows = st.session_state.grid_response['selected_rows']
                    if not selected_rows.empty:
                        deleted_ids = [row['id'] for index, row in selected_rows.iterrows() if 'id' in row]
                        for row_id in deleted_ids:
                            st.session_state.janai.delete_assistant(row_id)
                        st.write("Deleted Vector Store IDs:", deleted_ids)
                        utils.refresh_assistants()
                    else:
                        st.write("No rows selected for deletion.")
    
        with button_col2:
            if st.button('Reload Assistants'):
                st.session_state.assistants = st.session_state.janai.list_assistants(order='asc', limit=100)
                st.session_state.update_grid = True
                        
        
    with vector_store_grid:
        st.write("### Vector Stores")

        st.session_state.grid_response = utils.display_vector_stores()
        st.write("Number of vector stores:", len(st.session_state.vector_stores))
        col1, col2, _ = st.columns([1,1,0.5])
        
        with col1:
            if st.button('Delete Vector Store(s)'):
                # Access grid_response from session state
                selected_rows = st.session_state.grid_response['selected_rows']
                if not selected_rows.empty:
                    deleted_ids = [row['id'] for index, row in selected_rows.iterrows() if 'id' in row]
                    for row_id in deleted_ids:
                        st.session_state.janai.delete_vector_store(row_id)
                    st.write("Deleted Vector Store IDs:", deleted_ids)
                    utils.refresh_vector_stores()
                else:
                    st.write("No rows selected for deletion.")
        with col2:
            if st.button('Reload Vector Stores'):
                st.session_state.files = st.session_state.janai.list_vector_stores()
                st.session_state.update_grid = True

    
    with file_grid:
        st.write("### Files")
        st.session_state.grid_response = utils.display_files()
        num_files = len(st.session_state.files)
        st.write(f"Number of files: {num_files}")

        col1, col2, _ = st.columns([1, 1, 1.5])
        
        with col1:
            if st.button('Delete File(s)'):
                selected_rows = st.session_state.grid_response['selected_rows']
                if not selected_rows.empty:
                    deleted_ids = [row['id'] for index, row in selected_rows.iterrows() if 'id' in row]
                    for row_id in deleted_ids:
                        st.session_state.janai.delete_file(row_id)
                    st.write("Deleted Vector Store IDs:", deleted_ids)
                    utils.refresh_files()
                else:
                    st.write("No rows selected for deletion.")
        
        with col2:
            if st.button('Reload Files'):
                st.session_state.files = st.session_state.janai.list_files()
                st.session_state.update_grid = True
    
if __name__ == '__main__':
    main()
    