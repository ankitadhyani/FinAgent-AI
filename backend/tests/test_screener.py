from data_loader import load_data
from screener import screen_transactions


if __name__ == "__main__":
    df = load_data()

    results = screen_transactions(df, limit=50, suspicious_only=True)

    print("\n===== SCREENED SUSPICIOUS TRANSACTIONS =====")
    for row in results[:10]:
        print(row)