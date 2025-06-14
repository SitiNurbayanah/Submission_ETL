import pandas as pd
import os
from datetime import datetime
from typing import Optional


class DataLoader:
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = "products.csv") -> str:
        """Save DataFrame ke CSV file"""
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"Data berhasil di save ke: {filepath}")
            print(f"File size: {os.path.getsize(filepath)} bytes")
            return filepath
        except Exception as e:
            print(f"Error menyimpan CSV file: {e}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Vallidasi data sebelum saving"""
        print("\n=== Data Validation ===")
        
        if df.empty:
            print("DataFrame is empty!")
            return False
        
        print(f"DataFrame shape: {df.shape}")
        
        required_columns = ['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Missing columns: {missing_columns}")
            return False
        
        print(f"All required columns present: {required_columns}")
        
        expected_types = {
            'Title': 'string',
            'Price': 'float64',
            'Rating': 'float64',
            'Colors': 'int64',
            'Size': 'string',
            'Gender': 'string'
        }
        
        for col, expected_type in expected_types.items():
            actual_type = str(df[col].dtype)
            if actual_type != expected_type:
                print(f"Column '{col}' type mismatch: expected {expected_type}, got {actual_type}")
            else:
                print(f"Column '{col}': {actual_type}")
        
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            print(f" Found null values:")
            for col, count in null_counts.items():
                if count > 0:
                    print(f"   {col}: {count} nulls")
            return False
        
        print("No null values found")
        
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            print(f" Found {duplicate_count} duplicate rows")
            return False
        
        print("No duplicate rows found")
        
        if (df['Price'] <= 0).any():
            print(" Found non-positive price values")
            return False
        
        print("All price values are positive")
        
        if not df['Rating'].between(0, 5).all():
            print(" Found rating values outside 0-5 range")
            return False
        
        print("All rating values are in valid range (0-5)")
        
        print("\nData validation passed!")
        return True
    
    def generate_summary(self, df: pd.DataFrame) -> str:
        """Generate data summary"""
        summary = f"""
=== ETL Pipeline Summary ===
Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Records: {len(df)}

Data Types:
{df.dtypes.to_string()}

Statistical Summary:
{df.describe()}

Value Counts:
Gender: {df['Gender'].value_counts().to_dict()}
Size: {df['Size'].value_counts().to_dict()}

Price Range: ${df['Price'].min():,.2f} - ${df['Price'].max():,.2f} IDR
Average Rating: {df['Rating'].mean():.2f}
        """
        return summary
    
    def save_summary(self, df: pd.DataFrame, filename: str = "summary.txt") -> str:
        """Save data summary to text file"""
        filepath = os.path.join(self.output_dir, filename)
        summary = self.generate_summary(df)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"Summary saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving summary: {e}")
            raise


def load_fashion_data(df: pd.DataFrame, filename: str = "products.csv", 
                     output_dir: str = ".", validate: bool = True) -> str:
    """Main function to load fashion data"""
    loader = DataLoader(output_dir)
    
    if validate:
        if not loader.validate_data(df):
            raise ValueError("Data validation failed!")
    
    csv_path = loader.save_to_csv(df, filename)
    
    loader.save_summary(df)
    
    print(f"\n=== Loading completed! ===")
    print(f"CSV file: {csv_path}")
    print(f"Records saved: {len(df)}")
    
    return csv_path