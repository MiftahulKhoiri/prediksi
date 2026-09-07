import json
import os


DATA_FILE = 'prediction_data.json'


def _empty_state():
    return {
        'data': [],
        'history': []
    }


def load_state():
    if not os.path.exists(DATA_FILE):
        return _empty_state()

    try:
        with open(
            DATA_FILE,
            'r',
            encoding='utf-8'
        ) as f:
            state = json.load(f)

        if not isinstance(
            state,
            dict
        ):
            return _empty_state()

        data = state.get(
            'data',
            []
        )

        history = state.get(
            'history',
            []
        )

        if not isinstance(
            data,
            list
        ):
            data = []

        if not isinstance(
            history,
            list
        ):
            history = []

        return {
            'data': data,
            'history': history
        }

    except (
        OSError,
        json.JSONDecodeError,
        TypeError
    ):
        return _empty_state()


def save_state(state):
    temp_file = (
        DATA_FILE
        +
        '.tmp'
    )

    with open(
        temp_file,
        'w',
        encoding='utf-8'
    ) as f:
        json.dump(
            state,
            f,
            indent=2,
            ensure_ascii=False
        )

    os.replace(
        temp_file,
        DATA_FILE
    )


def record_result(
    state,
    prediction,
    actual
):
    correct = (
        prediction == actual
    )

    state.setdefault(
        'history',
        []
    ).append({
        'prediction': prediction,
        'actual': actual,
        'correct': correct
    })

    # Yang dimasukkan ke data adalah hasil aktual.
    state.setdefault(
        'data',
        []
    ).append(actual)

    save_state(
        state
    )

    return correct