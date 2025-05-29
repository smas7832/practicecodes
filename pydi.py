import pandas as pd

# Load the Excel file
file_path = "/mnt/data/KGN Menu.xlsx"

# Load all sheet names
xls = pd.ExcelFile(file_path)
sheet_names = xls.sheet_names  # List of sheet names

# Load data from the first sheet
df = pd.read_excel(xls, sheet_name=sheet_names[0])

# Display basic info about the file
sheet_names, df.head(), df.info()
