import pandas as pd
import os
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def get_canada_df():
    """
    Reads Canadian baby name Excel files (1980-2020 and 2024) and combine them.
    Renames columns, convert gender labels (Boy/Girl → M/F), adds a 'country' column
    Returns:
        pd.DataFrame: Columns include name (str), year (int), gender ('M'/'F'), count (int), and country ('CA').
    """
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    ca1 = pd.read_excel(os.path.join(RAW_DATA_DIR, "baby-names-frequency_1980_2020.xlsx"), engine="openpyxl", skiprows=1)
    ca2 = pd.read_excel(os.path.join(RAW_DATA_DIR, "baby-names-frequency_2024.xlsx"), engine="openpyxl", skiprows=1)

    drop_column = ["Ranking by Gender & Year", "Gender"]
    ca1 = ca1.drop(drop_column, axis=1)
    ca2 = ca2.drop(drop_column, axis=1)
    
    # Combine and filter necessary columns
    ca_df = pd.concat([ca1, ca2], ignore_index=True)
    ca_df["First Name"] = ca_df["First Name"].str.strip().str.capitalize()

    ca_df = ca_df.rename(columns={
        "First Name": "name",
        "Frequency": "count",
        "Year": "year"
    })

    # This is necessary because the raw Excel files contain multiple rows with the same name and year
    ca_df = ca_df.groupby(['name', 'year'], as_index=False)['count'].sum()
    # We don't need baby name data between 1980 - 1986
    ca_df = ca_df[ca_df["year"].between(1987, 2024)]
    return ca_df


def main():
    filename = "baby_names_by_year.csv"
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    ca_df = get_canada_df()
    ca_df.to_csv(os.path.join(PROCESSED_DATA_DIR, filename))
    print(f"{filename} with {ca_df.shape[0]} rows has been saved in '{PROCESSED_DATA_DIR}'")

if __name__ == '__main__':
    main()