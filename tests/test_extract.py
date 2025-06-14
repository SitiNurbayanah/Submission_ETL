import unittest
from unittest.mock import Mock, patch
import os
import sys
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.extract import ProductExtractor, extract_fashion_data
from bs4 import BeautifulSoup


class TestProductExtractor(unittest.TestCase):
    
    def setUp(self):
        self.extractor = ProductExtractor()
    
    def test_init(self):
        """initialization"""
        self.assertEqual(self.extractor.base_url, "https://fashion-studio.dicoding.dev/")
        self.assertIsNotNone(self.extractor.session)
    
    def test_extract_product_data_with_valid_html(self):
        """Test extract data dari html"""
        html_content = """
        <div class="collection-card">
            <h3 class="product-title">T-shirt 1</h3>
            <span class="price">$50.00</span>
            <p style="font-size: 14px; color: #777;">Rating:  4.5 / 5</p>
            <p style="font-size: 14px; color: #777;">3 Colors</p>
            <p style="font-size: 14px; color: #777;">Size: M</p>
            <p style="font-size: 14px; color: #777;">Gender: Men</p>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        products = self.extractor.extract_product_data(soup)
        
        self.assertEqual(len(products), 1)
        product = products[0]
        
        self.assertEqual(product['Title'], 'T-shirt 1')
        self.assertEqual(product['Price'], '$50.00')
        self.assertEqual(product['Rating'], 'Rating:  4.5 / 5')
        self.assertEqual(product['Colors'], '3 Colors')
        self.assertEqual(product['Size'], 'Size: M')
        self.assertEqual(product['Gender'], 'Gender: Men')
    
    def test_extract_product_data_with_price_unavailable(self):
        """Test extract data dengan price unavailable"""
        html_content = """
        <div class="collection-card">
            <h3 class="product-title">T-shirt 2</h3>
            <p class="price">Price Unavailable</p>
            <p style="font-size: 14px; color: #777;">Rating: Not Rated</p>
            <p style="font-size: 14px; color: #777;">5 Colors</p>
            <p style="font-size: 14px; color: #777;">Size: L</p>
            <p style="font-size: 14px; color: #777;">Gender: Women</p>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        products = self.extractor.extract_product_data(soup)
        
        self.assertEqual(len(products), 1)
        product = products[0]
        
        self.assertEqual(product['Title'], 'T-shirt 2')
        self.assertEqual(product['Price'], 'Price Unavailable')
    
    def test_extract_product_data_empty_html(self):
        """Test extractdata dari html kosong"""
        html_content = "<div></div>"
        soup = BeautifulSoup(html_content, 'html.parser')
        products = self.extractor.extract_product_data(soup)
        
        self.assertEqual(len(products), 0)
    
    @patch('utils.extract.requests.Session.get')
    def test_scrape_page_success(self, mock_get):
        """Test web scraping sukses"""
        mock_response = Mock()
        mock_response.content = """
        <div class="collection-card">
            <h3 class="product-title">Test Product</h3>
            <span class="price">$100.00</span>
        </div>
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        products = self.extractor.scrape_page(1)
        
        self.assertIsInstance(products, list)
        mock_get.assert_called_once()
    
    @patch('utils.extract.requests.Session.get')
    def test_scrape_page_error(self, mock_get):
        """Test page scraping dengan internet error"""
        
        mock_get.side_effect = requests.RequestException("Network error")
        
        products = self.extractor.scrape_page(1)
        
        self.assertEqual(products, [])
    
    @patch('utils.extract.ProductExtractor.scrape_page')
    @patch('time.sleep')
    def test_scrape_all_pages(self, mock_sleep, mock_scrape_page):
        """Test scraping banyak pages"""
        mock_scrape_page.return_value = [{'Title': 'Test Product', 'Price': '$50.00'}]
        
        products = self.extractor.scrape_all_pages(1, 3)
        
        self.assertEqual(mock_scrape_page.call_count, 3)
        self.assertEqual(len(products), 3)
    
    @patch('utils.extract.ProductExtractor')
    def test_extract_fashion_data(self, mock_extractor_class):
        """Test main extract function"""
        mock_extractor = Mock()
        mock_extractor.scrape_all_pages.return_value = [
            {'Title': 'Product 1', 'Price': '$25.00'},
            {'Title': 'Product 2', 'Price': '$35.00'}
        ]
        mock_extractor_class.return_value = mock_extractor
        
        products = extract_fashion_data(1, 2)
        
        self.assertEqual(len(products), 2)
        mock_extractor.scrape_all_pages.assert_called_once_with(1, 2)


if __name__ == '__main__':
    unittest.main()