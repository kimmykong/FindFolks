# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root',
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

    query = 'SELECT * FROM an_event'
    cursor.execute(query)
    events = cursor.fetchall()

    cursor.close()
    return render_template('index.html', interests=interests, event=events)


@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor();
    # displays events in the next three days by default
    query = 'SELECT * FROM sign_up JOIN an_event ON sign_up.event_id = an_event.event_id WHERE sign_up.username = %s AND NOW() < an_event.start_time < DATE_ADD(NOW(),INTERVAL 3 DAY)'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    cursor.close()

    # query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    # cursor.execute(quersy, (username))
    # data = cursor.fetchall()
    # cursor.close()

    return render_template('home.html', username=username, event=data)


@app.route('/sandbox')
def sandbox():
    cursor = conn.cursor()

    query = 'SELECT * FROM interest'
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    return render_template('sandbox.html', data=data)

@app.route('/interest/<categoryKeyword>', methods=['GET','POST'])
def interest(categoryKeyword):
    catKey = str(categoryKeyword).split("+")
    cursor = conn.cursor()

    query = 'SELECT group.name FROM group JOIN about ON group.group_id = about.group_id WHERE aboout.category = catKey[0] AND about.keyword = catKey[1]'
    cursor.execute(query)
    groups = cursor.fetchall()

    cursor.close()

    return render_template('interest.html', category=catKey[0], keyword=catKey[1], groups = groups )


@app.route('/events/<id>', methods=['GET','POST'])
def eventPage(id):

    cursor = conn.cursor()
    query = 'SELECT * FROM an_event WHERE event_id = %s'
    cursor.execute(query, (str(id)))
    # stores the results in a variable
    data = cursor.fetchone()
    return render_template("event.html", event=data )

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
# Run the app on localhost port 5007
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5007, debug=True)
