import os

from src.storage import (
    load_state,
    save_state,
    record_result,
    record_range_result
)

from src.prediction import (
    predict,
    show_prediction
)

from src.range_prediction import (
    predict_range,
    show_range_prediction,
    to_label,
    label_name
)

from src.statistics import (
    show_statistics,
    show_range_statistics
)


MIN_VALUE = 3
MAX_VALUE = 18


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def input_initial_data(state):
    print("=" * 65)
    print("Masukkan data historis.")
    print("Contoh:")
    print("4,8,3,12,4,6,15,9,9,7")

    raw = input("\nData: ")

    try:
        data = [
            int(x.strip())
            for x in raw.split(",")
            if x.strip()
        ]

        for value in data:
            if not (
                MIN_VALUE <= value <= MAX_VALUE
            ):
                raise ValueError

        state["data"] = data

        save_state(state)

        return True

    except ValueError:
        print("Data tidak valid.")
        return False


def show_round_result(
    state,
    prediction,
    range_prediction,
    actual,
    correct
):
    print("=" * 65)
    print(" HASIL")
    print("=" * 65)

    if correct:
        print(
            f"\n✓ BENAR — mesin menebak {prediction},"
            f" aktual {actual}"
        )
    else:
        print(
            f"\n✗ SALAH — mesin: {prediction}"
            f" | aktual: {actual}"
        )

    if range_prediction is not None:
        actual_range = to_label(actual)
        range_ok = range_prediction == actual_range
        mark = "✓" if range_ok else "✗"

        print(
            f"{mark} Rentang — mesin: {label_name(range_prediction)}"
            f" | aktual: {label_name(actual_range)}"
        )

    show_statistics(state)
    show_range_statistics(state)

    print("\n" + "=" * 65)


def main():
    state = load_state()

    if not state["data"]:
        if not input_initial_data(state):
            return

    round_number = len(state.get("history", [])) + 1

    while True:
        clear_screen()

        ranking = predict(
            state,
            MIN_VALUE,
            MAX_VALUE
        )

        show_prediction(
            state,
            ranking,
            round_number
        )

        range_ranking = predict_range(state)

        show_range_prediction(range_ranking)

        prediction = ranking[0][0]

        range_prediction = (
            range_ranking[0][0]
            if range_ranking
            else None
        )

        print("\nMasukkan hasil sebenarnya.")
        print("Ketik Q untuk keluar.")

        raw = input("\nHasil: ").strip()

        if raw.lower() == "q":
            save_state(state)

            print("\nData disimpan.")
            break

        try:
            actual = int(raw)

        except ValueError:
            print("Masukkan angka 3-18.")
            input("\nTekan ENTER untuk coba lagi...")
            continue

        if not (
            MIN_VALUE <= actual <= MAX_VALUE
        ):
            print("Nilai harus 3-18.")
            input("\nTekan ENTER untuk coba lagi...")
            continue

        correct = record_result(
            state,
            prediction,
            actual
        )

        if range_prediction is not None:
            actual_range = to_label(actual)

            record_range_result(
                state,
                range_prediction,
                actual_range
            )

        clear_screen()

        show_round_result(
            state,
            prediction,
            range_prediction,
            actual,
            correct
        )

        round_number += 1

        input("\nTekan ENTER untuk prediksi berikutnya...")


if __name__ == "__main__":
    main()