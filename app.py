import os
from flask import Flask, render_template, send_from_directory, url_for, session, request, redirect
from flask_oauth import OAuth
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageOps

DEBUG = True
FACEBOOK_APP_ID = '1276374105779390'
FACEBOOK_APP_SECRET = 'f5b0355b0cbc57a454468fb48e06ab99'

#----------------------------------------
# initialization
#----------------------------------------
app = Flask(__name__)
app.secret_key = '5x07x0bOx84x0cx99x8bxf7xf8xbdxcexd3xd9xfax16x19x89x01xc7W6'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hrvmzdcoakadyp:19c0494b83012af8c82731022251bbebeeb0ebc4bcf6e3610df5233537316dc1@ec2-75-101-142-182.compute-1.amazonaws.com:5432/dcdlstuh600udj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#----------------------------------------
# User Table
#----------------------------------------
from app import db

class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    facebook_id = db.Column(db.String(200))
    facebook_img = db.Column(db.String(200))
    email = db.Column(db.String(200))
    logged = db.Column(db.String(200))
    facebook_token = db.Column(db.String(200))
    sexta = db.Column(db.String(200))
    sabado = db.Column(db.String(200))
    domingo = db.Column(db.String(200))
    segunda = db.Column(db.String(200))
    terca = db.Column(db.String(200))

    def __repr__(self):
        return '<User %r>' % (self.facebook_id)


#----------------------------------------
# initializations
#----------------------------------------
app.debug = DEBUG
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

    me = facebook.get('me?fields=id,name,picture.height(300),email')
    name = me.data['name']
    facebook_id = me.data['id']
    facebook_img = me.data['picture']['data']['url']
    email = me.data['email']
    logged = 'true'
    facebook_token = resp['access_token']
    sexta = ''
    sabado = ''
    domingo = ''
    segunda = ''
    terca = ''

    if not db.session.query(User).filter(User.email == email).count():
      user = User(name= name, facebook_id=facebook_id, facebook_img=facebook_img, email=email, logged=logged, facebook_token=facebook_token, sexta=sexta, sabado=sabado, domingo=domingo, segunda=segunda, terca=terca)
      db.session.add(user)
      db.session.commit()

    session['email'] = email

    return redirect(url_for('generate', email=email))

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


@app.route('/generate/<email>')
def generate(email):
    session['email'] = email
    return render_template('generate.html')

@app.route('/create_calendar', methods=['GET', 'POST'])
def create_calendar():
    if request.method == 'POST':
        me = facebook.get('me?fields=id,name,picture.height(300),email')   
        email = me.data['email']
        user = User.query.filter_by(email=email).first()
        user.sexta = request.form['sexta']
        user.sabado = request.form['sabado']
        user.domingo = request.form['domingo']
        user.segunda = request.form['segunda']
        user.terca = request.form['terca']
        db.session.commit()
        return redirect(url_for('generate_image'))
    else:
        return render_template('generate.html')
 

@app.route('/sucess')
def sucess():
  return render_template('sucess.html')

@app.route('/generate_image')
def generate_image():
    me = facebook.get('me?fields=id,name,picture.height(300),email')   
    email = me.data['email']
    user = User.query.filter_by(email=email).first()
    
    fonts_path = os.path.join(app.root_path, 'static'), 'fonts/roboto_slab'
    background = Image.open('static/mg/fundo_carna_tomatzo.png')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.join(fonts_path, 'RobotoSlab-Regular.ttf'), 24)

    draw.text((220, 325),blocos[0]["nome"],(0,0,0),font=font)
    pathToSave = os.path.join(app.root_path, 'generated')
    img.save(pathToSave, 'sample-out.png')  

    return redirect(url_for('sucess'))

#----------------------------------------
# launch
#----------------------------------------

if __name__ == '__main__':
    app.run()