import csv
import time
import random
import logging
from bs4 import BeautifulSoup
import cloudscraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Rotating User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edge/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

def get_random_headers():
    """Generate random headers for each request"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

def create_scraper():
    """Create a cloudscraper instance to bypass Cloudflare"""
    logger.info("Initializing Cloudscraper...")
    
    try:
        # Create scraper with browser-like settings
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'mobile': False,
            },
            delay=10,  # Delay between requests
            interpreter='nodejs',  # Use Node.js interpreter for better compatibility
        )
        
        logger.info("Cloudscraper initialized successfully")
        return scraper
        
    except Exception as e:
        logger.error(f"Failed to initialize Cloudscraper: {e}")
        raise

def warm_up_scraper(scraper):
    """Test the scraper with initial requests"""
    logger.info("Testing scraper connection...")
    
    test_urls = [
        "https://www.google.com/",
        "https://www.apartments.com/"
    ]
    
    for url in test_urls:
        try:
            logger.info(f"  Testing: {url}")
            headers = get_random_headers()
            response = scraper.get(
                url, 
                headers=headers,
                timeout=30
            )
            
            logger.info(f"    Status: {response.status_code}")
            logger.info(f"    Response size: {len(response.text):,} characters")
            
            if response.status_code == 200:
                logger.info(f"    Successfully connected to {url}")
            
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            logger.warning(f"    Connection test failed for {url}: {e}")
    
    logger.info("Scraper warm-up complete")
    time.sleep(3)

def fetch_with_retry(scraper, url, max_retries=3):
    """Fetch URL with retry logic"""
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait_time = random.uniform(5 * attempt, 10 * attempt)
                logger.info(f"  Retry attempt {attempt}/{max_retries}, waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
            
            headers = get_random_headers()
            logger.info(f"  Attempt {attempt}: Fetching {url}")
            
            response = scraper.get(
                url,
                headers=headers,
                timeout=60,
                allow_redirects=True
            )
            
            # Check if we got a valid response
            response.raise_for_status()
            
            if len(response.text) < 1000:
                logger.warning("  Response is suspiciously small, might be blocked")
                raise ValueError("Response too small")
            
            logger.info(f"  Success! Status: {response.status_code}")
            return response
            
        except cloudscraper.exceptions.CloudflareChallengeError as e:
            logger.error(f"  Cloudflare challenge detected: {e}")
            if attempt == max_retries:
                raise
            time.sleep(random.uniform(20, 30))
            
        except Exception as e:
            logger.error(f"  Error on attempt {attempt}: {type(e).__name__}: {e}")
            if attempt == max_retries:
                raise
    
    raise Exception(f"Failed to fetch {url} after {max_retries} attempts")

def extract_listing_data(card):
    """Extract data from a listing card"""
    data = {
        'title': '',
        'prices': '',
        'phone': '',
        'email_available': '',
        'description': ''
    }
    
    try:
        # Title
        title_selectors = [
            'span.propertyTitleWrapper',
            'a.property-link',
            '.placardTitle',
            'h2.property-title',
            'h2 a',
            '.property-title a'
        ]
        for selector in title_selectors:
            elem = card.select_one(selector)
            if elem:
                data['title'] = elem.get_text(strip=True)
                break
        
        # Prices
        price_selectors = [
            'p.property-pricing',
            '.price-range',
            '.rentLabel',
            '.pricing-info',
            '.property-rents'
        ]
        for selector in price_selectors:
            elem = card.select_one(selector)
            if elem:
                data['prices'] = elem.get_text(' ', strip=True)
                break
        
        # Phone
        phone_selectors = [
            'div.phone',
            '.phone-number',
            '.contact-phone',
            'span[class*="phone"]',
            'a[href*="tel:"]'
        ]
        for selector in phone_selectors:
            elem = card.select_one(selector)
            if elem:
                data['phone'] = elem.get_text(strip=True)
                break
        
        # Email Available
        email_selectors = [
            'a[href*="mailto:"]',
            'a:contains("Email")',
            '.email-option',
            '[data-tracking="email"]'
        ]
        for selector in email_selectors:
            if card.select_one(selector):
                data['email_available'] = 'Yes'
                break
        if not data['email_available']:
            data['email_available'] = 'No'
        
        # Description
        desc_selectors = [
            'div.property-description',
            '.description',
            '.property-details',
            '.info-section'
        ]
        for selector in desc_selectors:
            elem = card.select_one(selector)
            if elem:
                description = elem.get_text(' ', strip=True)
                if len(description) > 300:
                    description = description[:297] + '...'
                data['description'] = description
                break
        
    except Exception as e:
        logger.debug(f"Error extracting listing data: {e}")
    
    return data

def main():
    """Main scraping function"""
    logger.info("=" * 60)
    logger.info("TAMPA APARTMENTS SCRAPER (Cloudscraper Edition)")
    logger.info("=" * 60)
    
    # Initialize scraper
    scraper = create_scraper()
    warm_up_scraper(scraper)
    
    # Open CSV file
    output_file = "tampa_apartments_cloudscraper.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Property Title',
            'Prices',
            'Phone',
            'Email Available',
            'Description'
        ])
        
        total_listings = 0
        
        # Scrape pages 1 through 17
        for page_num in range(1, 18):
            page_start_time = time.time()
            
            # Construct URL
            if page_num == 1:
                url = 'https://www.apartments.com/tampa-fl/'
            else:
                url = f'https://www.apartments.com/tampa-fl/{page_num}/'
            
            logger.info(f"\n📄 PAGE {page_num}/17")
            logger.info(f"   URL: {url}")
            
            try:
                # Fetch page
                response = fetch_with_retry(scraper, url)
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find listings using multiple possible selectors
                listings = []
                listing_selectors = [
                    'article.placard',
                    'li.mortar-wrapper',
                    'div.property-item',
                    '[data-tracking="property-item"]',
                    '.placardContainer',
                    '.propertyListing'
                ]
                
                for selector in listing_selectors:
                    listings = soup.select(selector)
                    if listings:
                        logger.info(f"   Found {len(listings)} listings using: '{selector}'")
                        break
                
                if not listings:
                    logger.warning("   No listings found! The page structure may have changed.")
                    # Save for debugging
                    debug_file = f'debug_page_{page_num}.html'
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    logger.info(f"   Saved page HTML to {debug_file}")
                    continue
                
                # Process each listing
                page_listings_count = 0
                for i, listing in enumerate(listings, 1):
                    listing_data = extract_listing_data(listing)
                    
                    if listing_data['title']:  # Only save if we got a title
                        writer.writerow([
                            listing_data['title'],
                            listing_data['prices'],
                            listing_data['phone'],
                            listing_data['email_available'],
                            listing_data['description']
                        ])
                        page_listings_count += 1
                        total_listings += 1
                
                page_time = time.time() - page_start_time
                logger.info(f"   ✅ Saved {page_listings_count} listings from this page")
                logger.info(f"   📊 Total so far: {total_listings} listings")
                logger.info(f"   ⏱️  Page processed in {page_time:.1f} seconds")
                
                # Delay between pages (except after last page)
                if page_num < 17:
                    # Dynamic delay based on page number
                    if page_num % 5 == 0:
                        delay = random.uniform(20, 30)  # Longer delay every 5 pages
                        logger.info(f"   ⏳ Taking longer break: {delay:.1f}s...")
                    elif page_num % 3 == 0:
                        delay = random.uniform(12, 18)  # Medium delay every 3 pages
                        logger.info(f"   ⏳ Medium break: {delay:.1f}s...")
                    else:
                        delay = random.uniform(8, 15)  # Normal delay
                        logger.info(f"   ⏳ Short break: {delay:.1f}s...")
                    
                    time.sleep(delay)
                
            except cloudscraper.exceptions.CloudflareChallengeError as e:
                logger.error(f"   ❌ Cloudflare blocked the request: {e}")
                logger.info("   Waiting 60 seconds before continuing...")
                time.sleep(60)
                continue
                
            except Exception as e:
                logger.error(f"   ❌ Error processing page {page_num}: {type(e).__name__}: {e}")
                logger.info("   Waiting 30 seconds before next page...")
                time.sleep(30)
                continue
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("✨ SCRAPING COMPLETED SUCCESSFULLY!")
    logger.info(f"📁 Output file: {output_file}")
    logger.info(f"📊 Total listings scraped: {total_listings}")
    logger.info("=" * 60)
    
    # Clean up
    scraper.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Scraping interrupted by user")
    except Exception as e:
        logger.error(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Program ended")
