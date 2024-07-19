import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from janai import JanAI
from utils import JanAIUtils as utils
import constants as c





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
    utils.init_session_state()
    
    if st.session_state.update_grid:
        # This is a dummy operation to make the grid's rendering logic dependent on update_grid
        pass
    
    st.write("# JanAI")
    st.write("## List of Vector Stores")
    # Store grid response in session state
    st.session_state.grid_response = utils.display_vector_stores()


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

if __name__ == '__main__':
    main()
    
    
    
