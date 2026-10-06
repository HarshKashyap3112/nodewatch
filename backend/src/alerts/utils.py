from src.alerts.constants import Operator


def evaluate_condition(current_value: float, operator: Operator, threshold: float) -> bool:
    if operator == Operator.GT:
        return current_value > threshold
    elif operator == Operator.GTE:
        return current_value >= threshold
    elif operator == Operator.LT:
        return current_value < threshold
    elif operator == Operator.LTE:
        return current_value <= threshold
    elif operator == Operator.EQ:
        return current_value == threshold
    return False
