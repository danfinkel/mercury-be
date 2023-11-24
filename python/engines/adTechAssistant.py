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
    from concurrent.futures import ThreadPoolExecutor, TimeoutError
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


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--prompt", help="The prompt for the AI")
    # args = parser.parse_args()

    # if not args.prompt:
    #     print("Please provide a prompt")
    #     return

    # raw_prompt = args.prompt
    raw_prompt = "How many users saw an ad?"

    assistant_name = "Turbo4"

    assistant = Turbo4()

    session_id = rand.generate_session_id(assistant_name + raw_prompt)

    agent_instruments = AgentInstruments(session_id=session_id)

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
        f"Use these {POSTGRES_TABLE_DEFINITION_CAP_REF} to get data to support the analysis.", 
        POSTGRES_TABLE_DEFINITION_CAP_REF, 
        table_definitions # type: ignore
    )    

    prompt += '\n\n The database connection parameters can be found in env variables:\nhost: DATABASE_HOST\ndatabase: DATABASE_NAME\nusername: DATABASE_USERNAME\npassword: DATABASE_PASSWORD'

    # print(prompt)

    # (
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
    #     .spy_on_assistant(agent_instruments.make_agent_chat_file(assistant_name))
    #     .get_costs_and_tokens(
    #         agent_instruments.make_agent_cost_file(assistant_name)
    #     )
    #     .bank_results() # type: ignore
    # )

    return prompt


# if __name__ == '__main__':
#     print(main())
