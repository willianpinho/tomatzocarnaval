import os
from flask import Flask, render_template, send_from_directory

#----------------------------------------
# initialization
#----------------------------------------
app = Flask(__name__)

app.config.update(
    DEBUG = True,
)

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

#----------------------------------------
# launch
#----------------------------------------


if __name__ == '__main__':
    app.run()