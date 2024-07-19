import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
from janai import JanAI
from utils import OpenAIUtils as utils
import constants as c


def main():
    """
    Main function to run the Streamlit app.

    This function sets up the Streamlit page configuration and initializes session state variables if they are not already set.
    It displays the UI components for listing files, including a file uploader for adding new files and a button for deleting
    selected files. It handles file uploads and deletions by updating the session state and refreshing the displayed list of files.
    """
    st.set_page_config(layout="wide")
    utils.init_session_state()

    st.write("# JanAI")
    st.write("## List of Files")
    st.session_state.grid_response = utils.display_files()
    num_files = len(st.session_state.files)
    st.write(f"Number of files: {num_files}")

    col1, col2, _ = st.columns([1, 1, 8])
    
    with col1:
        if st.button('Delete'):
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
        if st.button('Reload'):
            st.session_state.files = st.session_state.janai.list_files()
            st.session_state.update_grid = True
            
    st.write("---")
    st.write("## Upload File")
    uploaded_file = st.file_uploader("## Upload File", type=None, key="file_uploader")

    if uploaded_file is not None:
        current_file_hash = utils.file_hash(uploaded_file)
        if current_file_hash != st.session_state.last_file_hash:
            st.session_state.file_processed = False

        if not st.session_state.file_processed:
            st.session_state.janai.create_file(file=uploaded_file)
            st.success("File uploaded successfully.")
            st.session_state.file_processed = True
            st.session_state.last_file_hash = current_file_hash
            utils.refresh_files()

if __name__ == '__main__':
    main()