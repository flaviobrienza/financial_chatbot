import streamlit as st
from langchain.agents import AgentExecutor, create_openai_functions_agent 
from langchain_openai.chat_models import ChatOpenAI 
from langchain.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import typing
import langchain_core
import time
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from secret_api_key import openaikey 
from UI_helper import CompanyData, PlotCompanyData

st.set_option('deprecation.showPyplotGlobalUse', False)
msgs = StreamlitChatMessageHistory()

# Importing tools
tools = [CompanyData(), PlotCompanyData()]

# Creating the Agent 
model = ChatOpenAI(temperature=0, openai_api_key=openaikey) 
prompt = ChatPromptTemplate(input_variables=['agent_scratchpad', 'input'], 
                   input_types={'chat_history': typing.List[typing.Union[langchain_core.messages.ai.AIMessage, langchain_core.messages.human.HumanMessage, langchain_core.messages.chat.ChatMessage, langchain_core.messages.system.SystemMessage, langchain_core.messages.function.FunctionMessage, langchain_core.messages.tool.ToolMessage]], 'agent_scratchpad': typing.List[typing.Union[langchain_core.messages.ai.AIMessage, langchain_core.messages.human.HumanMessage, langchain_core.messages.chat.ChatMessage, langchain_core.messages.system.SystemMessage, langchain_core.messages.function.FunctionMessage, langchain_core.messages.tool.ToolMessage]]}, 
                   messages=[SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template='You are a financial chatbot that answers about stock prices. You can even plot them. Do not say anything when the chain starts.')), 
                             MessagesPlaceholder(variable_name='chat_history'), 
                             HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')), 
                             MessagesPlaceholder(variable_name='agent_scratchpad')])
memory = ConversationBufferWindowMemory(k=5, chat_memory=msgs, return_messages=True, memory_key='chat_history') 
agent = create_openai_functions_agent(
    llm=model,
    tools=tools, 
    prompt=prompt
) 
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory)  

st.title('Financial Chatbot :chart_with_upwards_trend:')
st.header('Gather Financial Data from the Chatbot :necktie:')
question = st.chat_input('Ask your question')

plot_messages = [] 

st.sidebar.title('Plot your data here :desktop_computer:')
plot_box = st.sidebar.text_input('What do you want to plot? :left_speech_bubble:', help="Use terms like 'plot' or 'show' to create the graph") 
if plot_box: 
    plot_messages.append(plot_box)
    plot_answer = agent_executor.invoke({'input':plot_box})['output'] 
    st.sidebar.pyplot(plot_answer)
    plot_messages.append(plot_answer)

print(plot_messages)
print(msgs)

for msg in msgs.messages:
    if msg.content not in plot_messages:
        st.chat_message(msg.type).write(msg.content)

if question:
    answer = agent_executor.invoke({'input':question})['output']
    st.chat_message('human').write(question)
    st.chat_message('ai').write(answer)
