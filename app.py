from python.engines.adTechAssistant import main

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    # return main()
    return 'Hello, World!'

@app.route('/test') # type: ignore
def get_index():   
    def simplefcn():
        yield '1'
        yield '2'
        yield '3'
        yield '4'
        yield '5'
    
    return simplefcn()
