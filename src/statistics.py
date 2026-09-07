def show_statistics(state):
    history = state.get(
        'history',
        []
    )

    if not history:
        print(
            '\nBelum ada histori.'
        )
        return

    total = len(
        history
    )

    correct = sum(
        1
        for item in history
        if item.get(
            'correct',
            item.get('prediction')
            ==
            item.get('actual')
        )
    )

    accuracy = (
        correct
        /
        total
        *
        100.0
    )

    recent = history[-20:]

    recent_correct = sum(
        1
        for item in recent
        if item.get(
            'correct',
            item.get('prediction')
            ==
            item.get('actual')
        )
    )

    recent_accuracy = (
        recent_correct
        /
        len(recent)
        *
        100.0
        if recent
        else 0.0
    )

    print()
    print('=' * 72)
    print(' STATISTIK MESIN')
    print('=' * 72)

    print(
        f'Total prediksi       : {total}'
    )

    print(
        f'Benar                : {correct}'
    )

    print(
        f'Salah                : {total - correct}'
    )

    print(
        f'Akurasi total        : '
        f'{accuracy:.2f}%'
    )

    print(
        f'Akurasi 20 terakhir  : '
        f'{recent_accuracy:.2f}%'
    )

    print('=' * 72)