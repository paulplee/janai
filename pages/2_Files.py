import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from janai import JanAI

import warnings

# Suppress future warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def display_files():
    df = pd.DataFrame([file.to_dict() for file in st.session_state.files])
    gb = GridOptionsBuilder.from_dataframe(df)
    grid_options = gb.build()
    grid_options['rowSelection'] = 'multiple'

    # Calculate dynamic height
    base_height_per_row = 30  # Example height per row in pixels
    header_height = 60  # Approximate height for headers and padding
    dynamic_height = min(max(len(df) * base_height_per_row + header_height, 100), 600)  # Set min and max height

    grid_response = AgGrid(df, gridOptions=grid_options, height=dynamic_height, width='100%', update_mode='MODEL_CHANGED', fit_columns_on_grid_load=True)
    return grid_response

def refresh_files():
    st.session_state.files = st.session_state.janai.list_files()
    # Explicitly trigger a rerender of the grid by toggling the update_grid state
    st.session_state.update_grid = not st.session_state.update_grid
    # Force Streamlit to rerender the page, which includes the grid
    st.experimental_rerun()
    

def main():
    if 'janai' not in st.session_state:
        st.session_state.janai = JanAI()
    if 'files' not in st.session_state:
        st.session_state.files = st.session_state.janai.list_files()
    if 'update_grid' not in st.session_state:
        st.session_state.update_grid = True  # Initialize the trigger for updating the grid
   # Example of making grid display dependent on update_grid
    if st.session_state.update_grid:
        # This is a dummy operation to make the grid's rendering logic dependent on update_grid
        pass
    
    st.write("# JanAI")
    st.write("## List of Files")
    # Store grid response in session state
    st.session_state.grid_response = display_files()
    num_files = len(st.session_state.grid_response)
    st.write(f"Number of files: {num_files}")

    if st.button('Delete Selected'):
        # Access grid_response from session state
        selected_rows = st.session_state.grid_response['selected_rows']
        if not selected_rows.empty:
            deleted_ids = [row['id'] for index, row in selected_rows.iterrows() if 'id' in row]
            for row_id in deleted_ids:
                st.session_state.janai.delete_file(row_id)
            st.write("Deleted Vector Store IDs:", deleted_ids)
            refresh_files()
        else:
            st.write("No rows selected for deletion.")


if __name__ == '__main__':
    main()
    
    
    
