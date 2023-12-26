from sympy import use
from python.tools.turbo4 import Turbo4
from python.tools.teachable import Teachable_Turbo4
from python.tools.llmtypes import Chat, TurboTool
from python.tools import rand
from python.tools.instruments import AgentInstruments
from python.tools.llm import add_cap_ref
from python.tools.llm import getTableDefs
from python.tools.helpers import run_python

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