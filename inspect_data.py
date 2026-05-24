import pandas as pd
import os

file_path = r"D:\data ana\M.Sc_thesis_non-thesis_final_data_sheet.xlsx"

print(f"Checking file existence: {os.path.exists(file_path)}")

# Read all sheets in the Excel file
excel_file = pd.ExcelFile(file_path)
print(f"Sheet names: {excel_file.sheet_names}")

for sheet_name in excel_file.sheet_names:
    print("\n" + "="*50)
    print(f"Sheet Name: {sheet_name}")
    print("="*50)
    
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"Shape: {df.shape} (rows, columns)")
    print("\nColumns and Data Types:")
    print(df.dtypes)
    print("\nMissing Values Summary:")
    print(df.isnull().sum())
    print("\nFirst 5 Rows:")
    print(df.head())
