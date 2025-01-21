import streamlit as st  # Import python packages
from snowflake_session import create_snowflake_session  # Import the custom session creation function

from snowflake.cortex import Complete
from snowflake.core import Root

import pandas as pd
import json

pd.set_option("max_colwidth", None)

### Default Values
NUM_CHUNKS = 3  # Num-chunks provided as context. Play with this to check how it affects your accuracy
slide_window = 7  # how many last conversations to remember. This is the slide window.

# Service parameters
CORTEX_SEARCH_DATABASE = "SUSTAINABLITY_CORTEX_SEARCH_DOCS"
CORTEX_SEARCH_SCHEMA = "DATA"
CORTEX_SEARCH_SERVICE = "CC_SEARCH_SERVICE_CS"
###### ######

# Columns to query in the service
COLUMNS = [
    "chunk",
    "relative_path",
    "category"
]

# Use the new session creation function
session = create_snowflake_session()
root = Root(session)

svc = root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]

### Functions
def config_options():
    st.sidebar.selectbox('Select your model:', (
        'mixtral-8x7b',
        'snowflake-arctic',
        'mistral-large',
        'mistral-large2',
        'llama3-8b',
        'llama3-70b',
        'reka-flash',
        'mistral-7b',
        'llama2-70b-chat',
        'gemma-7b'), key="model_name")

    categories = session.table('docs_chunks_table').select('category').distinct().collect()

    cat_list = ['ALL']
    for cat in categories:
        cat_list.append(cat.CATEGORY)

    st.sidebar.selectbox('Select what products you are looking for', cat_list, key="category_value")

    st.sidebar.checkbox('Do you want that I remember the chat history?', key="use_chat_history", value=True)

    st.sidebar.checkbox('Debug: Click to see summary generated of previous conversation', key="debug", value=True)
    st.sidebar.button("Start Over", key="clear_conversation", on_click=init_messages)
    st.sidebar.expander("Session State").write(st.session_state)

# Other functions (init_messages, get_similar_chunks_search_service, etc.) remain unchanged...

def main():
    st.title(f":speech_balloon: EcoGuide : Sustainability and Environmental Awareness Assistant with Snowflake Cortex")
    st.header("Introduction for the Sustainability Chatbot:")
    st.write("Welcome to EcoGuide – your trusted companion on the journey toward sustainable living and environmental stewardship! 🌱")
    # Introduction content...

    config_options()
    init_messages()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if question := st.chat_input("What do you want to know about your products?"):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            question = question.replace("'", "")
            with st.spinner(f"{st.session_state.model_name} thinking..."):
                response, relative_paths = answer_question(question)
                response = response.replace("'", "")
                message_placeholder.markdown(response)

                if relative_paths != "None":
                    with st.sidebar.expander("Related Documents"):
                        for path in relative_paths:
                            cmd2 = f"select GET_PRESIGNED_URL(@docs, '{path}', 360) as URL_LINK from directory(@docs)"
                            df_url_link = session.sql(cmd2).to_pandas()
                            url_link = df_url_link._get_value(0, 'URL_LINK')
                            display_url = f"Doc: [{path}]({url_link})"
                            st.sidebar.markdown(display_url)

        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
