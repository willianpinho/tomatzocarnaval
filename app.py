import os
from flask import Flask, render_template, send_from_directory, url_for, session, request, redirect
from flask_oauth import OAuth
from flask.ext.sqlalchemy import SQLAlchemy


SECRET_KEY = '5\x07\x0bO\x84\x0c\x99\x8b\xf7\xf8\xbd \xce\xd3\xd9\xfa\x16\x19)\x89\x01\xc7W6'
DEBUG = True
FACEBOOK_APP_ID = '1276374105779390'
FACEBOOK_APP_SECRET = 'f5b0355b0cbc57a454468fb48e06ab99'

#----------------------------------------
# initialization
#----------------------------------------
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
oauth = OAuth()

#----------------------------------------
# User Table
#----------------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<Name %r>' % self.name


#----------------------------------------
# facebook authentication
#----------------------------------------

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': ('email, ')}
)

#----------------------------------------
# Views Controller
#----------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')

    me = facebook.get('me?fields=name,picture')
 
    user = User('me.data['name']', 'willjrpp@gmail.com')
    db.session.add(user)
    db.session.commit()
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'],request.args.get('next'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_token')

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)

@app.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/generate')
def generate():
    return render_template('generate.html')
 
@app.route('/sucess')
def sucess():
  return render_template('sucess.html')

@app.route('/image_test')
def test():
  return render_template('test.html')

#----------------------------------------
# launch
#----------------------------------------

if __name__ == '__main__':
  db.create_all()
  app.run()