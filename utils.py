class OpenAIUtils:
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
                    result[key] = OpenAIUtils.convert(value)
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