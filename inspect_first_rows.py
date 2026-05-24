import pandas as pd

file_path = r"D:\data ana\M.Sc_thesis_non-thesis_final_data_sheet.xlsx"
df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)

print("Rows 0 to 7:")
for i in range(8):
    print(f"Row {i}: {list(df.iloc[i])}")
