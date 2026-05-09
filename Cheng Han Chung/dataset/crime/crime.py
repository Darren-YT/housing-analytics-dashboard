import pandas as pd
import requests
import time

def fetch_and_clean_crime_data():
    # 1. State Abbreviation Dictionary (Standardizing Identifiers)
    state_abbr_map = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire',
        'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina',
        'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
        'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee',
        'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
        'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
    }

    api_key = "A1x31gEqkW0tWxAuSttATUzDlJHmt0NZmtgsOtcB"
    year = 2022
    raw_data_list = []

    print(f"Fetching {year} Violent Crime data from FBI API (This may take ~20-30 seconds)...")

    # --- Step 1: Data Collection (Fetch from API) ---
    for abbr, full_name in state_abbr_map.items():
        url = f"https://api.usa.gov/crime/fbi/cde/estimate/state/{abbr}/violent-crime?from={year}&to={year}&api_key={api_key}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                # Check if data exists for the state in 2022
                if data.get('results'):
                    result = data['results'][0]
                    raw_data_list.append({
                        'State_Name': full_name,
                        'Violent_Crime_Rate_2022': result.get('violent_crime_rate', None),
                        'Violent_Crime_Total_2022': result.get('violent_crime', None)
                    })
                else:
                    # Append empty records to represent Missing Values
                    raw_data_list.append({
                        'State_Name': full_name,
                        'Violent_Crime_Rate_2022': None,
                        'Violent_Crime_Total_2022': None
                    })
            else:
                print(f"⚠️ API Error for {full_name}: Status Code {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Error fetching {full_name}: {e}")
        
        # Pause for 0.5 seconds to respect API rate limits
        time.sleep(0.5)

    # Convert raw data list to DataFrame
    df_raw = pd.DataFrame(raw_data_list)
    
    # Save Raw Data
    raw_filename = "raw_crime_data_2022.csv"
    df_raw.to_csv(raw_filename, index=False)
    print(f"\n📥 Raw data saved to: {raw_filename} (Total rows: {len(df_raw)})")

    # --- Step 2: Data Cleaning ---
    print("\nStarting data cleaning process (Handling missing values and data types)...")
    df_clean = df_raw.copy()

    # Detect duplicates (Sanity check)
    duplicates_count = df_clean.duplicated(subset=['State_Name']).sum()
    df_clean = df_clean.drop_duplicates(subset=['State_Name'])

    # Count missing values before imputation
    missing_count = df_clean['Violent_Crime_Rate_2022'].isna().sum()

    # Handle Missing Values (Median Imputation)
    # If a state didn't report to FBI in 2022, we fill the NaN with the national median
    if missing_count > 0:
        median_rate = df_clean['Violent_Crime_Rate_2022'].median()
        median_total = df_clean['Violent_Crime_Total_2022'].median()
        
        df_clean['Violent_Crime_Rate_2022'] = df_clean['Violent_Crime_Rate_2022'].fillna(median_rate)
        df_clean['Violent_Crime_Total_2022'] = df_clean['Violent_Crime_Total_2022'].fillna(median_total)

    # Correct Data Types
    df_clean['Violent_Crime_Total_2022'] = df_clean['Violent_Crime_Total_2022'].astype(int)
    df_clean['Violent_Crime_Rate_2022'] = df_clean['Violent_Crime_Rate_2022'].round(2)

    # Save Cleaned Data
    cleaned_filename = "cleaned_crime_data_2022.csv"
    df_clean.to_csv(cleaned_filename, index=False)
    print(f"📤 Cleaned data saved to: {cleaned_filename} (Total rows: {len(df_clean)})")

    # --- Step 3: Before/After Summary for Report ---
    print("\n📊 Before/After Summary (for your report):")
    print(f"- Rows before: {len(df_raw)}")
    print(f"- Columns before: {df_raw.shape[1]} (State_Name, Violent_Crime_Rate_2022, Violent_Crime_Total_2022)")
    print(f"- Duplicates detected & removed: {duplicates_count}")
    print(f"- Missing values detected: {missing_count} (Successfully imputed using median)")
    print(f"- Final rows after cleaning: {len(df_clean)}")
    print(f"- Final columns after cleaning: {df_clean.shape[1]}")
    
    return df_clean

if __name__ == "__main__":
    fetch_and_clean_crime_data()