import os
import json
from flask import Flask, render_template, send_from_directory
from flask import url_for, request, session, redirect
from flask import Flask, redirect, url_for, session, request
from flask_oauthlib.client import OAuth, OAuthException
from flask import jsonify
from flask_thumbnails import Thumbnail




FACEBOOK_APP_ID = '1276374105779390'
FACEBOOK_APP_SECRET = 'f5b0355b0cbc57a454468fb48e06ab99'

#----------------------------------------
# initialization
#----------------------------------------

app = Flask(__name__)  
app = Flask('tomatzocarnaval')
app.debug = True
app.secret_key = "super secret key"
oauth = OAuth(app)

facebook = oauth.remote_app(
                            'facebook',
                            consumer_key=FACEBOOK_APP_ID,
                            consumer_secret=FACEBOOK_APP_SECRET,
                            request_token_params={'scope': 'email'},
                            base_url='https://graph.facebook.com',
                            request_token_url=None,
                            access_token_url='/oauth/access_token',
                            access_token_method='GET',
                            authorize_url='https://www.facebook.com/dialog/oauth'
                            )


app.config['MEDIA_FOLDER'] = 'public/images/'
app.config['MEDIA_URL'] = '/media/'
thumb = Thumbnail(app)



#----------------------------------------
# controllers
#----------------------------------------

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
  	return render_template('index.html')

@app.route('/generate')
def generate():
  	return render_template('generate.html')
 
@app.route('/sucess')
def sucess():
  return render_template('sucess.html')

@app.route('/image_test')
def test():
  return render_template('test.html')


@app.route('/login')
def login():
    callback = url_for(
                       'facebook_authorized',
                       next=request.args.get('next') or request.referrer or None,
                       _external=True
                       )
    return facebook.authorize(callback=callback)


@app.route('/login/authorized')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
                                                      request.args['error_reason'],
                                                      request.args['error_description']
                                                      )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message
    
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('me?fields=picture.height(300),name')
    return render_template('generate.html', dados = {'id': me.data['id'], 'nome':me.data['name'], 'url':me.data['picture']['url']})


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


#----------------------------------------
# launch
#----------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)