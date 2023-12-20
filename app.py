from python.engines.adTechAssistant import runAdTechAI, runTeachableAI
from python.tools.helpers import run_python

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
    
    # prompt = request.form.get("prompt")
    prompt = request.get_json().get('prompt', None)
    print(prompt)
    print(request.get_json())
    return simplefcn(prompt)

@app.route('/promptAI', methods=['POST']) # type: ignore
def executeAI():
    prompt = request.form.get("prompt")
    useTeachableAI = request.form.get("useTeachableAI", False)
    if prompt is None:
        prompt = request.get_json().get('prompt', None)
        useTeachableAI = request.get_json().get("useTeachableAI", False)
    print(f"prompt is: {prompt}")
    print(f"useTeachableAI is: {useTeachableAI}")

    return runAdTechAI(prompt, useTeachableAI) # type: ignore

@app.route('/runPython', methods=['POST']) # type: ignore
def runPython():
    pythonScript = request.form.get("pythonScript")
    if pythonScript is None:
        pythonScript = request.get_json().get('pythonScript', None)
    print(pythonScript)
    return run_python(pythonScript)

@app.route('/teachAI', methods=['POST']) # type: ignore
def teachAI():
    print('teaching ai api')
    prompt = request.form.get("prompt")
    thread_id = request.form.get("thread_id", '')
    save_result = request.form.get("save_result", False)

    print(f"thread_id is: {thread_id}")
    print(f"prompt is: {prompt}")
    print(f"save_result is: {save_result}")
    if prompt is None:
        prompt = request.get_json().get('prompt', None)
        thread_id = request.get_json().get("thread_id", '')
        save_result = request.get_json().get("save_result", False)

    return runTeachableAI(prompt, thread_id, save_result) # type: ignore