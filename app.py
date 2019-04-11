from config import *

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PW_REGEX = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$')

#Navaigation
nav.Bar('top', [
    nav.Item('Home', 'members'),
    nav.Item('New Event', 'new_event'),
    nav.Item('Search', 'search'),
    nav.Item('Account','account'),
    nav.Item('Logout','logout')
])


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

    #events = db.relationship('Event', backref='my_events', cascade="all, delete-orphan")

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
    def get_user(cls, form):
        user = User.query.get(session['user_id'])
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
        return event.id

    @classmethod
    def get_event(cls):
        events = Event.query.all()
        return events

@app.route('/')
def index():
    #add location map with events
    return render_template('index.html')

@app.route('/new_user', methods=['POST'])
def new_user():
    errors = User.validate(request.form)
    if errors:
        for error in errors:
            flash(error)
        return redirect('/')
    user_id = User.add_user(request.form)
    session['user_id'] = user_id
    return redirect('/dashboard')

@app.route('/login', methods=['POST'])
def login():
    valid, response = User.login_assist(request.form)
    if not valid:
            flash(error)
            return redirect('/')
    session['user_id'] = response
    print(response)
    return redirect('/dashboard')

@app.route('/dashboard')
def members():
    if 'user_id' not in session:
        return redirect('/')
    user = User.get_user(session['user_id'])
    session['first_name'] = user.first_name
    return render_template('dashboard.html', name = user.first_name )

###Render New Event Page###
@app.route('/new')
def new_event():
    return render_template('new.html', name = session['first_name'])

###Add new event###
@app.route('/add_event', methods=['POST'])
def add_event():
    event = Event.add_event(request.form)
    return redirect('/search')

#search for Events
@app.route('/search')
def search():
    events = Event.get_event()

    return render_template('search.html',
    name = session['first_name'],
    fevents = events
    )

#add search query route and controller


#render the account page. Add id variable###
@app.route('/user')
def account():
    account = User.get_user(session['user_id'])
    return render_template('account.html',
    name = account.first_name,
    last= account.last_name,
    email=account.email,
    )
###upadate user profile###
@app.route('/user/update', methods=['POST'])
def update_user():
    profile = User.edit_user(request.form)
    return redirect('/dashboard')

####Logout####
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
