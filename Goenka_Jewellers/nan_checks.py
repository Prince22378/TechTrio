import pandas as pd

# Hardcoded path to your CSV file
csv_file_path = 'Final_limelight.csv'  # <-- Change this to your actual path

# Load the data into a DataFrame
df = pd.read_csv(csv_file_path)

# Identify columns with NaN values and count them
nan_counts = df.isna().sum()
nan_counts = nan_counts[nan_counts > 0]

print("Columns with NaN values and their counts:\n")
print(nan_counts)

# Get all rows that contain at least one NaN value
rows_with_nan = df[df.isna().any(axis=1)]

print("\nRows with at least one NaN value:\n")
print(rows_with_nan)
