"""
Front-end far an experimental search engine called "Rookie"
"""

from flask import Flask


@app.route('/rookie/hello', methods=['GET'])
def search():
    """
    Hello!
    """
    return "Hello, world"


if __name__ == '__main__':
    app.run(debug=True)
