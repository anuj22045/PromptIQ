
from core.llm_client import generate_response
from core.response_generator import generate_llm_response
import streamlit as st


st.set_page_config(
    page_title="PromptIQ",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 PromptIQ")
st.subheader("LLM Evaluation & Prompt Optimization Platform")

st.markdown(
    "Generate AI responses, evaluate their quality, "
    "and optimize prompts intelligently."
)

st.divider()

st.header("Enter your prompt")


user_prompt = st.text_area(
    "Your prompt",
    placeholder="what is RAG",
    height=150
)


if st.button("Generate Response", type="primary"):
    if not user_prompt.strip():
        st.warning("Please enter the prompt to get the response")

    else:
        try:
            with st.spinner("Generating the response"):
                response = generate_llm_response(user_prompt)

            st.success("response generated successfully")

            st.subheader("Original prompt")
            st.info(user_prompt)

            st.subheader("Generated response")
            st.markdown(response)

        except Exception as e:
            st.error(f"something went wrong: {str(e)} ")


st.divider()

st.caption("PromptIQ | Intelligent LLM Evaluation & Prompt Optimization")