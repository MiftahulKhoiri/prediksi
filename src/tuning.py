from collections import Counter

from .scoring import (
    frequency_scores,
    recency_scores,
    gap_scores,
    transition_scores,
    pair_scores,
    triple_scores,
    delta_scores,
    normalize,
)


METHOD_FUNCS = {
    "frequency": frequency_scores,
    "recency": recency_scores,
    "gap": gap_scores,
    "transition": transition_scores,
    "pair": pair_scores,
    "triple": triple_scores,
    "delta": delta_scores,
}

DEFAULT_WEIGHTS = {
    "frequency": 1.0,
    "recency": 0.8,
    "gap": 0.25,
    "transition": 1.8,
    "pair": 2.5,
    "triple": 3.0,
    "delta": 1.0,
    "learning": 1.0,
}

# Grid diperhalus (langkah lebih kecil) dan plafon dinaikkan supaya
# coordinate ascent tidak "mentok" di nilai tertinggi -- kalau hasil
# tuning tetap kena 8.0, itu tandanya plafon perlu dinaikkan lagi.
CANDIDATES = [
    0.0, 0.25, 0.5, 0.75,
    1.0, 1.5, 2.0, 2.5,
    3.0, 4.0, 5.0, 6.0, 8.0,
]

MIN_BACKTEST_POINTS = 15
RETUNE_INTERVAL = 5
MAX_TUNE_DATA = 300
WARMUP = 5


def _learning_scores_from_counts(learning_correct, learning_total, min_value, max_value):
    """
    Sama persis dengan scoring.learning_scores, tapi dari counter
    yang di-update inkremental (bukan scan ulang seluruh histori
    tiap langkah). Ini yang bikin "learning" bisa ikut dibacktest
    tanpa bikin backtest_accuracy jadi O(n^2).
    """
    scores = {
        value: 0
        for value in range(min_value, max_value + 1)
    }

    for value in scores:
        total = learning_total[value]

        if total:
            scores[value] = learning_correct[value] / total

    return normalize(scores)


def _predict_with_weights(
    data_slice, weights, min_value, max_value,
    learning_correct, learning_total,
):
    scores = {
        value: 0.0
        for value in range(min_value, max_value + 1)
    }

    for method, func in METHOD_FUNCS.items():
        method_scores = func(data_slice, min_value, max_value)
        weight = weights.get(method, 0.0)

        for value in scores:
            scores[value] += method_scores.get(value, 0) * weight

    # "learning" butuh histori prediksi (bukan cuma nilai historis).
    # Dihitung dari counter yang dibangun sendiri sepanjang backtest
    # ini -- konsisten dengan bobot yang lagi dicoba, bukan histori
    # dari kombinasi bobot lain, dan tanpa scan ulang tiap langkah.
    learning_weight = weights.get("learning", 0.0)

    if learning_weight:
        learning = _learning_scores_from_counts(
            learning_correct, learning_total, min_value, max_value
        )

        for value in scores:
            scores[value] += learning.get(value, 0) * learning_weight

    return max(scores, key=lambda v: scores[v])


def backtest_accuracy(data, weights, min_value, max_value, warmup=WARMUP):
    """
    Jalan ulang seluruh histori dengan gaya walk-forward: di
    setiap titik t, cuma pakai data[:t] (+ statistik prediksi yang
    dibangun sendiri sepanjang backtest ini) buat nebak data[t] --
    persis kayak kondisi asli saat prediksi dibuat (tidak
    mengintip "masa depan"). Total hit dibagi total percobaan
    itulah akurasi backtest untuk kombinasi bobot tsb.
    """
    if len(data) <= warmup + 1:
        return 0.0, 0

    correct = 0
    total = 0

    learning_correct = Counter()
    learning_total = Counter()

    for t in range(warmup, len(data)):
        guess = _predict_with_weights(
            data[:t], weights, min_value, max_value,
            learning_correct, learning_total,
        )

        total += 1
        is_correct = guess == data[t]

        if is_correct:
            correct += 1

        learning_total[guess] += 1

        if is_correct:
            learning_correct[guess] += 1

    if total == 0:
        return 0.0, 0

    return correct / total, total


def baseline_accuracy(data, min_value, max_value, warmup=WARMUP):
    """
    Sanity check: akurasi walk-forward kalau cuma nebak nilai
    yang paling sering muncul sejauh ini (modus berjalan), tanpa
    metode apa pun. Kalau algoritma kalah dari ini, tandanya
    kompleksitas ensemble-nya belum tentu nambah nilai di data
    yang ada.
    """
    if len(data) <= warmup + 1:
        return 0.0, 0

    correct = 0
    total = 0

    for t in range(warmup, len(data)):
        guess = Counter(data[:t]).most_common(1)[0][0]

        total += 1

        if guess == data[t]:
            correct += 1

    if total == 0:
        return 0.0, 0

    return correct / total, total


def tune_weights(data, min_value, max_value, base_weights=None):
    """
    Coordinate ascent sederhana: satu metode dicoba ganti-ganti
    nilai bobotnya (yang lain tetap), simpan kalau akurasi
    backtest naik. Diulang beberapa putaran sampai tidak ada
    perbaikan lagi. Hasilnya bobot yang didasarkan pada bukti
    di histori, bukan tebakan manual. "learning" ikut di sini,
    bukan lagi bobot tetap yang di-hardcode di luar.
    """
    tune_data = data[-MAX_TUNE_DATA:]

    if len(tune_data) < MIN_BACKTEST_POINTS:
        return dict(base_weights or DEFAULT_WEIGHTS)

    weights = dict(base_weights or DEFAULT_WEIGHTS)

    best_accuracy, _ = backtest_accuracy(
        tune_data, weights, min_value, max_value
    )

    for _ in range(2):
        improved = False

        for method in weights:
            best_value = weights[method]

            for candidate in CANDIDATES:
                trial = dict(weights)
                trial[method] = candidate

                accuracy, _ = backtest_accuracy(
                    tune_data, trial, min_value, max_value
                )

                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_value = candidate
                    improved = True

            weights[method] = best_value

        if not improved:
            break

    return weights


def tuning_report(data, weights, min_value, max_value):
    """
    Ringkasan buat dicek tiap kali retuning jalan: akurasi
    backtest algoritma vs baseline modus-sederhana, di rentang
    data yang sama. Dipakai main.py (lewat show_prediction) buat
    kasih peringatan kalau algoritma ternyata kalah dari baseline
    sepele.
    """
    tune_data = data[-MAX_TUNE_DATA:]

    algo_accuracy, n = backtest_accuracy(
        tune_data, weights, min_value, max_value
    )
    base_accuracy, _ = baseline_accuracy(
        tune_data, min_value, max_value
    )

    return {
        "algo_accuracy": algo_accuracy,
        "baseline_accuracy": base_accuracy,
        "n": n,
        "algo_wins": algo_accuracy > base_accuracy,
    }