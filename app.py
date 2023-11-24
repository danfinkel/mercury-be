from python.engines.adTechAssistant import main

from flask import Flask
app = Flask(__name__)

@app.route('/') # type: ignore
def hello_world():
    return main()
    # return 'Hello, World!'
