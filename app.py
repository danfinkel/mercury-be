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
        import time
        yield '1' + '\n'
        time.sleep(2)
        yield '2' + '\n'
        time.sleep(2)
        yield '3' + '\n'
        time.sleep(2)
        yield '4' + '\n'
        time.sleep(2)
        yield '5' + '\n'
    
    return simplefcn()
