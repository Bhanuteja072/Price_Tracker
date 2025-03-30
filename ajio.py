from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_ajio_price(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")  
        chrome_options.add_argument("--disable-gpu")  
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-dev-shm-usage")  
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36')

        driver = webdriver.Chrome(options=chrome_options)

        driver.get(url)

        # Wait for the price element to load
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "prod-sp"))
        )
        # product_price = product_price.replace("₹", "").strip()

        product_price = price_element.text.strip()  # Extract the price)
        driver.quit()
        return float(product_price.replace('₹', '').replace(',', ''))
    except Exception as e:
        print(f"Meesho price extraction error: {e}")
    finally:
        driver.quit()
    return None

