# Price_Tracker
This is a Flask-based web application that tracks product prices from Amazon and Flipkart. Users can register, log in, add products to track, and receive email alerts when prices drop below a target value. The application also includes an admin dashboard and a price trend analysis feature.

## Features
- User authentication (registration & login)
- Admin dashboard to view registered users
- Track product prices from Amazon ,Flipkart,Myntra,Meesho and Ajio
- Receive email alerts when prices drop
- Background scheduler to periodically check prices
- Visual price trend analysis using Matplotlib

## Tech Stack
- Backend: Flask, MySQL, BeautifulSoup, APScheduler
- Frontend: HTML, CSS, JavaScript
- Database: MySQL
- Email Service: SMTP (Gmail)

## Installation
### 1. Clone the Repository
git clone https://github.com/yourusername/yourrepository.git
cd yourrepository

### 2. Install Dependencies
pip install flask mysql-connector-python requests beautifulsoup4 smtplib matplotlib apscheduler

### 3. Configure Database
- Create a MySQL database
- Update the database credentials in the `connect_to_db()` function in `app.py`
- Create necessary tables for users and price tracking

### 4. Run the Application
python app.py

### 5. Open in Browser
Visit: `http://127.0.0.1:5000/`

## Usage
1. **Register/Login** as a user or admin.
2. **Add a product URL** (Amazon/Flipkart) and set a target price.
3. The system will track the price and **send an email alert** when the price drops.
4. Admins can view all users in the **admin dashboard**.
5. Users can **analyze price trends** using the analysis feature.





