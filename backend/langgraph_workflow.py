from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from groq_client import call_groq_json


class ComplaintState(TypedDict):
    customer_name: str
    product_name: Optional[str]
    batch_number: Optional[str]
    complaint_text: str

    is_complete: bool
    missing_fields: List[str]

    risk_level: Optional[str]
    risk_reasoning: Optional[str]


def check_completeness_node(state: ComplaintState) -> ComplaintState:
    system_prompt = (
        "You are a pharmaceutical Quality Management System (QMS) assistant. "
        "A valid customer complaint for API/FDF manufacturing should ideally include: "
        "product name, batch/lot number, and a clear description of the issue. "
        "Respond ONLY with valid JSON, no extra text, in this exact format: "
        '{"is_complete": true/false, "missing_fields": ["field1", "field2"]}'
    )

    user_prompt = f"""
    Customer Name: {state['customer_name']}
    Product Name: {state.get('product_name') or 'NOT PROVIDED'}
    Batch Number: {state.get('batch_number') or 'NOT PROVIDED'}
    Complaint Text: {state['complaint_text']}

    Check if this complaint has enough information to be investigated.
    """

    result = call_groq_json(system_prompt, user_prompt)

    state["is_complete"] = bool(result.get("is_complete", False))
    state["missing_fields"] = result.get("missing_fields", [])
    return state


def classify_risk_node(state: ComplaintState) -> ComplaintState:
    system_prompt = (
        "You are a pharmaceutical QMS risk classification assistant. "
        "Classify the customer complaint's risk level based on patient safety impact, "
        "product quality impact, and regulatory implications (e.g., GMP deviations). "
        "Categories: High (safety/regulatory risk, e.g. contamination, wrong labeling, adverse reaction), "
        "Medium (quality issue, no immediate safety risk, e.g. packaging defect), "
        "Low (cosmetic/minor issue, e.g. late delivery, minor label smudge). "
        "Respond ONLY with valid JSON in this exact format: "
        '{"risk_level": "High/Medium/Low", "reasoning": "one sentence explanation"}'
    )

    user_prompt = f"""
    Product Name: {state.get('product_name')}
    Batch Number: {state.get('batch_number')}
    Complaint Text: {state['complaint_text']}

    Classify the risk level of this complaint.
    """

    result = call_groq_json(system_prompt, user_prompt)

    state["risk_level"] = result.get("risk_level", "Unclassified")
    state["risk_reasoning"] = result.get("reasoning", "")
    return state


def route_after_completeness(state: ComplaintState) -> str:
    if state["is_complete"]:
        return "classify_risk"
    return END


def build_complaint_graph():
    graph = StateGraph(ComplaintState)

    graph.add_node("check_completeness", check_completeness_node)
    graph.add_node("classify_risk", classify_risk_node)

    graph.set_entry_point("check_completeness")
    graph.add_conditional_edges(
        "check_completeness",
        route_after_completeness,
        {"classify_risk": "classify_risk", END: END},
    )
    graph.add_edge("classify_risk", END)

    return graph.compile()


complaint_graph = build_complaint_graph()


def run_complaint_workflow(customer_name, product_name, batch_number, complaint_text) -> ComplaintState:
    initial_state: ComplaintState = {
        "customer_name": customer_name,
        "product_name": product_name,
        "batch_number": batch_number,
        "complaint_text": complaint_text,
        "is_complete": False,
        "missing_fields": [],
        "risk_level": None,
        "risk_reasoning": None,
    }
    final_state = complaint_graph.invoke(initial_state)
    return final_state