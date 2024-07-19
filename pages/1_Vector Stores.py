import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from janai import JanAI
from utils import OpenAIUtils as utils
import constants as c


def display_vector_stores():
    vs_converted = [utils.convert(vector_store) for vector_store in st.session_state.vector_stores]
    for vector_store in vs_converted:
        for key in ['created_at', 'last_active_at']:
            if key in vector_store:
                # Ensure the datetime is timezone-aware in UTC
                utc_datetime = pd.to_datetime(vector_store[key], unit='s', utc=True)
                vector_store[key] = utc_datetime.strftime('%d/%m/%Y %H:%M') + " UTC"
            if 'bytes' in vector_store:
                vector_store['bytes'] = utils.bytes_to_readable(vector_store['bytes'])
    
    df = pd.DataFrame([utils.convert(vector_store) for vector_store in st.session_state.vector_stores])
    gb = GridOptionsBuilder.from_dataframe(df)
    
    gb.configure_columns(df.columns, hide=True)
    column_order = ['id', 'name', 'usage_bytes', 'created_at', 'last_active_at']
    for column in column_order:
        match column:
            case "id":
                # Configure 'id' column
                gb.configure_column("id", hide=False, width=c.COL_WIDTHS['id'])
            case "name":
                # Configure 'filename' column
                gb.configure_column("name", hide=False, width=c.COL_WIDTHS['name'])
            case "usage_bytes":
                # Configure 'bytes' column with specific width
                gb.configure_column("usage_bytes", hide=False, width=c.COL_WIDTHS['bytes'])
            case "created_at":
                # Configure 'created_at' column
                gb.configure_column("created_at", hide=False, width=c.COL_WIDTHS['datetime'])
            case "last_active_at":
                # Configure 'created_at' column
                gb.configure_column("last_active_at", hide=False, width=c.COL_WIDTHS['datetime'])
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

    # Calculate dynamic height
    base_height_per_row = 30  # Example height per row in pixels
    header_height = 60  # Approximate height for headers and padding
    dynamic_height = min(max(len(df) * base_height_per_row + header_height, 100), 600)  # Set min and max height

    grid_response = AgGrid(df, gridOptions=grid_options, height=dynamic_height, width='100%', update_mode='MODEL_CHANGED', fit_columns_on_grid_load=True)
    return grid_response

def refresh_vector_stores():
    st.session_state.vector_stores = st.session_state.janai.list_vector_stores()
    # Explicitly trigger a rerender of the grid by toggling the update_grid state
    st.session_state.update_grid = not st.session_state.update_grid
    # Force Streamlit to rerender the page, which includes the grid
    st.rerun()
    
def create_vector_store_action():
    user_input = st.session_state.user_input
    if user_input:
        st.session_state.janai.create_vector_store(name=user_input)
        st.success(f"Vector store '{user_input}' created successfully!")
        refresh_vector_stores() 


def main():
    """
    This module provides a Streamlit application interface for managing vector stores using the JanAI library. It includes functionalities to display, refresh, and create vector stores. The application makes use of the AgGrid component to display the vector stores in a tabular format, allowing for a dynamic and interactive user experience.

    Functions:
        display_vector_stores():
            Converts vector store data into a human-readable format and displays it using AgGrid. It formats datetime and byte size fields for better readability. The function also configures the grid's columns, including their visibility and width, and dynamically adjusts the grid's height based on the number of rows.

        refresh_vector_stores():
            Refreshes the list of vector stores from the JanAI instance and triggers a rerender of the grid. This function is useful for reflecting changes in the vector stores, such as after creating a new vector store.

        create_vector_store_action():
            Creates a new vector store with a name provided by the user through the Streamlit interface. Upon successful creation, it refreshes the list of vector stores to include the newly created one.

        main():
            The main entry point of the Streamlit application. It initializes the JanAI instance and the list of vector stores if they are not already in the session state. It also handles the logic for updating the grid display and processes the action of deleting selected vector stores.

    Constants:
        The module makes use of constants defined in an external `constants.py` file for configuring column widths in the grid display.

    External Libraries:
        - streamlit: Used for creating the web application interface.
        - st_aggrid: Provides the AgGrid component for Streamlit, used for displaying the vector stores in a grid.
        - pandas: Utilized for data manipulation and formatting, especially for converting vector store data into a DataFrame for the grid display.
        - janai: A custom library (assumed) for managing JanAI instances and their vector stores.
        - utils: Contains utility functions for converting data into a human-readable format and for other data manipulation tasks.

    Note:
        This module assumes the existence of a `JanAI` class for managing vector stores and a `utils` module with specific functions like `convert` and `bytes_to_readable`. It also relies on a `constants.py` file for grid configuration constants.
    """
    if 'janai' not in st.session_state:
        st.session_state.janai = JanAI()
    if 'vector_stores' not in st.session_state:
        st.session_state.vector_stores = st.session_state.janai.list_vector_stores()
    if 'update_grid' not in st.session_state:
        st.session_state.update_grid = True  # Initialize the trigger for updating the grid
   # Example of making grid display dependent on update_grid
    if st.session_state.update_grid:
        # This is a dummy operation to make the grid's rendering logic dependent on update_grid
        pass
    
    st.write("# JanAI")
    st.write("## List of Vector Stores")
    # Store grid response in session state
    st.session_state.grid_response = display_vector_stores()


    col1, col2, _ = st.columns([1, 1, 8])
    
    with col1:
        if st.button('Delete'):
            # Access grid_response from session state
            selected_rows = st.session_state.grid_response['selected_rows']
            if not selected_rows.empty:
                deleted_ids = [row['id'] for index, row in selected_rows.iterrows() if 'id' in row]
                for row_id in deleted_ids:
                    st.session_state.janai.delete_vector_store(row_id)
                st.write("Deleted Vector Store IDs:", deleted_ids)
                refresh_vector_stores()
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
        create_vector_store_action()
        refresh_vector_stores()

if __name__ == '__main__':
    main()
    
    
    
