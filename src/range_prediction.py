from .scoring import (
    frequency_scores,
    recency_scores,
    gap_scores,
    transition_scores,
    pair_scores,
    triple_scores,
    delta_scores,
    learning_scores
)

from .tuning import (
    DEFAULT_WEIGHTS,
    MIN_BACKTEST_POINTS,
    RETUNE_INTERVAL,
    tune_weights
)


def get_weights(state, min_value, max_value):
    data = state.get("data", [])
    history = state.get("history", [])

    if len(data) < MIN_BACKTEST_POINTS:
        # Belum cukup data buat backtest yang bisa dipercaya --
        # pakai default sampai histori cukup panjang.
        weights = dict(DEFAULT_WEIGHTS)
    else:
        tuned_at = state.get("tuned_at_len", -RETUNE_INTERVAL)

        needs_retune = (
            "tuned_weights" not in state
            or len(data) - tuned_at >= RETUNE_INTERVAL
        )

        if needs_retune:
            # Retune tiap RETUNE_INTERVAL data baru, bukan tiap
            # tebakan, biar tetap ringan walau histori makin panjang.
            state["tuned_weights"] = tune_weights(
                data, min_value, max_value
            )
            state["tuned_at_len"] = len(data)

        weights = dict(state["tuned_weights"])

    weights["learning"] = 2.0

    if len(history) >= 5:
        correct = 0
        total = 0

        for item in history[-50:]:
            total += 1

            if item.get("prediction") == item.get("actual"):
                correct += 1

        if total:
            accuracy = correct / total

            weights["learning"] *= (
                0.5 + accuracy
            )

    return weights


def calculate_scores(
    state,
    min_value,
    max_value
):
    data = state["data"]

    if not data:
        return {}

    weights = get_weights(state, min_value, max_value)

    methods = {
        "frequency": frequency_scores(
            data, min_value, max_value
        ),

        "recency": recency_scores(
            data, min_value, max_value
        ),

        "gap": gap_scores(
            data, min_value, max_value
        ),

        "transition": transition_scores(
            data, min_value, max_value
        ),

        "pair": pair_scores(
            data, min_value, max_value
        ),

        "triple": triple_scores(
            data, min_value, max_value
        ),

        "delta": delta_scores(
            data, min_value, max_value
        ),

        "learning": learning_scores(
            state, min_value, max_value
        ),
    }

    final = {
        value: 0.0
        for value in range(min_value, max_value + 1)
    }

    for method, scores in methods.items():
        weight = weights[method]

        for value in final:
            final[value] += (
                scores.get(value, 0)
                * weight
            )

    return final


def predict(state, min_value, max_value):
    scores = calculate_scores(
        state,
        min_value,
        max_value
    )

    return sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )


def confidence(ranking):
    if not ranking:
        return 0

    values = [
        score
        for _, score in ranking
    ]

    if len(values) < 2:
        return 0

    maximum = values[0]
    second = values[1]

    if maximum <= 0:
        return 0

    gap = (
        maximum - second
    ) / maximum

    return min(
        100,
        gap * 100
    )


def show_prediction(state, ranking):
    print()
    print("=" * 65)
    print(" PREDICTION ENGINE")
    print("=" * 65)

    print("\nData tersimpan:")
    print(state["data"])

    print("\nTOP PREDICTION")
    print("-" * 65)

    for i, (value, score) in enumerate(
        ranking[:10],
        start=1
    ):
        print(
            f"{i:2}. "
            f"Nilai {value:2} "
            f"Score {score:.6f}"
        )

    prediction = ranking[0][0]
    conf = confidence(ranking)

    print("-" * 65)

    print(
        f"TEBAKAN MESIN : {prediction}"
    )

    print(
        f"CONFIDENCE     : {conf:.2f}%"
    )

    print("=" * 65)