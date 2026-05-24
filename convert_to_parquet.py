import pandas as pd
import os
from analysis_core import load_data, DATA_FILE

def convert():
    excel_path = os.path.join(os.path.dirname(__file__), "M.Sc_thesis_non-thesis_final_data_sheet.xlsx")
    parquet_path = DATA_FILE # Ends in .parquet now
    
    if not os.path.exists(excel_path):
        print(f"Error: Could not find {excel_path}")
        return

    print("Reading and cleaning Excel data...")
    df_clean = load_data(excel_path)
    
    print(f"Saving to {parquet_path}...")
    df_clean.to_parquet(parquet_path, engine='pyarrow', index=False)
    print("Conversion complete! You can now commit the .parquet file to Git.")

if __name__ == "__main__":
    convert()