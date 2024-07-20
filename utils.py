import hashlib
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from datetime import datetime, timezone
import constants as c
from janai import JanAI  # Assuming JanAI is defined and accessible

class JanAIUtils:
    @staticmethod
    def init_session_state():
        # Initialize session state variables if they don't exist
        if 'janai' not in st.session_state:
            st.session_state.janai = JanAI()
        if 'assistants' not in st.session_state:
            st.session_state.assistants = st.session_state.janai.list_assistants(order='asc', limit=100)
        if 'vector_stores' not in st.session_state:
            st.session_state.vector_stores = st.session_state.janai.list_vector_stores()
        if 'files' not in st.session_state:
            st.session_state.files = st.session_state.janai.list_files()
        if 'update_grid' not in st.session_state:
            st.session_state.update_grid = True
        if 'file_processed' not in st.session_state:
            st.session_state.file_processed = False
        if 'last_file_hash' not in st.session_state:
            st.session_state.last_file_hash = ''
        if 'grid_key' not in st.session_state:  # Initialize grid_key in session state
            st.session_state.grid_key = "grid"
        
    @staticmethod
    def convert(obj):
        """
        Converts an object's attributes to a dictionary for easy serialization or display.

        This method is particularly useful for converting complex objects, including those with nested objects,
        into a dictionary format. It first checks if the object has a custom `to_dict` method and uses it for conversion.
        If not, it falls back to using `vars()` for a direct conversion. This process is applied recursively for nested objects,
        ensuring a deep conversion.

        Parameters:
        - obj (object): The object to convert. This can be any Python object, potentially containing nested objects.

        Returns:
        - dict: A dictionary representation of the object. Attributes that cannot be converted retain their original form.

        Note:
        - Custom `to_dict` methods in nested objects are respected and used for conversion.
        - If an object or its attributes cannot be directly converted to a dictionary (e.g., simple data types like integers or strings),
          they are included in the dictionary as is.
        """
        if hasattr(obj, "to_dict"):
            # If the object has a custom `to_dict` method defined, it's used for conversion.
            # This allows for custom conversion logic specific to the object's class.
            return obj.to_dict()
        elif hasattr(obj, "__dict__"):
            # If the object does not have a `to_dict` method but can be directly converted using `vars()`,
            # which returns the `__dict__` attribute of the object (a dictionary of its attributes).
            result = {}
            for key, value in vars(obj).items():
                if hasattr(value, "to_dict"):
                    # For nested objects that have a `to_dict` method, use that method for conversion.
                    # This allows for deep conversion of nested objects.
                    result[key] = value.to_dict()
                elif hasattr(value, "__dict__"):
                    # For nested objects without a `to_dict` method, recursively call this convert method.
                    # This ensures that deeply nested objects can still be converted to a dictionary.
                    result[key] = JanAIUtils.convert(value)
                else:
                    # For attributes that are neither objects with a `to_dict` method nor objects that can be
                    # directly converted, assign their value directly in the result dictionary.
                    result[key] = value
            return result
        else:
            # If the object cannot be converted to a dictionary (e.g., it's a simple data type like an integer or string),
            # return the object itself.
            return obj

    @staticmethod
    def bytes_to_readable(bytes):
        """
        Converts a byte size into a human-readable string with the most appropriate unit.

        This method follows the binary prefix for units (powers of 1024), starting from bytes (B) up to petabytes (PB).
        It formats the size into a string with two decimal places, appending the appropriate unit. The conversion scales
        the size down by 1024 for each unit until the most suitable unit is found for representation.

        Parameters:
        - bytes (int, float): The size in bytes to convert. Should be a numeric value representing the size in bytes.

        Returns:
        - str: A string representing the size with the appropriate unit, formatted to two decimal places. If the size exceeds
               petabytes, it is still represented in petabytes, which is the upper limit of this method's conversion logic.

        Example:
        - `bytes_to_readable(2048)` would return `'2.00 KB'`, indicating the size is 2 kilobytes.
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if bytes < 1024.0:
                # If the size is smaller than the next unit (1024), return it formatted with the current unit.
                # This loop iterates through the units, scaling down the size each time until the appropriate unit is found.
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0  # Scale down the size by 1024 to convert to the next unit.
        # If the size exceeds petabytes, it's still formatted in petabytes.
        # This is the upper limit of this method's conversion logic.
        return f"{bytes:.2f} PB"
    
    def delete_all_resources():
        # Delete all assistants
        for assistant in st.session_state.assistants:
            st.session_state.janai.delete_assistant(assistant.id)
        st.write("All assistants deleted.")

        # Delete all vector stores
        for vector_store in st.session_state.vector_stores:
            st.session_state.janai.delete_vector_store(vector_store.id)
        st.write("All vector stores deleted.")

        # Delete all files
        for file in st.session_state.files:
            st.session_state.janai.delete_file(file.id)
        st.write("All files deleted.")

        # Refresh the lists in session state
        st.session_state.assistants = st.session_state.janai.list_assistants()
        st.session_state.vector_stores = st.session_state.janai.list_vector_stores()
        st.session_state.files = st.session_state.janai.list_files()
        st.session_state.update_grid = True
    
    def file_hash(file):
        """
        Calculates the SHA-256 hash of a file's contents.

        This function reads the entire content of a file, calculates its SHA-256 hash, and then returns the hexadecimal
        representation of this hash. It ensures the file's read pointer is reset to its original position after reading.

        Parameters:
        - file (file-like object): The file for which to calculate the hash. This should be an open file object.

        Returns:
        - str: The hexadecimal string representation of the SHA-256 hash of the file's contents.
        """
        file.seek(0)
        hash_obj = hashlib.sha256()
        hash_obj.update(file.read())
        file.seek(0)
        return hash_obj.hexdigest()

    def display_files():
        """
        Displays a list of files in a Streamlit app using the AgGrid component.

        This function converts a list of file metadata into a pandas DataFrame, then formats certain columns for better readability
        (e.g., converting byte sizes to a human-readable format and formatting timestamps). It uses the AgGrid component to display
        the DataFrame in a grid format, allowing for interactive sorting and selection. The grid's columns are configured for
        display properties and order.

        Returns:
        - Grid response object from AgGrid, containing information about the grid state, including selected rows.
        """
        files_converted = [JanAIUtils.convert(file) for file in st.session_state.files]
        for file in files_converted:
            # Convert 'created_at' to datetime and then format it
            if 'created_at' in file:
                # Ensure the datetime is timezone-aware in UTC
                utc_datetime = pd.to_datetime(file['created_at'], unit='s', utc=True)
                file['created_at'] = utc_datetime.strftime('%d/%m/%Y %H:%M') + " UTC"        # Convert 'bytes' to a human-readable format
            if 'bytes' in file:
                file['bytes'] = JanAIUtils.bytes_to_readable(file['bytes'])
        
        df = pd.DataFrame(files_converted)
        
        gb = GridOptionsBuilder.from_dataframe(df)
        # Hide all columns initially
        gb.configure_columns(df.columns, hide=True)
        # Specify the order and visibility of columns
        column_order = ['id', 'filename', 'bytes', 'created_at']
        for column in column_order:
            match column:
                case "id":
                    # Configure 'id' column
                    gb.configure_column("id", hide=False, width=c.COL_WIDTHS['id'])
                case "filename":
                    # Configure 'filename' column
                    gb.configure_column("name", hide=False, width=c.COL_WIDTHS['name'])
                case "bytes":
                    # Configure 'bytes' column with specific width
                    gb.configure_column("bytes", hide=False, width=c.COL_WIDTHS['bytes'])
                case "created_at":
                    # Configure 'created_at' column
                    gb.configure_column("created_at", hide=False, width=c.COL_WIDTHS['datetime'])
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
        base_height_per_row = 30
        header_height = 60
        dynamic_height = min(max(len(df) * base_height_per_row + header_height, 100), 600)
        # grid_response = AgGrid(df, gridOptions=grid_options, height=dynamic_height, width='100%', update_mode='MODEL_CHANGED', fit_columns_on_grid_load=True)
        grid_response = AgGrid(df, gridOptions=grid_options, height=dynamic_height, width='100%', update_mode='MODEL_CHANGED', fit_columns_on_grid_load=True)
        return grid_response


    def refresh_files():
        """
        Refreshes the list of files displayed in the Streamlit app.

        This function updates the global session state with a new list of files by calling a method to list files from an external
        source (e.g., a database or file storage system). It then triggers a rerun of the Streamlit app to reflect the updated file list.
        """
        st.session_state.files = st.session_state.janai.list_files()
        st.session_state.update_grid = not st.session_state.update_grid
        st.rerun()


    def display_vector_stores():
        vs_converted = [JanAIUtils.convert(vector_store) for vector_store in st.session_state.vector_stores]
        for vector_store in vs_converted:
            for key in ['created_at', 'last_active_at']:
                if key in vector_store:
                    # Ensure the datetime is timezone-aware in UTC
                    utc_datetime = pd.to_datetime(vector_store[key], unit='s', utc=True)
                    vector_store[key] = utc_datetime.strftime('%d/%m/%Y %H:%M') + " UTC"
                if 'bytes' in vector_store:
                    vector_store['bytes'] = JanAIUtils.bytes_to_readable(vector_store['bytes'])
        
        df = pd.DataFrame([JanAIUtils.convert(vector_store) for vector_store in st.session_state.vector_stores])
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
            JanAIUtils.refresh_vector_stores() 
            
            

    def display_assistant_form(assistant=None):
        # Initialize default values
        default_values = {
            "model": "",
            "name": "",
            "description": "",
            "instructions": "",
            "tools": "",
            "tools_array": "None",  # Assuming 'None' is a valid default option
            "tool_resources": "",
            "temperature": 1.0,
            "top_p": 2.0,
            "response_format": ""
        }
        
        tools_array = []

        # If an assistant is provided, use its properties for default values
        if assistant:
            # Convert each tool object to a dictionary with a 'type' key
            tools_array = [{"type": tool.type} for tool in assistant.tools] if assistant.tools else []

            default_values.update({
                "model": assistant.model,
                "name": assistant.name,
                "description": assistant.description,
                "instructions": assistant.instructions,
                # Ensure 'tools' is assigned correctly. If tools is expected to be a list of dictionaries, this line is correct.
                # If 'tools' should be the original objects or a different format, adjust accordingly.
                "tools": assistant.tools,
                "tools_array": tools_array, 
                "tool_resources": assistant.tools,  # Assuming this information needs to be fetched or is not available
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
        

        tools_array = default_values["tools_array"] if isinstance(default_values["tools_array"], list) else []
        
        # Replace the st.radio calls with st.checkbox for a more direct interaction
        file_search_selected = st.toggle("File search", value=any(tool["type"] == "file_search" for tool in tools_array))
        if file_search_selected:
            try:
                st.write(f"VS: {assistant.tool_resources.file_search.vector_store_ids}")
            except:
                pass

        code_interpreter_selected = st.toggle("Code interpreter", value=any(tool["type"] == "code_interpreter" for tool in tools_array))
        
        functions_selected = st.toggle("Function", value=any(tool["type"] == "function" for tool in tools_array))


        tool_resources = st.text_input("Tool Resources", value=default_values["tool_resources"])
        temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=default_values["temperature"], step=0.01)
        top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=default_values["top_p"], step=0.01)
        response_format = st.text_input("Response Format", value=default_values["response_format"])

        def generate_tools_array():
            tools_array = []
            if file_search_selected and code_interpreter_selected:
                tools_array = [{"type": "code_interpreter"}, {"type": "file_search"}]
            elif file_search_selected:
                tools_array = [{"type": "file_search"}]
            elif code_interpreter_selected:
                tools_array = [{"type": "code_interpreter"}]
            return tools_array


        if st.session_state.creation_mode:
            if st.button("Create Assistant"):
                st.session_state.janai.create_assistant(
                    model=model,
                    name=name,
                    description=description,
                    instructions=instructions,
                    tools=generate_tools_array(),
                    tool_resources=tool_resources,
                    temperature=temperature,
                    top_p=top_p,
                    response_format=response_format
                )
                st.session_state.creation_mode = False
                JanAIUtils.refresh_assistants()
        else:
            if st.button("Update Assistant"):
                tool_str = '';
                st.session_state.janai.update_assistant(
                    assistant_id=assistant.id,
                    model=model,
                    name=name,
                    description=description,
                    instructions=instructions,
                    tools=generate_tools_array(),
                    tool_resources=tool_resources,
                    temperature=temperature,
                    top_p=top_p,
                    response_format=response_format
                )
                JanAIUtils.refresh_assistants()
            
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
