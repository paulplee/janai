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

    # selected_project = st.selectbox("Select a Project", options=list(projects.keys()), format_func=lambda x: x[8:], index=0, on_change=lambda: st.session_state.janai.set_project(projects[st.session_state.selected_project]))
    selected_project = st.selectbox(
        "Select a Project",
        options=list(projects.keys()),
        format_func=lambda x: x[8:],
        index=list(projects.keys()).index(st.session_state.selected_project) if st.session_state.selected_project in projects else 0,
        on_change=lambda: st.session_state.janai.set_project(projects[st.session_state.selected_project])
    )
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
        
    with vector_store_grid:
        st.write("### Vector Stores")

        st.session_state.grid_response = utils.display_vector_stores()


        col1, col2, _ = st.columns(3)
        
        with col1:
            if st.button('Delete'):
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
            if st.button('Reload'):
                st.session_state.files = st.session_state.janai.list_vector_stores()
                st.session_state.update_grid = True

        st.write("---")
        st.write("## Create Vector Store")
        st.text_input("Enter a name for the new vector store:", key="user_input")
        if st.button("Create Vector Store"):
            utils.create_vector_store_action()
            utils.refresh_vector_stores()


    
    with file_grid:
        st.write("### Files")
        st.session_state.grid_response = utils.display_files()
        num_files = len(st.session_state.files)
        st.write(f"Number of files: {num_files}")

    
if __name__ == '__main__':
    main()
    