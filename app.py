from config import *

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PW_REGEX = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$')

#Navaigation
#nav.Bar('top', [
#    nav.Item('Home', 'members'),
#    nav.Item('New Event', 'new_event'),
#    nav.Item('Search', 'search'),
#    nav.Item('Account','account'),
#    nav.Item('Logout','logout')
#])
###Add Date time
#today = date.today()
##joined_events table

joined_events = db.Table('joined',
              db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
              db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
              db.Column('created_at', db.DateTime, server_default=func.now()))

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(45), nullable = False)
    last_name = db.Column(db.String(45), nullable = False)
    email = db.Column(db.String(45), nullable = False)
    pw_hash = db.Column(db.String(255), nullable = False)
    birth_day = db.Column(db.String(25), nullable = False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    #add joined_events relationship
    events_this_user_joins = db.relationship('Event', secondary=joined_events)

    @classmethod
    def validate(cls, form):
        errors = []
        if len(form['first_name']) < 2:
            errors.append('First name must be at least 2 characters long')
        if len(form['last_name']) < 2:
            errors.append('Last name must be at least 2 characters long')
        if not EMAIL_REGEX.match(form['email']):
            errors.append('Please enter a valid email address')
        if not PW_REGEX.match(request.form['password']):
            flash('* Please enter a valid password: 6-20 characters, A-Z and (# $ % @ &)')

        return errors

    @classmethod
    def add_user(cls, form):
        pw_hash = bcrypt.generate_password_hash(form['password'])
        user = User(
         first_name=form['first_name'],
         last_name=form['last_name'],
         email=form['email'],
         pw_hash=pw_hash,
         birth_day=form['bday']
         )
        db.session.add(user)
        db.session.commit()
        return user.id

    @classmethod
    def login_assist(cls, form):
        user = User.query.filter_by(email=form['email']).first()
        if user:
            if bcrypt.check_password_hash(user.pw_hash, form['password']):
                return (True, user.id)
        return (False, 'email or password incorrect')

    @classmethod
    def get_user(cls, id):
        user = User.query.get(id)
        print(user)
        return user

###Add Option to change Password ###
    @classmethod
    def edit_user(cls,form):
        user_update = User.query.get(session['user_id'])
        user_update.first_name = form['first_name']
        user_update.last_name = form['last_name']
        user_update.email = form['email']
        db.session.commit()
        return user_update.id

#### Events Table #####
class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(25), nullable = False)
    location = db.Column(db.String(25), nullable = False)
    info = db.Column(db.String(125), nullable = False)
    attendess = db.Column(db.Integer, nullable = True)
    date = db.Column(db.String(20), nullable = False)
    time = db.Column(db.String(10), nullable = False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    #add relationship
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    user = db.relationship('User', foreign_keys=[user_id], backref="my_events", cascade="all")
    #add joined_events relationship
    users_who_joined_this_event = db.relationship('User', secondary=joined_events)

### validate event
    @classmethod
    def validate(cls, form):
        errors = []
        if len(form['type']) < 2:
            errors.append('Events must be at least 2 characters long')
        if len(form['location']) < 2:
            errors.append('Location must be at least 2 characters long')
        if len(form['info']) < 5:
            errors.append('Event Information must be at least 2 characters long')
        if len(form['attendees']) < 1:
            errors.append('Attedees must be at more than one')
        if len(form['edate']) < 8:
            errors.append('Please enter a valid date mm/dd/yyyy')
        if len(form['etime']) < 2:
            errors.append('Please enter a valid time 00:00 AM/PM')
        return errors

### create a new event
    @classmethod
    def add_event(cls, form):
        event = Event(
        type=form['type'],
        location=form['location'],
        info=form['info'],
        attendess=form['attendees'],
        date=form['edate'],
        time=form['etime'],
        user_id=session['user_id']
        )
        db.session.add(event)
        db.session.commit()
        return event

# method for event edit
    @classmethod
    def edit_event(cls, form, id):
        event_update = Event.query.get(id)
        print(form['location'])
        event_update.type=form['type']
        event_update.location=form['location']
        event_update.info=form['info']
        event_update.attendess=form['attendees']
        event_update.date=form['edate']
        event_update.time=form['etime']
        #even_update.user_id=session['user_id']
        db.session.commit()
        return event_update

# method does not work #
    @classmethod
    def get_event(cls, form):
        events = Event.query.filter_by(type=form['search'], location=form['search_opt'],date=form['search_opt'] )
        return events

    @classmethod
    def all_events(cls):
        all_events = Event.query.all()
        return all_events

#method for events the user organized
    @classmethod
    def my_event(cls, id):
        my_events = Event.query.filter_by(user_id = id)
        print('user id: ', id)
        return my_events

#get event for single events page
    @classmethod
    def event(cls, id):
        one_event = Event.query.get(id)
        print('event id: ', id)
        return one_event

#
    @classmethod
    def delete(cls, id):
        delete_event = Event.query.get(id)
        db.session.delete(delete_event)
        db.session.commit()

#### Controller Functions ####        
## Render index page
@app.route('/')
def index():
    #add location map with events
    return render_template('index.html')

##User controllers
## Add new user
@app.route('/user/new', methods=['POST'])
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
@app.route('/login', methods=['POST'])
def login():
    valid, response = User.login_assist(request.form)
    if not valid:
            flash(response)
            return redirect('/')
    session['user_id'] = response
    print(response)
    return redirect('/dashboard')

##render dashboard
@app.route('/dashboard')
def members():
    if 'user_id' not in session:
        return redirect('/')

    user = User.get_user(session['user_id'])
    #myevents = Event.my_event(session['user_id'])

    session['first_name'] = user.first_name
    return render_template('dashboard.html',
    user=user
    #events = myevents
    )

### Render the account page ###
@app.route('/user/<id>')
def account(id):
    account = User.get_user(id)
    my_events = Event.my_event(id)
    print(my_events)
    return render_template('account.html',
    account = account
    #events = my_events
    )

### upadate user profile ###
@app.route('/user/<id>/update', methods=['POST'])
def update_user(id):
    errors = User.validate(request.form)
    if errors:
        for error in errors:
            flash(error)
        return redirect(f'/user/{id}')
    profile = User.edit_user(request.form)
    return redirect('/dashboard')

### Event Controllers ###
### Render New Event Page ###
@app.route('/new/event')
def new_event():
    return render_template('new.html', name = session['first_name'])

### Add new event ###
@app.route('/add_event', methods=['POST'])
def add_event():
    errors = Event.validate(request.form)
    if errors:
        for error in errors:
            flash(error)
        return redirect('/new/event')
    event = Event.add_event(request.form)
    return redirect('/search')

### Render events search page ###
@app.route('/search')
def search():
    all_events = Event.all_events()
    return render_template('search.html',
    name = session['first_name'],
    fevents = all_events
    )

### Search and filter for events ### Not working
@app.route('/search/events', methods=['POST'])
def search_event():
    events = Event.get_event(request.form)
    return redirect('/search')

### Render the events page ###
@app.route('/event/<id>')
def show_event(id):
    one_event = Event.event(id)
    return render_template('event.html', event = one_event)

### update event ###
@app.route('/event/<id>/update', methods=['POST'])
def update_event(id):
    errors = Event.validate(request.form)
    if errors:
        for error in errors:
            flash(error)
        return redirect(f'/event/{id}')#fix this
    update = Event.edit_event(request.form, id )
    return redirect('/search')

### Delete event ###
@app.route('/event/<id>/delete')
def cancel_event(id):
    delete_event = Event.delete(id)
    return redirect('/search')

#### Logout ####
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

###ADD ROUTES ###


if __name__ == "__main__":
    app.run(debug=True)
