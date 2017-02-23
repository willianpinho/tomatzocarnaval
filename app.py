import os, boto3, StringIO, re, urllib, cStringIO
from io import BytesIO
from flask import Flask, render_template, send_from_directory, url_for, session, request, redirect, abort, send_file
from flask_oauth import OAuth
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageOps

from tempfile import NamedTemporaryFile
from shutil import copyfileobj
from os import remove

DEBUG = True
FACEBOOK_APP_ID = '1276374105779390'
FACEBOOK_APP_SECRET = 'f5b0355b0cbc57a454468fb48e06ab99'

BUCKET_NAME = 'bucketeer-a0950fe0-0534-45c0-a578-24cdfe574b12'
REGION = 'us-east-1'
ACCESS_KEY = 'AKIAI6OMT5QF3D3K74YA'
SECRET_ACCESS_KEY = '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'
PUBLIC_URL = 'https://bucketeer-a0950fe0-0534-45c0-a578-24cdfe574b12.s3.amazonaws.com/public/'

#----------------------------------------
# initialization
#----------------------------------------
app = Flask(__name__)
app.secret_key = '5x07x0bOx84x0cx99x8bxf7xf8xbdxcexd3xd9xfax16x19x89x01xc7W6'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hrvmzdcoakadyp:19c0494b83012af8c82731022251bbebeeb0ebc4bcf6e3610df5233537316dc1@ec2-75-101-142-182.compute-1.amazonaws.com:5432/dcdlstuh600udj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

        return redirect(url_for('sucess'))
    else:
        return render_template('generate.html')
 
@app.route('/create/<facebook_id>.png')
def create(facebook_id):
    me = facebook.get('me?fields=id,name,picture.height(300),email') 
    email = me.data['email']
    user = User.query.filter_by(email=email).first()
  
    formats = {
        'image/jpeg': 'JPEG',
        'image/png': 'PNG',
        'image/gif': 'GIF'
    }

    response = urllib.urlopen(user.facebook_img)
    image_type = response.info().get('Content-Type')
    try:
        format = formats[image_type]
    except KeyError:
        raise ValueError('Not a supported image format')

    file = cStringIO.StringIO(response.read())
    user_img = Image.open(file)
    user_img_size = (150,150)
    user_img_position = (325,31)
    user_img = user_img.resize(user_img_size, Image.ANTIALIAS)
 
    #Extract digits from request variable e.g 200x300
    dimensions = '800x800'
    sizes = [int(s) for s in re.findall(r'\d+', dimensions)]
    if len(sizes) != 2:
      abort(400)
    width = sizes[0]
    height = sizes[1]
    
    image = Image.open("static/img/fundo_carna_tomatzo.png")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('static/fonts/roboto_slab/RobotoSlab-Regular.ttf', 24)

    image.paste(user_img, user_img_position)

    #Position text roughly in the center
    w,h = font.getsize(user.name)
    draw.text(((800-w)/2,190),user.name,(0,0,0),font=font)

    draw.text((220, 325),user.sexta,(0,0,0),font=font)
    draw.text((220, 370),user.sabado,(0,0,0),font=font)
    draw.text((220, 415),user.domingo,(0,0,0),font=font)
    draw.text((220, 457),user.segunda,(0,0,0),font=font)
    draw.text((220, 502),user.terca,(0,0,0),font=font)

    byte_io = BytesIO()
    image.save(byte_io, 'PNG')
    byte_io.seek(0)

    return send_file(byte_io, mimetype='image/png')

@app.route('/sucess')
def sucess():
    me = facebook.get('me?fields=id,name,picture.height(300),email') 
    email = me.data['email']
    user = User.query.filter_by(email=email).first()
    src = 'http://www.tomatzocarnaval.com/create/' + user.facebook_id + '.png'

    return render_template('sucess.html', src=src)


#----------------------------------------
# launch
#----------------------------------------

if __name__ == '__main__':
    app.run()