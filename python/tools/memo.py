import chromadb
from chromadb.config import Settings
import pickle
import os

class MemoStore:
    """
    Provides memory storage and retrieval for a TeachableAgent, using a vector database.
    Each DB entry (called a memo) is a pair of strings: an input text and an output text.
    The input text might be a question, or a task to perform.
    The output text might be an answer to the question, or advice on how to perform the task.
    Vector embeddings are currently supplied by Chroma's default Sentence Transformers.
    """

    def __init__(self, verbosity, reset, path_to_db_dir):
        """
        Args:
            - verbosity (Optional, int): 1 to print memory operations, 0 to omit them. 3+ to print memo lists.
            - path_to_db_dir (Optional, str): path to the directory where the DB is stored.
        """
        self.verbosity = verbosity
        self.reset = reset
        self.path_to_db_dir = path_to_db_dir

        # Load or create the vector DB on disk.
        settings = Settings(
            anonymized_telemetry=False, allow_reset=True, is_persistent=True, persist_directory=path_to_db_dir
        )
        self.db_client = chromadb.Client(settings)
        self.vec_db = self.db_client.create_collection("memos", get_or_create=True)  # The collection is the DB.
        if reset:
            self.reset_db()

        # Load or create the associated memo dict on disk.
        self.path_to_dict = os.path.join(path_to_db_dir, "uid_text_dict.pkl")
        self.uid_text_dict = {}
        self.last_memo_id = 0
        if (not reset) and os.path.exists(self.path_to_dict):
            print("\nLOADING MEMORY FROM DISK")
            print("    Location = {}".format(self.path_to_dict))
            with open(self.path_to_dict, "rb") as f:
                self.uid_text_dict = pickle.load(f)
                self.last_memo_id = len(self.uid_text_dict)
                if self.verbosity >= 3:
                    self.list_memos()

    def list_memos(self):
        """Prints the contents of MemoStore."""
        print("LIST OF MEMOS")
        for uid, text in self.uid_text_dict.items():
            input_text, output_text = text
            print(
                    "  ID: {}\n    INPUT TEXT: {}\n    OUTPUT TEXT: {}".format(uid, input_text, output_text),
                )

    def close(self):
        """Saves self.uid_text_dict to disk."""
        print("\nSAVING MEMORY TO DISK")
        print("    Location = {}".format(self.path_to_dict))
        with open(self.path_to_dict, "wb") as file:
            pickle.dump(self.uid_text_dict, file)

    def reset_db(self):
        """Forces immediate deletion of the DB's contents, in memory and on disk."""
        print("\nCLEARING MEMORY", "light_green")
        self.db_client.delete_collection("memos")
        self.vec_db = self.db_client.create_collection("memos")
        self.uid_text_dict = {}

    def add_input_output_pair(self, input_text, output_text):
        """Adds an input-output pair to the vector DB."""
        self.last_memo_id += 1
        self.vec_db.add(documents=[input_text], ids=[str(self.last_memo_id)])
        self.uid_text_dict[str(self.last_memo_id)] = input_text, output_text
        if self.verbosity >= 1:
            print(
                    "\nINPUT-OUTPUT PAIR ADDED TO VECTOR DATABASE:\n  ID\n    {}\n  INPUT\n    {}\n  OUTPUT\n    {}".format(
                        self.last_memo_id, input_text, output_text
            ))
        if self.verbosity >= 3:
            self.list_memos()

    def get_nearest_memo(self, query_text):
        """Retrieves the nearest memo to the given query text."""
        results = self.vec_db.query(query_texts=[query_text], n_results=1)
        uid, input_text, distance = results["ids"][0][0], results["documents"][0][0], results["distances"][0][0] # pyright: ignore[reportOptionalSubscript]
        input_text_2, output_text = self.uid_text_dict[uid]
        assert input_text == input_text_2
        if self.verbosity >= 1:
            print(
                    "\nINPUT-OUTPUT PAIR RETRIEVED FROM VECTOR DATABASE:\n  INPUT1\n    {}\n  OUTPUT\n    {}\n  DISTANCE\n    {}".format(
                        input_text, output_text, distance
                    ),
            )
        return input_text, output_text, distance

    def get_related_memos(self, query_text, n_results, threshold):
        """Retrieves memos that are related to the given query text within the specified distance threshold."""
        if n_results > len(self.uid_text_dict):
            n_results = len(self.uid_text_dict)
        results = self.vec_db.query(query_texts=[query_text], n_results=n_results)
        memos = []
        num_results = len(results["ids"][0])
        for i in range(num_results):
            uid, input_text, distance = results["ids"][0][i], results["documents"][0][i], results["distances"][0][i] # pyright: ignore[reportOptionalSubscript]
            if distance < threshold:
                input_text_2, output_text = self.uid_text_dict[uid]
                assert input_text == input_text_2
                if self.verbosity >= 1:
                    print(
                            "\nINPUT-OUTPUT PAIR RETRIEVED FROM VECTOR DATABASE:\n  INPUT1\n    {}\n  OUTPUT\n    {}\n  DISTANCE\n    {}".format(
                                input_text, output_text, distance
                            ),
                            "light_green",
                    )
                memos.append((input_text, output_text, distance))
        return memos

    def prepopulate(self):
        """Adds a few arbitrary examples to the vector DB, just to make retrieval less trivial."""
        if self.verbosity >= 1:
            print("\nPREPOPULATING MEMORY", "light_green")
        examples = []
        examples.append({"text": "When I say papers I mean research papers, which are typically pdfs.", "label": "yes"})
        examples.append({"text": "Please verify that each paper you listed actually uses langchain.", "label": "no"})
        examples.append({"text": "Tell gpt the output should still be latex code.", "label": "no"})
        examples.append({"text": "Hint: convert pdfs to text and then answer questions based on them.", "label": "yes"})
        examples.append(
            {"text": "To create a good PPT, include enough content to make it interesting.", "label": "yes"}
        )
        examples.append(
            {
                "text": "No, for this case the columns should be aspects and the rows should be frameworks.",
                "label": "no",
            }
        )
        examples.append({"text": "When writing code, remember to include any libraries that are used.", "label": "yes"})
        examples.append({"text": "Please summarize the papers by Eric Horvitz on bounded rationality.", "label": "no"})
        examples.append({"text": "Compare the h-index of Daniel Weld and Oren Etzioni.", "label": "no"})
        examples.append(
            {
                "text": "Double check to be sure that the columns in a table correspond to what was asked for.",
                "label": "yes",
            }
        )
        for example in examples:
            self.add_input_output_pair(example["text"], example["label"])