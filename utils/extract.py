import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict


class ProductExtractor:
    def __init__(self, base_url: str = "https://fashion-studio.dicoding.dev/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_product_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract product dari single page"""
        products = []
        collection_cards = soup.find_all('div', class_='collection-card')
        
        for card in collection_cards:
            try:
                product = {}
                
                title_elem = card.find('h3', class_='product-title')
                product['Title'] = title_elem.text.strip() if title_elem else 'Unknown Product'
                
                price_elem = card.find('span', class_='price')
                if price_elem:
                    price_text = price_elem.text.strip()
                    product['Price'] = price_text
                else:
                    price_unavailable = card.find('p', class_='price')
                    if price_unavailable and 'Price Unavailable' in price_unavailable.text:
                        product['Price'] = 'Price Unavailable'
                    else:
                        product['Price'] = 'Unknown'
                
                detail_paragraphs = card.find_all('p', style="font-size: 14px; color: #777;")
                
                product['Rating'] = 'Invalid Rating'
                product['Colors'] = 'Unknown'
                product['Size'] = 'Unknown'
                product['Gender'] = 'Unknown'
                
                for p in detail_paragraphs:
                    text = p.text.strip()
                    if 'Rating:' in text:
                        product['Rating'] = text
                    elif 'Colors' in text:
                        product['Colors'] = text
                    elif 'Size:' in text:
                        product['Size'] = text
                    elif 'Gender:' in text:
                        product['Gender'] = text
                
                products.append(product)
                
            except Exception as e:
                print(f"Ekstraksi error: {e}")
                continue
        
        return products
    
    def scrape_page(self, page_num: int) -> List[Dict]:
        """Scrape single page"""
        if page_num == 1:
            url = self.base_url
        else:
            url = f"{self.base_url}Page{page_num}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = self.extract_product_data(soup)
            
            print(f"Scraped page {page_num}: {len(products)} products")
            return products
            
        except requests.RequestException as e:
            print(f"Scraping page error {page_num}: {e}")
            return []

    def scrape_all_pages(self, start_page: int = 1, end_page: int = 50) -> List[Dict]:
        """Scrape semua page dari start_page ke end_page"""
        all_products = []
        
        for page_num in range(start_page, end_page + 1):
            products = self.scrape_page(page_num)
            all_products.extend(products)
            
            time.sleep(1)
            
            if page_num % 10 == 0:
                print(f"Progress: {page_num}/{end_page} pages completed")
        
        return all_products


def extract_fashion_data(start_page: int = 1, end_page: int = 50) -> List[Dict]:
    """Fungsi main untuk extract fashion data"""
    extractor = ProductExtractor()
    products = extractor.scrape_all_pages(start_page, end_page)
    
    print(f"\Ekstraksi completed!")
    print(f"Total products: {len(products)}")
    
    return products