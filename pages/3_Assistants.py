import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from janai import JanAI
from datetime import datetime, timezone

def display_assistants():
    # Convert each assistant to a dict and filter for specific columns
    assistants_data = [{
        'id': assistant.id,  # Use dot notation to access attributes
        'created_at': datetime.fromtimestamp(assistant.created_at, timezone.utc).strftime('%d/%m/%y %H:%M'),  # Convert timestamp to DDMMYY using timezone-aware datetime
        'instructions': assistant.instructions,
        'name': assistant.name
    } for assistant in st.session_state.assistants]
    
    df = pd.DataFrame(assistants_data)
    gb = GridOptionsBuilder.from_dataframe(df)
    grid_options = gb.build()
    grid_options['rowSelection'] = 'multiple'

    # Calculate dynamic height
    base_height_per_row = 30  # Example height per row in pixels
    header_height = 60  # Approximate height for headers and padding
    dynamic_height = min(max(len(df) * base_height_per_row + header_height, 100), 600)  # Set min and max height

    grid_response = AgGrid(df, gridOptions=grid_options, height=dynamic_height, width='100%', update_mode='MODEL_CHANGED', fit_columns_on_grid_load=True)
    return grid_response

def refresh_assistants():
    st.session_state.assistants = st.session_state.janai.list_assistants(order='asc', limit=100)
    # Explicitly trigger a rerender of the grid by toggling the update_grid state
    st.session_state.update_grid = not st.session_state.update_grid
    # Force Streamlit to rerender the page, which includes the grid
    st.rerun()
    

def main():
    if 'janai' not in st.session_state:
        st.session_state.janai = JanAI()
    if 'assistants' not in st.session_state:
        st.session_state.assistants = st.session_state.janai.list_assistants(order='asc', limit=100)
    if 'update_grid' not in st.session_state:
        st.session_state.update_grid = True  # Initialize the trigger for updating the grid

    # Split the screen into two columns
    col1, col2 = st.columns([4, 6])
    
    with col1:
        # Store grid response in session state
        st.write("## List of Assistants")
        st.session_state.grid_response = display_assistants()

        num_assistants = len(st.session_state.assistants)
        st.write(f"Number of assistants: {num_assistants}")

        if st.button('Delete Selected'):
            # Access grid_response from session state
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
    # Check if any row is selected
        if 'selected_rows' in st.session_state.grid_response and st.session_state.grid_response['selected_rows'] is not None:
            selected_rows = st.session_state.grid_response['selected_rows']
            if not selected_rows.empty:
                # Assuming only one row can be selected for displaying details
                selected_row = selected_rows.iloc[0]
                # Display the details of the selected assistant
                st.write("## Assistant Details")
                st.table(selected_row)

if __name__ == '__main__':
    main()
    
    
    
