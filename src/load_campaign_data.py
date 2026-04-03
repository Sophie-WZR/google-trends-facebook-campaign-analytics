from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "data" / "raw" / "facebook_ads.csv"

def main():
    df = pd.read_csv(INPUT_PATH)
    print(df.head())
    print(df.info())
    print(df.isna().sum())

if __name__ == "__main__":
    main()