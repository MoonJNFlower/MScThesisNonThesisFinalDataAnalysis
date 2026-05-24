import pandas as pd

file_path = r"D:\data ana\M.Sc_thesis_non-thesis_final_data_sheet.xlsx"
df = pd.read_excel(file_path, sheet_name='Sheet1', header=3)
df.columns = df.columns.str.strip()

print("All unique Taxa involved and their counts:")
taxa_counts = df['Taxa involved'].value_counts(dropna=False)
for taxa, count in taxa_counts.items():
    print(f"  {repr(taxa)}: {count}")
