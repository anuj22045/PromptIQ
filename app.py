
import streamlit as st

from ambiguity.detector import detect_ambiguity
from ambiguity.clarifier import resolve_intent

from core.response_generator import generate_llm_response
from evaluation.evaluation_service import run_full_evaluation


from weakness.analyzer import(
    analyze_weaknesses,
    analyze_deeper_weaknesses
)




# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="PromptIQ",
    page_icon="🧠",
    layout="wide"
)


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================

defaults = {
    "ambiguity_result": None,
    "analyzed_prompt": None,
    "clarification_result": None,
    "generated_response": None,
    "evaluation_result": None,
    "result_original_prompt": None,
    "execution_prompt": None,
    "reference_answer": "",
    "supporting_context": "",
    "pipeline_error": None,
    "weakness_result":None,
    "deeper_weakness_result":None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# HELPER: GENERATE AND EVALUATE
# ==========================================

def generate_and_evaluate(
    original_prompt,
    execution_prompt,
    reference_answer=None,
    context=None,
    clarification_result=None
):

    # Reset previous results
    st.session_state.generated_response = None
    st.session_state.evaluation_result = None
    st.session_state.pipeline_error = None
    st.session_state.weakness_result = None
    st.session_state.deeper_weakness_result = None

    st.session_state.result_original_prompt = original_prompt
    st.session_state.execution_prompt = execution_prompt
    st.session_state.clarification_result = clarification_result

    try:

        # STEP 1: Generate response
        with st.spinner("Generating LLM response..."):

            response = generate_llm_response(
                execution_prompt
            )

        st.session_state.generated_response = response

        # STEP 2: Evaluate response
        with st.spinner(
            "Evaluating response using Custom Judge and DeepEval..."
        ):

            evaluation = run_full_evaluation(
                prompt=execution_prompt,
                response=response,
                reference_answer=reference_answer,
                context=context
            )

        st.session_state.evaluation_result = evaluation
        #phase 5 A Weakness analysis
        with st.spinner("Analyzing evaluation weaknesses..."):
            weakness_result = analyze_weaknesses(evaluation)
            st.session_state.weakness_result = weakness_result

        #phase 5 B deeper analysis
        if weakness_result.needs_deeper_analysis:
            with st.spinner("Verifying weakness using Groq..."):
                deeper_result = analyze_deeper_weaknesses(
                    prompt = execution_prompt,
                    response = response,
                    phase5a_result = weakness_result 
                )
                st.session_state.deeper_weakness_result = deeper_result

    except Exception as e:

        st.session_state.pipeline_error = str(e)


# ==========================================
# APPLICATION HEADER
# ==========================================

st.title("🧠 PromptIQ")

st.subheader(
    "Intelligent LLM Evaluation & Prompt Optimization Platform"
)

st.write(
    "Generate AI responses, detect prompt ambiguity, "
    "clarify user intent and evaluate response quality."
)

st.divider()


# ==========================================
# USER PROMPT INPUT
# ==========================================

st.header("✍️ Enter Your Prompt")

user_prompt = st.text_area(
    "Your Prompt",
    placeholder="Example: What is LLD?",
    height=130,
    key="user_prompt"
)


# ==========================================
# OPTIONAL EVALUATION INPUTS
# ==========================================

with st.expander("Advanced Evaluation Inputs (Optional)"):

    reference_answer = st.text_area(
        "Reference Answer",
        placeholder="Enter the expected answer if available...",
        key="reference_answer"
    )

    supporting_context = st.text_area(
        "Supporting Context",
        placeholder="Enter supporting information...",
        key="supporting_context"
    )


# ==========================================
# ANALYZE PROMPT BUTTON
# ==========================================

if st.button(
    "🔍 Analyze Prompt",
    type="primary"
):

    if not user_prompt.strip():

        st.warning("Please enter a prompt.")

    else:

        # Clear previous workflow
        st.session_state.ambiguity_result = None
        st.session_state.analyzed_prompt = None
        st.session_state.clarification_result = None
        st.session_state.generated_response = None
        st.session_state.evaluation_result = None
        st.session_state.pipeline_error = None
        st.session_state.weakness_result = None
        st.session_state.deeper_weakness_result = None

        # st.session_state.reference_answer = reference_answer
        # st.session_state.supporting_context = supporting_context

        try:

            # Run ambiguity detection
            with st.spinner("Analyzing prompt ambiguity..."):

                ambiguity_result = detect_ambiguity(
                    prompt=user_prompt
                )

            st.session_state.ambiguity_result = ambiguity_result
            st.session_state.analyzed_prompt = user_prompt

            # If clarification is not required,
            # directly generate and evaluate
            if not ambiguity_result.needs_clarification:

                generate_and_evaluate(
                    original_prompt=user_prompt,
                    execution_prompt=user_prompt,
                    reference_answer=reference_answer or None,
                    context=supporting_context or None
                )

        except Exception as e:

            st.session_state.pipeline_error = str(e)


# ==========================================
# DISPLAY AMBIGUITY DETECTION RESULTS
# ==========================================

ambiguity_result = st.session_state.ambiguity_result

if (
    ambiguity_result is not None
    and st.session_state.analyzed_prompt == user_prompt
):

    st.divider()

    st.header("🔎 Ambiguity Detection")

    if ambiguity_result.needs_clarification:

        st.warning(
            "Ambiguous prompt detected! "
            "Please clarify your intended meaning."
        )

        st.write(
            f"**Reason:** {ambiguity_result.reason}"
        )

        st.write(
            f"**Ambiguity Level:** "
            f"{ambiguity_result.ambiguity_level.title()}"
        )

        st.subheader("Possible Interpretations")

        # Display available interpretations
        for i, option in enumerate(
            ambiguity_result.possible_interpretations,
            start=1
        ):

            st.markdown(
                f"**{i}. {option.title}**"
            )

            st.caption(option.description)

        st.divider()

        # ==================================
        # USER CLARIFICATION
        # ==================================

        st.subheader("💬 Clarify Your Intent")

        st.info(
            ambiguity_result.clarification_question
            or "Please select your intended meaning."
        )

        options = [
            option.title
            for option in ambiguity_result.possible_interpretations
        ]

        options.append("Something else")

        if len(options) == 1:

            st.error(
                "No interpretation options were returned. "
                "Please check the ambiguity detector output."
            )

        else:

            selected_interpretation = st.radio(
                "Which meaning are you referring to?",
                options,
                key="selected_interpretation"
            )

            custom_intent = None

            if selected_interpretation == "Something else":

                custom_intent = st.text_input(
                    "Enter your intended meaning",
                    placeholder="Example: Meta Language",
                    key="custom_intent"
                )

            # ==================================
            # CONFIRM INTENT
            # ==================================

            if st.button(
                "✅ Confirm Intent & Generate Response",
                type="primary"
            ):

                try:

                    # Resolve selected user intent
                    clarification_result = resolve_intent(
                        original_prompt=user_prompt,
                        ambiguity_result=ambiguity_result,
                        selected_interpretation=selected_interpretation,
                        custom_intent=custom_intent
                    )

                    # Store and execute clarified prompt
                    st.session_state.clarification_result = (
                        clarification_result
                    )

                    generate_and_evaluate(
                        original_prompt=user_prompt,
                        execution_prompt=clarification_result.clarified_prompt,
                        reference_answer=reference_answer or None,
                        context=supporting_context or None,
                        clarification_result=clarification_result
                    )

                except Exception as e:

                    st.error(
                        f"Clarification error: {e}"
                    )

    else:

        st.success(
            "No clarification required. "
            "Your prompt is sufficiently clear."
        )

        st.write(
            f"**Reason:** {ambiguity_result.reason}"
        )


# ==========================================
# DISPLAY PIPELINE ERRORS
# ==========================================

if st.session_state.pipeline_error:

    st.error(
        f"Application error: {st.session_state.pipeline_error}"
    )


# ==========================================
# DISPLAY CLARIFICATION RESULT
# ==========================================

if (
    st.session_state.clarification_result is not None
    and st.session_state.result_original_prompt == user_prompt
):

    clarification = st.session_state.clarification_result

    st.divider()

    st.header("🎯 Intent Resolution")

    st.success(
        f"Selected Intent: {clarification.selected_intent}"
    )

    st.write("**Original Prompt:**")
    st.info(clarification.original_prompt)

    st.write("**Clarified Prompt:**")

    st.code(
        clarification.clarified_prompt,
        language="text"
    )


# ==========================================
# DISPLAY GENERATED RESPONSE
# ==========================================

if (
    st.session_state.generated_response
    and st.session_state.result_original_prompt == user_prompt
):

    st.divider()

    st.header("📝 Generated Response")

    st.write("**Original User Prompt:**")

    st.info(st.session_state.result_original_prompt)

    st.write("**Prompt Sent to LLM:**")

    st.code(
        st.session_state.execution_prompt,
        language="text"
    )

    st.subheader("LLM Response")

    st.markdown(
        st.session_state.generated_response
    )


# ==========================================
# DISPLAY EVALUATION DASHBOARD
# ==========================================

if (
    st.session_state.evaluation_result
    and st.session_state.result_original_prompt == user_prompt
):

    evaluation = st.session_state.evaluation_result

    st.divider()

    st.header("📊 Evaluation Dashboard")


    # ======================================
    # CUSTOM LLM-AS-A-JUDGE
    # ======================================

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

                st.write(
                    f"Score: {metric['score']}/10"
                    if metric["score"] is not None
                    else "Score: N/A"
                )

                st.write(metric["reason"])

                if metric["weaknesses"]:

                    st.write("Identified Weaknesses:")

                    for weakness in metric["weaknesses"]:
                        st.write(f"- {weakness}")

        if custom_data["overall_score"] is not None:

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


    # ======================================
    # DEEPEVAL G-EVAL
    # ======================================

    st.divider()

    st.subheader("2. DeepEval – G-Eval")

    deepeval_results = evaluation["deepeval"]

    if deepeval_results:

        columns = st.columns(3)

        for i, (metric_name, details) in enumerate(
            deepeval_results.items()
        ):

            with columns[i]:

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

    # Display independent evaluator errors
    if evaluation["errors"]:

        st.warning(
            "One or more evaluation engines encountered errors."
        )

        for component, error in evaluation["errors"].items():

            st.write(f"**{component}:** {error}")


# ==========================================
# PHASE 5 - WEAKNESS ANALYSIS REPORT
# ==========================================

if (
    st.session_state.weakness_result is not None
    and st.session_state.result_original_prompt == user_prompt
):

    weakness = st.session_state.weakness_result
    deeper = st.session_state.deeper_weakness_result

    st.divider()
    st.header("🔍 Weakness Analysis Report")

    # =====================================
    # PHASE 5A - INITIAL ANALYSIS
    # =====================================

    st.subheader("1. Initial Weakness Analysis")

    st.write("**Analysis Status:**", weakness.analysis_status)

    st.write(
        "**Needs Deeper Analysis:**",
        weakness.needs_deeper_analysis
    )

    st.write("**Summary:**", weakness.summary)

    # Low-scoring dimensions
    if weakness.low_scoring_dimensions:

        st.markdown("#### Low-Scoring Dimensions")

        for item in weakness.low_scoring_dimensions:

            st.warning(
                f"{item.evaluator} - {item.metric}: "
                f"{item.score_out_of_10}/10"
            )

            if item.reason:
                st.write(item.reason)

    else:
        st.success("No low-scoring dimensions detected.")

    # Existing evaluator weaknesses
    st.markdown("#### Existing Evaluator Weaknesses")

    if weakness.existing_weaknesses:

        for item in weakness.existing_weaknesses:
            st.write(f"- {item}")

    else:
        st.write("No explicit weaknesses reported.")

    # =====================================
    # PHASE 5B - DEEPER ANALYSIS
    # =====================================

    st.divider()
    st.subheader("2. Deeper Weakness Analysis")

    if deeper is not None:

        st.write("**Overall Status:**", deeper.overall_status)

        st.write(
            "**Needs Prompt Refinement:**",
            deeper.needs_refinement
        )

        st.write("**Summary:**", deeper.summary)

        # Requirement checks
        st.markdown("#### Requirement Checks")

        for item in deeper.requirement_checks:

            st.write(
                f"**{item.requirement}** - {item.status}"
            )

            st.caption(item.explanation)

        # Confirmed weaknesses
        st.markdown("#### Confirmed Weaknesses")

        if deeper.identified_weaknesses:

            for item in deeper.identified_weaknesses:
                st.write(f"- {item}")

        else:
            st.success("No genuine weaknesses confirmed.")

        # Missing requirements
        st.markdown("#### Missing Requirements")

        if deeper.missing_requirements:

            for item in deeper.missing_requirements:
                st.write(f"- {item}")

        else:
            st.write("No missing requirements identified.")

        # Recommendations
        st.markdown("#### Improvement Recommendations")

        if deeper.recommendations:

            for item in deeper.recommendations:
                st.write(f"- {item}")

        else:
            st.success("No improvements necessary.")

    elif weakness.analysis_status == "satisfactory":

        st.success(
            "Initial evaluation is satisfactory. "
            "Deeper analysis was not required."
        )

    elif weakness.analysis_status == "insufficient_evaluation_data":

        st.warning(
            "Evaluation data is insufficient. "
            "Deeper analysis was not performed."
        )

    else:

        st.warning(
            "Deeper weakness analysis is not available."
        )

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "PromptIQ | Intelligent LLM Evaluation & Prompt Optimization"
)
