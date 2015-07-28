import pdb
from flask import Flask
from flask import render_template
from experiment import log

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/answer/<string:name>', methods=['POST'])
def log_answer(name):
    pdb.set_trace()
    log.debug(name)
    return "awesome bro"

if __name__ == '__main__':
    app.run(debug=True)