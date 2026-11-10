
import streamlit as st

from core.response_generator import generate_llm_response
from evaluation.evaluation_service import run_full_evaluation


# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="PromptIQ",
    page_icon="🧠",
    layout="wide"
)


# ----------------------------------
# SESSION STATE
# ----------------------------------

if "prompt" not in st.session_state:
    st.session_state.prompt = ""

if "response" not in st.session_state:
    st.session_state.response = None

if "evaluation" not in st.session_state:
    st.session_state.evaluation = None


# ----------------------------------
# HEADER
# ----------------------------------

st.title("🧠 PromptIQ")

st.subheader(
    "Intelligent LLM Evaluation & Prompt Optimization Platform"
)

st.write(
    "Generate AI responses and evaluate their quality "
    "using Custom LLM-as-a-Judge and DeepEval."
)

st.divider()


# ----------------------------------
# USER INPUT
# ----------------------------------

st.header("✍️ Enter Your Prompt")

user_prompt = st.text_area(
    "Your Prompt",
    placeholder="Example: Explain RAG in AI with a practical example...",
    height=130
)


# Optional reference answer and context
with st.expander("Advanced Evaluation Inputs (Optional)"):

    reference_answer = st.text_area(
        "Reference Answer",
        placeholder="Enter the expected answer if available..."
    )

    context = st.text_area(
        "Supporting Context",
        placeholder="Enter supporting information or source context..."
    )


# GENERATE AND EVALUATE


if st.button("🚀 Generate & Evaluate", type="primary"):

    if not user_prompt.strip():

        st.warning("Please enter a prompt.")

    else:

        # Clear previous results
        st.session_state.prompt = user_prompt
        st.session_state.response = None
        st.session_state.evaluation = None

        try:

            # STEP 1: Generate response
            with st.spinner("Generating LLM response..."):

                response = generate_llm_response(user_prompt)

            st.session_state.response = response

            # STEP 2: Evaluate response
            with st.spinner(
                "Running Custom Judge and DeepEval..."
            ):

                evaluation = run_full_evaluation(
                    prompt=user_prompt,
                    response=response,
                    reference_answer=reference_answer or None,
                    context=context or None
                )

            st.session_state.evaluation = evaluation

        except Exception as e:

            st.error(f"Application error: {e}")


# ----------------------------------
# DISPLAY ORIGINAL RESPONSE
# ----------------------------------

if st.session_state.response:

    st.divider()

    st.header("📝 Generated Response")

    st.subheader("Original Prompt")

    st.info(st.session_state.prompt)

    st.subheader("LLM Response")

    st.markdown(st.session_state.response)


# ----------------------------------
# DISPLAY EVALUATION RESULTS
# ----------------------------------

if st.session_state.evaluation:

    evaluation = st.session_state.evaluation

    st.divider()

    st.header("📊 Evaluation Dashboard")


    # ==================================
    # CUSTOM LLM-AS-A-JUDGE
    # ==================================

    st.subheader("1. Custom LLM-as-a-Judge")

    custom_results = evaluation["custom_judge"]

    if custom_results:

        custom_data = custom_results.model_dump()

        metrics = [
            "accuracy",
            "relevance",
            "faithfulness",
            "clarity",
            "completeness"
        ]

        columns = st.columns(3)

        for i, metric_name in enumerate(metrics):

            metric = custom_data[metric_name]

            with columns[i % 3]:

                score = metric["score"]

                if score is not None:
                    st.metric(
                        metric_name.title(),
                        f"{score}/10"
                    )
                else:
                    st.metric(
                        metric_name.title(),
                        "N/A"
                    )

        st.subheader("Custom Judge Explanations")

        for metric_name in metrics:

            metric = custom_data[metric_name]

            with st.expander(metric_name.title()):

                if metric["score"] is not None:
                    st.write(
                        f"Score: {metric['score']}/10"
                    )
                else:
                    st.write("Score: N/A")

                st.write(metric["reason"])

                if metric["weaknesses"]:

                    st.write("Identified Weaknesses:")

                    for weakness in metric["weaknesses"]:
                        st.write(f"- {weakness}")

        st.info(
            f"Overall Custom Judge Score: "
            f"{custom_data['overall_score']}/10"
        )

    else:

        st.error(
            "Custom Judge evaluation failed: "
            + evaluation["errors"].get(
                "custom_judge",
                "Unknown error"
            )
        )


    # ==================================
    # DEEPEVAL
    # ==================================

    st.divider()

    st.subheader("2. DeepEval – G-Eval")

    deepeval_results = evaluation["deepeval"]

    if deepeval_results:

        deepeval_columns = st.columns(3)

        for i, (metric_name, details) in enumerate(
            deepeval_results.items()
        ):

            with deepeval_columns[i]:

                st.metric(
                    metric_name,
                    f"{details['score_out_of_10']}/10"
                )

                if details["passed"]:
                    st.success("Passed")
                else:
                    st.error("Failed")

                with st.expander("View Explanation"):
                    st.write(details["reason"])

    else:

        st.error(
            "DeepEval evaluation failed: "
            + evaluation["errors"].get(
                "deepeval",
                "Unknown error"
            )
        )


    # ==================================
    # ERRORS
    # ==================================

    if evaluation["errors"]:

        st.divider()

        st.warning("Some evaluation components encountered errors.")

        for component, error in evaluation["errors"].items():

            st.write(f"**{component}:** {error}")


# ----------------------------------
# FOOTER
# ----------------------------------

st.divider()

st.caption(
    "PromptIQ | Intelligent LLM Evaluation & Prompt Optimization"
)
