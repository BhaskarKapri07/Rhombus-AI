"""
Data type inference and conversion module.

This module provides functionality to automatically infer and convert data types
in pandas DataFrames. It handles various data types including:
- Numeric (Int64, float64)
- DateTime
- Boolean
- Categorical
- Text (object)

The module includes special handling for:
- Null values
- Mixed data types
- Non-standard date formats
"""


import pandas as pd
import numpy as np
from pandas.api.types import is_datetime64_any_dtype
from dateutil.parser import parse
import time


def is_date(string):
    """
    Check if a string can be parsed as a date.

    Args:
        string: Value to check for date format

    Returns:
        bool: True if string can be parsed as date, False otherwise
    """
    try:
        parse(str(string))
        return True
    except (ValueError, TypeError):
        return False

def is_numeric_with_na(series):
    """
    Check if a series is numeric, allowing for 'Not Available' or similar strings.
    
    Args:
        series (pd.Series): Input series to check

    Returns:
        tuple: (bool, pd.Series) indicating if numeric and converted series
    """
    na_values = ['Not Available', 'NA', 'N/A', 'not available', 'n/a', '', ' ', '-']
    temp_series = series.copy()
    
    temp_series = temp_series.astype(str)
    
    na_mask = temp_series.str.strip().isin(na_values)
    
    numeric_mask = ~na_mask
    numeric_series = pd.Series(index=series.index, dtype='float64')
    
    try:
        numeric_series[numeric_mask] = pd.to_numeric(temp_series[numeric_mask], errors='raise')
        numeric_series[na_mask] = pd.NA
        
        non_na_mask = numeric_series.notna()
        if non_na_mask.any() and (numeric_series[non_na_mask] % 1 == 0).all():
            return True, pd.Series(numeric_series, dtype='Int64')  
        return True, numeric_series
    except (ValueError, TypeError):
        return False, series

def is_boolean(series):
    """
    Check if a series contains boolean data.

    Args:
        series (pd.Series): Input series to check

    Returns:
        bool: True if series contains boolean data, False otherwise
    """
    if series.dtype in ['int64', 'int32', 'Int64']:
        non_na_values = series.dropna().unique()
        return set(non_na_values).issubset({0, 1})
    
    if series.dtype == 'object':
        bool_values = {'true', 'false', 't', 'f', 'yes', 'no', 'y', 'n', '1', '0'}
        non_na_values = series.dropna().astype(str).str.lower().unique()
        return set(non_na_values).issubset(bool_values)
    
    return False

def is_categorical(series, threshold=0.5):
    """
    Check if a series should be treated as categorical data.

    Args:
        series (pd.Series): Input series to check
        threshold (float): Maximum ratio of unique values to total values

    Returns:
        bool: True if series should be categorical, False otherwise
    """
    if isinstance(series.dtype, pd.CategoricalDtype):
        return True
        
    if series.dtype == 'object':
        non_na_values = series.dropna().unique()
        if len(non_na_values) <= 10 and all(len(str(x)) == 1 for x in non_na_values):
            return True
            
    n_unique = len(series.dropna().unique())
    n_total = len(series.dropna())
    return n_total > 0 and (n_unique / n_total) < threshold and n_total >= 10

def convert_to_boolean(series):
    """
    Convert a series to boolean type.

    Args:
        series (pd.Series): Input series to convert

    Returns:
        pd.Series: Converted boolean series
    """
    bool_map = {
        'true': True, 'false': False,
        't': True, 'f': False,
        'yes': True, 'no': False,
        'y': True, 'n': False,
        '1': True, '0': False,
        1: True, 0: False,
        1.0: True, 0.0: False
    }
    
    if series.dtype in ['int64', 'int32', 'Int64', 'float64']:
        return series.map({1: True, 0: False}).astype('boolean')
    
    return series.map(lambda x: bool_map.get(str(x).lower()) if pd.notna(x) else None).astype('boolean')

def infer_column_type(series):
    """
    Infer and convert the data type of a given series.
    
    Args:
        series (pd.Series): Input series to convert

    Returns:
        pd.Series: Series with inferred data type
    """
    if series.dtype == 'object':
        series = series.str.strip()

    if is_datetime64_any_dtype(series.dtype):
        return series
    
    if series.dtype == 'bool':
        return series

    if is_boolean(series):
        return convert_to_boolean(series)

    is_numeric, numeric_series = is_numeric_with_na(series)
    if is_numeric:
        return numeric_series

    if series.dtype == 'object' and all(is_date(x) for x in series.dropna()):
        try:
            return pd.to_datetime(series, format='mixed', dayfirst=False)
        except ValueError:
            return pd.to_datetime(series)

    if is_categorical(series):
        return pd.Categorical(series)

    return series


def infer_and_convert_data_types(df):
    """
    Infer and convert data types for each column in the DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: DataFrame with inferred and converted data types
    """
    result_df = df.copy()
    
    for col in df.columns:
        if result_df[col].dtype == 'object':
            result_df[col] = result_df[col].astype(str)
        
        result_df[col] = infer_column_type(result_df[col])
    
    return result_df
