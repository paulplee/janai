import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from janai import JanAI
from datetime import datetime, timezone

def display_assistants():
    assistants_data = [{
        'id': assistant.id,
        'created_at': datetime.fromtimestamp(assistant.created_at, timezone.utc).strftime('%d/%m/%y %H:%M'),
        'instructions': assistant.instructions,
        'name': assistant.name
    } for assistant in st.session_state.assistants]
    
    df = pd.DataFrame(assistants_data)
    gb = GridOptionsBuilder.from_dataframe(df)
    grid_options = gb.build()
    grid_options['rowSelection'] = 'multiple'

    base_height_per_row = 30
    header_height = 60
    dynamic_height = min(max(len(df) * base_height_per_row + header_height, 100), 600)

    # Use the grid_key from session state to force rerendering when needed
    grid_response = AgGrid(df, gridOptions=grid_options, height=dynamic_height, width='100%', update_mode='MODEL_CHANGED', fit_columns_on_grid_load=True, key=st.session_state.grid_key)
    return grid_response

def refresh_assistants():
    st.session_state.assistants = st.session_state.janai.list_assistants(order='asc', limit=100)
    st.session_state.update_grid = not st.session_state.update_grid
    st.rerun()

def main():
    if 'janai' not in st.session_state:
        st.session_state.janai = JanAI()
    if 'assistants' not in st.session_state:
        st.session_state.assistants = st.session_state.janai.list_assistants(order='asc', limit=100)
    if 'update_grid' not in st.session_state:
        st.session_state.update_grid = True
    if 'grid_key' not in st.session_state:  # Initialize grid_key in session state
        st.session_state.grid_key = "grid"

    col1, col2 = st.columns([35, 65])
    
    with col1:
        st.write("## List of Assistants")
        st.session_state.grid_response = display_assistants()

        num_assistants = len(st.session_state.assistants)
        st.write(f"Number of assistants: {num_assistants}")

        if st.button('Create'):
            # Update the grid_key to force the grid to rerender without selections
            st.session_state.grid_key = "grid" + str(datetime.now())
            st.session_state.creation_mode = True

        if st.button('Delete Selected'):
            if 'selected_rows' in st.session_state.grid_response and st.session_state.grid_response['selected_rows'] is not None:
                selected_rows = st.session_state.grid_response['selected_rows']
                if not selected_rows.empty:
                    deleted_ids = [row['id'] for index, row in selected_rows.iterrows() if 'id' in row]
                    for row_id in deleted_ids:
                        st.session_state.janai.delete_assistant(row_id)
                    st.write("Deleted Vector Store IDs:", deleted_ids)
                    refresh_assistants()
                else:
                    st.write("No rows selected for deletion.")

    with col2:
        if 'creation_mode' in st.session_state and st.session_state.creation_mode:
            st.write("CREATING ASSISTANT")
            st.session_state.creation_mode = False
        else:
            if 'selected_rows' in st.session_state.grid_response and st.session_state.grid_response['selected_rows'] is not None:
                selected_rows = st.session_state.grid_response['selected_rows']
                if not selected_rows.empty:
                    selected_row = selected_rows.iloc[0]
                    assistant_id = selected_row['id']
                    
                    matching_assistant = next((assistant for assistant in st.session_state.assistants if assistant.id == assistant_id), None)
                    
                    if matching_assistant:
                        st.write("## Assistant Details")
                        st.write(f"ID: {matching_assistant.id}")
                        st.write(f"Object: {matching_assistant.object}")
                        st.write(f"Created At: {matching_assistant.created_at}")
                        st.write(f"Name: {matching_assistant.name}")
                        st.write(f"Description: {matching_assistant.description}")
                        st.write(f"Model: {matching_assistant.model}")
                        st.write(f"Instructions: {matching_assistant.instructions}")
                        st.write(f"Tools: {matching_assistant.tools}")
                        st.write(f"Metadata: {matching_assistant.metadata}")
                        st.write(f"Top P: {matching_assistant.top_p}")
                        st.write(f"Temperature: {matching_assistant.temperature}")
                        st.write(f"Response Format: {matching_assistant.response_format}")

if __name__ == '__main__':
    main()