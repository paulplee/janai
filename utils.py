import hashlib
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
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