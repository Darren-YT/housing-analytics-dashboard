import pandas as pd
import requests

def fetch_and_clean_insurance_data():
    # Set API endpoint for data collection (2022 ACS 1-Year PUMS)
    url = "https://api.census.gov/data/2022/acs/acs1/pums?get=ST,INSP&for=state:*"
    print("Fetching 2022 Home Insurance data from Census API...")

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        # --- 1. Process and Save Raw Data ---
        df_raw = pd.DataFrame(data[1:], columns=data[0])
        raw_filename = "raw_home_insurance_2022.csv"
        df_raw.to_csv(raw_filename, index=False)
        print(f"📥 Raw data saved to: {raw_filename} (Total rows: {len(df_raw)})")
        
        # --- 2. Data Cleaning ---
        print("\nStarting data cleaning process and recording differences...")
        df_clean = df_raw.copy()
        
        # Correct data types (API returns strings by default, convert to numeric)
        df_clean['INSP'] = pd.to_numeric(df_clean['INSP'], errors='coerce')
        
        # Record invalid/missing values (Premium <= 0 means no insurance or N/A, plus any NaNs)
        invalid_count = df_clean[df_clean['INSP'] <= 0].shape[0] + df_clean['INSP'].isna().sum()
        
        # Handle missing/invalid values (Keep only samples with actual payments)
        df_clean = df_clean[df_clean['INSP'] > 0]
        
        # --- 3. Data Aggregation ---
        # Group by state and calculate the mean premium
        state_avg_insurance = df_clean.groupby('ST')['INSP'].mean().round(2).reset_index()
        state_avg_insurance.rename(columns={'INSP': 'Avg_Home_Insurance_2022'}, inplace=True)
        
        # --- 4. Standardize Identifiers ---
        # Map FIPS codes to State Names to match with teammates' datasets
        fips_to_state = {
            '01': 'Alabama', '02': 'Alaska', '04': 'Arizona', '05': 'Arkansas', '06': 'California',
            '08': 'Colorado', '09': 'Connecticut', '10': 'Delaware', '11': 'District of Columbia',
            '12': 'Florida', '13': 'Georgia', '15': 'Hawaii', '16': 'Idaho', '17': 'Illinois',
            '18': 'Indiana', '19': 'Iowa', '20': 'Kansas', '21': 'Kentucky', '22': 'Louisiana',
            '23': 'Maine', '24': 'Maryland', '25': 'Massachusetts', '26': 'Michigan', '27': 'Minnesota',
            '28': 'Mississippi', '29': 'Missouri', '30': 'Montana', '31': 'Nebraska', '32': 'Nevada',
            '33': 'New Hampshire', '34': 'New Jersey', '35': 'New Mexico', '36': 'New York',
            '37': 'North Carolina', '38': 'North Dakota', '39': 'Ohio', '40': 'Oklahoma', '41': 'Oregon',
            '42': 'Pennsylvania', '44': 'Rhode Island', '45': 'South Carolina', '46': 'South Dakota',
            '47': 'Tennessee', '48': 'Texas', '49': 'Utah', '50': 'Vermont', '51': 'Virginia',
            '53': 'Washington', '54': 'West Virginia', '55': 'Wisconsin', '56': 'Wyoming'
        }
        
        state_avg_insurance['State_Name'] = state_avg_insurance['ST'].map(fips_to_state)
        state_avg_insurance = state_avg_insurance.dropna(subset=['State_Name'])
        final_insurance_df = state_avg_insurance[['State_Name', 'Avg_Home_Insurance_2022']]
        
        # --- 5. Save Cleaned Data ---
        cleaned_filename = "cleaned_home_insurance_2022.csv"
        final_insurance_df.to_csv(cleaned_filename, index=False)
        print(f"📤 Cleaned data saved to: {cleaned_filename} (Total rows: {len(final_insurance_df)})")
        
        # --- 6. Before/After Summary for Report ---
        print("\n📊 Before/After Summary (for your report):")
        print(f"- Rows before: {len(df_raw)}")
        print(f"- Columns before: {df_raw.shape[1]} (ST, INSP, state)")
        print(f"- Invalid/Missing samples removed: {invalid_count}")
        print(f"- Final rows after cleaning & aggregation: {len(final_insurance_df)}")
        print(f"- Final columns after cleaning: {final_insurance_df.shape[1]} (State_Name, Avg_Home_Insurance_2022)")
        
        return final_insurance_df
        
    else:
        print(f"❌ API Request Failed, Status Code: {response.status_code}")
        return None

if __name__ == "__main__":
    fetch_and_clean_insurance_data()