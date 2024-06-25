import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from janai import JanAI
from datetime import datetime, timezone

def display_form(assistant=None):
    # Initialize default values
    default_values = {
        "model": "",
        "name": "",
        "description": "",
        "instructions": "",
        "tools": "None",  # Assuming 'None' is a valid default option
        "tool_resources": "",
        "temperature": 1.0,
        "top_p": 1.0,
        "response_format": ""
    }

    # If an assistant is provided, use its properties for default values
    if assistant:
        default_values.update({
            "model": assistant.model,
            "name": assistant.name,
            "description": assistant.description,
            "instructions": assistant.instructions,
            "tools": assistant.tools,  # This might need additional processing if tools is not a string
            "tool_resources": "",  # Assuming this information needs to be fetched or is not available
            "temperature": assistant.temperature,
            "top_p": assistant.top_p,
            "response_format": assistant.response_format
        })

    tools_options = {
        "None": [],
        "code_interpreter": [{"type": "code_interpreter"}],
        "file_search": [{"type": "file_search"}],
        "function": [{"type": "function"}]
    }


    assistant_id = "N/A"  # Default value when in creation mode or no row is selected
    
    # Ensure default_values["model"] is valid
    if default_values["model"] not in ["gpt-4o", "gpt-3.5-turbo"]:
        default_values["model"] = "gpt-4o"  # Set to a valid default value

    model = st.selectbox(
        "Model", 
        ["gpt-4o", "gpt-3.5-turbo"], 
        index=["gpt-4o", "gpt-3.5-turbo"].index(default_values["model"])
    )
    name = st.text_input("Name", value=default_values["name"])
    description = st.text_input("Description", value=default_values["description"])
    instructions = st.text_area("Instructions", value=default_values["instructions"])
    
    # Check if default_values["tools"] is a list and convert to a valid key if necessary
    if isinstance(default_values["tools"], list):
        # Assuming the first item in the list is the desired default, or use a suitable default key
        default_tool = default_values["tools"][0] if default_values["tools"] else "None"
    else:
        default_tool = default_values["tools"]

    # Ensure default_tool is a valid key in tools_options
    if default_tool not in tools_options:
        default_tool = "None"  # Set to a valid default key

    tools = st.selectbox(
        "Tools",
        list(tools_options.keys()),
        index=list(tools_options.keys()).index(default_tool)  # Set default selection
    )
    tool_resources = st.text_input("Tool Resource", value=default_values["tool_resources"])
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=default_values["temperature"], step=0.01)
    top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=default_values["top_p"], step=0.01)
    response_format = st.text_input("Response Format", value=default_values["response_format"])

    if st.session_state.creation_mode:
        if st.button("Create Assistant"):
            st.session_state.janai.create_assistant(
                model=model,
                name=name,
                description=description,
                instructions=instructions,
                tools=tools,
                tool_resources=tool_resources,
                temperature=temperature,
                top_p=top_p,
                response_format=response_format
            )
            st.session_state.creation_mode = False
            refresh_assistants()
    else:
        if st.button("Update Assistant"):
            st.session_state.janai.update_assistant(
                assistant_id=assistant.id,
                model=model,
                name=name,
                description=description,
                instructions=instructions,
                tools=tools,
                tool_resources=tool_resources,
                temperature=temperature,
                top_p=top_p,
                response_format=response_format
            )
            refresh_assistants()
        
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
    
    # Check if 'selected_rows' is not None and then if any row is selected
    if grid_response.get('selected_rows') is not None and len(grid_response['selected_rows']) > 0:
        st.session_state.creation_mode = False       
        st.session_state.creation_mode = False        
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
            # Display the assistant ID or 'N/A' based on the selection or creation mode
            if 'creation_mode' in st.session_state and st.session_state.creation_mode:
                st.write("Assistant ID: N/A")
                display_form()
            else:
                if 'selected_rows' in st.session_state.grid_response and st.session_state.grid_response['selected_rows'] is not None:
                    selected_rows = st.session_state.grid_response['selected_rows']
                    if not selected_rows.empty:
                        selected_row = selected_rows.iloc[0]
                        assistant_id = selected_row['id']
                        st.write(f"Assistant ID: {assistant_id}")  # Display the selected assistant's ID
                        matching_assistant = next((assistant for assistant in st.session_state.assistants if assistant.id == assistant_id), None)
                        if matching_assistant:
                            display_form(matching_assistant)
                    else:
                        st.write("Assistant ID: N/A")  # Display 'N/A' if no row is selected
                else:
                    st.write("Assistant ID: N/A")  # Display 'N/A' if no row is selected

if __name__ == '__main__':
    main()