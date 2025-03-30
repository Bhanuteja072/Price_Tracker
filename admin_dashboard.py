from flask import Blueprint, render_template, request
from db import connect_to_db 

auth_admin_bp = Blueprint('auth_admin', __name__) 
@auth_admin_bp.route('/admin_dashboard')
def admin_dashboard():
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM users"
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('admin_dashboard.html', users=users)