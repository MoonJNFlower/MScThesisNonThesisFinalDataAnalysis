import pandas as pd

file_path = r"D:\data ana\M.Sc_thesis_non-thesis_final_data_sheet.xlsx"
df = pd.read_excel(file_path, sheet_name='Sheet1', header=3)
df.columns = df.columns.str.strip()

print("Unique Research Types:")
print(df['Types of research'].value_counts(dropna=False))

print("\nUnique Years (sorted):")
print(sorted(df['Year'].dropna().unique().astype(str)))

print("\nUnique Fates:")
print(df['Fate'].value_counts(dropna=False))

print("\nTop 20 Taxa:")
print(df['Taxa involved'].value_counts(dropna=False).head(20))

print("\nTop 20 Districts:")
print(df['District'].value_counts(dropna=False).head(20))
