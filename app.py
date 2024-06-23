import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd

from janai import JanAI

def refresh_vector_stores(state):
    # a. Clear state.vector_stores
    state.vector_stores.clear()

    # b. Repopulate state.vector_stores with state.janai.list_vector_stores()
    state.vector_stores = state.janai.list_vector_stores()

    # c. Refresh grid_response with the contents of the updated state.vector_stores
    vs_list = [vector_store.to_dict() for vector_store in state.vector_stores]
    df = pd.DataFrame(vs_list)
    
    # Configure grid options for AgGrid
    gb = GridOptionsBuilder.from_dataframe(df)
    grid_options = gb.build()
    grid_options['rowSelection'] = 'multiple'  # Use 'single' for single row selection
    
    # Display the updated DataFrame with AgGrid
    grid_response = AgGrid(df, gridOptions=grid_options, height=300, 
                           width='100%', update_mode='MODEL_CHANGED', 
                           fit_columns_on_grid_load=True)
    return grid_response

def create_vector_store_action(state):
    user_input = st.session_state.user_input  # Access the user input from the session state
    if user_input:  # Check if the input is not empty
        # Call the create_vector_store function with the user input
        state.janai.create_vector_store(name=user_input)
        st.success(f"Vector store '{user_input}' created successfully!")
        refresh_vector_stores(state)  # Assuming refresh_vector_stores is correctly defined to update the UI


def main():
    state = st.session_state
    st.write("# JanAI")

    state.janai = JanAI()

    state.vector_stores = state.janai.list_vector_stores()

    vs_list = []
    for vector_store in state.vector_stores:
        vs_list.append(vector_store.to_dict())
    df = pd.DataFrame(vs_list)

    st.write("## List of  Vector Stores")

    # Configure grid options for AgGrid
    gb = GridOptionsBuilder.from_dataframe(df)
    grid_options = gb.build()

    # Enable row selection
    grid_options['rowSelection'] = 'multiple'  # Use 'single' for single row selection

    # Display the DataFrame with AgGrid
    grid_response = AgGrid(df, gridOptions=grid_options, height=300, 
                        width='100%', update_mode='MODEL_CHANGED', 
                        fit_columns_on_grid_load=True)



    if st.button('Delete Selected'):
        # Retrieve selected rows
        selected_rows = grid_response['selected_rows']

        # Check if selected_rows is a DataFrame and not empty
        if not selected_rows.empty:
            deleted_ids = [row['id'] for index, row in selected_rows.iterrows() if 'id' in row]
            for row_id in deleted_ids:
                state.janai.delete_vector_store(row_id)
            
            # Update the list of vector stores
            state.vector_stores = state.janai.list_vector_stores()
            
            # Convert the updated list to a DataFrame
            vs_list = [vector_store.to_dict() for vector_store in state.vector_stores]
            df = pd.DataFrame(vs_list)
            
            # Display the updated DataFrame with AgGrid
            grid_response = AgGrid(df, gridOptions=grid_options, height=300, 
                                width='100%', update_mode='MODEL_CHANGED', 
                                fit_columns_on_grid_load=True)
            
            st.write("Deleted Vector Store IDs:", deleted_ids)
        else:
            st.write("No rows selected for deletion.")
            
    # 1. A text input for the user to enter a name for a new vector store
    user_input = st.text_input("Enter a name for the new vector store:", on_change=create_vector_store_action(state), key="user_input")

    # 2. A button "Create Vector Store"
    if st.button("Create Vector Store"):
        # 3. When clicked, calls state.janai.create_vector_store with the user input
        state.janai.create_vector_store(name=user_input)
        st.success(f"Vector store '{user_input}' created successfully!")
        refresh_vector_stores(state)
        
if __name__ == '__main__':
    main()