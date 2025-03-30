from db import connect_to_db
from amazon import extract_amazon_price
from flipkart import extract_flipkart_price
from myntra import extract_myntra_price
from meesho import extract_meesho_price
from ajio import extract_ajio_price
from reg import send_email
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()
tracking_list = []




def periodic_scrape():
    print("Running periodic scrape...")

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        # Fetch only the latest added product
        query = "SELECT id, product_url, target_price, email, email_alert_sent FROM tracked_products WHERE tracking_active = 1 ORDER BY id DESC LIMIT 1"

        cursor.execute(query)
        latest_product = cursor.fetchone()
        if latest_product:
            product_id, product_url, target_price, email,email_alert_sent = latest_product

            # if email_alert_sent:
            #     print(f"Alert already sent for {email} and Skipping...")
            #     cursor.close()
            #     connection.close()
            #     return 
            
            headers = {'User-Agent': 'Mozilla/5.0'}

            # Detect website and extract price accordingly
            if "amazon.in" in product_url:
                current_price = extract_amazon_price(product_url, headers)
            elif "flipkart.com" in product_url:
                current_price = extract_flipkart_price(product_url, headers)
            elif "myntra.com" in product_url:
                current_price = extract_myntra_price(product_url)
            elif "meesho.com" in product_url:
                current_price = extract_meesho_price(product_url)
            elif "ajio.com" in product_url:
                current_price = extract_ajio_price(product_url)
            else:
                print("Unsupported URL")
                cursor.close()
                connection.close()
                return  # Exit function if the URL is not supported

            if current_price is None:
                print("Price not tracked")
                cursor.close()
                connection.close()
                return  # Exit function if price couldn't be fetched

            # Update the price in the database
            query = "INSERT INTO price_history (product_url, tracked_price) VALUES (%s, %s)"
            cursor.execute(query, (product_url, current_price))
            connection.commit()
            if email_alert_sent:
                print(f"Alert already sent for {email} and Skipping...")
                cursor.close()
                connection.close()
                return 


            # Send email if price drops
            if current_price <= target_price:
                send_email(
                    to_email=email,
                    subject="Price Drop Alert!",
                    body=f"The product at {product_url} is now available for ₹{current_price}, which is within or below your target price of ₹{target_price}!"
                )
                query = "UPDATE tracked_products SET email_alert_sent = 1 WHERE id = %s"
                cursor.execute(query, (product_id,))
                connection.commit()


        else:
            print("No products found in the database.")

        cursor.close()
        connection.close()

# Schedule scraping every 1 minute, but only for the latest product
scheduler.add_job(func=periodic_scrape, trigger="interval", minutes=1)




