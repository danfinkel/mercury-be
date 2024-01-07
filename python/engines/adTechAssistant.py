from sympy import use
from ..tools.turbo4 import Turbo4
from ..tools.teachable import Teachable_Turbo4
from ..tools.llmtypes import Chat, TurboTool
from ..tools import rand
from ..tools.instruments import AgentInstruments
from ..tools.llm import add_cap_ref
from ..tools.llm import getTableDefs
from ..tools.helpers import run_python


from typing import List, Callable
import os
import argparse
import dotenv
import time

# from postgres_da_ai_agent.agents.instruments import PostgresAgentInstruments
# from postgres_da_ai_agent.modules import embeddings

os.environ.pop('OPENAI_API_KEY', None)
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
        "description": "A function that executes a python script. If you pass in a string, it will be executed as a python script. It returns a tuple of the form (status, output).",
        "parameters": {
            "type": "object",
            "properties": {"pythonScript": {"type": "string"}},
        },
    },
}

def runAdTechAI(raw_prompt, useTeachableAI: bool = False):
    assistant_name = "Turbo4"
    print(f"useTeachableAI is: {useTeachableAI} and its type is {type(useTeachableAI)}")
    if useTeachableAI:
        assistant= Teachable_Turbo4()
        lessons_list = assistant.memo_store.get_related_memos(raw_prompt, n_results=3, threshold=2.5)
    else:
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
        f"\n\nThe data you need to execute the task can be found in a postgres database with {POSTGRES_TABLE_DEFINITION_CAP_REF} described below.", 
        POSTGRES_TABLE_DEFINITION_CAP_REF, 
        table_definitions # type: ignore
    )    

    if useTeachableAI:
        prompt = add_cap_ref(
            prompt,  # type: ignore
            f"\n\nFinally, here are some lessons on this topic provided by previous users.", 
            'PREVIOUS LESSONS',
            lessons_list # type: ignore
        )    

    prompt += '\n\n To connect to the postgres database with the relevent datasets you can use the following env variables:\nhost: RENDER_PG_HOST\ndatabase: RENDER_PG_NAME\nusername: RENDER_PG_USER\npassword: RENDER_PG_PASSWORD'

    print('***** 1')
    assistant, status_msg = assistant.get_or_create_assistant(assistant_name)
    yield status_msg
    time.sleep(1)

    print('***** 2')
    assistant, instruct_msg = assistant.set_instructions("You are an elite python developer that specializes in adtech. You generate the most concise and performant python scripts.") # type: ignore
    yield instruct_msg
    time.sleep(1)

    print('***** 3')
    assistant = assistant.equip_tools(ai_tools, equip_on_assistant=False) # type: ignore
    
    print('***** 4')
    assistant, thread_id = assistant.make_thread()
    
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

def runTeachableAI(latest_prompt: str, thread_id: str = '', save_result: bool = False):
    """
    This function will return once the user types 'exit'.
    """
    new_thread = True if thread_id == '' else False

    assistant_name = "Roger"
    roger = Teachable_Turbo4()
    
    print('***** 1')
    roger, status_msg = roger.get_or_create_assistant(assistant_name)
    if new_thread:
        yield status_msg
    time.sleep(1)

    if new_thread:
        print('***** 2')
        roger, instruct_msg = roger.set_instructions("You are an assistant data scientist that specializes in adtech measurement. We are going to work together to build some detailed descriptions of common measurement tasks in advertising tech. Our goal is to create descriptions that will help future AI assistants when the user provides vague or incomplete prompts.") # type: ignore
        yield instruct_msg
        time.sleep(1)
        
        print('***** 3a')
        roger, thread_id = roger.make_thread()
        yield str({"user": "sys_internal", "thread_id": thread_id, "content": ""}) + "\n"
    else:
        print('***** 3b')
        roger.current_thread_id = thread_id
    
    print('***** 4')
    roger, prompt_msg = roger.add_message(latest_prompt)

    print('***** 5')
    roger, new_msgs = roger.run_thread()
    if new_thread:
        for msg in new_msgs:
            yield str({"user": "dan", "thread_id": thread_id, "content": msg.message}) + "\n"
    else:
        # new_msgs isnt reliable -- TODO: fix this
        yield str({"user": "dan", "thread_id": thread_id, "content": new_msgs[0].message}) + "\n"
        
    print('***** 6')
    if save_result:
        for msg in new_msgs:
            if 'SUMMARY' in msg.message:
                roger, save_msg = roger.save_lesson(msg.message) # type: ignore
                break


