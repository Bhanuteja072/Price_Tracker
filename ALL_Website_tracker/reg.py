

from flask import Flask, render_template, request, redirect, url_for,send_file
import os
import mysql.connector
from mysql.connector import Error
import requests as r
import bs4
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt
import io
import datetime

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('login.html')

# Email credentials
sender_email = "Your email"
sender_password = "Your app password"

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
            password='Your Password',
            database='Your database name'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        connection = connect_to_db()
        if connection:
            cursor = connection.cursor()
            
            if role == "admin":
                query = "SELECT * FROM Table name WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                admin = cursor.fetchone()

                if admin:
                    return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
                else:
                    return "Invalid admin credentials, please try again."
            
            else:
                query = "SELECT * FROM Your_Table_Name WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                user = cursor.fetchone()

                if user:
                    return redirect(url_for('index'))  # Redirect to user page
                else:
                    return "Invalid credentials, please try again."

            cursor.close()
            connection.close()
        return "Failed to connect to the database."

    return render_template('login.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        email = request.form['email']
        pwd1 = request.form['pwd1']
        pwd2 = request.form['pwd2']

        if pwd1 != pwd2:
            return "Passwords do not match, please try again."

        connection = connect_to_db()
        if connection:
            cursor = connection.cursor()
            try:
                query = "INSERT INTO Your_Table_Name (fname, lname, username, email, password) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (fname, lname, username, email, pwd1))
                connection.commit()
                return redirect(url_for('login'))  # Redirect to login page after successful registration
            except Error as e:
                return f"Error: {e}"
            finally:
                cursor.close()
                connection.close()
        else:
            return "Failed to connect to the database."

    return render_template('Registration.html')

# Admin Dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM Your_Table_Name"
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('admin_dashboard.html', users=users)

# Index route (after login)
@app.route('/index')
def index():
    return render_template('index.html')







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




# Function to send email alert
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")









def stop_tracking(product_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        query = "UPDATE Your_table_name SET tracking_active = 0 WHERE id = %s"
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
    else:
        return render_template('error.html', message="Currently, only Amazon and Flipkart and Meesho  URLs are supported.")

    if current_price is None:
        return render_template('error.html', message="Unable to fetch the price. Try again later.")

    # Store tracking details in the database
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        query = "INSERT INTO Your_table_name (product_url, target_price, email, tracking_active) VALUES (%s, %s, %s, 1)"

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

        # query = "SELECT id, product_url, target_price, email, email_alert_sent FROM tracked_products ORDER BY id DESC LIMIT 1"
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

scheduler.add_job(func=periodic_scrape, trigger="interval", minutes=5)













 
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
        query = "SELECT created_at, tracked_price FROM Your_table_name WHERE id BETWEEN %s AND %s ORDER BY id ASC"

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
    app.run(debug=True, use_reloader=False, threaded=True)

