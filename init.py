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

    query = 'INSERT INTO sign_up (`event_id`, `username`) VALUES (%s,%s)'
    cursor.execute(query, ((str(id)), str(session['username'])))
    conn.commit()

    cursor.close()
    return render_template("event.html", event=data, signedup=True )

@app.route('/joinGroup/<id>', methods=['GET', 'POST'])
def joinGroup(id):
    cursor = conn.cursor()

    query = 'INSERT INTO belongs_to VALUES (%s,%s,0)'
    cursor.execute(query, ((str(id)), str(session['username'])))
    conn.commit()

    query = 'SELECT * FROM a_group WHERE group_id = %s'
    cursor.execute(query, (str(id)))
    data = cursor.fetchone()

    query = 'SELECT * FROM about WHERE group_id = %s'
    cursor.execute(query, (str(id)))
    interest = cursor.fetchone()

    query = 'SELECT * FROM an_event JOIN organize ON  an_event.event_id = organize.event_id  JOIN a_group ON a_group.group_id = organize.group_id WHERE organize.group_id = %s'
    cursor.execute(query, (str(id)))
    event = cursor.fetchall()

    cursor.close()

    return render_template("group.html", data=data, event=event, interest=interest, inGroup=True, loggedIn=True)


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
    color = request.form['color']

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

        ins = 'INSERT INTO member VALUES(%s, MD5(%s), %s, %s, %s, %s %s)'
        cursor.execute(ins, (username, password, firstname,lastname,email,zipcode, color))
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

# note: updates to home need to be made to eventSearch too
@app.route('/home')
def home():
    username = session['username']
    font_color = getColor(username)
    futureEvents = nextThreeDaysOfSignedUpEvents(username)
    pastEvents = pastEventsSIgnedUpFor(username)
    friends = getFriends(username)
    friendEvents = getFriendsFutureEvents(username)

    query = 'SELECT AVG(sign_up.rating) as avgRate, a_group.group_id, a_group.group_name FROM a_group JOIN organize on a_group.group_id = organize.group_id JOIN an_event ON an_event.event_id = organize.event_id JOIN sign_up on an_event.event_id = sign_up.event_id WHERE a_group.group_id IN ( SELECT a_group.group_id FROM belongs_to JOIN a_group on belongs_to.group_id = a_group.group_id WHERE belongs_to.username = %s) GROUP BY an_event.event_id'
    groups = executeSQLManyResponses(query,username)

    # groups that share your interests that you're not in
    query = 'SELECT * FROM interested_in JOIN interest ON (interested_in.category=interest.category and interested_in.keyword=interest.keyword) JOIN about ON (interest.category = about.category AND interest.keyword = about.keyword) JOIN a_group ON a_group.group_id = about.group_id WHERE a_group.group_id not in (SELECT a_group.group_id FROM belongs_to JOIN a_group on belongs_to.group_id = a_group.group_id WHERE belongs_to.username = %s)'
    newGroups = executeSQLManyResponses(query,username)

    return render_template('home.html', username=username, futureEvents=futureEvents, pastEvents=pastEvents, friends = friends, groups= groups, friendEvents = friendEvents, newGroups = newGroups, font_color=font_color)

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

@app.route('/events/<id>', methods=['GET','POST'])
def eventPage(id):
    username = session['username']
    signedup = False
    private = False

    if(username):
        private = True
        signedup = goingToEvent(username,id)

    query = 'SELECT * FROM sponsors JOIN an_event on sponsors.event_id=an_event.event_id WHERE an_event.event_id = %s'
    sponsor = executeSQLManyResponses(query,id)

    return render_template("event.html", event=getEventInfo(id), signedup=signedup, private=private, sponsors = sponsor)

@app.route('/groups/<id>', methods=['GET', 'POST'])
def groupPage(id):
    username = session['username']

    cursor = conn.cursor()
    query = 'SELECT * FROM a_group WHERE group_id = %s'
    cursor.execute(query, (str(id)))
    data = cursor.fetchone()

    query = 'SELECT * FROM about WHERE group_id = %s'
    cursor.execute(query, (str(id)))
    interest = cursor.fetchone()

    query = 'SELECT * FROM an_event JOIN organize ON  an_event.event_id = organize.event_id  JOIN a_group ON a_group.group_id = organize.group_id WHERE organize.group_id = %s'
    cursor.execute(query, (str(id)))
    event = cursor.fetchall()

    inGroup=False
    loggedIn=False

    if(username): #logged in
        loggedIn = True
        query = 'SELECT * FROM belongs_to WHERE belongs_to.username = %s AND belongs_to.group_id = %s '
        inTheGroup = executeSQLOneResponse(query,(username,id))
        if (inTheGroup):
            inGroup=True

    return render_template("group.html", data=data, event=event, interest = interest, inGroup=inGroup, loggedIn =loggedIn)

# Search for events with interest
@app.route('/eventSearch', methods=['GET', 'POST'])
def eventSearch():
    username = session['username']

    query = 'SELECT AVG(sign_up.rating) as avgRate, a_group.group_id, a_group.group_name FROM a_group JOIN organize on a_group.group_id = organize.group_id JOIN an_event ON an_event.event_id = organize.event_id JOIN sign_up on an_event.event_id = sign_up.event_id WHERE a_group.group_id IN ( SELECT a_group.group_id FROM belongs_to JOIN a_group on belongs_to.group_id = a_group.group_id WHERE belongs_to.username = %s) GROUP BY an_event.event_id'
    groups = executeSQLManyResponses(query,username)

    futureEvents = nextThreeDaysOfSignedUpEvents(username)
    pastEvents = pastEventsSIgnedUpFor(username)
    friends = getFriends(username)
    friendEvents = getFriendsFutureEvents(username)
    query = 'SELECT * FROM interested_in JOIN about ON interested_in.keyword = about.keyword JOIN organize ON about.group_id = organize.group_id JOIN an_event ON organize.event_id = an_event.event_id JOIN a_group ON about.group_id = a_group.group_id WHERE interested_in.username = %s'

    eventSearch = executeSQLManyResponses(query,username)

    query = 'SELECT * FROM interested_in JOIN interest ON (interested_in.category=interest.category and interested_in.keyword=interest.keyword) JOIN about ON (interest.category = about.category AND interest.keyword = about.keyword) JOIN a_group ON a_group.group_id = about.group_id WHERE a_group.group_id not in (SELECT a_group.group_id FROM belongs_to JOIN a_group on belongs_to.group_id = a_group.group_id WHERE belongs_to.username = %s)'
    newGroups = executeSQLManyResponses(query,username)

    font_color = getColor(username)

    return render_template('home.html', font_color=font_color, username=username, eventSearch=eventSearch, futureEvents=futureEvents, pastEvents=pastEvents,friends=friends, friendEvents=friendEvents, button=True, groups = groups, newGroups=newGroups)

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

@app.route('/createEvent')
def createEventPage():
    username = session['username']
    cursor = conn.cursor()
    # Get groups that user is authorized to create a group in
    query = 'SELECT * FROM belongs_to JOIN a_group ON belongs_to.group_id = a_group.group_id where belongs_to.username = %s AND belongs_to.authorized = 1'
    cursor.execute(query,(username))
    groups = cursor.fetchall()
    error = 'NOT AUTHORIZED TO CREATE ANY EVENT'
    if (groups):
        return render_template("createEvent.html", groups = groups)
    else :
        return render_template("createEvent.html", groups = groups, error = error)
        

@app.route('/createAnEvent',methods=['GET', 'POST'])
def createAnEvent():
    username = session['username']
    # Get information from html
    group_id = request.form['Group']
    event_id = request.form['Event_ID']
    event_name = request.form['Event_Name']
    description = request.form['Description']
    startdate = request.form['Start_Date']
    starttime = request.form['Start_Time']
    enddate = request.form['End_Date']
    endtime = request.form['End_Time']
    location_name = request.form['Location_Name']
    zipcode = request.form['Zipcode']
    address = request.form['Address']
    loc_desc = request.form['Loc_Description']
    latitude = request.form['Latitude']
    longitude = request.form['Longitude']
    cursor = conn.cursor()
    # Check to see if location already exists
    checkQ = 'SELECT * FROM location WHERE location_name = %s AND zipcode = %s'
    cursor.execute(checkQ,(location_name, int(zipcode)))
    if(cursor.fetchone()):
        return render_template("createEvent.html", error='This location already exists')
    else:
        # Insert location into SQL
        query = 'INSERT INTO location (location_name, zipcode, address, description, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(query,(location_name, int(zipcode), address, loc_desc, float(latitude), float(longitude)))
        conn.commit()
        # Insert event into SQL
        query = 'INSERT INTO an_event (event_id, title, description, start_time, end_time, location_name, zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s);'
        cursor.execute(query,(int(event_id), event_name, description, startdate+' '+starttime, enddate+' '+endtime, location_name, zipcode))
        conn.commit()
        # Insert into ORGANIZE table
        query = 'INSERT INTO organize (event_id, group_id) VALUES (%s, %s)'
        cursor.execute(query,(event_id,group_id))
        conn.commit()
        cursor.close()
    return redirect(url_for('createEventPage'))

@app.route('/addAFriend/<username>',methods=['GET', 'POST'])
def addAFriend(username):
    mainUser = session['username']
    cursor = conn.cursor()
    query = 'INSERT INTO friend(friend_of, friend_to) VALUES (%s, %s)'
    cursor.execute(query,(mainUser, username))
    conn.commit()
    cursor.close()
    return redirect(url_for('friend', username = username))


@app.route('/friends/<username>',methods=['GET', 'POST'])
def friend(username):
    mainUser = session['username']
    addFriend = friendsWithUser(mainUser, username)
    futureEvents = nextThreeDaysOfSignedUpEvents(username)
    pastEvents = pastEventsSIgnedUpFor(username)
    friends = getFriends(username)
    friendEvents = getFriendsFutureEvents(username)
    return render_template('friends.html', username=username, futureEvents=futureEvents, pastEvents=pastEvents, friends = friends, friendEvents = friendEvents, addFriend = addFriend)

@app.route('/createGroup')
def createGroup():
    return render_template('createGroup.html')

@app.route('/createAGroup', methods=['GET', 'POST'])
def createAGroup():
    username=session['username']
    group_id = request.form['Group_ID']
    group_name = request.form['Group_Name']
    desc = request.form['Description']
    cursor = conn.cursor()
    query = 'INSERT INTO a_group (group_id, group_name, description, creator) VALUES (%s, %s, %s, %s);'
    cursor.execute(query,(int(group_id), group_name, desc, username))
    conn.commit()
    query = 'INSERT INTO belongs_to (group_id, username, authorized) VALUES (%s, %s, %s);'
    cursor.execute(query,(int(group_id), username, 0))
    conn.commit()
    cursor.close()
    return redirect(url_for('createGroup'))

# a bunch of SQL statements
def getColor(username):
    query = 'SELECT color FROM member WHERE username=%s'
    return executeSQLOneResponse(query,(str(username)))

def friendsWithUser(mainUser, member):
    query = 'SELECT * FROM friend WHERE friend_of = %s AND friend_to = %s'
    return executeSQLManyResponses(query,(str(mainUser), str(member)))

def goingToEvent(username, id):
    query = 'SELECT * FROM sign_up WHERE event_id = %s AND username=%s'
    return executeSQLOneResponse(query,(str(id), str(username)))

def executeSQLOneResponse(query,args):
    return  executeSQL(query,args)

def executeSQLManyResponses(query,args):
    return executeSQL(query,args, False)

def executeSQL(query,args,one=True):
    cursor = conn.cursor()
    cursor.execute(query, args)
    if(one):
        out = cursor.fetchone()
    else:
        out = cursor.fetchall()
    cursor.close()
    return out

def eventInPast(id):
    query = 'SELECT * FROM an_event WHERE event_id = %s AND end_time < NOW() '
    return executeSQLOneResponse(query, (str(id)))

def nextThreeDaysOfSignedUpEvents(username):
    return executeSQLManyResponses('SELECT * FROM sign_up JOIN an_event ON sign_up.event_id = an_event.event_id WHERE sign_up.username = %s AND NOW() < an_event.start_time  AND an_event.start_time < DATE_ADD(NOW(),INTERVAL 3 DAY)',username)

def pastEventsSIgnedUpFor(username):
    query = 'SELECT * FROM sign_up JOIN an_event ON sign_up.event_id = an_event.event_id WHERE sign_up.username = %s AND NOW() > an_event.start_time'
    return executeSQLManyResponses(query,username)

def getFriends(username):
    query = 'SELECT * FROM friend WHERE friend_of = %s'
    return executeSQLManyResponses(query,username)

def getFriendsFutureEvents(username):
    query = 'SELECT friend.friend_to, sign_up.event_id, an_event.title FROM friend JOIN sign_up ON friend.friend_to = sign_up.username JOIN an_event ON an_event.event_id = sign_up.event_id WHERE friend.friend_of = %s AND NOW() < an_event.start_time'
    return executeSQLManyResponses(query,username)

def getEventInfo(id):
    query = 'SELECT * FROM an_event WHERE event_id = %s'
    return executeSQLOneResponse(query,id)

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
