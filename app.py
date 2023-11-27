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
        yield {"user": 'dan', "content": 'Hello this is a test'}
        time.sleep(2)
        yield {"user": "dan", "content": 'AI is not wired up yet'}
        time.sleep(2)
        yield {"user": "dan", "content": 'So instead you are getting this automatic response'}
        time.sleep(2)
        yield {"user": "dan", "content": 'Perhaps next time...'}
        time.sleep(2)
        yield {"user": "dan", "content": 'OK goodbye'}
    
    return simplefcn()
