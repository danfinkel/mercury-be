from ast import parse
from ..tools.turbo4 import Turbo4
from ..tools.llmtypes import Chat
from ..tools.memo import MemoStore

from datetime import date

CODE_REPAIR_INSTRUCTIONS = """You are an expert in python code.
The user will give you CODE written in python and a corresponding ERROR that was produced when the user.
You will diagnose the problem with the CODE and correct it.
You will respond by publishing the entire corrected CODE, not just the line that was changed. 
Please do not provide any additional text -- just the corrected CODE. 
Please do not format the code to markdown."""


class CodeRepair_Turbo4(Turbo4):
    def __init__(self, python_code, error_message):
        super().__init__()

        self.python_code = python_code
        self.error_message = error_message

        self.assistant_name = "code_repairer"

    def _generate_prompt(self):
        prompt = f"""
        Hello - There is a mistake in my CODE. Based on the ERROR 
        can you find the mistake, and print an updated version of 
        the code? Please only print the corrected version of the code. Thank you!

        CODE:
        {self.python_code}

        ERROR:
        {self.error_message}
        """

        return prompt

    def repair_code(self):
        """
        Returns the repaired code.
        """

        print('Starting code repair...')
        assistant, status_msg = self.get_or_create_assistant(self.assistant_name)

        assistant, instruct_msg = assistant.set_instructions(CODE_REPAIR_INSTRUCTIONS) # type: ignore

        assistant, thread_id = assistant.make_thread()

        assistant, prompt_msg = assistant.add_message(self._generate_prompt())

        print('Repairing code...')
        assistant, new_msgs = assistant.run_thread()

        return new_msgs[-1]

