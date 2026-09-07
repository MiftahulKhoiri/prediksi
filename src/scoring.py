from collections import Counter
from statistics import mean
import math


def empty_scores(
    min_value,
    max_value
):
    return {
        value: 0.0
        for value in range(
            min_value,
            max_value + 1
        )
    }


def normalize(scores):
    if not scores:
        return scores

    minimum = min(
        scores.values()
    )

    maximum = max(
        scores.values()
    )

    difference = (
        maximum - minimum
    )

    if difference <= 0:
        return {
            key: 1.0
            for key in scores
        }

    return {
        key: (
            value - minimum
        ) / difference
        for key, value in scores.items()
    }


def frequency_scores(
    data,
    min_value,
    max_value
):
    scores = empty_scores(
        min_value,
        max_value
    )

    if not data:
        return scores

    counter = Counter(data)

    alpha = 1.0

    denominator = (
        len(data)
        +
        alpha * len(scores)
    )

    for value in scores:
        scores[value] = (
            counter[value]
            +
            alpha
        ) / denominator

    return normalize(scores)


def recency_scores(
    data,
    min_value,
    max_value
):
    scores = empty_scores(
        min_value,
        max_value
    )

    if not data:
        return scores

    decay = 0.90

    for distance, value in enumerate(
        reversed(data),
        start=0
    ):
        scores[value] += (
            decay ** distance
        )

        if distance >= 50:
            break

    return normalize(scores)


def gap_scores(
    data,
    min_value,
    max_value
):
    scores = empty_scores(
        min_value,
        max_value
    )

    if not data:
        return scores

    n = len(data)

    for value in scores:

        gap = n + 1

        for distance, actual in enumerate(
            reversed(data),
            start=1
        ):
            if actual == value:
                gap = distance
                break

        # Gap tidak boleh mendominasi metode lain.
        scores[value] = math.log1p(gap)

    return normalize(scores)


def transition_scores(
    data,
    min_value,
    max_value
):
    scores = empty_scores(
        min_value,
        max_value
    )

    if len(data) < 2:
        return scores

    current = data[-1]

    counter = Counter()

    total_weight = 0.0

    decay = 0.94

    for i in range(
        len(data) - 2,
        -1,
        -1
    ):

        if data[i] != current:
            continue

        distance = (
            len(data) - 2
        ) - i

        weight = (
            decay ** distance
        )

        counter[
            data[i + 1]
        ] += weight

        total_weight += weight

        if total_weight >= 15:
            break

    if total_weight <= 0:
        return scores

    alpha = 0.35

    denominator = (
        total_weight
        +
        alpha * len(scores)
    )

    for value in scores:
        scores[value] = (
            counter[value]
            +
            alpha
        ) / denominator

    return normalize(scores)


def pair_scores(
    data,
    min_value,
    max_value
):
    scores = empty_scores(
        min_value,
        max_value
    )

    if len(data) < 3:
        return scores

    pattern = tuple(
        data[-2:]
    )

    counter = Counter()

    total_weight = 0.0

    decay = 0.95

    for end in range(
        2,
        len(data)
    ):
        previous = tuple(
            data[end - 2:end]
        )

        if previous != pattern:
            continue

        distance = (
            len(data) - 1
        ) - end

        weight = (
            decay ** distance
        )

        counter[
            data[end]
        ] += weight

        total_weight += weight

    if total_weight <= 0:
        return scores

    alpha = 0.30

    denominator = (
        total_weight
        +
        alpha * len(scores)
    )

    for value in scores:
        scores[value] = (
            counter[value]
            +
            alpha
        ) / denominator

    return normalize(scores)


def triple_scores(
    data,
    min_value,
    max_value
):
    scores = empty_scores(
        min_value,
        max_value
    )

    if len(data) < 4:
        return scores

    pattern = tuple(
        data[-3:]
    )

    counter = Counter()

    total_weight = 0.0

    decay = 0.96

    for end in range(
        3,
        len(data)
    ):
        previous = tuple(
            data[end - 3:end]
        )

        if previous != pattern:
            continue

        distance = (
            len(data) - 1
        ) - end

        weight = (
            decay ** distance
        )

        counter[
            data[end]
        ] += weight

        total_weight += weight

    if total_weight <= 0:
        return scores

    alpha = 0.25

    denominator = (
        total_weight
        +
        alpha * len(scores)
    )

    for value in scores:
        scores[value] = (
            counter[value]
            +
            alpha
        ) / denominator

    return normalize(scores)


def delta_scores(
    data,
    min_value,
    max_value
):
    scores = empty_scores(
        min_value,
        max_value
    )

    if len(data) < 3:
        return scores

    deltas = [
        data[i] - data[i - 1]
        for i in range(
            1,
            len(data)
        )
    ]

    recent = deltas[-7:]

    ordered = sorted(
        recent
    )

    if len(ordered) % 2:
        center = ordered[
            len(ordered) // 2
        ]
    else:
        middle = len(ordered) // 2

        center = (
            ordered[middle - 1]
            +
            ordered[middle]
        ) / 2

    predicted = (
        data[-1]
        +
        center
    )

    for value in scores:

        distance = abs(
            value - predicted
        )

        scores[value] = (
            1.0
            /
            (1.0 + distance)
        )

    return normalize(scores)


def neighbor_scores(
    data,
    min_value,
    max_value
):
    scores = empty_scores(
        min_value,
        max_value
    )

    if len(data) < 2:
        return scores

    current = data[-1]

    deltas = []

    for i in range(
        len(data) - 2,
        -1,
        -1
    ):
        if data[i] == current:
            deltas.append(
                data[i + 1] - current
            )

        if len(deltas) >= 20:
            break

    if not deltas:
        return scores

    center = sorted(
        deltas
    )[len(deltas) // 2]

    predicted = (
        current
        +
        center
    )

    for value in scores:

        distance = abs(
            value - predicted
        )

        scores[value] = (
            1.0
            /
            (1.0 + distance)
        )

    return normalize(scores)


def learning_scores(
    state,
    min_value,
    max_value
):
    scores = empty_scores(
        min_value,
        max_value
    )

    history = state.get(
        'history',
        []
    )

    if not history:
        return scores

    correct = Counter()
    attempts = Counter()

    for item in history:

        prediction = item.get(
            'prediction'
        )

        actual = item.get(
            'actual'
        )

        if prediction is None:
            continue

        if not (
            min_value
            <= prediction
            <= max_value
        ):
            continue

        attempts[prediction] += 1

        if prediction == actual:
            correct[prediction] += 1

    for value in scores:

        scores[value] = (
            correct[value] + 1.0
        ) / (
            attempts[value] + 2.0
        )

    return normalize(scores)