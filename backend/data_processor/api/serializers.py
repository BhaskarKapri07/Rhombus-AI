"""
Serializers for data processing API.

This module defines the serializers for data type inference responses
and data type updates. It handles serialization of pandas data types
and preview data for API responses.
"""

from rest_framework import serializers

class DataTypeInfoSerializer(serializers.Serializer):
    """
    Serializer for data type information of each column.

    Fields:
        inferred_type (str): The pandas data type inferred for the column
        display_type (str): User-friendly name of the data type
        possible_types (list): List of available data types for conversion
    """
    inferred_type = serializers.CharField()
    display_type = serializers.CharField()
    possible_types = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )


class FileProcessResponseSerializer(serializers.Serializer):
    """
    Serializer for file processing response.

    Fields:
        columns (dict): Dictionary mapping column names to their data type information
        preview_data (list): List of dictionaries containing sample rows from the data
    
    Example Response:
        {
            "columns": {
                "name": {
                    "inferred_type": "object",
                    "display_type": "Text",
                    "possible_types": [
                        {"value": "object", "label": "Text"},
                        {"value": "Int64", "label": "Integer"},
                        ...
                    ]
                },
                ...
            },
            "preview_data": [
                {"name": "John", "age": 25, ...},
                {"name": "Jane", "age": 30, ...},
                ...
            ]
        }
    """
    columns = serializers.DictField(
        child=DataTypeInfoSerializer()
    )
    preview_data = serializers.ListField(
        child=serializers.DictField(
            child=serializers.JSONField()
        )
    )
    
    def validate_preview_data(self, value):
        """
        Validate preview data to ensure it's not empty and has consistent structure.

        Args:
            value (list): List of dictionaries containing preview data

        Returns:
            list: Validated preview data

        Raises:
            serializers.ValidationError: If data is empty or inconsistent
        """
        if not value:
            raise serializers.ValidationError("Preview data cannot be empty")
        
        # Check if all rows have the same columns
        columns = set(value[0].keys())
        for row in value[1:]:
            if set(row.keys()) != columns:
                raise serializers.ValidationError("Inconsistent columns in preview data")
        
        return value

    def validate_columns(self, value):
        """
        Validate column information.

        Args:
            value (dict): Dictionary of column information

        Returns:
            dict: Validated column information

        Raises:
            serializers.ValidationError: If column information is invalid
        """
        if not value:
            raise serializers.ValidationError("Column information cannot be empty")
        
        valid_types = {
            'Int64', 'float64', 'datetime64[ns]', 
            'bool', 'category', 'object'
        }
        
        for column_info in value.values():
            inferred_type = column_info.get('inferred_type')
            if inferred_type and inferred_type not in valid_types:
                raise serializers.ValidationError(
                    f"Invalid data type: {inferred_type}. "
                    f"Must be one of: {', '.join(valid_types)}"
                )
        
        return value
