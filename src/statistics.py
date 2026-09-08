def show_statistics(state):
    history = state.get("history", [])

    if not history:
        print("\nBelum ada histori.")
        return

    total = len(history)

    correct = sum(
        1
        for x in history
        if x["correct"]
    )

    accuracy = (
        correct /
        total *
        100
    )

    print()
    print("=" * 65)
    print(" STATISTIK MESIN")
    print("=" * 65)

    print(f"Total prediksi : {total}")
    print(f"Benar         : {correct}")
    print(f"Salah         : {total - correct}")
    print(f"Akurasi       : {accuracy:.2f}%")

    print("=" * 65)


def show_range_statistics(state):
    history = state.get("range_history", [])

    if not history:
        return

    total = len(history)

    correct = sum(
        1
        for x in history
        if x["correct"]
    )

    accuracy = (
        correct /
        total *
        100
    )

    print()
    print("=" * 65)
    print(" STATISTIK RENTANG (BESAR/KECIL)")
    print("=" * 65)

    print(f"Total prediksi : {total}")
    print(f"Benar         : {correct}")
    print(f"Salah         : {total - correct}")
    print(f"Akurasi       : {accuracy:.2f}%")

    print("=" * 65)