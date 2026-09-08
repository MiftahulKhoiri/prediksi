from .scoring import (
    frequency_scores,
    recency_scores,
    gap_scores,
    transition_scores,
    pair_scores,
    triple_scores,
    delta_scores,
)

from .tuning import (
    DEFAULT_WEIGHTS,
    MIN_BACKTEST_POINTS,
    RETUNE_INTERVAL,
    tune_weights,
)


KECIL_MIN = 3
KECIL_MAX = 10
BESAR_MIN = 11
BESAR_MAX = 18

KECIL = 0
BESAR = 1

METHOD_FUNCS = {
    "frequency": frequency_scores,
    "recency": recency_scores,
    "gap": gap_scores,
    "transition": transition_scores,
    "pair": pair_scores,
    "triple": triple_scores,
    "delta": delta_scores,
}


def to_label(value):
    return KECIL if value <= KECIL_MAX else BESAR


def label_name(label):
    if label == KECIL:
        return f"KECIL ({KECIL_MIN}-{KECIL_MAX})"

    return f"BESAR ({BESAR_MIN}-{BESAR_MAX})"


def get_range_weights(state):
    data = state.get("data", [])
    labels = [to_label(v) for v in data]

    if len(labels) < MIN_BACKTEST_POINTS:
        return dict(DEFAULT_WEIGHTS)

    tuned_at = state.get("range_tuned_at_len", -RETUNE_INTERVAL)

    needs_retune = (
        "range_tuned_weights" not in state
        or len(labels) - tuned_at >= RETUNE_INTERVAL
    )

    if needs_retune:
        state["range_tuned_weights"] = tune_weights(labels, 0, 1)
        state["range_tuned_at_len"] = len(labels)

    return dict(state["range_tuned_weights"])


def calculate_range_scores(state):
    data = state.get("data", [])

    if not data:
        return {}

    labels = [to_label(v) for v in data]

    weights = get_range_weights(state)

    scores = {KECIL: 0.0, BESAR: 0.0}

    for method, func in METHOD_FUNCS.items():
        method_scores = func(labels, 0, 1)
        weight = weights.get(method, 0.0)

        for label in scores:
            scores[label] += method_scores.get(label, 0) * weight

    return scores


def predict_range(state):
    scores = calculate_range_scores(state)

    if not scores:
        return None

    return sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )


def range_confidence(ranking):
    if not ranking or len(ranking) < 2:
        return 0

    maximum = ranking[0][1]
    second = ranking[1][1]

    if maximum <= 0:
        return 0

    gap = (maximum - second) / maximum

    return min(100, gap * 100)


def show_range_prediction(ranking):
    if not ranking:
        return

    print("\nPREDIKSI RENTANG (BESAR / KECIL)")
    print("-" * 65)

    for label, score in ranking:
        print(
            f"  {label_name(label):<14} "
            f"Score {score:.6f}"
        )

    prediction = ranking[0][0]
    conf = range_confidence(ranking)

    print("-" * 65)

    print(f"TEBAKAN RENTANG : {label_name(prediction)}")
    print(f"CONFIDENCE      : {conf:.2f}%")

    print("=" * 65)