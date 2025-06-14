import unittest
import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.transform import DataTransformer, transform_fashion_data


class TestDataTransformer(unittest.TestCase):
    
    def setUp(self):
        self.transformer = DataTransformer()
    
    def test_init(self):
        """inisialisasi"""
        self.assertEqual(self.transformer.usd_to_idr_rate, 16000.0)
    
    def test_clean_price_valid(self):
        """Test cleaning valid price"""
        result = self.transformer.clean_price("$50.00")
        self.assertEqual(result, 800000.0)  # 50 * 16000
        
        result = self.transformer.clean_price("$100")
        self.assertEqual(result, 1600000.0)  # 100 * 16000
    
    def test_clean_price_invalid(self):
        """Test cleaning invalid price"""
        result = self.transformer.clean_price("Price Unavailable")
        self.assertIsNone(result)
        
        result = self.transformer.clean_price("Unknown")
        self.assertIsNone(result)
        
        result = self.transformer.clean_price("")
        self.assertIsNone(result)
        
        result = self.transformer.clean_price(None)
        self.assertIsNone(result)
    
    def test_clean_rating_valid(self):
        """Test cleaning valid rating"""
        result = self.transformer.clean_rating("Rating:  4.5 / 5")
        self.assertEqual(result, 4.5)
        
        result = self.transformer.clean_rating("Rating:  3.0 / 5")
        self.assertEqual(result, 3.0)
    
    def test_clean_rating_invalid(self):
        """Test cleaning invalid rating"""
        result = self.transformer.clean_rating("Rating:  Invalid Rating / 5")
        self.assertIsNone(result)
        
        result = self.transformer.clean_rating("Rating: Not Rated")
        self.assertIsNone(result)
        
        result = self.transformer.clean_rating(None)
        self.assertIsNone(result)
    
    def test_clean_colors_valid(self):
        """Test cleaning valid colors"""
        result = self.transformer.clean_colors("3 Colors")
        self.assertEqual(result, 3)
        
        result = self.transformer.clean_colors("5 Colors")
        self.assertEqual(result, 5)
        
        result = self.transformer.clean_colors("1 Color")
        self.assertEqual(result, 1)
    
    def test_clean_colors_invalid(self):
        """Test cleaning invalid colors"""
        result = self.transformer.clean_colors("Unknown Colors")
        self.assertIsNone(result)
        
        result = self.transformer.clean_colors(None)
        self.assertIsNone(result)
    
    def test_clean_size_valid(self):
        """Test cleaning valid size"""
        result = self.transformer.clean_size("Size: M")
        self.assertEqual(result, "M")
        
        result = self.transformer.clean_size("Size: XL")
        self.assertEqual(result, "XL")
        
        result = self.transformer.clean_size("Size: XXL")
        self.assertEqual(result, "XXL")
    
    def test_clean_size_invalid(self):
        """Test cleaning invalid size"""
        result = self.transformer.clean_size("Unknown Size")
        self.assertIsNone(result)
        
        result = self.transformer.clean_size(None)
        self.assertIsNone(result)
    
    def test_clean_gender_valid(self):
        """Test cleaning valid gender"""
        result = self.transformer.clean_gender("Gender: Men")
        self.assertEqual(result, "Men")
        
        result = self.transformer.clean_gender("Gender: Women")
        self.assertEqual(result, "Women")
        
        result = self.transformer.clean_gender("Gender: Unisex")
        self.assertEqual(result, "Unisex")
    
    def test_clean_gender_invalid(self):
        """Test cleaning invalid gender"""
        result = self.transformer.clean_gender("Unknown Gender")
        self.assertIsNone(result)
        
        result = self.transformer.clean_gender(None)
        self.assertIsNone(result)
    
    def test_clean_title_valid(self):
        """Test cleaning valid title"""
        result = self.transformer.clean_title("T-shirt 1")
        self.assertEqual(result, "T-shirt 1")
        
        result = self.transformer.clean_title("  Hoodie 2  ")
        self.assertEqual(result, "Hoodie 2")
    
    def test_clean_title_invalid(self):
        """Test cleaning invalid title"""
        result = self.transformer.clean_title("Unknown Product")
        self.assertIsNone(result)
        
        result = self.transformer.clean_title("")
        self.assertIsNone(result)
        
        result = self.transformer.clean_title(None)
        self.assertIsNone(result)
    
    def test_transform_data_complete(self):
        """Test complete data transformation"""
        # Sample raw data
        raw_data = [
            {
                'Title': 'T-shirt 1',
                'Price': '$50.00',
                'Rating': 'Rating:  4.5 / 5',
                'Colors': '3 Colors',
                'Size': 'Size: M',
                'Gender': 'Gender: Men'
            },
            {
                'Title': 'Hoodie 2',
                'Price': '$75.25',
                'Rating': 'Rating:  3.8 / 5',
                'Colors': '5 Colors',
                'Size': 'Size: L',
                'Gender': 'Gender: Women'
            },
            {
                'Title': 'Unknown Product',  # Harus terfilter
                'Price': 'Price Unavailable',
                'Rating': 'Invalid Rating',
                'Colors': '2 Colors',
                'Size': 'Size: XL',
                'Gender': 'Gender: Unisex'
            }
        ]
        
        df_result = self.transformer.transform_data(raw_data)
        
        self.assertEqual(len(df_result), 2)
        
        self.assertEqual(str(df_result['Title'].dtype), 'string')
        self.assertEqual(str(df_result['Price'].dtype), 'float64')
        self.assertEqual(str(df_result['Rating'].dtype), 'float64')
        self.assertEqual(str(df_result['Colors'].dtype), 'int64')
        self.assertEqual(str(df_result['Size'].dtype), 'string')
        self.assertEqual(str(df_result['Gender'].dtype), 'string')
        
        self.assertEqual(df_result.iloc[0]['Title'], 'T-shirt 1')
        self.assertEqual(df_result.iloc[0]['Price'], 800000.0)  # 50 * 16000
        self.assertEqual(df_result.iloc[0]['Rating'], 4.5)
        self.assertEqual(df_result.iloc[0]['Colors'], 3)
        self.assertEqual(df_result.iloc[0]['Size'], 'M')
        self.assertEqual(df_result.iloc[0]['Gender'], 'Men')
    
    def test_transform_data_with_duplicates(self):
        """Test transform data dengan remove duplicates"""
        raw_data = [
            {
                'Title': 'T-shirt 1',
                'Price': '$50.00',
                'Rating': 'Rating:  4.5 / 5',
                'Colors': '3 Colors',
                'Size': 'Size: M',
                'Gender': 'Gender: Men'
            },
            {
                'Title': 'T-shirt 1',  # Duplikat
                'Price': '$50.00',
                'Rating': 'Rating:  4.5 / 5',
                'Colors': '3 Colors',
                'Size': 'Size: M',
                'Gender': 'Gender: Men'
            }
        ]
        
        df_result = self.transformer.transform_data(raw_data)
        
        self.assertEqual(len(df_result), 1)
    
    def test_transform_fashion_data(self):
        """Test fungsi main transform"""
        raw_data = [
            {
                'Title': 'Jacket 1',
                'Price': '$100.00',
                'Rating': 'Rating:  4.0 / 5',
                'Colors': '4 Colors',
                'Size': 'Size: L',
                'Gender': 'Gender: Unisex'
            }
        ]
        
        df_result = transform_fashion_data(raw_data)
        
        self.assertIsInstance(df_result, pd.DataFrame)
        self.assertEqual(len(df_result), 1)
        self.assertEqual(df_result.iloc[0]['Title'], 'Jacket 1')


if __name__ == '__main__':
    unittest.main()