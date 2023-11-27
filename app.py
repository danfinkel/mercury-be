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
        # yield str({"user": "dan", "content": "Hello this is a test"})
        yield "Hello this is a test"
        time.sleep(2)
        yield "AI is not wired up yet"
        time.sleep(2)
        yield "So instead you are getting this automatic response"
        time.sleep(2)
        yield "Perhaps next time..."
        time.sleep(2)
        yield "OK goodbye"
    
    return simplefcn()
