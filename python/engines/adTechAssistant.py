from ..tools.turbo4 import Turbo4
from ..tools.llmtypes import Chat, TurboTool
from ..tools import rand
from ..tools.instruments import AgentInstruments
from ..tools.llm import add_cap_ref
from ..tools.llm import getTableDefs


from typing import List, Callable
import os
import argparse
import dotenv
import time

# from postgres_da_ai_agent.agents.instruments import PostgresAgentInstruments
# from postgres_da_ai_agent.modules import embeddings

dotenv.load_dotenv()

assert os.environ.get("RENDER_PG_URL"), "POSTGRES_CONNECTION_URL not found in .env file"
assert os.environ.get("RENDER_PG_SCHEMA"), "DATABASE_SCHEMA not found in .env file"

DB_URL = os.environ.get("RENDER_PG_URL")
DATABASE_SCHEMA = os.environ.get("RENDER_PG_SCHEMA")
POSTGRES_TABLE_DEFINITION_CAP_REF = "TABLE_DEFINITIONS"

table_definitions = getTableDefs(DB_URL, DATABASE_SCHEMA)

custom_function_tool_config = {
    "type": "function",
    "function": {
        "name": "run_python",
        "description": "A function that executes a python script locally.",
        "parameters": {
            "type": "object",
            "properties": {"pythonScript": {"type": "string"}},
        },
    },
}


def run_python(pythonScript: str) -> str:
    import os
    import sys   
    import subprocess
    
    # write out script
    filename="runpython.py"
    work_dir = "./pythonscript"

    filepath = os.path.join(work_dir, filename)
    stdoutpath = os.path.join(work_dir, 'stdout.txt')
    file_dir = os.path.dirname(filepath)

    os.makedirs(file_dir, exist_ok=True)
    if pythonScript is not None:
        with open(filepath, "w", encoding="utf-8") as fout:
            fout.write(pythonScript) # type: ignore
    
    cmd = [
        sys.executable, filepath,
        ]
    
    f = open(stdoutpath, "w")
    subprocess.call(cmd, stdout=f)
    f.close()

    try:
        with open(stdoutpath, "r") as f:
            return f.read() # type: ignore
    except Exception as e:
        return e # type: ignore


def runAdTechAI(raw_prompt):
    assistant_name = "Turbo4"

    assistant = Turbo4()

    # session_id = rand.generate_session_id(assistant_name + raw_prompt)
    # agent_instruments = AgentInstruments(session_id=session_id)

    ai_tools = [
        TurboTool("run_python", custom_function_tool_config, run_python),
    ]

    prompt = add_cap_ref(
        "", # type: ignore
        "Write a python script that will print an answer the QUESTION.",
        "QUESTION:",
        raw_prompt
    )

    prompt = add_cap_ref(
        prompt,  # type: ignore
        f"\n\nUse these {POSTGRES_TABLE_DEFINITION_CAP_REF} to get data to support the analysis.", 
        POSTGRES_TABLE_DEFINITION_CAP_REF, 
        table_definitions # type: ignore
    )    

    prompt += '\n\n The database connection parameters can be found in env variables:\nhost: RENDER_PG_HOST\ndatabase: RENDER_PG_NAME\nusername: RENDER_PG_USER\npassword: RENDER_PG_PASSWORD'

    print('***** 1')
    assistant, status_msg = assistant.get_or_create_assistant(assistant_name)
    yield status_msg
    time.sleep(1)

    print('***** 2')
    assistant, instruct_msg = assistant.set_instructions("You are an elite python developer that specializes in adtech. You generate the most concise and performant python scripts.") # type: ignore
    yield instruct_msg
    time.sleep(1)

    print('***** 3')
    assistant = assistant.equip_tools(ai_tools) # type: ignore
    
    print('***** 4')
    assistant = assistant.make_thread()
    
    print('***** 5')
    assistant, prompt_msg = assistant.add_message(prompt)
    yield str({"user": "sys_admin", 
                "content": "Here is your enriched prompt"}) + "\n"
    yield prompt_msg

    print('***** 6')
    assistant, new_msgs = assistant.run_thread()
    for msg in new_msgs:
        yield str({"user": "dan", "content": msg.message}) + "\n"

    print('***** 7')
    assistant, next_step_msg = assistant.add_message("use the run_python function to run the python you have just generated.")
    yield str({"user": "dan", 
               "content": "Next we ask AI to execute the script"}) + "\n"
    yield next_step_msg

    print('***** 8')
    assistant, new_msgs = assistant.run_thread(toolbox=[ai_tools[0].name]) # this is a function that executes a string of python passed into it
    for msg in new_msgs:
        yield str({"user": "dan", "content": msg.message}) + "\n"

    
    print('***** 9')
    assistant, summary_msg = assistant.add_message("Please summarize the conversation in the following format:\n\n QUESTION: {copy the original question here}\n\n PYTHON SCRIPT: {copy the python script here}\n\nANSWER: {copy the answer here}")
    yield str({"user": "sys_admin", "content": "Generating a summary message"}) + "\n"
    
    print('***** 10')
    assistant, new_msgs = assistant.run_thread()
    for msg in new_msgs:
        yield str({"user": "dan", "content": msg.message}) + "\n"    


    # print('***** 11')
    # print(assistant.get_conversation())

    return 'Made it all the way through'

    # print(prompt)

    # return (
    #     assistant.get_or_create_assistant(assistant_name)
    #     .set_instructions("You're an elite python developer that specializes in adtech. You generate the most concise and performant python scripts.")
    #     .equip_tools(ai_tools) # type: ignore
    #     .make_thread()
    #     .add_message(prompt)
    #     .run_thread()
    #     .add_message("use the run_python function to run the python you've just generated.")
    #     .run_thread(toolbox=[ai_tools[0].name]) # this is a function that executes a string of python passed into it
    #     .add_message("Please summarize the conversation in the following format:\n\n QUESTION: {copy the original question here}\n\n PYTHON SCRIPT: {copy the python script here}\n\nANSWER: {copy the answer here}")
    #     .run_thread()
    #     .print_conversion()    
    #     .get_conversation()
    #     # .spy_on_assistant(agent_instruments.make_agent_chat_file(assistant_name))
    #     # .get_costs_and_tokens(
    #     #     agent_instruments.make_agent_cost_file(assistant_name)
    #     #     )
    #     # .bank_results() # type: ignore
    # )

    # return prompt
