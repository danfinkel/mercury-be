import streamlit as st
from code_editor import code_editor
import asyncio
import json
import requests as re

import aiohttp

CHAT_ICONS = {
    "dan": "⛹️",
    "Engineer": "⛹️",
    "databaseAdmin": "🖥️",
    "user": "🦁",
    "sys_admin": "🔧",
    "robot": "🤖"
}

# URL = 'https://mercury-jzz5.onrender.com/promptAI'
URL = "http://127.0.0.1:5000/promptAI"

prompts = {'reach': 'How many users saw an ad?',
           '7-Day Daily Reach': 'Please report daily campaign reach where reach for a given day is defined to be total number of users who were exposed in the previous 7 day window. Perform the calculation for each day from August 1 2023 to September 1 2023',
           'impressions': 'How many ads were served?',
           'lift': 'What was the lift of the campaign?'
           }


class StreamlitPage():
    def __init__(self, page_title):
        self.page_title = page_title        

    @property
    def page_title(self):
        return self._page_title
    
    @page_title.setter
    def page_title(self, value):
        self._page_title = value

class StreamlitChatPage(StreamlitPage):
    def __init__(self, page_title):
        super().__init__(page_title) # type: ignore        

        st.set_page_config(page_title=self.page_title)
        self.tab1, self.tab2, self.tab3, self.tab4, self.tab5 = st.tabs(["AI Chat", "Summary", "Run Python Code", "Audit Results", "Save for Reuse"])
        self.ai_question = 'No Question Yet Submitted'
        self.ai_code = 'No Python Yet Generated'
        self.ai_answer = "No AI Answer Yet Generated"

        self.ai_response = {
                            "question": 'No Question Yet Submitted',
                            "code": 'No Code Yet Generated',
                            "answer": 'No AI Answer Has Been Created'
                            }

    @property
    def ai_response(self):
        return self._ai_response
    
    @ai_response.setter
    def ai_response(self, value):
        self._ai_response = value
        if 'chat_responses' in st.session_state.keys() and len(st.session_state.chat_responses) > 0:
            for chat in st.session_state.chat_responses:
                if 'QUESTION' in chat["content"]:
                    self._ai_response["question"] = chat["content"].split('QUESTION:')[1].split('PYTHON SCRIPT')[0]
                if 'PYTHON SCRIPT' in chat["content"]:
                    self._ai_response["code"] = chat["content"].split('PYTHON SCRIPT:')[1].split('ANSWER')[0]
                if 'ANSWER' in chat["content"]:
                    self._ai_response["answer"] = chat["content"].split('ANSWER:')[1]
                    break
    
    def _top_ai_page(self):    
        header = st.container()
        header.title('📈💬 OpenAI Powered Analytics', help="AI Enabled Agents Prompted to Solve Data Science Tasks. This application is pointed at a Postgres database with a set of (fake) exposures for an advertising campaign for Bob's Hamburgers. There is also a (fake) conversions file and a (fake) universe file.")

        form = header.form("my_form")
        self.promptForAI = form.text_input("Hey 🦁 enter your request here", key="text")
        self.runAI = form.form_submit_button("Submit")

        header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

        ### Custom CSS for the sticky header
        st.markdown(
            """
        <style>
            div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
                position: sticky;
                top: 2.875rem;
                background-color: #0f1117;
                z-index: 999;
            }
            .fixed-header {
                border-bottom: 1px solid black;
            }
        </style>
            """,
            unsafe_allow_html=True
        )            
        
        # st.write("AI Enabled Agents Prompted to Solve Data Science Tasks. This application is pointed at a Postgres database with a set of (fake) exposures for an advertising campaign for Bob's Hamburgers. There is also a (fake) conversions file and a (fake) universe file.")        
        # st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    def _set_chat(self):
        if 'chat_responses' not in st.session_state:            
            st.session_state.chat_responses = [{"chatName": "Engineer", "content": "Hello, I am your AI Assistant"}]
            st.session_state.chat_responses.append({"chatName": "sys_admin", "content": "And I am System Admin that will help you work with your AI Assistant. How can we help you?"})

    def _populate_chat(self):
        self._set_chat()
        for msg in st.session_state.chat_responses:
            with st.chat_message(name=msg["chatName"], avatar=CHAT_ICONS.get(msg["chatName"])):
                st.write(str(msg["content"]))

    def _build_menu(self):
        with st.sidebar:
            st.title('⚙️ Configuration')

            self.api_secret = st.text_input("Enter API Secret")

            self.selected_prompt = st.selectbox(label="Pre-Build Prompts", 
                                                options=list(prompts.keys()), 
                                                index=0, 
                                                )
            self.menu_preview = st.button("Preview Prompt", on_click=self.on_preview_click)
            
            self.clear_button = st.button("Clear", on_click=self.clear_chat)  
    
    def on_preview_click(self):
        st.session_state.prompt = prompts[self.selected_prompt] # type: ignore      
        st.session_state.text = prompts[self.selected_prompt] # type: ignore

        # self._populate_chat()

    def clear_chat(self):
        st.session_state.pop("chat_responses")
        st.session_state.text = None


    async def chatWAI(self, promptForAI=st.session_state.get("prompt")):
        """
        Inspired by: https://stackoverflow.com/questions/59681726/how-to-read-lines-of-a-streaming-api-with-aiohttp-in-python
        and: https://stackoverflow.com/questions/74800726/running-asyncio-with-streamlit-dashboard
        General async Tutorial here: https://realpython.com/python-async-features/
        """
        with st.chat_message(name='user', avatar=CHAT_ICONS.get('user')):
            st.write(promptForAI)
            st.session_state.chat_responses.append({"chatName": 'user', "content": promptForAI})    

        async with aiohttp.ClientSession() as session:
            async with session.post(URL, data={'prompt': promptForAI}) as r:
                async for line in r.content:
                    formatted_line = line.replace(b'"', b'\\\'').decode('utf-8').replace("'",'"')                
                    try:
                        content = json.loads(formatted_line)["content"]
                        chatName = json.loads(formatted_line)["user"]
                    except json.decoder.JSONDecodeError:
                        print('ERROR ERROR ERROR')
                        print(line)
                        content = str(formatted_line.split('"content": ')[1].split('}\n')[0])
                        chatName = str(formatted_line.split('"user": ')[1]).split(', "content')[0]
                    with st.chat_message(name=chatName, avatar=CHAT_ICONS.get(chatName)):
                        st.write(str(content))
                        st.session_state.chat_responses.append({"chatName": chatName, "content": str(content)})

    def initialize(self):
        with self.tab1:
            self._top_ai_page()        
            self._build_menu()
            
            self._populate_chat()  

            # self._chat_input()      

            if self.runAI:
                if self.promptForAI != '':
                    st.session_state.prompt = self.promptForAI # type: ignore
                    asyncio.run(self.chatWAI(st.session_state.prompt))
                else:
                    st.alert('Enter a Prompt!') # type: ignore
        
        with self.tab2:
            self.ai_response = {
                            "question": 'No Question Yet Submitted',
                            "code": 'No Code Yet Generated',
                            "answer": 'No AI Answer Has Been Created'
                            }
            st.markdown('## Analytic Question:\n\n' + self.ai_response["question"])
            st.markdown('## Python Script:\n\n' + self.ai_response["code"])
            st.markdown('## Answer:\n\n' + self.ai_response["answer"])
        
        with self.tab3:
            run_python_form = st.form("Run Python")
            with run_python_form:
                st.markdown("## Python Script")
                response_dict = code_editor(self.ai_response["code"])
                run_python_button = st.form_submit_button("Run Python")
                if run_python_button:
                    print('here')
                    response = re.post('http://127.0.0.1:5000/runPython', json={'pythonScript': self.ai_response["code"].replace('```python', '').replace('```', '').replace('```python', '')})
                    print('here2')
                    st.write(response.text)

cp = StreamlitChatPage(page_title='📈💬 OpenAI Powered Analytics')
cp.initialize()  