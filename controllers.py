from flask import render_template, redirect, request, session, flash
from config import db, datetime
from models import User, Event

#### Controller Functions ####
## Render index page
def index():
    #add location map with events
    return render_template('index.html')

##User controllers
## Add new user
def new_user():
    errors = User.validate(request.form)
    if errors:
        for error in errors:
            flash(error)
        return redirect('/')
    user_id = User.add_user(request.form)
    session['user_id'] = user_id
    return redirect('/dashboard')

#Log in new user
def login():
    valid, response = User.login_assist(request.form)
    if not valid:
            flash(response)
            return redirect('/')
    session['user_id'] = response
    print(response)
    return redirect('/dashboard')
##adding first name
def first():
    user = User.query.get(session['user_id'])
    return user.first_name

#rendering navigation on the dashboard
def nav():
    user = User.query.get(session['user_id'])
    return render_template('nav.html', user = user)

##render dashboard
def members():
    if 'user_id' not in session:
        return redirect('/')
    today = datetime.now().strftime('%A, %B %d, %Y')

    user = User.get_user(session['user_id'])
    myevents = User.user_event(user.id)

    print(myevents)

    session['first_name'] = user.first_name
    return render_template('dashboard.html',
    user=user, today=today,
    events = myevents
    )

### Render the account page ###
def account(id):
    account = User.get_user(id)
    my_events = Event.my_event(id)
    print(my_events)
    return render_template('account.html',
    account = account
    #events = my_events
    )

### upadate user profile ###
def update_user(id):
    errors = User.validate(request.form)
    if errors:
        for error in errors:
            flash(error)
        return redirect(url_for('account',id = id))
    profile = User.edit_user(request.form)
    return redirect('/dashboard')

### Event Controllers ###
### Render events search page ###
def search():
    all_events = Event.all_events()
    return render_template('search.html',
    name = session['first_name'],
    fevents = all_events
    )

### Search and filter for events ### Not working
def search_event():
    events = Event.get_event(request.form)
    return redirect('/search')

### Render New Event Page ###
def new_event():
    return render_template('new.html', name = session['first_name'])

# Joining an event
def like_event(id):
    like_event = User.join_event(id)
    return redirect('/search')

### Add new event ###
def add_event():
    errors = Event.validate(request.form)
    if errors:
        for error in errors:
            flash(error)
        return redirect('/new/event')
    event = Event.add_event(request.form)
    return redirect('/search')

### Render the events page ###
def show_event(id):
    one_event = Event.event(id)
    return render_template('event.html', event = one_event)

### update event ###
def update_event(id):
    errors = Event.validate(request.form)
    if errors:
        for error in errors:
            flash(error)
        return redirect(url_for('show_event', id = id))
    update = Event.edit_event(request.form, id )
    return redirect('/search')

### Delete event ###
def cancel_event(id):
    delete_event = Event.delete(id)
    return redirect('/search')

#### Logout ####
def logout():
    session.clear()
    return redirect('/')
