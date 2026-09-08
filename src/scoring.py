from collections import Counter
from statistics import mean


def normalize(scores):
    if not scores:
        return scores

    maximum = max(scores.values())
    minimum = min(scores.values())

    difference = maximum - minimum

    if difference == 0:
        return {
            k: 1.0
            for k in scores
        }

    return {
        k: (v - minimum) / difference
        for k, v in scores.items()
    }


def confidence_scale(scores, total, k=4):
    """
    Kecilkan skor kalau pola yang mendasarinya cuma didukung
    sedikit kejadian di histori (mis. konteks pair/triple yang
    baru muncul 1-2 kali). Makin besar `total`, faktor makin
    dekat ke 1.0 (skor dipakai penuh); makin kecil `total`,
    makin dekat ke 0 (skor nyaris diabaikan karena cuma
    kebetulan).
    """
    factor = total / (total + k)

    return {
        key: value * factor
        for key, value in scores.items()
    }


def frequency_scores(data, min_value, max_value):
    counter = Counter(data)
    total = len(data)

    if total == 0:
        return {
            value: 0
            for value in range(min_value, max_value + 1)
        }

    scores = {}

    for value in range(min_value, max_value + 1):
        scores[value] = counter[value] / total

    return normalize(scores)


def recency_scores(data, min_value, max_value):
    scores = {}

    for value in range(min_value, max_value + 1):
        score = 0

        for distance, x in enumerate(
            reversed(data),
            start=1
        ):
            if x == value:
                score = 1 / distance
                break

        scores[value] = score

    return normalize(scores)


def gap_scores(data, min_value, max_value):
    scores = {}

    for value in range(min_value, max_value + 1):
        gap = len(data) + 1

        for distance, x in enumerate(
            reversed(data),
            start=1
        ):
            if x == value:
                gap = distance
                break

        scores[value] = gap

    return normalize(scores)


def transition_scores(data, min_value, max_value):
    scores = {
        value: 0
        for value in range(min_value, max_value + 1)
    }

    if len(data) < 2:
        return scores

    current = data[-1]
    counter = Counter()

    for i in range(len(data) - 1):
        if data[i] == current:
            counter[data[i + 1]] += 1

    total = sum(counter.values())

    if total == 0:
        return scores

    for value in scores:
        scores[value] = counter[value] / total

    scores = normalize(scores)

    return confidence_scale(scores, total, k=3)


def pair_scores(data, min_value, max_value):
    scores = {
        value: 0
        for value in range(min_value, max_value + 1)
    }

    if len(data) < 3:
        return scores

    a = data[-2]
    b = data[-1]

    counter = Counter()

    for i in range(2, len(data)):
        if (
            data[i - 2] == a
            and data[i - 1] == b
        ):
            counter[data[i]] += 1

    total = sum(counter.values())

    if total == 0:
        return scores

    for value in scores:
        scores[value] = counter[value] / total

    scores = normalize(scores)

    return confidence_scale(scores, total, k=5)


def triple_scores(data, min_value, max_value):
    scores = {
        value: 0
        for value in range(min_value, max_value + 1)
    }

    if len(data) < 4:
        return scores

    pattern = tuple(data[-3:])
    counter = Counter()

    for i in range(3, len(data)):
        previous = tuple(data[i - 3:i])

        if previous == pattern:
            counter[data[i]] += 1

    total = sum(counter.values())

    if total == 0:
        return scores

    for value in scores:
        scores[value] = counter[value] / total

    scores = normalize(scores)

    return confidence_scale(scores, total, k=8)


def delta_scores(data, min_value, max_value):
    scores = {
        value: 0
        for value in range(min_value, max_value + 1)
    }

    if len(data) < 3:
        return scores

    deltas = [
        data[i] - data[i - 1]
        for i in range(1, len(data))
    ]

    recent = deltas[-5:]

    avg_delta = mean(recent)

    predicted = data[-1] + avg_delta

    for value in scores:
        distance = abs(value - predicted)

        scores[value] = 1 / (1 + distance)

    return normalize(scores)


def learning_scores(state, min_value, max_value):
    scores = {
        value: 0
        for value in range(min_value, max_value + 1)
    }

    history = state.get("history", [])

    if not history:
        return scores

    correct = Counter()
    total = Counter()

    for item in history:
        prediction = item.get("prediction")
        actual = item.get("actual")

        if prediction is None:
            continue

        total[prediction] += 1

        if prediction == actual:
            correct[prediction] += 1

    for value in scores:
        if total[value]:
            scores[value] = (
                correct[value] /
                total[value]
            )

    return normalize(scores)