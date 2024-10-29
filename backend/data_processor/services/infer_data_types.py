import pandas as pd
import numpy as np
from pandas.api.types import is_datetime64_any_dtype
from dateutil.parser import parse
import time


def is_date(string):
    try:
        parse(str(string))
        return True
    except (ValueError, TypeError):
        return False

def is_numeric_with_na(series):
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
    if series.dtype in ['int64', 'int32', 'Int64']:
        non_na_values = series.dropna().unique()
        return set(non_na_values).issubset({0, 1})
    
    if series.dtype == 'object':
        bool_values = {'true', 'false', 't', 'f', 'yes', 'no', 'y', 'n', '1', '0'}
        non_na_values = series.dropna().astype(str).str.lower().unique()
        return set(non_na_values).issubset(bool_values)
    
    return False

def is_categorical(series, threshold=0.5):
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
    result_df = df.copy()
    
    for col in df.columns:
        if result_df[col].dtype == 'object':
            result_df[col] = result_df[col].astype(str)
        
        result_df[col] = infer_column_type(result_df[col])
    
    return result_df

def test_inference(data, name):

    print(f"\nTesting {name}:")
    
    df_start_time = time.time()
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
    df_creation_time = time.time() - df_start_time
    
    print("Original types:")
    print(df.dtypes)
    
    # Start timing for type inference
    inference_start_time = time.time()
    df = infer_and_convert_data_types(df)
    inference_time = time.time() - inference_start_time
    
    print("\nInferred types:")
    print(df.dtypes)
    print("\nSample data:")
    print(df.head())
    
    # Print timing information
    print("\nPerformance Metrics:")
    print(f"DataFrame Creation Time: {df_creation_time:.4f} seconds")
    print(f"Type Inference Time: {inference_time:.4f} seconds")
    print(f"Total Processing Time: {(df_creation_time + inference_time):.4f} seconds")
    print(f"Number of Rows: {len(df)}")
    print(f"Number of Columns: {len(df.columns)}")
    print("-" * 50)
    print("\n----------------------------------------\n")


def create_complex_large_dataset(size=100000):
    np.random.seed(42)  
    
    dates = pd.date_range(start='1/1/2000', periods=size, freq='h')
    
    first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    
    complex_large_data = {
        'Timestamp': dates,
        
        'AltDate': dates.strftime('%Y-%m-%d'),
        
        'FullName': [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(size)],
        'ID': np.random.permutation(size * 2)[:size],
        'Value1': np.random.normal(100, 15, size),
        'Value2': np.random.exponential(50, size),
        'Periodic': np.sin(np.linspace(0, 100*np.pi, size)) * 100 + np.random.normal(0, 5, size),
        'MixedNumeric': [str(np.random.random() * 100) if np.random.random() > 0.01 
                        else np.random.choice(['N/A', 'Error', 'Not Available']) for _ in range(size)],
        'Status': [np.random.choice(['True', 'False', '1', '0', 'Yes', 'No', 'T', 'F']) for _ in range(size)],
        'Category': np.random.choice(['A', 'B', 'C', 'D', 'E'], size, p=[0.4, 0.3, 0.15, 0.1, 0.05]),
        'Subcategory': [f"{cat}{np.random.randint(1, 4)}" for cat in np.random.choice(['X', 'Y', 'Z'], size)],
        'SparseNumeric': [np.random.random() * 1000 if np.random.random() > 0.7 else 'Not Available' for _ in range(size)],
        'Code': [f"PRD-{np.random.randint(100, 999)}-{np.random.choice(['A', 'B', 'C'])}" for _ in range(size)],
        'Milliseconds': (dates - pd.Timestamp("1970-01-01")).total_seconds() * 1000,
    }
    
    return complex_large_data

if __name__ == "__main__":
    # Test case 1: Original sample data
    sample_data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Birthdate': ['1/01/1990', '2/02/1991', '3/03/1992', '4/04/1993', '5/05/1994'],
        'Score': [90, 75, 85, 70, 'Not Available'],
        'Grade': ['A', 'B', 'A', 'B', 'A']
    }
    test_inference(sample_data, "Sample Data")

    # Test case 2: Mixed numeric and string data
    mixed_data = {
        'Column1': [1, 2, '3', '4', 'five'],
        'Column2': ['1.1', '2.2', 3.3, '4.4', 5.5]
    }
    test_inference(mixed_data, "Mixed Numeric and String Data")

    # Test case 3: Various date formats
    date_data = {
        'Date1': ['2021-01-01', '2021-02-02', '2021-03-03'],
        'Date2': ['01/01/2021', '02/02/2021', '03/03/2021'],
        'Date3': ['Jan 1, 2021', 'Feb 2, 2021', 'Mar 3, 2021']
    }
    test_inference(date_data, "Various Date Formats")

    # Test case 4: Boolean data
    boolean_data = {
        'Bool1': ['True', 'False', 'True'],
        'Bool2': ['Yes', 'No', 'Yes'],
        'Bool3': [1, 0, 1]
    }
    test_inference(boolean_data, "Boolean Data")

    # Test case 5: Categorical data
    categorical_data = {
        'Category': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A'] * 10
    }
    test_inference(categorical_data, "Categorical Data")

    # Test case 6: Large dataset simulation
    np.random.seed(0)
    large_data = {
        'Numeric': np.random.rand(10000),
        'Integer': np.random.randint(0, 100, 10000),
        'Date': pd.date_range(start='1/1/2020', periods=10000),
        'Category': np.random.choice(['A', 'B', 'C', 'D'], 10000),
        'Boolean': np.random.choice([True, False], 10000),
        'Mixed': np.random.choice(['1', '2', 'three', '4', 'five'], 10000)
    }

    test_inference(large_data, "Large Dataset")

    file_path = 'C:/Users/Machine/Downloads/sample_data.csv'
    df = pd.read_csv(file_path)
    test_inference(df, "Sample Data from CSV")


    same_file_as_excel = 'C:/Users/Machine/Downloads/sample_data.xlsx'
    df = pd.read_excel(same_file_as_excel)
    test_inference(df, "Sample Data from Excel")

    
    print("\nGenerating very large complex dataset...")
    complex_large_data = create_complex_large_dataset(100000)
    print("Testing very large complex dataset...")
    test_inference(complex_large_data, "Very Large Complex Dataset")