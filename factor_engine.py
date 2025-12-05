import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# ------------- Helpers -------------

def zscore(series):
    """Standardize a pandas Series."""
    return (series - series.mean()) / series.std(ddof=0)

# ------------- Data download -------------

def download_price_history(tickers, years_back=2):
    end = datetime.today()
    start = end - timedelta(days=365 * years_back)

    data = yf.download(
        tickers,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
        threads=True
    )

    # Case 1 multiindex (normal)
    if isinstance(data.columns, pd.MultiIndex):
        if "Adj Close" in data.columns.levels[0]:
            prices = data["Adj Close"]
        else:
            # Sometimes yfinance uses 'Close' instead
            prices = data["Close"]
    else:
        # Case 2 single ticker returns a Series or simple DataFrame
        if "Adj Close" in data.columns:
            prices = data[["Adj Close"]]
        elif "Close" in data.columns:
            prices = data[["Close"]]
        else:
            raise ValueError("Price data does not contain Close or Adj Close columns.")

    # Drop tickers with too many missing values
    prices = prices.dropna(axis=1, thresh=50)

    if prices.empty:
        raise ValueError("No valid price data downloaded.")

    return prices


# ------------- Factor computation -------------

def compute_factor_table(prices, fundamentals):
    """
    Compute a table of factor scores for each ticker.
    Factors:
      - momentum_6m: 6 month return
      - vol_3m: 3 month realized volatility (lower is better)
      - value_pe: inverse P/E proxy
      - value_pb: inverse P/B proxy
      - size: log(market cap)
    """
    tickers = list(prices.columns)
    rets = compute_returns(prices)

    # Ensure fundamentals match tickers
    fundamentals = fundamentals.reindex(tickers)

    # Choose windows
    trading_days_6m = 126
    trading_days_3m = 63

    if len(prices) < trading_days_6m + 5:
        raise ValueError("Not enough price history for 6 month momentum.")

    # Last prices and lagged prices
    last_price = prices.iloc[-1]

    price_6m_ago = prices.iloc[-trading_days_6m]
    momentum_6m = (last_price / price_6m_ago) - 1.0

    # Volatility: standard deviation of daily returns over last 3 months
    vol_3m = rets.tail(trading_days_3m).std()

    # Value: low P/E and low P/B are better, so use negative of the raw metrics
    value_pe = -fundamentals["trailing_pe"]
    value_pb = -fundamentals["price_to_book"]

    # Size: log of market cap
    size = np.log(fundamentals["market_cap"])

    factors = pd.DataFrame(
        {
            "momentum_6m": momentum_6m,
            "vol_3m": vol_3m,
            "value_pe": value_pe,
            "value_pb": value_pb,
            "size": size,
        }
    )

    # Drop tickers with too many missing values
    factors = factors.dropna(thresh=3)  # at least 3 non NaN factors

    # Standardize each factor
    for col in factors.columns:
        factors[col + "_z"] = zscore(factors[col])

    return factors


# ------------- Composite score and ranking -------------

def rank_stocks(factors, weights=None):
    """
    Combine z scored factors into a composite score and rank.
    weights: dict from factor_z name to weight.
             If None, equal weight all z columns.
    """
    z_cols = [c for c in factors.columns if c.endswith("_z")]

    if weights is None:
        # Equal weight
        w = {c: 1.0 for c in z_cols}
    else:
        w = weights

    # Ensure weights only on existing columns
    w = {k: v for k, v in w.items() if k in z_cols}

    # Weighted sum
    composite = pd.Series(0.0, index=factors.index)
    for col, weight in w.items():
        composite += weight * factors[col]

    out = factors.copy()
    out["composite_score"] = composite
    out = out.sort_values("composite_score", ascending=False)

    return out


# ------------- Example main script -------------
def fetch_fundamentals(tickers):
    """
    Fetch basic fundamentals from Yahoo Finance.
    Returns a DataFrame indexed by ticker.
    """
    rows = []
    for t in tickers:
        tk = yf.Ticker(t)
        info = tk.info  # may be partially missing

        rows.append(
            {
                "ticker": t,
                "trailing_pe": info.get("trailingPE", np.nan),
                "price_to_book": info.get("priceToBook", np.nan),
                "market_cap": info.get("marketCap", np.nan),
            }
        )

    fundamentals = pd.DataFrame(rows).set_index("ticker")
    return fundamentals
def compute_returns(prices):
    """Compute daily percent returns."""
    returns = prices.pct_change()
    return returns.dropna(how="all")

if __name__ == "__main__":
    # Example universe (you should expand this)
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META",
        "NVDA", "JPM", "UNH", "JNJ"
    ]

    print("Downloading prices...")
    prices = download_price_history(tickers, years_back=2)

    print("Fetching fundamentals...")
    fundamentals = fetch_fundamentals(tickers)

    print("Computing factors...")
    factors = compute_factor_table(prices, fundamentals)

    # Example weights
    # Heavier weight to momentum and value, a bit to quality proxies
    weights = {
        "momentum_6m_z": 0.35,
        "vol_3m_z": -0.15,   # negative because high vol is bad
        "value_pe_z": 0.25,
        "value_pb_z": 0.15,
        "size_z": 0.10,
    }

    ranked = rank_stocks(factors, weights=weights)

    print("\nTop ranked stocks:")
    print(ranked[["composite_score"]].head(5))

    print("\nFull factor table (first few rows):")
    print(ranked.head())
