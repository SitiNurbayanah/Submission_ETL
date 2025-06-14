#!/usr/bin/env python3
"""
Fashion Studio ETL Pipeline
Web scraping dan pemrosesan data produk fashion dari https://fashion-studio.dicoding.dev/
"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.extract import extract_fashion_data
from utils.transform import transform_fashion_data
from utils.load import load_fashion_data


def main():
    """Main ETL pipeline function"""
    print("="*60)
    print("FASHION STUDIO ETL PIPELINE")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        print("EXTRACT: Starting web scraping...")
        print("-" * 40)
        
        raw_products = extract_fashion_data(start_page=1, end_page=50)
        
        if not raw_products:
            print("No data extracted. Exiting...")
            return
        
        print(f"Extraction completed: {len(raw_products)} products")
        print()
        
        print("TRANSFORM: Starting data transformation...")
        print("-" * 40)
        
        clean_df = transform_fashion_data(raw_products)
        
        if clean_df.empty:
            print("No data after transformation. Exiting...")
            return
        
        print(f"Transformation completed: {len(clean_df)} clean products")
        print()
        
        print("LOAD: Starting data loading...")
        print("-" * 40)
        
        csv_path = load_fashion_data(clean_df, filename="products.csv")
        
        print(f"Loading completed: {csv_path}")
        print()
        
        print("="*60)
        print("ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Final dataset: {len(clean_df)} records")
        print(f"Output file: {csv_path}")
        
        print("\nSample data (first 5 rows):")
        print("-" * 40)
        print(clean_df.head().to_string(index=False))
        
        print("\nData types:")
        print("-" * 40)
        print(clean_df.dtypes.to_string())
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error in ETL pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()