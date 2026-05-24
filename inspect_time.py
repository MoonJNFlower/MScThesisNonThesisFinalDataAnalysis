import pandas as pd

file_path = r"D:\data ana\M.Sc_thesis_non-thesis_final_data_sheet.xlsx"
df = pd.read_excel(file_path, sheet_name='Sheet1', header=3)
df.columns = df.columns.str.strip()

print("Time Required value counts:")
print(df['Time Required'].value_counts(dropna=False).head(40))
