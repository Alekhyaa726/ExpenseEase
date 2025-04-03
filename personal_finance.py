from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import mysql.connector
import io
import os
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from pymongo import MongoClient
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

# Connect to the MySQL database
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="4240519Alekhya",
        database="personal_finance_db1",
        autocommit=True
    )
except Exception as e:
    print(f"Database connection error: {e}")
    raise

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'this is a secret'

# Configure static folder
app.static_folder = 'static'

# Add template folder configuration
app.template_folder = 'templates'

expenses = []

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear any existing session
    if 'username' in session:
        session.pop('username', None)
    
    if request.method == 'GET':
        return render_template('login.html', user_logged_in=False)

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                return render_template('login.html', 
                                     error='Please enter both username and password',
                                     user_logged_in=False)
            
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("SELECT username, password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()

            if user and user['password'] == password:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return render_template('login.html', 
                                     error='Invalid username or password', 
                                     user_logged_in=False)
                                     
        except Exception as e:
            print(f"Login error: {e}")
            return render_template('login.html', 
                                 error='An error occurred. Please try again.', 
                                 user_logged_in=False)

@app.route('/sign_up', methods=['GET', 'POST'])
def signup():
    print("Signup route accessed")
    if request.method == 'GET':
        return render_template('register.html', user_logged_in=False)
    
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            name = request.form.get('name')
            phone = request.form.get('phone')
            email = request.form.get('email')
            budget = request.form.get('budget')

            # Debug prints
            print("Received signup data:")
            print(f"Username: {username}")
            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Phone: {phone}")
            print(f"Budget: {budget}")

            # Validate all fields are present
            if not all([username, password, confirm_password, name, phone, email, budget]):
                return render_template('register.html', 
                                     error='All fields are required', 
                                     user_logged_in=False)

            # Validate password match
            if password != confirm_password:
                return render_template('register.html', 
                                     error='Passwords do not match', 
                                     user_logged_in=False)

            cursor = mydb.cursor(dictionary=True)
            
            # Check if username exists
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                cursor.close()
                return render_template('register.html', 
                                     error='Username already exists', 
                                     user_logged_in=False)

            # Check if email exists
            cursor.execute("SELECT emailID FROM profile WHERE emailID = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                return render_template('register.html', 
                                     error='Email already registered', 
                                     user_logged_in=False)

            # Insert user data
            try:
                # Insert into users table
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                             (username, password))

                # Insert into profile table
                cursor.execute("""
                    INSERT INTO profile (Name, Phone, emailID, budget, user) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, phone, email, budget, username))

                mydb.commit()
                cursor.close()
                return redirect('/login')

            except Exception as e:
                mydb.rollback()
                cursor.close()
                print(f"Database error: {e}")
                return render_template('register.html', 
                                     error='Error creating account. Please try again.', 
                                     user_logged_in=False)

        except Exception as e:
            print(f"Signup error: {e}")
            return render_template('register.html', 
                                 error='An error occurred. Please try again.', 
                                 user_logged_in=False)

    return render_template('register.html', user_logged_in=False)

@app.route('/plot_payMode.png')
#@token_required
def plot_payMode():
    fig = create_payModefig()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_payModefig():
    fig = Figure(figsize=(18, 8), dpi=100)
    axis1 = fig.add_subplot(1, 3, 1)
    axis2 = fig.add_subplot(1, 3, 2)
    axis3 = fig.add_subplot(1, 3, 3)
    
    # Give a title to the figure
    fig.suptitle('Analysis of expenses')
    
    uname = session['username']
    
    # Fetch all the expenses by payment mode from the database
    sql_mode = "SELECT mode, SUM(amount) FROM Expense WHERE user = %s GROUP BY mode"
    cursor_mode = mydb.cursor() 
    cursor_mode.execute(sql_mode, (uname,))
    expenses_mode = cursor_mode.fetchall()
    cursor_mode.close()
    
    # Fetch all the expenses by category from the database
    sql_category = "SELECT category, SUM(amount) FROM Expense WHERE user = %s GROUP BY category"
    cursor_category = mydb.cursor() 
    cursor_category.execute(sql_category, (uname,))
    expenses_category = cursor_category.fetchall()
    cursor_category.close()
    
    # Fetch all the expenses by date from the database
    sql_date = "SELECT date_of_txn, SUM(amount) FROM Expense WHERE user = %s GROUP BY date_of_txn"
    cursor_date = mydb.cursor() 
    cursor_date.execute(sql_date, (uname,))
    expenses_date = cursor_date.fetchall()
    cursor_date.close()
    
    if uname == 'admin':
        # Fetch all the expenses by payment mode from the database for admin user
        sql_mode_admin = "SELECT mode, SUM(amount) FROM Expense GROUP BY mode"
        cursor_mode_admin = mydb.cursor() 
        cursor_mode_admin.execute(sql_mode_admin)
        expenses_mode_admin = cursor_mode_admin.fetchall()
        cursor_mode_admin.close()
        
        # Fetch all the expenses by category from the database for admin user
        sql_category_admin = "SELECT category, SUM(amount) FROM Expense GROUP BY category"
        cursor_category_admin = mydb.cursor() 
        cursor_category_admin.execute(sql_category_admin)
        expenses_category_admin = cursor_category_admin.fetchall()
        cursor_category_admin.close()
        
        # Fetch all the expenses by date from the database for admin user
        sql_date_admin = "SELECT date_of_txn, SUM(amount) FROM Expense GROUP BY date_of_txn"
        cursor_date_admin = mydb.cursor() 
        cursor_date_admin.execute(sql_date_admin)
        expenses_date_admin = cursor_date_admin.fetchall()
        cursor_date_admin.close()
        
        expenses_mode = expenses_mode_admin
        expenses_category = expenses_category_admin
        expenses_date = expenses_date_admin
    
    # Plotting expenses by payment mode
    categories_mode = []
    amounts_mode = []
    for expense in expenses_mode:
        categories_mode.append(expense[0])
        amounts_mode.append(expense[1])
    axis1.pie(amounts_mode, labels=categories_mode, autopct='%1.1f%%')
    axis1.set_title('Expenses by Payment Mode')
    
    # Plotting expenses by category
    categories_category = []
    amounts_category = []
    for expense in expenses_category:
        categories_category.append(expense[0])
        amounts_category.append(expense[1])
    axis2.pie(amounts_category, labels=categories_category, autopct='%1.1f%%')
    axis2.set_title('Expenses by Category')
    
    # Plotting expenses by date
    categories_date = []
    amounts_date = []
    for expense in expenses_date:
        categories_date.append(expense[0])
        amounts_date.append(expense[1])
    axis3.bar(categories_date, amounts_date)
    axis3.tick_params(axis='x', rotation=45)  # Adjust the rotation angle as per your preference
    axis3.set_title('Expenses by Date')
    
    return fig

@app.route('/reports', methods=['GET'])
def reports():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        username = session['username']
        cursor = mydb.cursor(dictionary=True)
        
        # Get expense breakdown by category
        cursor.execute("""
            SELECT category, COALESCE(SUM(amount), 0) as total 
            FROM Expense 
            WHERE user = %s 
            AND MONTH(date_of_txn) = MONTH(CURRENT_DATE())
            AND YEAR(date_of_txn) = YEAR(CURRENT_DATE())
            GROUP BY category
        """, (username,))
        categories = cursor.fetchall() or []
        
        # Get monthly trend - Modified to get last 6 months
        cursor.execute("""
            SELECT 
                DATE_FORMAT(date_of_txn, '%b %Y') as month,
                COALESCE(SUM(amount), 0) as total,
                MONTH(date_of_txn) as month_num,
                YEAR(date_of_txn) as year
            FROM Expense 
            WHERE user = %s 
            AND date_of_txn >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
            GROUP BY YEAR(date_of_txn), MONTH(date_of_txn), month
            ORDER BY year ASC, month_num ASC
        """, (username,))
        monthly_trend = cursor.fetchall() or []
        
        # Get budget info
        cursor.execute("SELECT budget FROM profile WHERE user = %s", (username,))
        budget_result = cursor.fetchone()
        monthly_budget = float(budget_result['budget']) if budget_result and budget_result['budget'] else 0
        
        # Get current month expenses
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM Expense 
            WHERE user = %s 
            AND MONTH(date_of_txn) = MONTH(CURRENT_DATE())
            AND YEAR(date_of_txn) = YEAR(CURRENT_DATE())
        """, (username,))
        current_month = cursor.fetchone()
        current_month_expenses = float(current_month['total']) if current_month and current_month['total'] else 0
        
        cursor.close()
        
        return render_template('reports.html',
                             categories=categories,
                             monthly_trend=monthly_trend,
                             monthly_budget=monthly_budget,
                             current_month_expenses=current_month_expenses,
                             user_logged_in=True)
                             
    except Exception as e:
        print(f"Error in reports route: {e}")
        return render_template('reports.html',
                             categories=[],
                             monthly_trend=[],
                             monthly_budget=0,
                             current_month_expenses=0,
                             error="An error occurred while generating reports.",
                             user_logged_in=True)

@app.route('/home')
def index():
    if 'username' not in session:
        return redirect('/login')

    try:
        username = session['username']
        cursor = mydb.cursor(dictionary=True)
        
        # Get total expenses
        if username == 'admin':
            cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM Expense")
        else:
            cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM Expense WHERE user = %s", (username,))
        total_expenses = cursor.fetchone()['total']
        
        # Get monthly budget
        cursor.execute("SELECT COALESCE(budget, 0) as budget FROM profile WHERE user = %s", (username,))
        budget_result = cursor.fetchone()
        monthly_budget = budget_result['budget'] if budget_result else 0
        
        # Get active loans count
        if username == 'admin':
            cursor.execute("SELECT COUNT(*) as count FROM Loan")
        else:
            cursor.execute("SELECT COUNT(*) as count FROM Loan WHERE user = %s", (username,))
        active_loans = cursor.fetchone()['count']
        
        # Get recent expenses
        if username == 'admin':
            cursor.execute("""
                SELECT e.*, DATE_FORMAT(e.date_of_txn, '%d-%m-%Y') as formatted_date 
                FROM Expense e 
                ORDER BY e.date_of_txn DESC 
                LIMIT 10
            """)
        else:
            cursor.execute("""
                SELECT e.*, DATE_FORMAT(e.date_of_txn, '%d-%m-%Y') as formatted_date 
                FROM Expense e 
                WHERE e.user = %s 
                ORDER BY e.date_of_txn DESC 
                LIMIT 10
            """, (username,))
        
        expenses = cursor.fetchall()
        cursor.close()
        
        return render_template('index.html',
                             expenses=expenses,
                             total_expenses=total_expenses,
                             monthly_budget=monthly_budget,
                             active_loans=active_loans,
                             user_logged_in=True,
                             uname=username)
                             
    except Exception as e:
        print(f"Error in index route: {e}")
        return render_template('index.html',
                             error="An error occurred while loading the dashboard.",
                             user_logged_in=True,
                             uname=username)

@app.route('/new_expense', methods=['GET', 'POST'])
def new_expense():
    if 'username' not in session:
        return redirect('/login')
        
    if request.method == 'GET':
        return render_template('new_expense.html', user_logged_in=True)
        
    if request.method == 'POST':
        try:
            username = session['username']
            amount = request.form.get('amount')
            category = request.form.get('category')
            mode = request.form.get('mode')
            
            # Print debug information
            print(f"Form data: amount={amount}, category={category}, mode={mode}")
            
            if not all([amount, category, mode]):
                return render_template('new_expense.html', 
                                     error="All fields are required",
                                     user_logged_in=True)
            
            cursor = mydb.cursor()
            
            try:
                # Insert expense
                expense_sql = """
                    INSERT INTO Expense (amount, category, date_of_txn, mode, user) 
                    VALUES (%s, %s, CURDATE(), %s, %s)
                """
                cursor.execute(expense_sql, (amount, category, mode, username))
                
                # Insert notification
                notify_sql = """
                    INSERT INTO Notification (type, user, content) 
                    VALUES ('EXPENSE', %s, %s)
                """
                notification_content = f"Added new expense of ₹{amount} for {category}"
                cursor.execute(notify_sql, (username, notification_content))
                
                mydb.commit()
                cursor.close()
                print("Successfully added expense and notification")
                return redirect('/home')
                
            except mysql.connector.Error as err:
                mydb.rollback()
                cursor.close()
                print(f"Database error: {err}")
                return render_template('new_expense.html', 
                                     error=f"Database error: {str(err)}",
                                     user_logged_in=True)
                
        except Exception as e:
            print(f"Error adding expense: {e}")
            return render_template('new_expense.html', 
                                 error=f"Error: {str(e)}",
                                 user_logged_in=True)

@app.route('/new_loan', methods=['GET', 'POST'])
def new_loan():
    if 'username' not in session:
        return redirect('/login')
        
    if request.method == 'GET':
        # Instead of rendering an empty loans page, redirect to /loans
        return redirect('/loans')
        
    if request.method == 'POST':
        try:
            username = session['username']
            loan_type = request.form.get('type')
            amount = request.form.get('amount')
            interest_rate = request.form.get('interest_rate')
            duration = request.form.get('duration')
            
            if not all([loan_type, amount, interest_rate, duration]):
                return redirect('/loans')
            
            cursor = mydb.cursor()
            
            try:
                # Insert loan
                loan_sql = """
                    INSERT INTO Loan (loan_amount, interest, type, startDate, endDate, balance, user) 
                    VALUES (%s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s MONTH), %s, %s)
                """
                cursor.execute(loan_sql, (amount, interest_rate, loan_type, duration, amount, username))
                
                # Insert notification
                notify_sql = """
                    INSERT INTO Notification (type, user, content) 
                    VALUES ('LOAN', %s, %s)
                """
                notification_content = f"Added new {loan_type} loan of ₹{amount}"
                cursor.execute(notify_sql, (username, notification_content))
                
                mydb.commit()
                cursor.close()
                return redirect('/loans')
                
            except mysql.connector.Error as err:
                mydb.rollback()
                cursor.close()
                print(f"Database error: {err}")
                return redirect('/loans')
                
        except Exception as e:
            print(f"Error adding loan: {e}")
            return redirect('/loans')

@app.route('/loans')
def loans():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        username = session['username']
        cursor = mydb.cursor(dictionary=True)
        
        # Simple query to fetch loans for the current user
        cursor.execute("""
            SELECT loan_id, loan_amount, interest, type, 
                   startDate as start_date, endDate as end_date, 
                   balance
            FROM loan 
            WHERE user = %s
        """, (username,))
        
        loans = cursor.fetchall()
        cursor.close()
        
        return render_template('loans.html', 
                             loans=loans,
                             user_logged_in=True)
                             
    except Exception as e:
        print(f"Error fetching loans: {e}")
        return render_template('loans.html',
                             loans=[],
                             error="Failed to fetch loans",
                             user_logged_in=True)

@app.route('/delete_loan', methods=['POST'])
def delete_loan():
    if 'username' not in session:
        return redirect('/login')
        
    try:
        data = request.get_json() if request.is_json else request.form
        loan_id = data.get('loanID')
        username = session['username']
        
        cursor = mydb.cursor()
        
        # First verify the loan belongs to the user and get loan details
        cursor.execute("SELECT type, loan_amount FROM loan WHERE loan_id = %s AND user = %s", (loan_id, username))
        loan_details = cursor.fetchone()
        
        if not loan_details:
            return redirect('/loans')
            
        # Delete the loan
        cursor.execute("DELETE FROM loan WHERE loan_id = %s", (loan_id,))
        
        # Create notification for loan deletion
        notification_sql = """
            INSERT INTO Notification (type, user, content) 
            VALUES (%s, %s, %s)
        """
        
        loan_type, loan_amount = loan_details
        content = f"Loan deleted: {loan_type} loan of ₹{loan_amount:.2f}"
        
        # Insert notification
        cursor.execute(notification_sql, (
            "LOAN",  # type
            username,  # user
            content   # content
        ))
        
        mydb.commit()
        cursor.close()
        return redirect('/loans')
        
    except Exception as e:
        print(f"Error deleting loan: {e}")
        mydb.rollback()
        return redirect('/loans')

@app.route('/add_loan', methods=['POST'])
def add_loan():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        # Get loan details from form
        loan_amount = request.form.get('loan_amount')
        interest = request.form.get('interest')
        loan_type = request.form.get('loan_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        description = request.form.get('description')
        account_num = request.form.get('account_num')  # Add this to your loan form
        username = session['username']
        
        cursor = mydb.cursor()
        
        # Verify the account belongs to the user
        cursor.execute("""
            SELECT acc_num FROM account 
            WHERE acc_num = %s AND user = %s
        """, (account_num, username))
        
        if not cursor.fetchone():
            return redirect('/loans')
        
        # Insert into loan table
        cursor.execute("""
            INSERT INTO loan (loan_amount, interest, type, startDate, endDate, balance, description, user)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (loan_amount, interest, loan_type, start_date, end_date, loan_amount, description, username))
        
        # Get the loan_id of the newly inserted loan
        loan_id = cursor.lastrowid
        
        # Create maintains relationship
        cursor.execute("""
            INSERT INTO maintains (acc_num, loan_id)
            VALUES (%s, %s)
        """, (account_num, loan_id))
        
        # Add notification
        cursor.execute("""
            INSERT INTO notification (notify_id, type, user, content, created_at) 
            SELECT COALESCE(MAX(notify_id), 0) + 1, 'ADD_LOAN', %s, %s, NOW()
            FROM notification 
            WHERE user = %s
        """, (username, f"Added new {loan_type} loan of ₹{loan_amount}", username))
        
        mydb.commit()
        cursor.close()
        return redirect('/loans')
        
    except Exception as e:
        print(f"Error adding loan: {e}")
        mydb.rollback()
        return redirect('/loans')

@app.route('/')
def root():
    if 'username' in session:
        return redirect('/home')
    return redirect('/login')

@app.route('/profile', methods=['GET'])
def profile_screen():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        username = session['username']
        cursor = mydb.cursor(dictionary=True)
        
        # Get profile information
        cursor.execute("""
            SELECT * FROM profile 
            WHERE user = %s
        """, (username,))
        profile = cursor.fetchone()
        cursor.close()
        
        # If no profile exists, create one with default values
        if not profile:
            cursor = mydb.cursor()
            try:
                cursor.execute("""
                    INSERT INTO profile (Name, Phone, emailID, budget, user)
                    VALUES (%s, %s, %s, %s, %s)
                """, ("Alekhya Lanka", "9030655615", "melxdiq777@gmail.com", 90000, username))
                mydb.commit()
            except Exception as e:
                print(f"Error creating default profile: {e}")
            finally:
                cursor.close()
            
            return render_template('profile.html',
                                profiles=[{
                                    'Name': 'Alekhya Lanka',
                                    'Phone': '9030655615',
                                    'emailID': 'melxdiq777@gmail.com',
                                    'budget': 90000
                                }],
                                user_logged_in=True,
                                uname=username)
        
        return render_template('profile.html',
                             profiles=[profile],
                             user_logged_in=True,
                             uname=username)
                             
    except Exception as e:
        print(f"Error in profile route: {e}")
        return render_template('profile.html',
                             error="An error occurred while loading profile.",
                             user_logged_in=True,
                             uname=username)

@app.route('/notifications')
def notifications():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        cursor = mydb.cursor(dictionary=True)
        # Get notifications and order by newest first
        cursor.execute("""
            SELECT notify_id, type, content, created_at 
            FROM notification 
            WHERE user = %s 
            ORDER BY created_at DESC, notify_id DESC
        """, (session['username'],))
        notifications = cursor.fetchall()
        
        # Debug print
        print("Fetched notifications:", notifications)
        for notif in notifications:
            print(f"Type: {notif['type']}, Content: {notif['content']}")
        
        cursor.close()
        return render_template('notifications.html', 
                             notifications=notifications, 
                             user_logged_in=True)
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return render_template('notifications.html', 
                             notifications=[], 
                             user_logged_in=True)

@app.route('/delete_notification', methods=['POST'])
def delete_notification():
    if 'username' not in session:
        return redirect('/login')
        
    try:
        username = session['username']
        notify_id = request.json.get('notify_id')
        
        cursor = mydb.cursor()
        
        if username == 'admin':
            cursor.execute("DELETE FROM Notification WHERE notify_id = %s", (notify_id,))
        else:
            cursor.execute("DELETE FROM Notification WHERE notify_id = %s AND user = %s", 
                         (notify_id, username))
            
        mydb.commit()
        cursor.close()
        return {'success': True}
        
    except Exception as e:
        print(f"Error deleting notification: {e}")
        return {'success': False, 'error': str(e)}, 500

@app.route('/clear_notifications', methods=['POST'])
def clear_notifications():
    if 'username' not in session:
        return {'success': False, 'error': 'Not authenticated'}, 401
    
    try:
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM notification WHERE user = %s", (session['username'],))
        mydb.commit()
        cursor.close()
        return {'success': True}
    except Exception as e:
        print(f"Error clearing notifications: {e}")
        return {'success': False, 'error': str(e)}, 500

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        username = session['username']
        amount = request.form['amount']
        category = request.form['category']
        paymentMode = request.form['paymentMode']
        date = request.form['date']
        
        cursor = mydb.cursor()
        
        # Get next expense ID
        cursor.execute("SELECT MAX(expenseID) FROM expense WHERE user = %s", (username,))
        tmp = cursor.fetchone()
        expenseID = 1 if tmp[0] is None else tmp[0] + 1
        
        # Insert expense
        cursor.execute("""
            INSERT INTO expense (expenseID, amount, category, date_of_txn, mode, user) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (expenseID, amount, category, date, paymentMode, username))
        
        # Add notification
        cursor.execute("""
            INSERT INTO notification (notify_id, type, user, content, created_at) 
            SELECT COALESCE(MAX(notify_id), 0) + 1, %s, %s, %s, NOW()
            FROM notification 
            WHERE user = %s
        """, ("EXPENSE", username, f"Added expense of ₹{amount} for {category}", username))
        
        mydb.commit()
        cursor.close()
        return redirect('/new_expense')
        
    except Exception as e:
        print(f"Error adding expense: {e}")
        mydb.rollback()
        return redirect('/new_expense')

@app.route('/loans/', methods=['GET'])
def get_loans():
    if 'username' not in session:
        return redirect('/login')
    uname = session['username']
    if uname == 'admin':
        sql = "SELECT * FROM Loan"
        cursor = mydb.cursor()
        cursor.execute(sql)
    else:
        sql = "SELECT * FROM Loan WHERE user = %s"
        cursor = mydb.cursor()
        cursor.execute(sql, (uname,))
    loans = cursor.fetchall()
    cursor.close()
    return render_template('loans.html', loans=loans,user_logged_in=session.get('username') is not None,uname=session.get('username'))

@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    if 'username' not in session:
        return redirect('/login')

    try:
        username = session['username']
        expense_id = request.form.get('expenseID')
        
        cursor = mydb.cursor()
        
        try:
            # Delete expense
            if username == 'admin':
                sql = "DELETE FROM Expense WHERE expenseID = %s"
                cursor.execute(sql, (expense_id,))
            else:
                sql = "DELETE FROM Expense WHERE expenseID = %s AND user = %s"
                cursor.execute(sql, (expense_id, username))
            
            # Add notification
            notify_sql = """
                INSERT INTO Notification (type, user, content) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(notify_sql, ("DELETE", username, "Deleted an expense"))
            
            mydb.commit()
            cursor.close()
            return redirect('/home')
            
        except mysql.connector.Error as err:
            mydb.rollback()
            cursor.close()
            print(f"Database error: {err}")
            return redirect('/home')
            
    except Exception as e:
        print(f"Error deleting expense: {e}")
        return redirect('/home')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect('/login')
        
    if request.method == 'GET':
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM profile WHERE user = %s", (session['username'],))
        profile = cursor.fetchone()
        cursor.close()
        return render_template('edit_profile.html', 
                             profile=profile, 
                             user_logged_in=True)
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            phone = request.form.get('phone')
            email = request.form.get('email')
            budget = request.form.get('budget')
            username = session['username']
            
            cursor = mydb.cursor(dictionary=True)
            
            # Get current profile
            cursor.execute("SELECT * FROM profile WHERE user = %s", (username,))
            current_profile = cursor.fetchone()
            
            try:
                if current_profile:
                    # Update existing profile
                    cursor.execute("""
                        UPDATE profile 
                        SET Name = %s, Phone = %s, emailID = %s, budget = %s 
                        WHERE user = %s AND id = %s
                    """, (name, phone, email, budget, username, current_profile['id']))
                else:
                    # Create new profile
                    cursor.execute("""
                        INSERT INTO profile (Name, Phone, emailID, budget, user) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (name, phone, email, budget, username))
                
                mydb.commit()
                cursor.close()
                return redirect('/profile')
                
            except mysql.connector.Error as err:
                mydb.rollback()
                cursor.close()
                print(f"Database error: {err}")
                return render_template('edit_profile.html', 
                                     error="Error updating profile. Please try again.",
                                     profile=current_profile,
                                     user_logged_in=True)
                
        except Exception as e:
            print(f"Error: {e}")
            return render_template('edit_profile.html', 
                                 error="An unexpected error occurred",
                                 profile={'Name': name, 'Phone': phone, 'emailID': email, 'budget': budget} if 'name' in locals() else None,
                                 user_logged_in=True)

@app.route('/accounts')
def accounts():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM account WHERE user = %s", (session['username'],))
        accounts = cursor.fetchall()
        cursor.close()
        return render_template('accounts.html', accounts=accounts, user_logged_in=True)
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return render_template('accounts.html', accounts=[], user_logged_in=True)

@app.route('/add_account', methods=['POST'])
def add_account():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        acc_num = request.form.get('acc_num')
        acc_type = request.form.get('acc_type')
        balance = request.form.get('balance')
        username = session['username']
        
        cursor = mydb.cursor()
        
        # Insert into account table
        cursor.execute("""
            INSERT INTO account (acc_num, acc_type, balance, user) 
            VALUES (%s, %s, %s, %s)
        """, (acc_num, acc_type, balance, username))
        
        # Insert into maintains table
        cursor.execute("""
            INSERT INTO maintains (AccNo, user) 
            VALUES (%s, %s)
        """, (acc_num, username))
        
        # Add notification - Note the type is now "ADD_ACCOUNT"
        cursor.execute("""
            INSERT INTO notification (notify_id, type, user, content, created_at) 
            SELECT COALESCE(MAX(notify_id), 0) + 1, 'ADD_ACCOUNT', %s, %s, NOW()
            FROM notification 
            WHERE user = %s
        """, (username, f"Added new {acc_type} account with balance ₹{balance}", username))
        
        mydb.commit()
        cursor.close()
        return redirect('/accounts')
        
    except Exception as e:
        print(f"Error adding account: {e}")
        mydb.rollback()
        return redirect('/accounts')

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return {'success': False, 'error': 'Not authenticated'}, 401
    
    try:
        data = request.get_json()
        acc_num = data.get('acc_num')
        username = session['username']
        
        cursor = mydb.cursor()
        
        # Delete from maintains table first (due to foreign key)
        cursor.execute("DELETE FROM maintains WHERE AccNo = %s AND user = %s", 
                      (acc_num, username))
        
        # Delete from account table
        cursor.execute("DELETE FROM account WHERE acc_num = %s AND user = %s", 
                      (acc_num, username))
        
        mydb.commit()
        cursor.close()
        return {'success': True}
        
    except Exception as e:
        print(f"Error deleting account: {e}")
        mydb.rollback()
        return {'success': False, 'error': str(e)}, 500

@app.route('/income')
def income():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        cursor = mydb.cursor(dictionary=True)
        
        # Get user's income records
        cursor.execute("SELECT * FROM income WHERE user = %s", (session['username'],))
        incomes = cursor.fetchall()
        
        # Get user's accounts for the dropdown
        cursor.execute("SELECT * FROM account WHERE user = %s", (session['username'],))
        accounts = cursor.fetchall()
        
        cursor.close()
        return render_template('income.html', 
                             incomes=incomes, 
                             accounts=accounts, 
                             user_logged_in=True)
    except Exception as e:
        print(f"Error fetching income data: {e}")
        return render_template('income.html', 
                             incomes=[], 
                             accounts=[], 
                             user_logged_in=True)

@app.route('/add_income', methods=['POST'])
def add_income():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        amount = request.form.get('amount')
        description = request.form.get('description')
        account = request.form.get('account')
        username = session['username']
        
        cursor = mydb.cursor()
        
        # Get next income number
        cursor.execute("SELECT MAX(incomeNum) FROM income WHERE user = %s", (username,))
        tmp = cursor.fetchone()
        income_num = 1 if tmp[0] is None else tmp[0] + 1
        
        # Insert income record
        cursor.execute("""
            INSERT INTO income (amount, description, incomeNum, user) 
            VALUES (%s, %s, %s, %s)
        """, (amount, description, income_num, username))
        
        # Link income to account
        cursor.execute("""
            INSERT INTO holds (AccNum, incomeID) 
            VALUES (%s, %s)
        """, (account, income_num))
        
        # Update account balance
        cursor.execute("""
            UPDATE account 
            SET balance = balance + %s 
            WHERE acc_num = %s AND user = %s
        """, (amount, account, username))
        
        # Add notification - Note the type is now "ADD_INCOME"
        cursor.execute("""
            INSERT INTO notification (notify_id, type, user, content, created_at) 
            SELECT COALESCE(MAX(notify_id), 0) + 1, 'ADD_INCOME', %s, %s, NOW()
            FROM notification 
            WHERE user = %s
        """, (username, f"Added income of ₹{amount} - {description}", username))
        
        mydb.commit()
        cursor.close()
        return redirect('/income')
        
    except Exception as e:
        print(f"Error adding income: {e}")
        mydb.rollback()
        return redirect('/income')

@app.route('/delete_income', methods=['POST'])
def delete_income():
    if 'username' not in session:
        return {'success': False, 'error': 'Not authenticated'}, 401
    
    try:
        data = request.get_json()
        income_num = data.get('income_num')
        username = session['username']
        
        cursor = mydb.cursor()
        
        # Get income amount and account to update balance
        cursor.execute("""
            SELECT i.amount, h.AccNum 
            FROM income i 
            JOIN holds h ON i.incomeNum = h.incomeID 
            WHERE i.incomeNum = %s AND i.user = %s
        """, (income_num, username))
        income_data = cursor.fetchone()
        
        if income_data:
            amount, acc_num = income_data
            
            # Update account balance
            cursor.execute("""
                UPDATE account 
                SET balance = balance - %s 
                WHERE acc_num = %s AND user = %s
            """, (amount, acc_num, username))
        
        # Delete from holds first (due to foreign key)
        cursor.execute("DELETE FROM holds WHERE incomeID = %s", (income_num,))
        
        # Delete from income
        cursor.execute("DELETE FROM income WHERE incomeNum = %s AND user = %s", 
                      (income_num, username))
        
        mydb.commit()
        cursor.close()
        return {'success': True}
        
    except Exception as e:
        print(f"Error deleting income: {e}")
        mydb.rollback()
        return {'success': False, 'error': str(e)}, 500

# Add this function to handle database reconnection
def get_db():
    try:
        if not mydb.is_connected():
            mydb.reconnect()
        return mydb
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/records')
def records():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        username = session['username']
        type_filter = request.args.get('type', 'all')
        days_filter = request.args.get('days', 'all')
        
        cursor = mydb.cursor(dictionary=True)
        
        # Build the date conditions
        expense_date_condition = ""
        if days_filter != 'all':
            expense_date_condition = f"AND date_of_txn >= DATE_SUB(CURRENT_DATE(), INTERVAL {days_filter} DAY)"
        
        # Get expenses
        expense_query = f"""
            SELECT 
                'EXPENSE' as type,
                amount,
                category,
                date_of_txn as date,
                mode,
                expenseID as account_num
            FROM expense 
            WHERE user = %s {expense_date_condition}
        """
        
        # Get income
        income_query = f"""
            SELECT 
                'INCOME' as type,
                i.amount,
                i.description as category,
                CURRENT_DATE() as date,
                COALESCE(h.AccNum, 'N/A') as account_num
            FROM income i
            LEFT JOIN holds h ON i.incomeNum = h.incomeID
            WHERE i.user = %s
        """

        # Get loans
        loan_query = f"""
            SELECT 
                'LOAN' as type,
                loan_amount as amount,
                CONCAT(type, ' - Balance: ₹', balance) as category,
                startDate as date,
                loan_id as account_num
            FROM loan
            WHERE user = %s
        """
        
        # Debug prints
        print(f"Type filter: {type_filter}")
        print(f"Days filter: {days_filter}")
        
        if type_filter == 'expense':
            print("Executing expense query:", expense_query % username)
            cursor.execute(expense_query, (username,))
            records = cursor.fetchall()
            print("Expense records:", records)
        elif type_filter == 'income':
            print("Executing income query:", income_query % username)
            cursor.execute(income_query, (username,))
            records = cursor.fetchall()
            print("Income records:", records)
        elif type_filter == 'loan':
            print("Executing loan query:", loan_query % username)
            cursor.execute(loan_query, (username,))
            records = cursor.fetchall()
            print("Loan records:", records)
        else:
            # Combine all types of records
            combined_query = f"""
                {expense_query}
                UNION ALL
                {income_query}
                UNION ALL
                {loan_query}
                ORDER BY date DESC
            """
            print("Executing combined query:", combined_query % (username, username, username))
            cursor.execute(combined_query, (username, username, username))
            records = cursor.fetchall()
            print("All records:", records)
        
        cursor.close()
        return render_template('records.html',
                             records=records,
                             user_logged_in=True,
                             selected_type=type_filter,
                             selected_days=days_filter)
                             
    except Exception as e:
        print(f"Error fetching records: {e}")
        print(f"Error details: {str(e)}")
        return render_template('records.html',
                             records=[],
                             user_logged_in=True,
                             selected_type='all',
                             selected_days='all')

@app.route('/add_maintains', methods=['POST'])
def add_maintains():
    if 'username' not in session:
        return {'success': False, 'error': 'Not authenticated'}, 401
    
    try:
        data = request.get_json()
        loan_id = data.get('loan_id')
        account_num = data.get('account_num')
        username = session['username']
        
        cursor = mydb.cursor()
        
        # Verify the account belongs to the user
        cursor.execute("""
            SELECT acc_num FROM account 
            WHERE acc_num = %s AND user = %s
        """, (account_num, username))
        
        if not cursor.fetchone():
            return {'success': False, 'error': 'Invalid account'}, 400
            
        # Add the maintains relationship
        cursor.execute("""
            INSERT INTO maintains (acc_num, loan_id)
            VALUES (%s, %s)
        """, (account_num, loan_id))
        
        mydb.commit()
        cursor.close()
        return {'success': True}
        
    except Exception as e:
        print(f"Error adding maintains relationship: {e}")
        mydb.rollback()
        return {'success': False, 'error': str(e)}, 500

@app.route('/add_holds', methods=['POST'])
def add_holds():
    if 'username' not in session:
        return {'success': False, 'error': 'Not authenticated'}, 401
    
    try:
        data = request.get_json()
        income_num = data.get('income_num')
        account_num = data.get('account_num')
        username = session['username']
        
        cursor = mydb.cursor()
        
        # Verify the account belongs to the user
        cursor.execute("""
            SELECT acc_num FROM account 
            WHERE acc_num = %s AND user = %s
        """, (account_num, username))
        
        if not cursor.fetchone():
            return {'success': False, 'error': 'Invalid account'}, 400
            
        # Add the holds relationship
        cursor.execute("""
            INSERT INTO holds (AccNum, incomeID)
            VALUES (%s, %s)
        """, (account_num, income_num))
        
        mydb.commit()
        cursor.close()
        return {'success': True}
        
    except Exception as e:
        print(f"Error adding holds relationship: {e}")
        mydb.rollback()
        return {'success': False, 'error': str(e)}, 500

@app.route('/update_loan/<int:loan_id>', methods=['POST'])
def update_loan(loan_id):
    if 'username' not in session:
        return redirect('/login')
    
    try:
        data = request.get_json()
        payment_amount = float(data.get('payment_amount', 0))
        username = session['username']
        
        cursor = mydb.cursor(dictionary=True)
        
        # Get current loan details
        cursor.execute("""
            SELECT * FROM loan 
            WHERE loan_id = %s AND user = %s
        """, (loan_id, username))
        
        loan = cursor.fetchone()
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
            
        # Calculate new balance
        new_balance = float(loan['balance']) - payment_amount
        if new_balance < 0:
            return jsonify({"error": "Payment amount exceeds loan balance"}), 400
            
        # Update loan balance
        cursor.execute("""
            UPDATE loan 
            SET balance = %s 
            WHERE loan_id = %s AND user = %s
        """, (new_balance, loan_id, username))
        
        # Add notification
        cursor.execute("""
            INSERT INTO Notification (type, user, content) 
            VALUES ('LOAN', %s, %s)
        """, (username, f"Updated loan balance. Paid ₹{payment_amount:.2f}"))
        
        cursor.close()
        return jsonify({"message": "Loan updated successfully"}), 200
        
    except Exception as e:
        print(f"Error updating loan: {e}")
        return jsonify({"error": "Error updating loan"}), 500

if __name__ == '__main__':
    app.run(debug=True)
