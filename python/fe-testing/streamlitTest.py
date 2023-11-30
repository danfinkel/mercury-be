import streamlit as st
import asyncio
import json

import aiohttp

CHAT_ICONS = {
    "dan": "⛹️",
    "Engineer": "⛹️",
    "databaseAdmin": "🖥️",
    "user": "🦁"
}

URL = 'https://mercury-jzz5.onrender.com/test'

prompts = {'reach': 'How many users saw an ad?',
           'impressions': 'How many ads were served?',
           'lift': 'What was the lift of the campaign?'
           }

async def chatWAI(promptForAI=st.session_state.get("prompt")):
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
                formatted_line = line.decode("utf-8").replace("'",'"').replace("\n","")
                content = json.loads(formatted_line)["content"]
                chatName = json.loads(formatted_line)["user"]
                with st.chat_message(name=chatName, avatar=CHAT_ICONS.get(chatName)):
                    st.write(str(content))
                    st.session_state.chat_responses.append({"chatName": chatName, "content": str(content)})
                    
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

    def _top_page(self):        

        st.title('📈💬 OpenAI Powered Analytics')
        st.write("AI Enabled Agents Prompted to Solve Data Science Tasks. This application is pointed at a Postgres database with a set of (fake) exposures for an advertising campaign for Bob's Hamburgers. There is also a (fake) conversions file and a (fake) universe file.")
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    def _set_chat(self):
        if 'chat_responses' not in st.session_state:
            st.session_state.chat_responses = [{"chatName": "Engineer", "content": "How may I help you?"}]

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
            
            st.text_area(
                "Prompt Preview", key="text"
            )

            self.run_button = st.button("Run Prompt")

            self.clear_button = st.button("Clear", on_click=self.clear_chat)  

    def _chat_input(self):
        promptForAI = st.chat_input(placeholder="Enter your request here")
        if promptForAI:
            st.session_state.prompt = promptForAI # type: ignore
            asyncio.run(chatWAI(promptForAI))    

    def inititate_chat(self, promptForAI):
        st.session_state.prompt = prompts[self.selected_prompt] # type: ignore
        asyncio.run(chatWAI())
    
    def on_preview_click(self):
        st.session_state.text = prompts[self.selected_prompt] # type: ignore      

        # self._populate_chat()

    def clear_chat(self):
        st.session_state.pop("chat_responses")
        st.session_state.text = None

    def initialize(self):
        self._top_page()
        self._build_menu()
        self._populate_chat()  
        self._chat_input()      

        if self.run_button:
            st.session_state.prompt = prompts[self.selected_prompt] # type: ignore
            asyncio.run(chatWAI(st.session_state.prompt))

cp = StreamlitChatPage(page_title='📈💬 OpenAI Powered Analytics')
cp.initialize()  