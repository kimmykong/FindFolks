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

@app.route('/signup/<id>', methods=['GET', 'POST'])
def signup(id):
    cursor = conn.cursor()

    query = 'SELECT * FROM an_event WHERE event_id = %s'
    cursor.execute(query, (str(id)))
    data = cursor.fetchone()

    query = 'INSERT INTO sign_up VALUES (%s,%s, -1)'
    cursor.execute(query, ((str(id)), str(session['username'])))
    conn.commit()

    cursor.close()
    return render_template("event.html", event=data, signedup=True )

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
    category = catKey[0] 
    keyword = catKey[1]
    cursor = conn.cursor()

    query = 'SELECT a_group.group_name FROM a_group JOIN about ON a_group.group_id = about.group_id WHERE about.category = category AND about.keyword = keyword'
    cursor.execute(query)
    groups = cursor.fetchall()

    cursor.close()

    return render_template('interest.html', category= category, keyword= keyword, groups = groups )


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

# Search for events with interest
@app.route('/eventSearch', methods=['GET', 'POST'])
def eventSearch():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM interested_in JOIN about ON interested_in.keyword = about.keyword JOIN organize ON about.group_id = organize.group_id JOIN an_event ON organize.event_id = an_event.event_id JOIN a_group ON about.group_id = a_group.group_id WHERE interested_in.username = %s'
    cursor.execute(query, (username))
    eventSearch = cursor.fetchall()
    # displays events in the next three days by default
    query = 'SELECT * FROM sign_up JOIN an_event ON sign_up.event_id = an_event.event_id WHERE sign_up.username = %s AND NOW() < an_event.start_time < DATE_ADD(NOW(),INTERVAL 3 DAY)'
    cursor.execute(query, (username))
    futureEvents = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=username, eventSearch=eventSearch, button=True, event=futureEvents)



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
