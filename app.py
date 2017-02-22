import os
from flask import Flask, render_template, send_from_directory, url_for, session, request, redirect
from flask_oauth import OAuth
from flask_sqlalchemy import SQLAlchemy


SECRET_KEY = '5\x07\x0bO\x84\x0c\x99\x8b\xf7\xf8\xbd \xce\xd3\xd9\xfa\x16\x19)\x89\x01\xc7W6'
DEBUG = True
FACEBOOK_APP_ID = '1276374105779390'
FACEBOOK_APP_SECRET = 'f5b0355b0cbc57a454468fb48e06ab99'

#----------------------------------------
# initialization
#----------------------------------------
app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hrvmzdcoakadyp:19c0494b83012af8c82731022251bbebeeb0ebc4bcf6e3610df5233537316dc1@ec2-75-101-142-182.compute-1.amazonaws.com:5432/dcdlstuh600udj'

#----------------------------------------
# User Table
#----------------------------------------
from app import db

class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    facebook_id = db.Column(db.String(64))
    facebook_img = db.Column(db.String(120))
    email = db.Column(db.String(120))
    logged = db.Column(db.String(120))
    facebook_token = db.Column(db.String(120))
    sexta = db.Column(db.String(120))
    sabado = db.Column(db.String(120))
    domingo = db.Column(db.String(120))
    segunda = db.Column(db.String(120))
    terca = db.Column(db.String(120))

    def __repr__(self):
        return '<User %r>' % (self.facebook_id)


#----------------------------------------
# initializations
#----------------------------------------
app.debug = DEBUG
app.secret_key = SECRET_KEY
db.create_all()
db.session.commit()
oauth = OAuth()

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

    me = facebook.get('me?fields=id,name,picture,email')

    name = me.data['name']
    facebook_id = me.data['id']
    facebook_img = me.data['picture']
    email = me.data['email']
    logged = 'true'
    facebook_token = (resp['access_token'], '')
    sexta = ''
    sabado = ''
    domingo = ''
    segunda = ''
    terca = ''

    user = User(name= name, facebook_id=facebook_id, facebook_img=facebook_img, email=email, logged=logged, facebook_token=facebook_token, sexta=sexta, sabado=sabado, domingo=domingo, segunda=segunda, terca=terca)
    db.session.add(user)
    
    db.session.commit()
    return redirect(url_for('generate'))

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
  app.run()