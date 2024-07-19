import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from janai import JanAI
import hashlib
from utils import OpenAIUtils as utils

def file_hash(file):
    """
    Calculates the SHA-256 hash of a file's contents.

    This function reads the entire content of a file, calculates its SHA-256 hash, and then returns the hexadecimal
    representation of this hash. It ensures the file's read pointer is reset to its original position after reading.

    Parameters:
    - file (file-like object): The file for which to calculate the hash. This should be an open file object.

    Returns:
    - str: The hexadecimal string representation of the SHA-256 hash of the file's contents.
    """
    file.seek(0)
    hash_obj = hashlib.sha256()
    hash_obj.update(file.read())
    file.seek(0)
    return hash_obj.hexdigest()

def display_files():
    """
    Displays a list of files in a Streamlit app using the AgGrid component.

    This function converts a list of file metadata into a pandas DataFrame, then formats certain columns for better readability
    (e.g., converting byte sizes to a human-readable format and formatting timestamps). It uses the AgGrid component to display
    the DataFrame in a grid format, allowing for interactive sorting and selection. The grid's columns are configured for
    display properties and order.

    Returns:
    - Grid response object from AgGrid, containing information about the grid state, including selected rows.
    """
    files_converted = [utils.convert(file) for file in st.session_state.files]
    for file in files_converted:
        # Convert 'created_at' to datetime and then format it
        if 'created_at' in file:
            # Ensure the datetime is timezone-aware in UTC
            utc_datetime = pd.to_datetime(file['created_at'], unit='s', utc=True)
            file['created_at'] = utc_datetime.strftime('%d/%m/%Y %H:%M') + " UTC"        # Convert 'bytes' to a human-readable format
        if 'bytes' in file:
            file['bytes'] = utils.bytes_to_readable(file['bytes'])
    
    df = pd.DataFrame(files_converted)
    
    gb = GridOptionsBuilder.from_dataframe(df)
    # Hide all columns initially
    gb.configure_columns(df.columns, hide=True)
    # Specify the order and visibility of columns
    column_order = ['id', 'filename', 'bytes', 'created_at']
    for column in column_order:
        match column:
            case "id":
                # Configure 'id' column
                gb.configure_column("id", hide=False, width=70)
            # case "filename":
            #     # Configure 'filename' column
            #     gb.configure_column("filename", hide=False)
            case "bytes":
                # Configure 'bytes' column with specific width
                gb.configure_column("bytes", hide=False, width=20)
            case "created_at":
                # Configure 'created_at' column
                gb.configure_column("created_at", hide=False, width=40)
            case _:
                # Default configuration for any other column
                gb.configure_column(column, hide=False)
                
    grid_options = gb.build()
    # Correctly reorder the columnDefs based on column_order
    # First, create a mapping of field names to column definitions
    field_to_colDef = {colDef['field']: colDef for colDef in grid_options['columnDefs']}
    # Then, reorder columnDefs using the column_order list
    grid_options['columnDefs'] = [field_to_colDef[column] for column in column_order if column in field_to_colDef]

    grid_options['rowSelection'] = 'multiple'
    base_height_per_row = 30
    header_height = 60
    dynamic_height = min(max(len(df) * base_height_per_row + header_height, 100), 600)
    # grid_response = AgGrid(df, gridOptions=grid_options, height=dynamic_height, width='100%', update_mode='MODEL_CHANGED', fit_columns_on_grid_load=True)
    grid_response = AgGrid(df, gridOptions=grid_options, height=dynamic_height, width='100%', update_mode='MODEL_CHANGED', fit_columns_on_grid_load=True)
    return grid_response


def refresh_files():
    """
    Refreshes the list of files displayed in the Streamlit app.

    This function updates the global session state with a new list of files by calling a method to list files from an external
    source (e.g., a database or file storage system). It then triggers a rerun of the Streamlit app to reflect the updated file list.
    """
    st.session_state.files = st.session_state.janai.list_files()
    st.session_state.update_grid = not st.session_state.update_grid
    st.rerun()

def main():
    """
    Main function to run the Streamlit app.

    This function sets up the Streamlit page configuration and initializes session state variables if they are not already set.
    It displays the UI components for listing files, including a file uploader for adding new files and a button for deleting
    selected files. It handles file uploads and deletions by updating the session state and refreshing the displayed list of files.
    """
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