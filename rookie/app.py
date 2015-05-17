"""
Front-end far an experimental search engine called "Rookie"
"""

import os
from flask import Flask, request
from rookie.models import Models
from rookie.views import Views
from contracts import (
    log,
    RELOADER,
    DEBUG
)

app = Flask(__name__)


@app.route('/rookie/', methods=['GET'])
def intro():
    """
    Intro page for the web app
    """

    log.debug('/')

    log.debug(os.environ)

    data = Models().get_home()

    log.debug('/ data:')
    # log.debug(data)

    view = Views().get_home(data)

    return view


if __name__ == '__main__':
    app.run(
        use_reloader=RELOADER,
        debug=DEBUG
    )
