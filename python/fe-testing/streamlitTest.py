import streamlit as st
import asyncio
import json

import aiohttp

prompts = {'reach': 'How many users saw an ad?'}

async def chatWAI():
    async with aiohttp.request('get', 'https://mercury-jzz5.onrender.com/test') as r:
        async for line in r.content:
            with st.chat_message(name='user'):
                st.write(json.loads(line))


st.set_page_config(page_title="📈💬 Analyics Agent Chat")

st.title('📈💬 OpenAI Powered Analytics')
st.write("AI Enabled Agents Prompted to Solve Data Science Tasks")
st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

with st.sidebar:
    st.title('⚙️ Configuration')

    selected_prompt = st.selectbox("Pre-Build Prompts", list(prompts.keys()), index=0)

    menu_selections = st.button("Select and Run")
    menu_preview = st.button("Preview Prompt")
    menu_clear = st.button("Reset Prompt")
    cost_estimate = st.button("Report Cost")

st.chat_input()

if menu_preview:
    st.write(prompts[selected_prompt]) # type: ignore
    # st.write(menu_preview) # type: ignore

if menu_selections:
    asyncio.run(chatWAI())