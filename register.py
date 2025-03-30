from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from db import connect_to_db

auth_register_bp = Blueprint('auth_register', __name__) 


@auth_register_bp.route('/register', methods=['GET', 'POST'])
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
                query = "INSERT INTO users (fname, lname, username, email, password) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (fname, lname, username, email, pwd1))
                connection.commit()
                return redirect(url_for('auth_login.login'))  # Redirect to login page after successful registration
            except Error as e:
                return f"Error: {e}"
            finally:
                cursor.close()
                connection.close()
        else:
            return "Failed to connect to the database."

    return render_template('Registration.html')
