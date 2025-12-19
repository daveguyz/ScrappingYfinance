from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_spx_options_table():
    # Chrome options for speed
    options = Options()
    options.add_argument("--headless=new")   # fast headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--blink-settings=imagesEnabled=false")

    driver = webdriver.Chrome(options=options)

    try:
        url = "https://finance.yahoo.com/quote/%5ESPX/options/"
        driver.get(url)

        # Wait only until the table exists (fast + reliable)
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.yf-1oeiges"))
        )

        rows = table.find_elements(By.TAG_NAME, "tr")

        table_data = []

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text for cell in cells]
            if row_data:
                table_data.append(row_data)

        return table_data

    finally:
        driver.quit()


if __name__ == "__main__":
    data = fetch_spx_options_table()
    for row in data:
        print("\t".join(row))
