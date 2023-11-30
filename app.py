from python.engines.adTechAssistant import runAdTechAI

from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def hello_world():
    # return main()
    return 'Hello, World!'

@app.route('/test', methods=['POST']) # type: ignore
def get_index():   
    def simplefcn(prompt):
        import time
        yield str({"user": "dan", "content": "Hello this is a test"}) + "\n"
        time.sleep(2)
        yield str({"user": "dan", "content": f"You asked: {prompt}"}) + "\n"
        time.sleep(2)
        yield str({"user": "dan", "content": "AI is not wired up yet"}) + "\n"
        time.sleep(2)
        yield str({"user": "dan", "content": "So instead you are getting this automatic response"}) + "\n"
        time.sleep(2)
        yield str({"user": "dan", "content": "Perhaps next time..."}) + "\n"
        time.sleep(2)
        yield str({"user": "dan", "content": "OK goodbye"}) + "\n"
    
    prompt = request.form.get("prompt")
    print(prompt)
    return simplefcn(prompt)

@app.route('/promptAI', methods=['POST']) # type: ignore
def executeAI():
    prompt = request.form.get("prompt")
    return runAdTechAI(prompt)