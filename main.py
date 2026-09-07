from src.storage import (
    load_state,
    save_state,
    record_result
)

from src.prediction import (
    predict,
    show_prediction
)

from src.statistics import (
    show_statistics
)


MIN_VALUE = 3
MAX_VALUE = 18


def parse_values(raw):
    values = []

    raw = raw.replace(';', ',')

    for token in raw.split(','):
        token = token.strip()
        if not token:
            continue

        value = int(token)

        if not (MIN_VALUE <= value <= MAX_VALUE):
            raise ValueError(
                f'Nilai {value} di luar rentang {MIN_VALUE}-{MAX_VALUE}.'
            )

        values.append(value)

    if not values:
        raise ValueError('Data kosong.')

    return values


def input_initial_data(state):
    print('=' * 72)
    print(' MASUKKAN DATA HISTORIS')
    print('=' * 72)
    print(f'Nilai yang diperbolehkan: {MIN_VALUE}-{MAX_VALUE}')
    print('Contoh:')
    print('4,8,3,12,4,6,15,9,9,7')

    raw = input('\nData: ').strip()

    try:
        data = parse_values(raw)
    except ValueError as error:
        print(f'Data tidak valid: {error}')
        return False

    state['data'] = data
    state.setdefault('history', [])
    save_state(state)

    print(f'{len(data)} data disimpan.')
    return True


def add_manual_data(state):
    raw = input(
        '\nTambahkan data aktual (contoh 4,8,12): '
    ).strip()

    try:
        values = parse_values(raw)
    except ValueError as error:
        print(f'Data tidak valid: {error}')
        return

    state['data'].extend(values)
    save_state(state)

    print(f'{len(values)} data ditambahkan.')


def reset_data(state):
    confirm = input(
        '\nKetik RESET untuk menghapus data: '
    ).strip()

    if confirm != 'RESET':
        print('Reset dibatalkan.')
        return

    state['data'] = []
    state['history'] = []
    save_state(state)

    print('Semua data dan histori dihapus.')


def main():
    state = load_state()

    if not state.get('data'):
        if not input_initial_data(state):
            return

    while True:
        ranking = predict(
            state,
            MIN_VALUE,
            MAX_VALUE
        )

        if not ranking:
            print('Belum cukup data untuk membuat prediksi.')
            return

        show_prediction(
            state,
            ranking
        )

        prediction = ranking[0][0]

        print('\nMasukkan hasil sebenarnya:')
        print(f'  Angka {MIN_VALUE}-{MAX_VALUE} = simpan hasil + prediksi lagi')
        print('  A = tambah data manual')
        print('  S = statistik')
        print('  R = reset data + histori')
        print('  Q = keluar')

        raw = input('\nHasil: ').strip()

        if raw.lower() == 'q':
            save_state(state)
            print('\nData disimpan. Program selesai.')
            break

        if raw.lower() == 'a':
            add_manual_data(state)
            continue

        if raw.lower() == 's':
            show_statistics(state)
            continue

        if raw.lower() == 'r':
            reset_data(state)

            if not state.get('data'):
                if not input_initial_data(state):
                    return

            continue

        try:
            actual = int(raw)
        except ValueError:
            print(
                f'Masukkan angka {MIN_VALUE}-{MAX_VALUE}, '
                'atau A/S/R/Q.'
            )
            continue

        if not (MIN_VALUE <= actual <= MAX_VALUE):
            print(f'Nilai harus {MIN_VALUE}-{MAX_VALUE}.')
            continue

        correct = record_result(
            state,
            prediction,
            actual
        )

        if correct:
            print(
                f'\n✓ BENAR — mesin={prediction}, aktual={actual}'
            )
        else:
            print(
                f'\n✗ SALAH — mesin={prediction}, aktual={actual}'
            )

        show_statistics(state)

        print('\nHasil aktual sudah dimasukkan ke data.')
        print('Mesin menghitung prediksi berikutnya...')


if __name__ == '__main__':
    main()