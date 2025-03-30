from flask import Blueprint, render_template, request, redirect, url_for
from db import connect_to_db  # Import your database connection function

auth_login_bp = Blueprint('auth_login', __name__)  # Create a Blueprint for authentication

@auth_login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        connection = connect_to_db()
        if connection:
            cursor = connection.cursor()
            
            if role == "admin":
                query = "SELECT * FROM admin WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                admin = cursor.fetchone()

                if admin:
                    return redirect(url_for('auth_admin.admin_dashboard'))  # Redirect to admin dashboard
                else:
                    return "Invalid admin credentials, please try again."
            
            else:
                query = "SELECT * FROM users WHERE username = %s AND password = %s"
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
