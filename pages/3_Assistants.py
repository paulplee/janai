import streamlit as st
from datetime import datetime
from st_aggrid import AgGrid
from utils import JanAIUtils as utils

def main():
    st.set_page_config(layout="wide")

    utils.init_session_state()

    if 'grid_key' not in st.session_state:  # Initialize grid_key in session state
        st.session_state.grid_key = "grid"

    col1, col2 = st.columns([35, 65])
        
    with col1:
        st.write("## List of Assistants")
        st.session_state.grid_response = utils.display_assistants()
    
        num_assistants = len(st.session_state.assistants)
        st.write(f"Number of assistants: {num_assistants}")
    
        button_col1, button_col2, button_col3, empty_space = st.columns([1,1,1,1])
        with button_col1:
            if st.button('New'):
                # Update the grid_key to force the grid to rerender without selections
                st.session_state.grid_key = "grid" + str(datetime.now())
                st.session_state.creation_mode = True
    
        with button_col2:
            if st.button('Delete'):
                if 'selected_rows' in st.session_state.grid_response and st.session_state.grid_response['selected_rows'] is not None:
                    selected_rows = st.session_state.grid_response['selected_rows']
                    if not selected_rows.empty:
                        deleted_ids = [row['id'] for index, row in selected_rows.iterrows() if 'id' in row]
                        for row_id in deleted_ids:
                            st.session_state.janai.delete_assistant(row_id)
                        st.write("Deleted Vector Store IDs:", deleted_ids)
                        utils.refresh_assistants()
                    else:
                        st.write("No rows selected for deletion.")
                        
        with button_col3:
            if st.button('Reload'):
                st.session_state.assistants = st.session_state.janai.list_assistants(order='asc', limit=100)
                st.session_state.update_grid = True

    
    with col2:
        # Display the assistant ID or 'N/A' based on the selection or creation mode
        if 'creation_mode' in st.session_state and st.session_state.creation_mode:
            st.write("Assistant ID: N/A")
            utils.display_assistant_form()
        else:
            if 'selected_rows' in st.session_state.grid_response and st.session_state.grid_response['selected_rows'] is not None:
                selected_rows = st.session_state.grid_response['selected_rows']
                if not selected_rows.empty:
                    selected_row = selected_rows.iloc[0]
                    assistant_id = selected_row['id']
                    st.write(f"Assistant ID: {assistant_id}")  # Display the selected assistant's ID
                    matching_assistant = next((assistant for assistant in st.session_state.assistants if assistant.id == assistant_id), None)
                    if matching_assistant:
                        utils.display_assistant_form(matching_assistant)
                else:
                    st.write("Assistant ID: N/A")  # Display 'N/A' if no row is selected
            else:
                st.write("Assistant ID: N/A")  # Display 'N/A' if no row is selected

if __name__ == '__main__':
    main()