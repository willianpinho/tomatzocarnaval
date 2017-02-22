import os
from flask import Flask, render_template, send_from_directory, url_for, session, request, redirect
from flask_oauth import OAuth

SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = '1276374105779390'
FACEBOOK_APP_SECRET = 'f5b0355b0cbc57a454468fb48e06ab99'

#----------------------------------------
# initialization
#----------------------------------------
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
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
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('me?fields=picture.height(300)')
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

def pop_login_session():
    session.pop('oauth_token', None)

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