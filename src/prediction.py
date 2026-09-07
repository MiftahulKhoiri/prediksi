from .scoring import (
    frequency_scores,
    recency_scores,
    gap_scores,
    transition_scores,
    pair_scores,
    triple_scores,
    delta_scores,
    neighbor_scores,
    learning_scores,
)


METHODS = (
    'frequency',
    'recency',
    'gap',
    'transition',
    'pair',
    'triple',
    'delta',
    'neighbor',
    'learning',
)


BASE_WEIGHTS = {
    'frequency': 1.00,
    'recency': 1.10,
    'gap': 0.20,
    'transition': 1.80,
    'pair': 2.20,
    'triple': 2.40,
    'delta': 0.90,
    'neighbor': 0.80,
    'learning': 1.50,
}


VALIDATION_WINDOW = 60
MIN_VALIDATION_TRAIN = 8


def get_weights(state, min_value, max_value):
    data = state.get('data', [])

    reliability = evaluate_methods(
        data,
        min_value,
        max_value
    )

    weights = {}

    for method in METHODS:
        score = reliability.get(method, 0.50)

        weights[method] = (
            BASE_WEIGHTS[method]
            *
            (0.35 + score) ** 1.25
        )

    total = sum(weights.values())
    base_total = sum(BASE_WEIGHTS.values())

    if total > 0:
        factor = base_total / total

        weights = {
            method: value * factor
            for method, value in weights.items()
        }

    return weights, reliability


def calculate_method_scores(
    data,
    min_value,
    max_value
):
    return {
        'frequency': frequency_scores(
            data,
            min_value,
            max_value
        ),

        'recency': recency_scores(
            data,
            min_value,
            max_value
        ),

        'gap': gap_scores(
            data,
            min_value,
            max_value
        ),

        'transition': transition_scores(
            data,
            min_value,
            max_value
        ),

        'pair': pair_scores(
            data,
            min_value,
            max_value
        ),

        'triple': triple_scores(
            data,
            min_value,
            max_value
        ),

        'delta': delta_scores(
            data,
            min_value,
            max_value
        ),

        'neighbor': neighbor_scores(
            data,
            min_value,
            max_value
        ),
    }


def calculate_scores(
    state,
    min_value,
    max_value
):
    data = state.get('data', [])

    if not data:
        return {}, {}, {}

    weights, reliability = get_weights(
        state,
        min_value,
        max_value
    )

    methods = calculate_method_scores(
        data,
        min_value,
        max_value
    )

    methods['learning'] = learning_scores(
        state,
        min_value,
        max_value
    )

    final = {
        value: 0.0
        for value in range(
            min_value,
            max_value + 1
        )
    }

    for method in METHODS:
        weight = weights[method]
        scores = methods[method]

        for value in final:
            final[value] += (
                weight
                *
                scores.get(
                    value,
                    0.0
                )
            )

    # Sedikit tie-break menggunakan frequency.
    for value in final:
        final[value] += (
            0.05
            *
            methods['frequency'].get(
                value,
                0.0
            )
        )

    return final, weights, reliability


def evaluate_methods(
    data,
    min_value,
    max_value
):
    reliability = {
        method: 0.50
        for method in METHODS
    }

    if len(data) <= MIN_VALIDATION_TRAIN:
        return reliability

    start = max(
        MIN_VALIDATION_TRAIN,
        len(data) - VALIDATION_WINDOW
    )

    hits = {
        method: 0
        for method in METHODS
    }

    trials = {
        method: 0
        for method in METHODS
    }

    for t in range(
        start,
        len(data)
    ):
        training = data[:t]
        actual = data[t]

        methods = calculate_method_scores(
            training,
            min_value,
            max_value
        )

        for method in METHODS:

            if method == 'learning':
                continue

            scores = methods[method]

            if not scores:
                continue

            prediction = max(
                scores,
                key=scores.get
            )

            trials[method] += 1

            if prediction == actual:
                hits[method] += 1

    for method in METHODS:

        if method == 'learning':
            continue

        if trials[method] > 0:
            reliability[method] = (
                hits[method] + 1.0
            ) / (
                trials[method] + 2.0
            )

    return reliability


def predict(
    state,
    min_value,
    max_value
):
    scores, weights, reliability = calculate_scores(
        state,
        min_value,
        max_value
    )

    ranking = sorted(
        scores.items(),
        key=lambda item: (
            -item[1],
            item[0]
        )
    )

    return ranking


def confidence(ranking):
    if len(ranking) < 2:
        return 0.0

    first = max(
        0.0,
        ranking[0][1]
    )

    second = max(
        0.0,
        ranking[1][1]
    )

    total = sum(
        max(0.0, score)
        for _, score in ranking
    )

    if total <= 0 or first <= 0:
        return 0.0

    concentration = (
        first / total
    )

    margin = (
        first - second
    ) / first

    value = (
        100.0
        *
        (
            0.60 * concentration
            +
            0.40 * max(
                0.0,
                margin
            )
        )
    )

    return min(
        100.0,
        max(0.0, value)
    )


def show_prediction(
    state,
    ranking
):
    print()
    print('=' * 72)
    print(
        ' PREDICTION ENGINE - ADAPTIVE ENSEMBLE'
    )
    print('=' * 72)

    print('\nData tersimpan:')
    print(
        state.get(
            'data',
            []
        )
    )

    print('\nTOP PREDICTION')
    print('-' * 72)

    for i, (
        value,
        score
    ) in enumerate(
        ranking[:10],
        start=1
    ):
        print(
            f'{i:2}. '
            f'Nilai {value:2} '
            f'| Score {score:.6f}'
        )

    if not ranking:
        print(
            'Belum cukup data untuk prediksi.'
        )
        return

    prediction = ranking[0][0]

    conf = confidence(
        ranking
    )

    print('-' * 72)

    print(
        f'TEBAKAN MESIN : {prediction}'
    )

    print(
        f'CONFIDENCE     : {conf:.2f}%'
    )

    print('=' * 72)