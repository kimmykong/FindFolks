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
    session['username'] = None
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

def renderIndexPage(logout=False):
    cursor = conn.cursor()

    query = 'SELECT * FROM interest'
    cursor.execute(query)
    interests = cursor.fetchall()

    query = 'SELECT * FROM an_event'
    cursor.execute(query)
    events = cursor.fetchall()

    cursor.close()
    return render_template('index.html', interests=interests, event=events, logout=logout)

@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor();

    # displays events in the next three days by default
    # signed up for and in next 3 days

    query = 'SELECT * FROM sign_up JOIN an_event ON sign_up.event_id = an_event.event_id WHERE sign_up.username = %s AND NOW() < an_event.start_time  AND an_event.start_time < DATE_ADD(NOW(),INTERVAL 3 DAY)'
    cursor.execute(query, (username))
    futureEvents = cursor.fetchall()

    # displays past events signed up for
    query = 'SELECT * FROM sign_up JOIN an_event ON sign_up.event_id = an_event.event_id WHERE sign_up.username = %s AND NOW() > an_event.start_time'
    cursor.execute(query, (username))
    pastEvents = cursor.fetchall()

    query = 'SELECT * FROM friend WHERE friend_of = %s'
    cursor.execute(query, (username))
    friends = cursor.fetchall()

    query = 'SELECT friend.friend_to, sign_up.event_id, an_event.title FROM friend JOIN sign_up ON friend.friend_to = sign_up.username JOIN an_event ON an_event.event_id = sign_up.event_id WHERE friend.friend_of = %s'
    cursor.execute(query, (username))
    friendEvents = cursor.fetchall()
    cursor.close()

    return render_template('home.html', username=username, futureEvents=futureEvents, pastEvents=pastEvents, friends = friends, friendEvents = friendEvents)

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

    query = 'SELECT a_group.group_name, a_group.group_id FROM a_group JOIN about ON a_group.group_id = about.group_id  WHERE about.category = category AND about.keyword = keyword'
    cursor.execute(query)
    data = cursor.fetchall()

    query = 'SELECT an_event.event_id, an_event.title, an_event.start_time, an_event.location_name, an_event.zipcode FROM a_group JOIN about ON a_group.group_id = about.group_id JOIN organize ON a_group.group_id = organize.group_id JOIN an_event ON an_event.event_id = organize.event_id WHERE about.category = category AND about.keyword = keyword AND NOW() < an_event.start_time'
    cursor.execute(query)
    events = cursor.fetchall()
    return render_template('interest.html', category= category, keyword= keyword, data = data, events = events  )

def goingToEvent(username, id):
    cursor = conn.cursor()
    query = 'SELECT * FROM sign_up WHERE event_id = %s AND username=%s'
    cursor.execute(query, (str(id), str(username)))
    going = cursor.fetchone()
    cursor.close()
    return going

def eventInPast(id):
    cursor = conn.cursor()
    query = 'SELECT * FROM an_event WHERE event_id = %s AND end_time < NOW() '
    cursor.execute(query, (str(id)))
    past = cursor.fetchone()
    cursor.close()
    return past

@app.route('/events/<id>', methods=['GET','POST'])
def eventPage(id):
    username = session['username']
    signedup = False
    private = False

    if(username):
        private = True
        signedup = goingToEvent(username,id)

    return render_template("event.html", event=getEventInfo(id), signedup=signedup, private=private)

@app.route('/groups/<id>', methods=['GET', 'POST'])
def groupPage(id):
    cursor = conn.cursor()
    query = 'SELECT * FROM a_group WHERE group_id = %s'
    cursor.execute(query, (str(id)))
    # stores the results in a variable
    data = cursor.fetchone()

    query = 'SELECT * FROM about WHERE group_id = %s'
    cursor.execute(query, (str(id)))
    # stores the results in a variable
    interest = cursor.fetchone()

    query = 'SELECT * FROM an_event JOIN organize ON  an_event.event_id = organize.event_id  JOIN a_group ON a_group.group_id = organize.group_id WHERE organize.group_id = %s'
    cursor.execute(query, (str(id)))
    event = cursor.fetchall()

    return render_template("group.html", data=data, event=event, interest = interest)

# Search for events with interest
@app.route('/eventSearch', methods=['GET', 'POST'])
def eventSearch():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM interested_in JOIN about ON interested_in.keyword = about.keyword JOIN organize ON about.group_id = organize.group_id JOIN an_event ON organize.event_id = an_event.event_id JOIN a_group ON about.group_id = a_group.group_id WHERE interested_in.username = %s AND an_event.start_time > NOW()'
    cursor.execute(query, (username))
    eventSearch = cursor.fetchall()
    # displays events in the next three days by default
    query = 'SELECT * FROM sign_up JOIN an_event ON sign_up.event_id = an_event.event_id WHERE sign_up.username = %s AND NOW() < an_event.start_time  AND an_event.start_time < DATE_ADD(NOW(),INTERVAL 3 DAY)'
    cursor.execute(query, (username))
    futureEvents = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=username, eventSearch=eventSearch, button=True, event=futureEvents)

@app.route('/rate/<int:id>', methods=["POST"])
def rate(id):
    username = session['username']
    signedUp = False

    if(goingToEvent(username,id)):
        signedUp = True
        if(eventInPast(id)):
            cursor = conn.cursor()
            query = 'UPDATE `sign_up` SET rating = %s WHERE event_id = %s AND username = %s'
            cursor.execute(query, (int(request.form['rate']), str(id), username))
            conn.commit()
            cursor.close()
            message = "Rating successful!"
        else:
            message = "Silly goose! You can't rate something you haven't gone to yet!"
    else:
        message = "lol you're not even going to this event, so stop trying to rate it"

    return render_template("event.html", event=getEventInfo(id), signedup = signedUp, rating=True, private=True, message = message)

def getEventInfo(id):
    cursor = conn.cursor()

    query = 'SELECT * FROM an_event WHERE event_id = %s'
    cursor.execute(query, (str(id)))
    # stores the results in a variable
    eventInfo = cursor.fetchone()

    cursor.close()

    return eventInfo

@app.route('/createEvent')
def createEventPage():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM belongs_to JOIN a_group ON belongs_to.group_id = a_group.group_id where belongs_to.username = %s'
    cursor.execute(query,(username))
    groups = cursor.fetchall()
    return render_template("createEvent.html", groups = groups)

@app.route('/createAnEvent',methods=['GET', 'POST'])
def createAnEvent():
    username = session['username']
    group_id = request.form['Group']
    event_id = request.form['Event_ID']
    event_name = request.form['Event_Name']
    description = request.form['Description']
    start = request.form['Start_Date']
    end = request.form['End_Date']
    location_name = request.form['Location_Name']
    zipcode = request.form['Zipcode']
    address = request.form['Address']
    loc_desc = request.form['Loc_Description']
    latitude = request.form['Latitude']
    longitude = request.form['Longitude']
    cursor = conn.cursor()
    # TODO: Add a check to see if the location already exists
    # TODO: allow for latitude and longitude to be allowed decimale values
    # TODO: allow user to choose from existing locations or choose to create a new location
    query = 'INSERT INTO location (location_name, zipcode, address, description, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s)'
    cursor.execute(query,(location_name, int(zipcode), address, loc_desc, int(latitude), int(longitude)))
    conn.commit()
    query = 'INSERT INTO an_event (event_id, title, description, start_time, end_time, location_name, zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s);'
    cursor.execute(query,(event_id, event_name, description, start, end, location_name, zipcode))
    conn.commit()
    # NEED TO UPDATE ORGANIZE TABLE
##    query = 'INSERT INTO organize (event_id, group_id) VALUES (%s, %s)'
##    cursor.execute(query,(event_id, group_id))
##    conn.commit()
    cursor.close()
    return redirect(url_for('createEventPage'))

@app.route('/logout')
def logout():
    session.pop('username')
    session['username'] = None
    return renderIndexPage(True)

app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5007
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5007, debug=True)
