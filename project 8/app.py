from flask import Flask, render_template, request, redirect, url_for,session
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Set the secret key
app.secret_key = 'Devika@1503'

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="DEVIKA",
            password="Devika@102015"
        )
        self.cursor = self.connection.cursor()

        # Create the 'authentication' database if it doesn't exist
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS authentication")
        self.cursor.execute("USE authentication")

        # Create the 'data' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                username VARCHAR(50) NOT NULL,
                phone_number INT NOT NULL,
                email VARCHAR(150) PRIMARY KEY,
                password VARCHAR(25) NOT NULL
            )
        """)
        self.connection.commit()

         # Create the 'java_table' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS java_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                option1 VARCHAR(255) NOT NULL,
                option2 VARCHAR(255) NOT NULL,
                option3 VARCHAR(255) NOT NULL,
                option4 VARCHAR(255) NOT NULL,
                answer VARCHAR(5) NOT NULL
            )
        """)
        self.connection.commit()

        # Create the 'py_table' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS py_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                option1 VARCHAR(255) NOT NULL,
                option2 VARCHAR(255) NOT NULL,
                option3 VARCHAR(255) NOT NULL,
                option4 VARCHAR(255) NOT NULL,
                answer VARCHAR(5) NOT NULL
            )
        """)
        self.connection.commit()

         # Create the 'c_table' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS c_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                option1 VARCHAR(255) NOT NULL,
                option2 VARCHAR(255) NOT NULL,
                option3 VARCHAR(255) NOT NULL,
                option4 VARCHAR(255) NOT NULL,
                answer VARCHAR(5) NOT NULL
            )
        """)
        self.connection.commit()

        # Create the 'html_table' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS html_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                option1 VARCHAR(255) NOT NULL,
                option2 VARCHAR(255) NOT NULL,
                option3 VARCHAR(255) NOT NULL,
                option4 VARCHAR(255) NOT NULL,
                answer VARCHAR(255) NOT NULL
            )
        """)
        self.connection.commit()

        # Create the 'css_table' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS css_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                option1 VARCHAR(255) NOT NULL,
                option2 VARCHAR(255) NOT NULL,
                option3 VARCHAR(255) NOT NULL,
                option4 VARCHAR(255) NOT NULL,
                answer VARCHAR(255) NOT NULL
            )
        """)
        self.connection.commit()

        # Create the 'sql_table' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sql_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                option1 VARCHAR(255) NOT NULL,
                option2 VARCHAR(255) NOT NULL,
                option3 VARCHAR(255) NOT NULL,
                option4 VARCHAR(255) NOT NULL,
                answer VARCHAR(255) NOT NULL
            )
        """)
        self.connection.commit()


        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_scores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(150),
                quiz_type VARCHAR(50),
                score INT
            )
        """)
        self.connection.commit()

    def execute_query(self, query, values=None):
        if values:
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def execute_insert(self, query, values):
        self.cursor.execute(query, values)
        self.connection.commit()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

# Connect to the database
db = Database()

@app.route('/')
def home():
    error_message = request.args.get('error_message')  # Get the error message from the query parameter
    return render_template('home.html', error_message=error_message)

# Route to render the login page
@app.route('/', methods=['GET', 'POST'])
def login():
    login_error = None
    if request.method == 'POST':
        email = request.form['email']

        # Query the database to check if the email exists
        query = "SELECT * FROM data WHERE email = %s"
        result = db.execute_query(query, (email,))
        session['email'] = request.form.get('email')
        if result:
            # Email exists, redirect to the password page
            return redirect(url_for('password',email=email))
        else:
            login_error = 'Email does not exist. Please sign up'

    return render_template('home.html', login_error=login_error)

# Route to render the password page
@app.route('/password', methods=['GET','POST'])
def password():
    # Check if user is logged in
    if 'email' not in session:
        return redirect(url_for('home', error_message='Please log in first'))
    
    password_error = None 
    email = session['email'] # Retrieve email from session
    if request.method == 'POST':
        entered_password = request.form['password']
        # Query the database to get the password for the given email
        query = "SELECT password FROM data WHERE email = %s"
        result = db.execute_query(query, (email,))
        if result:
            password_from_db = result[0][0]

            # Check if the entered password matches the password from the database
            if entered_password == password_from_db:
                # Redirect to the dashboard page
                return redirect('/dashboard')
            else:
                # Render the password page with "Invalid password" message
                password_error = 'Invalid password'

    # Render the password page with or without the "Invalid password" message
    return render_template('password.html', password_error=password_error)


# Route to render the dashboard page
@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'email' not in session:
        return redirect(url_for('home', error_message='Please log in first'))
    
    return render_template('dashboard.html')

# Route to render the profile page
@app.route('/profile')
def profile():
    # Check if user is logged in
    if 'email' not in session:
        return redirect(url_for('home', error_message='Please log in first'))

    # Fetch the user's details from the database based on the email stored in the session
    email = session['email']
    query_user = "SELECT username, phone_number, email, password FROM data WHERE email = %s"
    user_result = db.execute_query(query_user, (email,))
    if not user_result:
        return redirect(url_for('home', error_message='User not found'))

    # Extract user details from the database result
    username, phone_number, email, password = user_result[0]

    # Fetch quiz results for the user from the user_quizzes table
    query_quiz = "SELECT quiz_type, score FROM quiz_scores WHERE email = %s"
    quiz_results = db.execute_query(query_quiz, (email,))

    #current date
    current_date = datetime.now().strftime("%d-%m-%Y")

    user = {'username': username, 'email': email, 'phone_number': phone_number, 'password': password}
    return render_template('profile.html', user=user, quiz_results=quiz_results, current_date=current_date)



# Route to handle the logout action
@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Redirect the user to the home page
    return redirect(url_for('home'))


# Route to render the register page
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

# Route to handle form submissions for registration
@app.route('/register', methods=['POST'])
def register_user():
    username = request.form['username']
    phone_number = request.form['phone_number']  # Get phone number from the form
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Check if the email already exists
    query = "SELECT * FROM data WHERE email = %s"
    result = db.execute_query(query, (email,))
    if result:
        register_error = 'Email already exists. Please login'
        return redirect(url_for('home', error_message=register_error))

    # Check if the password and confirm password match
    if password != confirm_password:
        register_error = 'Password mismatched'
        return render_template('register.html', register_error=register_error)

    # Insert the user into the database
    insert_query = "INSERT INTO data (username, phone_number, email, password) VALUES (%s, %s, %s, %s)"
    db.execute_insert(insert_query, (username, phone_number, email, password))  # Include phone_number here

    # Display success message
    success_message = 'You have registered successfully!'
    return render_template('register.html', success_message=success_message)

@app.route('/programming')
def programming():
    return render_template('programming.html')

@app.route('/frontend')
def frontend():
    return render_template('frontend.html')

@app.route('/dbms')
def dbms():
    return render_template('dbms.html')

@app.route('/c_admin', methods=['GET', 'POST'])
def c_admin():
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']
        
        print("Question:", question)  # Print the question data
        
        # Check if the question already exists
        query = "SELECT * FROM c_table WHERE question = %s"
        result = db.execute_query(query, (question,))
        if result:
            register_error = 'Question already exists.'
            return render_template('c_admin.html', error_message=register_error)
        else:
            # Insert the data into the c_table
            query = "INSERT INTO c_table (question, option1, option2, option3, option4, answer) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (question, option1, option2, option3, option4, answer)
            db.execute_insert(query, values)
            success_message = 'Question added successfully'
            return render_template('c_admin.html', success_message= success_message)
        
    return render_template('c_admin.html')


# Route to render the c.html page and display C questions
@app.route('/c')
def c_questions():
    # Query the database to retrieve C questions
    query = "SELECT id, question, option1, option2, option3, option4 FROM c_table"
    questions = db.execute_query(query)
    return render_template('c.html', questions=questions)


@app.route('/py_admin', methods=['GET', 'POST'])
def py_admin():
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']
        
        print("Question:", question)  # Print the question data
        
        # Check if the question already exists
        query = "SELECT * FROM py_table WHERE question = %s"
        result = db.execute_query(query, (question,))
        if result:
            register_error = 'Question already exists.'
            return render_template('py_admin.html', error_message=register_error)
        else:
            # Insert the data into the java._table
            query = "INSERT INTO py_table (question, option1, option2, option3, option4, answer) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (question, option1, option2, option3, option4, answer)
            db.execute_insert(query, values)
            success_message = 'Question added successfully'
            return render_template('py_admin.html', success_message= success_message)
        
    return render_template('py_admin.html')


# Route to render the py.html page and display python questions
@app.route('/py')
def py_questions():
    # Query the database to retrieve C questions
    query = "SELECT id, question, option1, option2, option3, option4 FROM py_table"
    questions = db.execute_query(query)
    return render_template('py.html', questions=questions)

@app.route('/java_admin', methods=['GET', 'POST'])
def java_admin():
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']
        
        print("Question:", question)  # Print the question data
        
        # Check if the question already exists
        query = "SELECT * FROM java_table WHERE question = %s"
        result = db.execute_query(query, (question,))
        if result:
            register_error = 'Question already exists.'
            return render_template('java_admin.html', error_message=register_error)
        else:
            # Insert the data into the java_table
            query = "INSERT INTO java_table (question, option1, option2, option3, option4, answer) VALUES (%s, %s, %s, %s, %s,%s)"
            values = (question, option1, option2, option3, option4,answer)
            db.execute_insert(query, values)
            success_message = 'Question added successfully'
            return render_template('java_admin.html', success_message=success_message)
        
    return render_template('java_admin.html')


# Route to render the java.html page and display Java questions
@app.route('/java')
def java_questions():
    # Query the database to retrieve Java questions
    query = "SELECT id, question, option1, option2, option3, option4 FROM java_table"
    questions = db.execute_query(query)
    return render_template('java.html', questions=questions)


@app.route('/html_admin', methods=['GET', 'POST'])
def html_admin():
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']
        
        print("Question:", question)  # Print the question data
        
        # Check if the question already exists
        query = "SELECT * FROM html_table WHERE question = %s"
        result = db.execute_query(query, (question,))
        if result:
            register_error = 'Question already exists.'
            return render_template('html_admin.html', error_message=register_error)
        else:
            # Insert the data into the html_table
            query = "INSERT INTO html_table (question, option1, option2, option3, option4, answer) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (question, option1, option2, option3, option4, answer)
            db.execute_insert(query, values)
            success_message = 'Question added successfully'
            return render_template('html_admin.html', success_message=success_message)
        
    return render_template('html_admin.html')


# Route to render the html.html page and display html questions
@app.route('/html')
def html_questions():
    # Query the database to retrieve html questions
    query = "SELECT id, question, option1, option2, option3, option4 FROM html_table"
    questions = db.execute_query(query)
    return render_template('html.html', questions=questions)

@app.route('/css_admin', methods=['GET', 'POST'])
def css_admin():
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']
        
        print("Question:", question)  # Print the question data
        
        # Check if the question already exists
        query = "SELECT * FROM css_table WHERE question = %s"
        print(query)
        result = db.execute_query(query, (question,))
        if result:
            register_error = 'Question already exists.'
            return render_template('css_admin.html', error_message=register_error)
        else:
            # Insert the data into the css_table
            query = "INSERT INTO css_table (question, option1, option2, option3, option4, answer) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (question, option1, option2, option3, option4, answer)
            db.execute_insert(query, values)
            success_message = 'Question added successfully'
            return render_template('css_admin.html', success_message=success_message)
        
    return render_template('css_admin.html')


# Route to render the css.html page and display CSS questions
@app.route('/css')
def css_questions():
    # Query the database to retrieve CSS questions
    query = "SELECT id, question, option1, option2, option3, option4 FROM css_table"
    questions = db.execute_query(query)
    return render_template('css.html', questions=questions)

@app.route('/sql_admin', methods=['GET', 'POST'])
def sql_admin():
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']
        
        print("Question:", question)  # Print the question data
        
        # Check if the question already exists
        query = "SELECT * FROM sql_table WHERE question = %s"
        result = db.execute_query(query, (question,))
        if result:
            register_error = 'Question already exists.'
            return render_template('sql_admin.html', error_message=register_error)
        else:
            # Insert the data into the sql_table
            query = "INSERT INTO sql_table (question, option1, option2, option3, option4, answer) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (question, option1, option2, option3, option4, answer)
            db.execute_insert(query, values)
            success_message = 'Question added successfully'
            return render_template('sql_admin.html', success_message= success_message)
        
    return render_template('sql_admin.html')


# Route to render the sql.html page and display SQL questions
@app.route('/sql')
def sql_questions():
    # Query the database to retrieve SQL questions
    query = "SELECT id, question, option1, option2, option3, option4 FROM sql_table"
    questions = db.execute_query(query)
    return render_template('sql.html', questions=questions)



# Route to handle quiz submission
@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    if request.method == 'POST':
        # Get the quiz type from the form
        quiz_type = request.form.get('quiz_type')

        # Retrieve the selected answers from the form
        selected_answers = {}
        for key, value in request.form.items():
            if key.startswith('question_'):
                question_id = int(key.split('_')[1])
                selected_answers[question_id] = value

        # Query the database to retrieve the correct answers based on the quiz type
        query = f"SELECT id, answer FROM {quiz_type}_table"
        correct_answers = dict(db.execute_query(query))

        # Calculate the score
        correct_count = sum(1 for qid, correct_answer in correct_answers.items() if selected_answers.get(qid) == correct_answer)
        score = correct_count

        # Store the score in the database
        email = session.get('email')  # Get the user's email from the session
        db.execute_insert("INSERT INTO quiz_scores (email, quiz_type, score) VALUES (%s, %s, %s)", (email, quiz_type, score))

        # Redirect to the quiz result page
        return redirect(url_for('quiz_result', score=score))

# Route to display quiz result
@app.route('/quiz_result')
def quiz_result():
    score = request.args.get('score')
    return render_template('quiz_result.html', score=score)


if __name__ == '__main__':
    app.run(debug=True)