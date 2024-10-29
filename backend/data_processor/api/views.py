from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import numpy as np
from ..services.infer_data_types import infer_and_convert_data_types
import os

class ProcessFileView(APIView):
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {'error': 'No file was uploaded.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_extension = os.path.splitext(file_obj.name)[1].lower()
        if file_extension not in ['.csv', '.xlsx', '.xls']:
            return Response(
                {'error': 'Unsupported file type. Please upload CSV or Excel files.'},
                status=status.HTTP_400_BAD_ERROR
            )

        try:
            if file_extension == '.csv':
                df = pd.read_csv(file_obj)
            else:
                df = pd.read_excel(file_obj)

            processed_df = infer_and_convert_data_types(df)

            column_types = {col: str(dtype) for col, dtype in processed_df.dtypes.items()}

            def serialize_value(val):
                if pd.isna(val) or pd.isnull(val):
                    return None
                if isinstance(val, (pd.Timestamp, np.datetime64)):
                    return val.isoformat()
                if isinstance(val, (np.int64, np.int32)):
                    return int(val)
                if isinstance(val, (np.float64, np.float32)):
                    if np.isinf(val) or np.isnan(val):
                        return None
                    return float(val)
                return str(val)

            preview_data = [
                {k: serialize_value(v) for k, v in row.items()}
                for row in processed_df.head().to_dict(orient='records')
            ]

            response_data = {
                'column_types': column_types,    
                'preview_data': preview_data     
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Error processing file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class UpdateTypesView(APIView):
    def serialize_value(self, val):
        """Serialize values to JSON-compatible format."""
        if pd.isna(val) or pd.isnull(val):
            return None
        if isinstance(val, (pd.Timestamp, np.datetime64)):
            return val.isoformat()
        if isinstance(val, (np.int64, np.int32)):
            return int(val)
        if isinstance(val, (np.float64, np.float32)):
            if np.isinf(val) or np.isnan(val):
                return None
            return float(val)
        return str(val)

    def post(self, request):
        try:
            data = request.data
            file_data = data.get('preview_data', [])
            new_types = data.get('column_types', {})

            if not file_data or not new_types:
                return Response(
                    {'error': 'Missing required data'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            df = pd.DataFrame(file_data)

            for column, new_type in new_types.items():
                try:
                    if new_type == 'datetime64[ns]':
                        df[column] = pd.to_datetime(df[column])
                    elif new_type == 'category':
                        df[column] = df[column].astype('category')
                    elif new_type == 'int64':
                        # Use nullable integer type instead
                        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
                    elif new_type == 'float64':
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                    elif new_type == 'bool':
                        df[column] = df[column].astype('boolean')
                    else:
                        df[column] = df[column].astype('object')
                except Exception as e:
                    return Response(
                        {
                            'error': f'Failed to convert column "{column}" to type {new_type}',
                            'details': str(e)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            response_data = {
                'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'preview_data': [
                    {col: self.serialize_value(val) for col, val in row.items()}
                    for row in df.to_dict(orient='records')
                ]
            }

            return Response(response_data)

        except Exception as e:
            return Response(
                {'error': f'Error processing type changes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )