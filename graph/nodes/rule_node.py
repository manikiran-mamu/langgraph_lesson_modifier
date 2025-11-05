# graph/nodes/rule_node.py

from agents.rule_agent import generate_cleaned_rules

def rule_node(state: dict) -> dict:
    """
    LangGraph node to extract and filter adaptation rules based on student profile.
    Adds 'rules' to the state for downstream nodes.
    """
    profile = state.get("student_profile")
    if not profile:
        raise ValueError("Missing 'student_profile' in state.")
    
    cleaned_rules = generate_cleaned_rules(profile)
    state.update({"rules" : cleaned_rules})

    return state

def set_rules(state: dict, rules: list[str]) -> dict:
    """
    Directly sets the provided rules into the state.
    Useful for bypassing rule extraction when rules are already known.
    """
    if not rules:
        raise ValueError("Provided 'rules' list is empty.")
    
    state.update({"rules" : rules})
    return state