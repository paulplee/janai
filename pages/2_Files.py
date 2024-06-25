import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from janai import JanAI
import hashlib

def file_hash(file):
    file.seek(0)
    hash_obj = hashlib.sha256()
    hash_obj.update(file.read())
    file.seek(0)
    return hash_obj.hexdigest()

def display_files():
    df = pd.DataFrame([file.to_dict() for file in st.session_state.files])
    gb = GridOptionsBuilder.from_dataframe(df)
    grid_options = gb.build()
    grid_options['rowSelection'] = 'multiple'
    base_height_per_row = 30
    header_height = 60
    dynamic_height = min(max(len(df) * base_height_per_row + header_height, 100), 600)
    grid_response = AgGrid(df, gridOptions=grid_options, height=dynamic_height, width='100%', update_mode='MODEL_CHANGED', fit_columns_on_grid_load=True)
    return grid_response

def refresh_files():
    st.session_state.files = st.session_state.janai.list_files()
    st.session_state.update_grid = not st.session_state.update_grid
    st.rerun()

def main():
    st.set_page_config(layout="wide")
    if 'janai' not in st.session_state:
        st.session_state.janai = JanAI()
    if 'files' not in st.session_state:
        st.session_state.files = st.session_state.janai.list_files()
    if 'update_grid' not in st.session_state:
        st.session_state.update_grid = True
    if 'file_processed' not in st.session_state:
        st.session_state.file_processed = False
    if 'last_file_hash' not in st.session_state:
        st.session_state.last_file_hash = ''

    st.write("# JanAI")
    st.write("## List of Files")
    st.session_state.grid_response = display_files()
    num_files = len(st.session_state.files)
    st.write(f"Number of files: {num_files}")

    if st.button('Delete Selected'):
        selected_rows = st.session_state.grid_response['selected_rows']
        if not selected_rows.empty:
            deleted_ids = [row['id'] for index, row in selected_rows.iterrows() if 'id' in row]
            for row_id in deleted_ids:
                st.session_state.janai.delete_file(row_id)
            st.write("Deleted Vector Store IDs:", deleted_ids)
            refresh_files()
        else:
            st.write("No rows selected for deletion.")

    st.write("---")
    st.write("## Upload File")
    uploaded_file = st.file_uploader("## Upload File", type=None, key="file_uploader")

    if uploaded_file is not None:
        current_file_hash = file_hash(uploaded_file)
        if current_file_hash != st.session_state.last_file_hash:
            st.session_state.file_processed = False

        if not st.session_state.file_processed:
            st.session_state.janai.create_file(file=uploaded_file)
            st.success("File uploaded successfully.")
            st.session_state.file_processed = True
            st.session_state.last_file_hash = current_file_hash
            refresh_files()

if __name__ == '__main__':
    main()