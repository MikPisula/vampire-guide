import pandas as pd
import argparse
from tqdm import tqdm
import os
import numpy as np

def main(input_file, height):
    # Load the CSV file
    df = pd.read_csv(input_file)

    # Display initial number of rows
    initial_count = len(df)
    tqdm.write(f"Initial number of rows: {initial_count}")

    # Define a function to check if the 'geometry' column is valid
    def is_valid_geometry(geometry: str):
        vertices = geometry.split(',')
        return len(vertices) >= 3 # If it's a triangle or higher it's ok

    # Apply the functions to filter rows
    tqdm.pandas(desc="Processing rows for geometry validity")
    df['is_valid'] = df['geometry'].progress_apply(is_valid_geometry)

    # Filter the DataFrame
    df_valid = df[df['is_valid']].drop(columns=['is_valid'])

    # If height is invalid (like nan) set it to constant
    df_valid['height'] = df_valid['height'].fillna(height)

    # Display number of rows removed
    final_count = len(df_valid)
    removed_count = initial_count - final_count
    tqdm.write(f"Number of rows removed: {removed_count}")

    # Create output file name
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_clean{ext}"

    # Save the resulting DataFrame to a new CSV file
    df_valid.to_csv(output_file, index=False)
    tqdm.write(f"Processed file saved as: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a CSV file by removing rows with empty or invalid 'geometry' values.")
    parser.add_argument("input_file", type=str, help="Path to the input CSV file.")
    parser.add_argument("height", type=float, help="Height of the invalid buildings in meters.", default=8.0)
    args = parser.parse_args()
    main(args.input_file, args.height)
