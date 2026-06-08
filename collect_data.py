import pandas as pd
from data_collector import get_brand_data
import time

brands = [
    "Dior Sauvage",
    "Creed Aventus", 
    "YSL Black Opium",
    "Skinn by Titan",
    "Bella Vita Perfume",
    "Engage Perfume",
    "Fogg Perfume"
]

all_data = []

for brand in brands:
    print(f"Collecting data for {brand}...")
    df = get_brand_data(brand)
    if not df.empty:
        all_data.append(df)
        print(f"Got {len(df)} data points for {brand}")
    time.sleep(3)  # Avoid API rate limits

# Combine all brands into one CSV
final_df = pd.concat(all_data, ignore_index=True)
final_df.to_csv("brand_data.csv", index=False)
print(f"\nDone! Total data points: {len(final_df)}")
print(final_df['brand'].value_counts())