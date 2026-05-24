import pandas as pd

file_path = r"D:\data ana\M.Sc_thesis_non-thesis_final_data_sheet.xlsx"
df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)

print("Last 15 rows:")
print(df.iloc[-15:].to_string())
