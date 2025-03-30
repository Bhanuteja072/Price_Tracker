from flask import Flask, render_template, request, redirect, url_for,send_file
import os
from login import auth_login_bp 
from register import auth_register_bp
from admin_dashboard import auth_admin_bp
from amazon import extract_amazon_price
from flipkart import extract_flipkart_price
from myntra import extract_myntra_price
from meesho import extract_meesho_price
from ajio import extract_ajio_price
import mysql.connector
from mysql.connector import Error
from apscheduler.schedulers.background import BackgroundScheduler
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import sys
sys.stdout.reconfigure(encoding='utf-8')



app = Flask(__name__)
@app.route('/')
def home():
    return render_template('login.html')


def get_sender_credentials():
    sender_email = "bhanupusarla7@gmail.com"
    sender_password = "mltp zdro pqcs uvug"
    return sender_email, sender_password

# Tracking list
tracking_list = []

# Background scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Database connection details
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='bhanu@123',
            database='newr'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None



app.register_blueprint(auth_register_bp, url_prefix='/auth')
app.register_blueprint(auth_login_bp, url_prefix='/auth')
app.register_blueprint(auth_admin_bp,url_prefix='/auth')
# app.register_blueprint(auth_analysis_bp,url_prefix='/auth')


# Index route (after login)
@app.route('/index')
def index():
    return render_template('index.html')

            
@app.route('/stop-tracking/<int:product_id>', methods=['POST'])
def stop_tracking(product_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        query = "UPDATE tracked_products SET tracking_active = 0 WHERE id = %s"
        cursor.execute(query, (product_id,))
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('index'))  # Redirect back to the user dashboard


@app.route('/add-to-tracking', methods=['POST'])
def add_to_tracking():
    product_url = request.form['product_url']
    target_price = float(request.form['target_price'])
    email = request.form['email']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    # Detect the website
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
        return render_template('error.html', message="Currently, only Amazon and Flipkart and Myntra  URLs are supported.")

    if current_price is None:
        return render_template('error.html', message="Unable to fetch the price. Try again later.")

    # Store tracking details in the database
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        query = "INSERT INTO tracked_products (product_url, target_price, email, tracking_active) VALUES (%s, %s, %s, 1)"

        # query = "INSERT INTO tracked_products (product_url, target_price, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (product_url, target_price, email))
        connection.commit()
        cursor.close()
        connection.close()


        product_id = cursor.lastrowid  


    # Send an alert if the price is already lower

    tracking_list.append({
            'product_url': product_url,
            'target_price': target_price,
            'email': email,
        })
    if current_price <= target_price:
        from send_emaill import send_email
        send_email(
            to_email=email,
            subject="Price Drop Alert!",
            body=f"The product at {product_url} is now available for ₹{current_price}, which is within or below your target price of ₹{target_price}!"
        )

    return render_template('price_display.html', product_id=product_id,product_url=product_url, final_price=current_price, target_price=target_price)


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
                from send_emaill import send_email
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

@app.route('/Products',methods=['GET','POST'])
def Products():
    return render_template("/Products.html")


@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    button_id = request.form.get("button_id")

    button_id = int(button_id)
    id_ranges = {
        1: ("Noise buds ",18, 50),
        2: ("Nokio",52, 70),
        3: ("Moto Mobile",71, 77),
        4: ("Boat Neck band",78, 86)
    }
    if button_id in id_ranges:
        product_name,id_start, id_end = id_ranges[button_id]

    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        # query = "SELECT created_at, tracked_price FROM price_history  WHERE id BETWEEN 18 AND 50  ORDER BY id ASC"
        query = "SELECT created_at, tracked_price FROM price_history WHERE id BETWEEN %s AND %s ORDER BY id ASC"

        # cursor.execute(query)
        cursor.execute(query, (id_start, id_end))
        data = cursor.fetchall()
        cursor.close()
        connection.close()

        if not data:  # Handle empty data case
            return render_template("analysis.html", graph_url=None, graph_data=[])

        # Process data
        graph_data = [{"id": row[0], "target_price": row[1]} for row in data]
        print("Graph Data:", graph_data)  # Debugging

        # Extract values for plotting
        x = [row[0] for row in data]
        y = [row[1] for row in data]

        # Create a plot
        plt.figure(figsize=(8, 5))
        plt.plot(x, y, marker='o', linestyle='-', color='b', label="Tracked Price")
        plt.xlabel("Created_At")
        plt.ylabel("Tracked Price")
        plt.title(f"Price Trend for {product_name}")  # Use product name

        plt.ylim(min(y) - 50, max(y) + 50)  # Adjusted range to avoid 500 hardcoding
        plt.legend()
        plt.grid(True)

        # Save the plot in the static folder
        img_path = os.path.join("static", f"graph_{button_id}.png")
        plt.savefig(img_path)
        plt.close()
        return render_template("analysis.html", graph_url=f"static/graph_{button_id}.png", graph_data=data, product_name=product_name)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port='5000',debug=True, use_reloader=False, threaded=True)


