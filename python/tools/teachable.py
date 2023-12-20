from ast import parse
from ..tools.turbo4 import Turbo4
from ..tools.llmtypes import Chat
from ..tools.memo import MemoStore

from datetime import date

TEXT_ANALYZER_MESSAGE = """You are an expert in text analysis.
The user will give you TEXT to analyze.
The user will give you analysis INSTRUCTIONS copied twice, at both the beginning and the end.
You will follow these INSTRUCTIONS in analyzing the TEXT, then give the results of your expert analysis in the format requested."""


class Teachable_Turbo4(Turbo4):
    def __init__(self):
        super().__init__()

        self.memo_store = MemoStore(
                            verbosity=3, 
                            reset=False, 
                            path_to_db_dir="/Users/danfinkel/github/mercury-be/tmp/teachable_agent_db")

        self.max_num_retrievals = 3
        self.recall_threshold = 2.5

        # self.analyzer = self.initialize_analyzer()
        # self.prepopulate_db()

    def close_db(self):
        """Cleanly closes the memo store."""
        self.memo_store.close()

    def parse_message_for_storage(self, message: str):
        """Returns the general task and instructions from the given message."""

        general_task = message.split("SUMMARY:")[1].split("INSTRUCTIONS")[0].replace('\n','').strip()
        instructions = message.split("INSTRUCTIONS:\n")[1]

        return general_task, instructions
    
    def store_a_task(self, message: str):
        """Stores a question-answer pair in the DB."""

        general_task, instructions = self.parse_message_for_storage(message)

        self.memo_store.add_input_output_pair(general_task, instructions)

        return self, str({"user": "sys_admin", 
                          "assistant_id": self.assistant_id,
                          "thread_id": self.current_thread_id,
                          "content": "Stored a task"}) + "\n"

    def save_lesson(self, message: str):
        """Stores a summary-instruction pair in the DB."""
        general_task, instructions = self.parse_message_for_storage(message)

        self.memo_store.add_input_output_pair(general_task, instructions)

        self.close_db()

        return self, str({"user": "sys_admin", 
                          "assistant_id": self.assistant_id,
                          "thread_id": self.current_thread_id,
                          "content": "Saved a lesson"}) + "\n"
        
    def concatenate_memo_texts(self, memo_list):
        """Concatenates the memo texts into a single string for inclusion in the chat context."""
        memo_texts = ""
        if len(memo_list) > 0:
            info = "\n# Memories that might help\n"
            for memo in memo_list:
                info = info + "- " + memo + "\n"
            
            print("\nMEMOS APPENDED TO LAST USER MESSAGE...\n" + info + "\n")
            memo_texts = memo_texts + "\n" + info
        return memo_texts

    # def learn_from_user_feedback(self):
    #     from tqdm import tqdm

    #     """Reviews the user comments from the last chat, and decides what teachings to store as memos."""
    #     print("\nREVIEWING CHAT FOR USER TEACHINGS TO REMEMBER")
        
    #     conversation = self.get_conversation()

    #     if len(conversation) > 0:
    #         for snippet in tqdm(conversation):
    #             comment = snippet.message
    #             # Consider whether to store something from this user turn in the DB.
    #             self.consider_memo_storage(comment)
    #     self.user_comments = []

    # def consider_memo_storage(self, comment):
    #     """Decides whether to store something from one user comment in the DB."""
    #     # Check for a problem-solution pair.
    #     response = self.analyze(
    #         comment,
    #         "Does any part of the TEXT ask the agent to perform a task or solve a problem? Answer with just one word, yes or no.",
    #     )
    #     if "yes" in response.lower():
    #         # Can we extract advice?
    #         advice = self.analyze(
    #             comment,
    #             "Briefly copy any advice from the TEXT that may be useful for a similar but different task in the future. But if no advice is present, just respond with 'none'.",
    #         )
    #         if "none" not in advice.lower():
    #             # Yes. Extract the task.
    #             task = self.analyze(
    #                 comment,
    #                 "Briefly copy just the task from the TEXT, then stop. Don't solve it, and don't include any advice.",
    #             )
    #             # Generalize the task.
    #             general_task = self.analyze(
    #                 task,
    #                 "Summarize very briefly, in general terms, the type of task described in the TEXT. Leave out details that might not appear in a similar problem.",
    #             )
    #             # Add the task-advice (problem-solution) pair to the vector DB.
    #             print("\nREMEMBER THIS TASK-ADVICE PAIR")
    #             self.memo_store.add_input_output_pair(general_task, advice)

    #     # Check for information to be learned.
    #     response = self.analyze(
    #         comment,
    #         "Does the TEXT contain information that could be committed to memory? Answer with just one word, yes or no.",
    #     )
    #     if "yes" in response.lower():
    #         # Yes. What question would this information answer?
    #         question = self.analyze(
    #             comment,
    #             "Imagine that the user forgot this information in the TEXT. How would they ask you for this information? Include no other text in your response.",
    #         )
    #         # Extract the information.
    #         answer = self.analyze(
    #             comment, "Copy the information from the TEXT that should be committed to memory. Add no explanation."
    #         )
    #         # Add the question-answer pair to the vector DB.
    #         print("\nREMEMBER THIS QUESTION-ANSWER PAIR")
    #         self.memo_store.add_input_output_pair(question, answer)
        # def prepopulate_db(self):
    #     """Adds a few arbitrary memos to the DB."""
    #     self.memo_store.prepopulate()

    # def initialize_analyzer(self):
    #     self.analyzer_name='memo_aide'
    #     self.analyzer = Turbo4()
    #     self.analyzer, _ = self.analyzer.get_or_create_assistant(self.analyzer_name)
    #     self.analyzer, _ = self.analyzer.set_instructions(TEXT_ANALYZER_MESSAGE) # type: ignore
    #     self.analyzer = self.analyzer.make_thread()
        
    #     return self.analyzer
    
    # def analyze(self, comment, instructions):
    #     """Returns the AI's analysis of the given text."""

    #     # merge comment and instructions 
    #     message = "INSTRUCTIONS:\n" + instructions + "\nTEXT:\n" + comment + "\n"
        
    #     self.analyzer, _ = self.analyzer.add_message(message)
    #     self.analyzer, new_msgs = self.analyzer.run_thread()
        
    #     return new_msgs[-1].message
    # def consider_memo_retrieval(self, comment):
    #     """Decides whether to retrieve memos from the DB, and add them to the chat context."""

    #     # First, use the user comment directly as the lookup key.
    #     print("\nLOOK FOR RELEVANT MEMOS, AS QUESTION-ANSWER PAIRS")
    #     memo_list = self.retrieve_relevant_memos(comment)
    #     print('----')
    #     print(memo_list)
    #     print('----')

    #     # Next, if the comment involves a task, then extract and generalize the task before using it as the lookup key.
    #     response = self.analyze(
    #         comment,
    #         "Does any part of the TEXT ask the agent to perform a task or solve a problem? Answer with just one word, yes or no.",
    #     )
    #     if "yes" in response.lower():
    #         print("\nLOOK FOR RELEVANT MEMOS, AS TASK-ADVICE PAIRS")
    #         # Extract the task.
    #         task = self.analyze(
    #             comment, "Copy just the task from the TEXT, then stop. Don't solve it, and don't include any advice."
    #         )
    #         # Generalize the task.
    #         general_task = self.analyze(
    #             task,
    #             "Summarize very briefly, in general terms, the type of task described in the TEXT. Leave out details that might not appear in a similar problem.",
    #         )
    #         # Append any relevant memos.
    #         memo_list.extend(self.retrieve_relevant_memos(general_task))

    #     # De-duplicate the memo list.
    #     memo_list = list(set(memo_list))

    #     # Append the memos to the last user message.
    #     print('----')
    #     print(comment + self.concatenate_memo_texts(memo_list))
    #     print('----')        
    #     return comment + self.concatenate_memo_texts(memo_list)

    # def retrieve_relevant_memos(self, input_text):
    #     """Returns semantically related memos from the DB."""
    #     memo_list = self.memo_store.get_related_memos(
    #         input_text, n_results=self.max_num_retrievals, threshold=self.recall_threshold
    #     )

    #     # Was anything retrieved?
    #     if len(memo_list) == 0:
    #         # No. Look at the closest memo.
    #         print("\nTHE CLOSEST MEMO IS BEYOND THE THRESHOLD:")
    #         self.memo_store.get_nearest_memo(input_text)
    #         print()  # Print a blank line. The memo details were printed by get_nearest_memo().

    #     # Create a list of just the memo output_text strings.
    #     memo_list = [memo[1] for memo in memo_list]
    #     return memo_list