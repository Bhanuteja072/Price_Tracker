import requests as r
import bs4
def extract_flipkart_price(url, headers):
    try:
        response = r.get(url, headers=headers)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        price_element = soup.find('div', {'class': 'Nx9bqj CxhGGd'})  # Flipkart price class
        if price_element:
            price = float(price_element.get_text(strip=True).replace('₹', '').replace(',', ''))
            return price
    except Exception as e:
        print(f"Flipkart price extraction error: {e}")
    return None