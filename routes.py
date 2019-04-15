from config import app
from controllers import *
#index, new_user, login, members, new_event, add_event, search, search_event, account, update_user, logout


#master routes
app.add_url_rule('/', view_func=index)
app.add_url_rule('/logout', view_func=logout)

#User routes
app.add_url_rule('/user/new', view_func=new_user, methods=['POST'])
app.add_url_rule('/login', view_func=login, methods=['POST'])
app.add_url_rule('/dashboard', view_func=members)
app.add_url_rule('/user/<id>', view_func=account)
app.add_url_rule('/user/<id>/update', view_func=update_user, methods=['POST'])

#Event routes
app.add_url_rule('/search', view_func=search)
app.add_url_rule('/search/events', view_func=search_event,  methods=['POST'])
app.add_url_rule('/event/<id>/join', view_func=like_event, methods=['POST'])
app.add_url_rule('/new/event', view_func=new_event)
app.add_url_rule('/add_event', view_func=add_event, methods=['POST'])
app.add_url_rule('/event/<id>', view_func=show_event)
app.add_url_rule('/event/<id>/update', view_func=update_event, methods=['POST'])
app.add_url_rule('/event/<id>/delete', view_func=cancel_event)
