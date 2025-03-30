import requests as r
import bs4
def extract_amazon_price(url, headers):
    try:
        response = r.get(url, headers=headers)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        price_element = soup.find(class_='a-price-whole')
        if price_element:
            price = float(price_element.get_text(strip=True).replace(',', ''))
            return price
    except Exception as e:
        print(f"Amazon price extraction error: {e}")
    return None