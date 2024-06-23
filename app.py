import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from janai import JanAI

def display_vector_stores(df, grid_options):
    return AgGrid(df, gridOptions=grid_options, height=300, width='100%', update_mode='MODEL_CHANGED', fit_columns_on_grid_load=True)

def refresh_vector_stores(state):
    state.vector_stores.clear()
    state.vector_stores = state.janai.list_vector_stores()
    vs_list = [vector_store.to_dict() for vector_store in state.vector_stores]
    df = pd.DataFrame(vs_list)
    gb = GridOptionsBuilder.from_dataframe(df)
    grid_options = gb.build()
    grid_options['rowSelection'] = 'multiple'
    return display_vector_stores(df, grid_options)

def create_vector_store_action():
    user_input = st.session_state.user_input
    if user_input:
        st.session_state.janai.create_vector_store(name=user_input)
        st.success(f"Vector store '{user_input}' created successfully!")
        refresh_vector_stores(st.session_state)

def main():
    if 'janai' not in st.session_state:
        st.session_state.janai = JanAI()
    if 'vector_stores' not in st.session_state:
        st.session_state.vector_stores = st.session_state.janai.list_vector_stores()

    st.write("# JanAI")
    df = pd.DataFrame([vector_store.to_dict() for vector_store in st.session_state.vector_stores])
    st.write("## List of Vector Stores")
    gb = GridOptionsBuilder.from_dataframe(df)
    grid_options = gb.build()
    grid_options['rowSelection'] = 'multiple'
    grid_response = display_vector_stores(df, grid_options)

    if st.button('Delete Selected'):
        selected_rows = grid_response['selected_rows']
        if not selected_rows.empty:
            deleted_ids = [row['id'] for index, row in selected_rows.iterrows() if 'id' in row]
            for row_id in deleted_ids:
                st.session_state.janai.delete_vector_store(row_id)
            st.write("Deleted Vector Store IDs:", deleted_ids)
            refresh_vector_stores(st.session_state)
        else:
            st.write("No rows selected for deletion.")

    st.text_input("Enter a name for the new vector store:", key="user_input")
    st.button("Create Vector Store", on_click=create_vector_store_action)

if __name__ == '__main__':
    main()