import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from janai import JanAI

def display_vector_stores():
    df = pd.DataFrame([vector_store.to_dict() for vector_store in st.session_state.vector_stores])
    gb = GridOptionsBuilder.from_dataframe(df)
    grid_options = gb.build()
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

    if st.button('Delete Selected'):
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

    st.text_input("Enter a name for the new vector store:", key="user_input")
    if st.button("Create Vector Store"):
        create_vector_store_action()
        refresh_vector_stores()

if __name__ == '__main__':
    main()
    
    
    
