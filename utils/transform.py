import pandas as pd
import re
from typing import List, Dict


class DataTransformer:
    def __init__(self, usd_to_idr_rate: float = 16000.0):
        self.usd_to_idr_rate = usd_to_idr_rate
    
    def clean_price(self, price_str: str) -> float:
        """USD ke IDR"""
        if pd.isna(price_str) or price_str in ['Price Unavailable', 'Unknown', '']:
            return None
        
        price_match = re.search(r'\$(\d+\.?\d*)', str(price_str))
        if price_match:
            usd_price = float(price_match.group(1))
            idr_price = usd_price * self.usd_to_idr_rate
            return idr_price
        
        return None
    
    def clean_rating(self, rating_str: str) -> float:
        """Extract rating string ke float"""
        if pd.isna(rating_str) or 'Invalid Rating' in str(rating_str) or 'Not Rated' in str(rating_str):
            return None
        
        rating_match = re.search(r'(\d+\.?\d*)\s*/\s*5', str(rating_str))
        if rating_match:
            return float(rating_match.group(1))
        
        return None
    
    def clean_colors(self, colors_str: str) -> int:
        """Extract jumlah of colors sebagai integer"""
        if pd.isna(colors_str):
            return None
        
        colors_match = re.search(r'(\d+)\s*Colors?', str(colors_str))
        if colors_match:
            return int(colors_match.group(1))
        
        return None
    
    def clean_size(self, size_str: str) -> str:
        """Extract size string tanpa 'Size:' prefix"""
        if pd.isna(size_str):
            return None
        
        size_match = re.search(r'Size:\s*([A-Z]+)', str(size_str))
        if size_match:
            return size_match.group(1)
        
        return None
    
    def clean_gender(self, gender_str: str) -> str:
        """Extract gender string tanpa 'Gender:' prefix"""
        if pd.isna(gender_str):
            return None
        
        gender_match = re.search(r'Gender:\s*(\w+)', str(gender_str))
        if gender_match:
            return gender_match.group(1)
        
        return None
    
    def clean_title(self, title_str: str) -> str:
        """Bersihkan title and hapus invalid products"""
        if pd.isna(title_str) or str(title_str).strip() == '' or 'Unknown Product' in str(title_str):
            return None
        
        return str(title_str).strip()
    
    def transform_data(self, products: List[Dict]) -> pd.DataFrame:
        """Transform raw product data"""
        df = pd.DataFrame(products)
        
        print(f"Initial data shape: {df.shape}")
        
        df['Title_clean'] = df['Title'].apply(self.clean_title)
        df['Price_clean'] = df['Price'].apply(self.clean_price)
        df['Rating_clean'] = df['Rating'].apply(self.clean_rating)
        df['Colors_clean'] = df['Colors'].apply(self.clean_colors)
        df['Size_clean'] = df['Size'].apply(self.clean_size)
        df['Gender_clean'] = df['Gender'].apply(self.clean_gender)
        
        df_final = pd.DataFrame({
            'Title': df['Title_clean'],
            'Price': df['Price_clean'],
            'Rating': df['Rating_clean'],
            'Colors': df['Colors_clean'],
            'Size': df['Size_clean'],
            'Gender': df['Gender_clean']
        })
        
        print(f"After cleaning shape: {df_final.shape}")
        
        df_final = df_final.dropna()
        print(f"After removing null values: {df_final.shape}")
        
        df_final = df_final.drop_duplicates()
        print(f"After removing duplicates: {df_final.shape}")
        
        df_final['Title'] = df_final['Title'].astype('string')
        df_final['Price'] = df_final['Price'].astype('float64')
        df_final['Rating'] = df_final['Rating'].astype('float64')
        df_final['Colors'] = df_final['Colors'].astype('int64')
        df_final['Size'] = df_final['Size'].astype('string')
        df_final['Gender'] = df_final['Gender'].astype('string')
        
        df_final = df_final.reset_index(drop=True)
        
        return df_final


def transform_fashion_data(products: List[Dict]) -> pd.DataFrame:
    """Fungsi main untul transform fashion data"""
    transformer = DataTransformer()
    df_clean = transformer.transform_data(products)
    
    print(f"\nTransformation completed!")
    print(f"Final data shape: {df_clean.shape}")
    print(f"\nData types:")
    print(df_clean.dtypes)
    print(f"\nFirst few rows:")
    print(df_clean.head())
    
    return df_clean