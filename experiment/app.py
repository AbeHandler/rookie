import pdb
from flask import Flask
from flask import render_template
from experiment import log
from experiment import LENS_CSS, BANNER_CSS

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html',
                           lens_css=LENS_CSS,
                           banner_css=BANNER_CSS)


@app.route('/answer/<string:name>', methods=['POST'])
def log_answer(name):
    log.debug(name)
    return "awesome bro"

if __name__ == '__main__':
    app.run(debug=True)
