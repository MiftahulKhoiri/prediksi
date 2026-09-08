import json
import os


DATA_FILE = "prediction_data.json"


def load_state():
    if not os.path.exists(DATA_FILE):
        return {
            "data": [],
            "history": []
        }

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    except Exception:
        return {
            "data": [],
            "history": []
        }


def save_state(state):
    with open(DATA_FILE, "w") as f:
        json.dump(
            state,
            f,
            indent=2
        )


def record_result(state, prediction, actual):
    correct = prediction == actual

    state["history"].append({
        "prediction": prediction,
        "actual": actual,
        "correct": correct
    })

    state["data"].append(actual)

    save_state(state)

    return correct


def record_range_result(state, prediction_label, actual_label):
    correct = prediction_label == actual_label

    state.setdefault("range_history", []).append({
        "prediction": prediction_label,
        "actual": actual_label,
        "correct": correct
    })

    save_state(state)

    return correct