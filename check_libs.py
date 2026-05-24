import sys
try:
    import pandas as pd
    print("pandas imported successfully")
except Exception as e:
    print(f"pandas error: {e}")

try:
    import openpyxl
    print("openpyxl imported successfully")
except Exception as e:
    print(f"openpyxl error: {e}")

print(f"Python version: {sys.version}")
