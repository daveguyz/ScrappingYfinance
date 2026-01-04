import csv
import time
import random
import logging
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class UltimateStealthScraper:
    def __init__(self, headless=False, use_proxy=False):
        self.headless = headless
        self.use_proxy = use_proxy
        self.driver = None
        self.wait = None
        self.ua = UserAgent()
        self.action = None
        
        # Residential proxies (if you have them)
        self.proxies = [
            # Add your proxies here in format: 'ip:port' or 'user:pass@ip:port'
            # Example: '45.76.89.142:8080'
        ]
        
    def get_random_user_agent(self):
        """Get random realistic user agent"""
        return self.ua.random
    
    def get_random_viewport(self):
        """Get random viewport size"""
        viewports = [
            (1920, 1080), (1366, 768), (1536, 864), 
            (1440, 900), (1280, 720), (1600, 900),
            (2560, 1440), (1680, 1050), (1920, 1200)
        ]
        return random.choice(viewports)
    
    def get_random_mac_address(self):
        """Generate random MAC address (for fingerprinting)"""
        return ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])
    
    def create_stealth_options(self):
        """Create Chrome options with all stealth features"""
        options = Options()
        
        # ===== 1. BASIC STEALTH SETTINGS =====
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # ===== 2. DISABLE AUTOMATION INDICATORS =====
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-features=AudioServiceOutOfProcess')
        
        # ===== 3. RANDOMIZED SETTINGS =====
        # Random User Agent
        user_agent = self.get_random_user_agent()
        options.add_argument(f'--user-agent={user_agent}')
        logger.info(f"Using User Agent: {user_agent[:50]}...")
        
        # Random Viewport
        width, height = self.get_random_viewport()
        options.add_argument(f'--window-size={width},{height}')
        logger.info(f"Viewport size: {width}x{height}")
        
        # ===== 4. ANTI-DETECTION FEATURES =====
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-3d-apis')
        options.add_argument('--disable-webgl')
        options.add_argument('--disable-reading-from-canvas')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        # ===== 5. LANGUAGE AND LOCALE =====
        options.add_argument('--lang=en-US')
        options.add_argument('--accept-lang=en-US,en;q=0.9')
        
        # ===== 6. PROXY SUPPORT =====
        if self.use_proxy and self.proxies:
            proxy = random.choice(self.proxies)
            options.add_argument(f'--proxy-server={proxy}')
            logger.info(f"Using proxy: {proxy}")
        
        # ===== 7. HEADLESS MODE DETECTION BYPASS =====
        if self.headless:
            options.add_argument('--headless=new')
            # Additional headless bypass arguments
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--remote-debugging-address=0.0.0.0')
        
        # ===== 8. RANDOM BROWSER FINGERPRINT =====
        # Create random profile directory
        profile_id = random.randint(1000, 9999)
        profile_dir = f'chrome_profile_{profile_id}'
        options.add_argument(f'--user-data-dir={os.path.join(os.getcwd(), profile_dir)}')
        
        # ===== 9. ADDITIONAL STEALTH CAPABILITIES =====
        options.add_argument('--disable-client-side-phishing-detection')
        options.add_argument('--disable-component-update')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-domain-reliability')
        options.add_argument('--disable-sync')
        options.add_argument('--metrics-recording-only')
        options.add_argument('--safebrowsing-disable-auto-update')
        
        # ===== 10. DISABLE AUTOFILL AND PASSWORD SAVING =====
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2,
            "profile.managed_default_content_settings.images": 1,
            "profile.default_content_setting_values.cookies": 1,
            "profile.default_content_setting_values.popups": 2,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "download_restrictions": 3,
            "plugins.always_open_pdf_externally": True,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "safebrowsing.disable_download_protection": True,
            "autofill.profile_enabled": False,
            "autofill.credit_card_enabled": False,
        }
        options.add_experimental_option("prefs", prefs)
        
        # ===== 11. RANDOMIZE OTHER BROWSER PROPERTIES =====
        options.add_argument(f'--disable-features=TranslateUI')
        options.add_argument('--disable-bundled-ppapi-flash')
        options.add_argument('--disable-features=NetworkService')
        
        return options
    
    def execute_advanced_stealth_js(self):
        """Execute advanced JavaScript to hide automation"""
        stealth_scripts = [
            # Script 1: Hide webdriver
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """,
            
            # Script 2: Fake plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {0: {type: "application/x-google-chrome-pdf", description: "Portable Document Format"}, description: "Portable Document Format", filename: "internal-pdf-viewer", length: 1, name: "Chrome PDF Plugin"},
                    {0: {type: "application/pdf", description: "Portable Document Format"}, description: "Portable Document Format", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", length: 1, name: "Chrome PDF Viewer"},
                    {0: {type: "application/x-nacl", description: "Native Client Executable"}, description: "Native Client Executable", filename: "internal-nacl-plugin", length: 1, name: "Native Client"},
                    {0: {type: "application/x-pnacl", description: "Portable Native Client Executable"}, description: "Portable Native Client Executable", filename: "internal-pnacl-plugin", length: 1, name: "Portable Native Client"}
                ]
            });
            """,
            
            # Script 3: Fake languages
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'es']
            });
            
            Object.defineProperty(navigator, 'language', {
                get: () => 'en-US'
            });
            """,
            
            # Script 4: Fake Chrome properties
            """
            window.chrome = {
                app: {
                    isInstalled: false,
                    InstallState: {DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed'},
                    RunningState: {CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running'}
                },
                webstore: {
                    onInstallStageChanged: {},
                    onDownloadProgress: {}
                },
                runtime: {
                    PlatformOs: {MAC: 'mac', WIN: 'win', ANDROID: 'android', CROS: 'cros', LINUX: 'linux', OPENBSD: 'openbsd'},
                    PlatformArch: {ARM: 'arm', X86_32: 'x86-32', X86_64: 'x86-64'},
                    PlatformNaclArch: {ARM: 'arm', X86_32: 'x86-32', X86_64: 'x86-64'},
                    RequestUpdateCheckStatus: {THROTTLED: 'throttled', NO_UPDATE: 'no_update', UPDATE_AVAILABLE: 'update_available'},
                    OnInstalledReason: {INSTALL: 'install', UPDATE: 'update', CHROME_UPDATE: 'chrome_update', SHARED_MODULE_UPDATE: 'shared_module_update'},
                    OnRestartRequiredReason: {APP_UPDATE: 'app_update', OS_UPDATE: 'os_update', PERIODIC: 'periodic'}
                }
            };
            """,
            
            # Script 5: Fake permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """,
            
            # Script 6: Fake screen properties
            """
            Object.defineProperty(screen, 'width', { get: () => %d });
            Object.defineProperty(screen, 'height', { get: () => %d });
            Object.defineProperty(screen, 'availWidth', { get: () => %d });
            Object.defineProperty(screen, 'availHeight', { get: () => %d });
            Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
            Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
            """ % (1920, 1080, 1920, 1040),
            
            # Script 7: Fake hardware concurrency
            """
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => %d
            });
            """ % random.choice([4, 6, 8, 12]),
            
            # Script 8: Fake device memory
            """
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => %d
            });
            """ % random.choice([4, 8, 16]),
            
            # Script 9: Fake connection
            """
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    downlink: %f,
                    effectiveType: '%s',
                    rtt: %d,
                    saveData: false,
                    onchange: null
                })
            });
            """ % (random.uniform(5, 50), random.choice(['4g', '3g']), random.randint(50, 200)),
            
            # Script 10: Override getParameter for WebGL
            """
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return '%s';
                }
                if (parameter === 37446) {
                    return '%s';
                }
                return getParameter(parameter);
            };
            """ % ('Intel Inc.', 'Intel Iris OpenGL Engine'),
        ]
        
        for script in stealth_scripts:
            try:
                self.driver.execute_script(script)
                time.sleep(0.1)
            except:
                pass
    
    def create_driver(self):
        """Create and configure the stealth driver"""
        logger.info("Creating ultimate stealth Chrome driver...")
        
        # Create options
        options = self.create_stealth_options()
        
        # Set up service
        service = Service(ChromeDriverManager().install())
        
        # Create driver
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Execute stealth JavaScript
        self.execute_advanced_stealth_js()
        
        # Initialize action chains
        self.action = ActionChains(self.driver)
        
        # Set up wait
        self.wait = WebDriverWait(self.driver, 15)
        
        logger.info("Stealth driver created successfully")
        return self.driver
    
    def human_like_mouse_movement(self, element=None, duration=1):
        """Simulate human-like mouse movement"""
        try:
            if element:
                # Move to element with human-like path
                size = element.size
                location = element.location
                
                # Generate random path to element
                points = []
                start_x, start_y = 0, 0
                
                for i in range(random.randint(3, 7)):
                    if i == 0:
                        points.append((start_x, start_y))
                    elif i < 3:
                        # First few points are random
                        points.append((random.randint(0, 500), random.randint(0, 300)))
                    else:
                        # Gradually move toward target
                        target_x = location['x'] + size['width'] // 2
                        target_y = location['y'] + size['height'] // 2
                        progress = i / 6
                        points.append((
                            int(start_x + (target_x - start_x) * progress + random.randint(-20, 20)),
                            int(start_y + (target_y - start_y) * progress + random.randint(-20, 20))
                        ))
                
                # Execute movements
                for x, y in points:
                    self.driver.execute_script(f"""
                        var evt = new MouseEvent('mousemove', {{
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: {x},
                            clientY: {y}
                        }});
                        document.dispatchEvent(evt);
                    """)
                    time.sleep(random.uniform(0.05, 0.2))
                
                # Final hover
                if random.random() < 0.3:  # 30% chance to hover
                    time.sleep(random.uniform(0.3, 0.8))
            
            # Random mouse wiggle
            for _ in range(random.randint(1, 3)):
                x = random.randint(0, 500)
                y = random.randint(0, 300)
                self.driver.execute_script(f"""
                    var evt = new MouseEvent('mousemove', {{
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        clientX: {x},
                        clientY: {y}
                    }});
                    document.dispatchEvent(evt);
                """)
                time.sleep(random.uniform(0.1, 0.3))
                
        except Exception as e:
            logger.debug(f"Mouse movement error: {e}")
    
    def human_like_scroll(self):
        """Simulate human-like scrolling"""
        try:
            scroll_duration = random.uniform(1, 3)
            scroll_direction = random.choice(['down', 'up', 'mixed'])
            scroll_amount = random.randint(300, 1000)
            
            if scroll_direction == 'down':
                # Scroll down with random pauses
                scrolls = random.randint(3, 8)
                for i in range(scrolls):
                    scroll_step = scroll_amount // scrolls + random.randint(-50, 50)
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                    pause = random.uniform(0.1, 0.5)
                    time.sleep(pause)
                    
                    # Random chance to stop and read
                    if random.random() < 0.2:
                        read_time = random.uniform(0.5, 2)
                        time.sleep(read_time)
            
            elif scroll_direction == 'up':
                # Scroll up a bit (like checking something)
                self.driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)});")
                time.sleep(random.uniform(0.3, 0.8))
            
            else:  # mixed
                # Scroll down then up a bit
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.5, 1))
                self.driver.execute_script(f"window.scrollBy(0, -{random.randint(50, 200)});")
                time.sleep(random.uniform(0.2, 0.5))
        
        except Exception as e:
            logger.debug(f"Scroll error: {e}")
    
    def human_like_typing(self, element, text):
        """Type like a human with imperfections"""
        try:
            element.click()
            time.sleep(random.uniform(0.2, 0.5))
            
            for i, char in enumerate(text):
                # Type character
                element.send_keys(char)
                
                # Random typing speed
                if i % random.randint(2, 5) == 0:
                    # Pause like thinking
                    time.sleep(random.uniform(0.1, 0.3))
                else:
                    time.sleep(random.uniform(0.05, 0.15))
                
                # 2% chance of typo
                if random.random() < 0.02:
                    element.send_keys(Keys.BACK_SPACE)
                    time.sleep(random.uniform(0.1, 0.3))
                    element.send_keys(char)
                
                # 1% chance of longer pause
                if random.random() < 0.01:
                    time.sleep(random.uniform(0.5, 1))
        
        except Exception as e:
            logger.debug(f"Typing error: {e}")
    
    def random_browser_behavior(self):
        """Simulate random browser usage patterns"""
        behaviors = [
            self.simulate_tab_switching,
            self.simulate_page_refresh,
            self.simulate_bookmarking,
            self.simulate_zooming,
            self.simulate_context_menu,
        ]
        
        # Randomly execute 1-2 behaviors
        for behavior in random.sample(behaviors, random.randint(1, 2)):
            try:
                behavior()
            except:
                pass
    
    def simulate_tab_switching(self):
        """Simulate tab switching"""
        if random.random() < 0.3:  # 30% chance
            self.driver.execute_script("window.open('about:blank', '_blank');")
            time.sleep(random.uniform(0.5, 1.5))
            
            # Switch back to original tab
            self.driver.switch_to.window(self.driver.window_handles[0])
            time.sleep(random.uniform(0.3, 0.8))
    
    def simulate_page_refresh(self):
        """Simulate page refresh"""
        if random.random() < 0.1:  # 10% chance
            self.driver.refresh()
            time.sleep(random.uniform(2, 4))
    
    def simulate_bookmarking(self):
        """Simulate bookmark action (Ctrl+D)"""
        if random.random() < 0.05:  # 5% chance
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('d').key_up(Keys.CONTROL).perform()
            time.sleep(random.uniform(0.5, 1))
            # Escape the bookmark dialog
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
    
    def simulate_zooming(self):
        """Simulate zooming in/out"""
        if random.random() < 0.1:  # 10% chance
            zoom_level = random.choice([0.9, 1.0, 1.1, 1.2])
            self.driver.execute_script(f"document.body.style.zoom = '{zoom_level}'")
            time.sleep(random.uniform(0.5, 1.5))
    
    def simulate_context_menu(self):
        """Simulate right-click context menu"""
        if random.random() < 0.05:  # 5% chance
            ActionChains(self.driver).context_click().perform()
            time.sleep(random.uniform(0.2, 0.5))
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
    
    def wait_like_human(self, min_time=2, max_time=6):
        """Wait with human-like random timing"""
        wait_time = random.uniform(min_time, max_time)
        
        # During wait, simulate some activity
        start_time = time.time()
        while time.time() - start_time < wait_time:
            # Occasionally move mouse
            if random.random() < 0.3:
                self.human_like_mouse_movement()
            
            # Small pauses
            time.sleep(random.uniform(0.2, 0.8))
    
    def scrape_page(self, url):
        """Scrape a single page with ultimate stealth"""
        logger.info(f"🕷️  Navigating to: {url}")
        
        try:
            # Navigate
            self.driver.get(url)
            
            # Wait like human
            self.wait_like_human(3, 6)
            
            # Random browser behavior
            self.random_browser_behavior()
            
            # Human-like scrolling
            self.human_like_scroll()
            
            # More waiting
            self.wait_like_human(2, 4)
            
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))
            
            # Scroll up a bit
            self.driver.execute_script("window.scrollBy(0, -200);")
            time.sleep(random.uniform(0.5, 1))
            
            # Extract data
            return self.extract_listings()
            
        except Exception as e:
            logger.error(f"Error scraping page: {e}")
            return []
    
    def extract_listings(self):
        """Extract apartment listings"""
        listings = []
        
        try:
            # Multiple selectors for robustness
            selectors = [
                "article.placard",
                "li.mortar-wrapper",
                '[data-tracking="property-item"]',
                ".property-item",
                ".placardContainer"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Found {len(elements)} listings with: {selector}")
                        break
                except:
                    continue
            
            if not elements:
                logger.warning("No listings found")
                return []
            
            # Process each listing
            for i, element in enumerate(elements):
                try:
                    # Simulate viewing each listing
                    self.human_like_mouse_movement(element)
                    
                    # Scroll to element
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(random.uniform(0.1, 0.3))
                    
                    # Extract data
                    data = self.extract_listing_data(element)
                    if data and data.get('title'):
                        listings.append(data)
                    
                    # Pause between listings (like reading)
                    if i % random.randint(3, 6) == 0:
                        time.sleep(random.uniform(0.2, 0.5))
                    
                except Exception as e:
                    logger.debug(f"Error processing listing {i}: {e}")
                    continue
            
            return listings
            
        except Exception as e:
            logger.error(f"Error extracting listings: {e}")
            return []
    
    def extract_listing_data(self, element):
        """Extract data from listing element"""
        try:
            html = element.get_attribute('outerHTML')
            
            # Simple parsing (no BeautifulSoup needed)
            data = {
                'title': '',
                'prices': '',
                'phone': '',
                'email_available': 'No',
                'description': ''
            }
            
            # Extract title
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, 'span.propertyTitleWrapper, a.property-link, .placardTitle')
                data['title'] = title_elem.text.strip() if title_elem else ''
            except:
                pass
            
            # Extract prices
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, 'p.property-pricing, .price-range, .rentLabel')
                data['prices'] = price_elem.text.strip() if price_elem else ''
            except:
                pass
            
            # Extract phone
            try:
                phone_elem = element.find_element(By.CSS_SELECTOR, 'div.phone, .phoneNumber, .contact-phone')
                data['phone'] = phone_elem.text.strip() if phone_elem else ''
            except:
                pass
            
            # Check for email
            try:
                email_elems = element.find_elements(By.CSS_SELECTOR, 'a[href*="mailto:"], a:contains("Email")')
                if email_elems:
                    data['email_available'] = 'Yes'
            except:
                pass
            
            # Extract description
            try:
                desc_elem = element.find_element(By.CSS_SELECTOR, 'div.property-description, .description, .property-details')
                if desc_elem:
                    desc = desc_elem.text.strip()
                    if len(desc) > 200:
                        desc = desc[:197] + "..."
                    data['description'] = desc
            except:
                pass
            
            return data
            
        except Exception as e:
            logger.debug(f"Error extracting data: {e}")
            return {}
    
    def run(self):
        """Main scraping function"""
        logger.info("=" * 70)
        logger.info("ULTIMATE STEALTH APARTMENTS.COM SCRAPER")
        logger.info("=" * 70)
        
        # Create driver
        self.create_driver()
        
        try:
            # Create CSV file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tampa_apartments_stealth_{timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Property Title', 'Prices', 'Phone', 'Email Available', 'Description'])
                
                total_listings = 0
                
                # Scrape pages 1-17
                for page in range(1, 18):
                    page_start = time.time()
                    
                    # Build URL
                    if page == 1:
                        url = "https://www.apartments.com/tampa-fl/"
                    else:
                        url = f"https://www.apartments.com/tampa-fl/{page}/"
                    
                    logger.info(f"\n📄 PAGE {page}/17")
                    logger.info(f"   URL: {url}")
                    
                    # Scrape page
                    listings = self.scrape_page(url)
                    
                    if listings:
                        # Save listings
                        for listing in listings:
                            writer.writerow([
                                listing.get('title', ''),
                                listing.get('prices', ''),
                                listing.get('phone', ''),
                                listing.get('email_available', ''),
                                listing.get('description', '')
                            ])
                        
                        logger.info(f"   ✅ Saved {len(listings)} listings")
                        total_listings += len(listings)
                    
                    # Page statistics
                    page_time = time.time() - page_start
                    logger.info(f"   ⏱️  Page time: {page_time:.1f}s")
                    logger.info(f"   📊 Total: {total_listings} listings")
                    
                    # Human-like delay between pages
                    if page < 17:
                        # Variable delay based on progress
                        if page % 5 == 0:
                            delay = random.uniform(25, 40)
                            logger.info(f"   😴 Long break: {delay:.1f}s")
                        elif page % 3 == 0:
                            delay = random.uniform(15, 25)
                            logger.info(f"   ☕ Medium break: {delay:.1f}s")
                        else:
                            delay = random.uniform(10, 18)
                            logger.info(f"   ⏳ Short break: {delay:.1f}s")
                        
                        time.sleep(delay)
                
                # Final report
                logger.info("\n" + "=" * 70)
                logger.info(f"✨ SCRAPING COMPLETE!")
                logger.info(f"📁 File: {filename}")
                logger.info(f"📊 Total listings: {total_listings}")
                logger.info("=" * 70)
        
        except KeyboardInterrupt:
            logger.info("\n⚠️  Scraping interrupted by user")
        
        except Exception as e:
            logger.error(f"\n❌ Fatal error: {e}")
        
        finally:
            # Always quit driver
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")

# Installation requirements
REQUIRED_PACKAGES = """
Required packages:
pip install selenium webdriver-manager fake-useragent numpy

Optional for extra stealth:
pip install selenium-stealth  # Additional stealth features
"""

if __name__ == '__main__':
    print(REQUIRED_PACKAGES)
    
    # Choose mode: headless=False to see browser, headless=True for invisible
    scraper = UltimateStealthScraper(headless=False, use_proxy=False)
    scraper.run()
