# from pathlib import Path
# import pandas as pd
# import os
#
#
# def clean_year(year_str):
#     """Clean year values that might have 's' prefix or other issues"""
#     if isinstance(year_str, str):
#         # Remove 's' prefix if present
#         year_str = year_str.replace('s', '')
#         # Handle cases where year might have additional characters
#         year_str = ''.join(c for c in year_str if c.isdigit())
#         # Return None if we can't extract a valid year
#         return int(year_str) if year_str else None
#     return int(year_str) if pd.notnull(year_str) else None
#
#
# def load_and_process_data():
#     """Load and process vehicle data from multiple year files"""
#     try:
#         data_dir = Path(__file__).parent.parent / 'data'
#
#         if not data_dir.exists():
#             raise FileNotFoundError(f"Data directory not found: {data_dir}")
#
#         vehicle_files = [
#             f for f in os.listdir(data_dir)
#             if f.startswith("vehicle") and f.endswith(".csv")
#         ]
#
#         if not vehicle_files:
#             raise FileNotFoundError("No vehicle data files found in data directory")
#
#         combined_data = []
#         for file_name in vehicle_files:
#             # Extract year from filename (more reliable than file contents)
#             year_from_filename = file_name[7:11]  # From 'vehicleYYYY.csv'
#             try:
#                 year_from_filename = int(year_from_filename)
#             except ValueError:
#                 year_from_filename = None
#
#             file_path = data_dir / file_name
#
#             df = pd.read_csv(file_path, low_memory=False)
#             if df.empty:
#                 continue
#
#             # Clean and standardize fuel names
#             df['Fuel'] = df['Fuel'].str.strip().str.replace('-', ' ').str.title()
#
#             # Clean year values from data
#             if 'year' in df.columns:
#                 df['year'] = df['year'].apply(clean_year)
#                 # Use filename year if year column is invalid
#                 if df['year'].isnull().all():
#                     df['year'] = year_from_filename
#             else:
#                 df['year'] = year_from_filename
#
#             # Drop rows with invalid years
#             df = df[df['year'].notnull()]
#
#             if df.empty:
#                 continue
#
#             # Group and sum vehicles by fuel type
#             yearly_data = df.groupby('Fuel', as_index=False)['Vehicles'].sum()
#             yearly_data['year'] = df['year'].iloc[0]  # Use first valid year
#             combined_data.append(yearly_data)
#
#         if not combined_data:
#             raise ValueError("All data files were empty or had invalid data")
#
#         final_df = pd.concat(combined_data, ignore_index=True)
#
#         # Additional cleaning for known fuel types
#         fuel_mapping = {
#             'Diesel And Diesel Hybrid': 'Diesel Hybrid',
#             'Hybrid Gasoline': 'Gasoline Hybrid',
#             'Plug In Hybrid': 'Plug-in Hybrid',
#             'Battery Electric': 'Electric',
#             'Flex Fuel': 'Flex-Fuel'
#         }
#         final_df['Fuel'] = final_df['Fuel'].replace(fuel_mapping)
#
#         # Ensure year is integer
#         final_df['year'] = final_df['year'].astype(int)
#
#         return final_df.sort_values(['year', 'Fuel'])
#
#     except Exception as e:
#         print(f"Error loading data: {str(e)}")
#         return pd.DataFrame(columns=['Fuel', 'Vehicles', 'year'])

from pathlib import Path
import pandas as pd
import os
from datetime import datetime


def clean_year(year_str):
    """Clean year values that might have 's' prefix or other issues"""
    if isinstance(year_str, str):
        year_str = year_str.replace('s', '')
        year_str = ''.join(c for c in year_str if c.isdigit())
        return int(year_str) if year_str else None
    return int(year_str) if pd.notnull(year_str) else None


def load_pm25_data():
    """Load and process PM2.5 data from multiple year files"""
    data_dir = Path(__file__).parent.parent / 'data'
    pm25_files = [f for f in os.listdir(data_dir) if f.startswith('pm2.5-') and f.endswith('.csv')]

    pm25_dfs = []
    for file_name in pm25_files:
        try:
            year = int(file_name.split('-')[1].split('.')[0])
            df = pd.read_csv(data_dir / file_name)

            # Standardize column names
            df.columns = [col.strip() for col in df.columns]

            # Convert date and extract year/month
            df['Date'] = pd.to_datetime(df['Date'])
            df['year'] = df['Date'].dt.year
            df['month'] = df['Date'].dt.month

            # Filter for correct year (in case file contains multiple years)
            df = df[df['year'] == year]

            if not df.empty:
                pm25_dfs.append(df)
        except Exception as e:
            print(f"Error loading {file_name}: {str(e)}")

    return pd.concat(pm25_dfs, ignore_index=True) if pm25_dfs else pd.DataFrame()


def load_and_process_data():
    """Load and process both vehicle and PM2.5 data"""
    # Load vehicle data (existing implementation)
    vehicle_df = load_vehicle_data()

    # Load PM2.5 data
    pm25_df = load_pm25_data()

    # Aggregate PM2.5 data by year (for merging with vehicle data)
    pm25_annual = pm25_df.groupby('year')['Daily Mean PM2.5 Concentration'].mean().reset_index()
    pm25_annual.rename(columns={'Daily Mean PM2.5 Concentration': 'Avg PM2.5'}, inplace=True)

    # Aggregate electric vehicles by year
    electric_vehicles = vehicle_df[vehicle_df['Fuel'].str.contains('Electric', case=False)]
    ev_annual = electric_vehicles.groupby('year')['Vehicles'].sum().reset_index()

    # Merge the datasets
    combined_df = pd.merge(ev_annual, pm25_annual, on='year', how='outer').sort_values('year')

    return {
        'vehicle_data': vehicle_df,
        'pm25_data': pm25_df,
        'combined_data': combined_df
    }


def load_vehicle_data():
    """Original vehicle data loading function"""
    try:
        data_dir = Path(__file__).parent.parent / 'data'
        vehicle_files = [f for f in os.listdir(data_dir) if f.startswith("vehicle") and f.endswith(".csv")]

        combined_data = []
        for file_name in vehicle_files:
            year_from_filename = file_name[7:11]
            try:
                year_from_filename = int(year_from_filename)
            except ValueError:
                year_from_filename = None

            file_path = data_dir / file_name
            df = pd.read_csv(file_path, low_memory=False)

            if df.empty:
                continue

            df['Fuel'] = df['Fuel'].str.strip().str.replace('-', ' ').str.title()

            if 'year' in df.columns:
                df['year'] = df['year'].apply(clean_year)
                if df['year'].isnull().all():
                    df['year'] = year_from_filename
            else:
                df['year'] = year_from_filename

            df = df[df['year'].notnull()]

            if df.empty:
                continue

            yearly_data = df.groupby('Fuel', as_index=False)['Vehicles'].sum()
            yearly_data['year'] = df['year'].iloc[0]
            combined_data.append(yearly_data)

        if not combined_data:
            raise ValueError("No valid vehicle data found")

        final_df = pd.concat(combined_data, ignore_index=True)

        fuel_mapping = {
            'Diesel And Diesel Hybrid': 'Diesel Hybrid',
            'Hybrid Gasoline': 'Gasoline Hybrid',
            'Plug In Hybrid': 'Plug-in Hybrid',
            'Battery Electric': 'Electric',
            'Flex Fuel': 'Flex-Fuel'
        }
        final_df['Fuel'] = final_df['Fuel'].replace(fuel_mapping)
        final_df['year'] = final_df['year'].astype(int)

        return final_df.sort_values(['year', 'Fuel'])

    except Exception as e:
        print(f"Error loading vehicle data: {str(e)}")
        return pd.DataFrame(columns=['Fuel', 'Vehicles', 'year'])