import unittest
import pandas as pd
import os
import sys
import tempfile
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.load import DataLoader, load_fashion_data


class TestDataLoader(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.loader = DataLoader(self.test_dir)
        
        self.sample_df = pd.DataFrame({
            'Title': pd.Series(['T-shirt 1', 'Hoodie 2'], dtype='string'),
            'Price': pd.Series([800000.0, 1200000.0], dtype='float64'),
            'Rating': pd.Series([4.5, 3.8], dtype='float64'),
            'Colors': pd.Series([3, 5], dtype='int64'),
            'Size': pd.Series(['M', 'L'], dtype='string'),
            'Gender': pd.Series(['Men', 'Women'], dtype='string')
        })
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Inisialisasi"""
        self.assertEqual(self.loader.output_dir, self.test_dir)
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_save_to_csv(self):
        """Save ke CSV"""
        filename = "test_products.csv"
        filepath = self.loader.save_to_csv(self.sample_df, filename)
        
        self.assertTrue(os.path.exists(filepath))
        
        loaded_df = pd.read_csv(filepath)
        self.assertEqual(len(loaded_df), 2)
        self.assertEqual(loaded_df.iloc[0]['Title'], 'T-shirt 1')
    
    def test_validate_data_valid(self):
        """Test validasi data dengan data valid"""
        result = self.loader.validate_data(self.sample_df)
        self.assertTrue(result)
    
    def test_validate_data_empty(self):
        """Test validasi data dengan DataFrame kosong"""
        empty_df = pd.DataFrame()
        result = self.loader.validate_data(empty_df)
        self.assertFalse(result)
    
    def test_validate_data_missing_columns(self):
        """Test validasi daya dengan missing columns"""
        incomplete_df = pd.DataFrame({
            'Title': ['T-shirt 1'],
            'Price': [800000.0]
        })
        result = self.loader.validate_data(incomplete_df)
        self.assertFalse(result)
    
    def test_validate_data_with_nulls(self):
        """Test validasi data dengan null values"""
        df_with_nulls = self.sample_df.copy()
        df_with_nulls.loc[0, 'Title'] = None
        result = self.loader.validate_data(df_with_nulls)
        self.assertFalse(result)
    
    def test_validate_data_with_duplicates(self):
        """Test validasi data dengan duplicate"""
        df_with_duplicates = pd.concat([self.sample_df, self.sample_df.iloc[[0]]], ignore_index=True)
        result = self.loader.validate_data(df_with_duplicates)
        self.assertFalse(result)
    
    def test_validate_data_negative_price(self):
        """Test validasi data dengan nilai harga negative"""
        df_negative_price = self.sample_df.copy()
        df_negative_price.loc[0, 'Price'] = -100.0
        result = self.loader.validate_data(df_negative_price)
        self.assertFalse(result)
    
    def test_validate_data_invalid_rating(self):
        """Test validasi data dengan invalid rating"""
        df_invalid_rating = self.sample_df.copy()
        df_invalid_rating.loc[0, 'Rating'] = 6.0
        result = self.loader.validate_data(df_invalid_rating)
        self.assertFalse(result)
        
        df_invalid_rating.loc[0, 'Rating'] = -1.0
        result = self.loader.validate_data(df_invalid_rating)
        self.assertFalse(result)
    
    def test_generate_summary(self):
        """Test membuat summary"""
        summary = self.loader.generate_summary(self.sample_df)
        
        self.assertIn("ETL Pipeline Summary", summary)
        self.assertIn("Total Records: 2", summary)
        self.assertIn("Data Types:", summary)
        self.assertIn("Statistical Summary:", summary)
        self.assertIn("Value Counts:", summary)
    
    def test_save_summary(self):
        """Test simpan ke file"""
        filename = "test_summary.txt"
        filepath = self.loader.save_summary(self.sample_df, filename)
        
        self.assertTrue(os.path.exists(filepath))
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("ETL Pipeline Summary", content)
            self.assertIn("Total Records: 2", content)
    
    def test_load_fashion_data_with_validation(self):
        """Test fungsi load dengan validasi"""
        csv_path = load_fashion_data(
            self.sample_df, 
            filename="test_output.csv", 
            output_dir=self.test_dir,
            validate=True
        )
        
        self.assertTrue(os.path.exists(csv_path))
        
        summary_path = os.path.join(self.test_dir, "summary.txt")
        self.assertTrue(os.path.exists(summary_path))
    
    def test_load_fashion_data_without_validation(self):
        """Test main load tanpa validasi"""
        csv_path = load_fashion_data(
            self.sample_df, 
            filename="test_output_no_val.csv", 
            output_dir=self.test_dir,
            validate=False
        )
        
        self.assertTrue(os.path.exists(csv_path))
    
    def test_load_fashion_data_validation_failure(self):
        """Test main load dengan validasi kesalahan"""
        invalid_df = pd.DataFrame()
        
        with self.assertRaises(ValueError):
            load_fashion_data(
                invalid_df, 
                filename="invalid.csv", 
                output_dir=self.test_dir,
                validate=True
            )
    
    def test_data_types_preservation(self):
        """Test data type setelah save"""
        filename = "type_test.csv"
        filepath = self.loader.save_to_csv(self.sample_df, filename)
        
        loaded_df = pd.read_csv(filepath)
        
        loaded_df['Title'] = loaded_df['Title'].astype('string')
        loaded_df['Price'] = loaded_df['Price'].astype('float64')
        loaded_df['Rating'] = loaded_df['Rating'].astype('float64')
        loaded_df['Colors'] = loaded_df['Colors'].astype('int64')
        loaded_df['Size'] = loaded_df['Size'].astype('string')
        loaded_df['Gender'] = loaded_df['Gender'].astype('string')
        
        result = self.loader.validate_data(loaded_df)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()