import streamlit as st
from main import get_qa_chain
st.title("Saaki.ai QA")
query=st.text_input("Enter your query: ")
if st.button("Search"):
    st.write(f"The entered query is: {query}")
    chain=get_qa_chain()
    response=chain(query)
    st.header("Answer: ")
    st.write(response.get("result"))