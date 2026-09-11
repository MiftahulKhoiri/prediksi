def show_statistics(state):
    history = state.get("history", [])

    if not history:
        print("\nBelum ada histori angka.")
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

    print("\nSTATISTIK ANGKA")
    print("-" * 65)

    print(
        f"Total: {total}   "
        f"Benar: {correct}   "
        f"Salah: {total - correct}   "
        f"Akurasi: {accuracy:.2f}%"
    )


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

    print("\nSTATISTIK RENTANG (BESAR/KECIL)")
    print("-" * 65)

    print(
        f"Total: {total}   "
        f"Benar: {correct}   "
        f"Salah: {total - correct}   "
        f"Akurasi: {accuracy:.2f}%"
    )