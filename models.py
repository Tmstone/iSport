from sqlalchemy.sql import func
from config import *

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PW_REGEX = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$')


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

    def __repr__(self):
        return '<User {}>'.format(self.first_name)

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

### events_this_user_joins
    @classmethod
    def join_event(cls, id):
        current_user = User.query.get(session['user_id'])
        event = Event.query.get(id)
        current_user.events_this_user_joins.append(event)
        db.session.commit()
        return current_user

## get events user joined
    @classmethod
    def user_event(cls, id):
        my_events = User.query.get(id)
        print(my_events.events_this_user_joins)
        return my_events.events_this_user_joins

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

    def __repr__(self):
        return '<Event {}>'.format(self.type)

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

# Filtered Search method ### method does not work #
    @classmethod
    def get_event(cls, form, id):
        events = Event.query.get(id)
        return events

    @classmethod
    def all_events(cls):
        all_events = Event.query.all()
        return all_events

#method for users who joined this event
    @classmethod
    def my_event(cls, id):
        my_events = Event.query.get(id)
        print(my_events)
        return my_events.users_who_joined_this_event

#get event for single events page
    @classmethod
    def event(cls, id):
        one_event = Event.query.get(id)
        print('event id: ', id)
        return one_event

#delete an event
    @classmethod
    def delete(cls, id):
        delete_event = Event.query.get(id)
        db.session.delete(delete_event)
        db.session.commit()
