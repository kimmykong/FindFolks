# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       # password='root',
                       db='findfolks',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

# Define a route to hello function
@app.route('/')
def hello():
    return renderIndexPage()


# Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

# Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

# Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM member WHERE username = %s and password = MD5(%s)'
    cursor.execute(query, (username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if (data):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

# Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    zipcode = request.form['zipcode']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM member WHERE username = %s'
    cursor.execute(query, (username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        # TODO: zipcode should probs be diff

        ins = 'INSERT INTO member VALUES(%s, MD5(%s), %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, firstname,lastname,email,zipcode))
        conn.commit()
        cursor.close()
        return renderIndexPage()

def renderIndexPage():
    cursor = conn.cursor()

    query = 'SELECT * FROM interest'
    cursor.execute(query)
    interests = cursor.fetchall()

    query = 'SELECT title FROM an_event'
    cursor.execute(query)
    events = cursor.fetchall()

    cursor.close()
    return render_template('index.html', interests=interests, event=events)


@app.route('/home')
def home():
    username = session['username']
    return render_template('home.html', username=username)


@app.route('/sandbox')
def sandbox():
    cursor = conn.cursor()

    query = 'SELECT * FROM interest'
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    return render_template('sandbox.html', data=data)

@app.route('/sandbox2', methods=['GET'])
def interest():

    # username = request.form['username']
    # catName = request.table
    print request.table
    print "here"

# @app.route('/post', methods=['GET', 'POST'])
# def post():
#     username = session['username']
#     cursor = conn.cursor();
#     blog = request.form['blog']
#     query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
#     cursor.execute(query, (blog, username))
#     conn.commit()
#     cursor.close()
#     return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5007, debug=True)
