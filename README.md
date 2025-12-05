Factor Based Equity Ranking Engine

A quantitative research engine that ranks equities using multi factor modeling, combining momentum, volatility, valuation, and size signals to generate systematic investment insights.
This project was built in Python using Pandas, NumPy, and yfinance. AI tools supported documentation clarity, debugging, and refinement of analytical logic, while all financial modeling decisions were human driven.

Overview

 - Equity factor models are widely used in quantitative investing, smart beta funds, and multi asset research. This engine implements a simplified but powerful version of that framework:

- Pulls historical price and fundamental data

 - Computes factor signals (momentum, volatility, value, size)

- Standardizes metrics with z scores

- Produces composite scores based on user defined weights

- Ranks each stock cross sectionally

- The result is an interpretable multi factor ranking that can be used for research, screening, or as the foundation for a systematic long short strategy.

Features

- Automated data ingestion from yfinance

- 6 month momentum calculation

- 3 month realized volatility

- Value metrics using P/E and P/B ratios

- Market cap based size factor

- Statistical standardization using z scores

- Weighted composite scoring

- Sorted equity rankings with complete factor table output


SAMPLE OUTPUT

UNH          -0.038063
MSFT         -0.163421

Full factor table (first few rows):
        momentum_6m vol_3m   value_pe  value_pb       size  momentum_6m_z  vol_3m_z     value_pe_z  value_pb_z  size_z        composite_score
GOOGL     0.832617  0.018650 -31.603160 -9.994069  28.986231       2.369164  0.380442   -0.256814    0.321688  0.854889         0.841680     
JNJ       0.324010  0.008888 -19.532848 -6.136067  26.911684       0.322782 -1.596960    1.038544    0.544624 -1.331927         0.560655     
JPM       0.201095  0.011805 -15.642326 -2.528670  27.490440      -0.171765 -1.006061    1.456066    0.753079 -0.721850         0.495585     
UNH       0.114624  0.020077 -17.250520 -3.129487  26.426082      -0.519683  0.669446    1.283478    0.718360 -1.843809        -0.038063     
MSFT      0.025834  0.011727 -34.289173 -9.857084  28.905958      -0.876928 -1.022027   -0.545071    0.329604  0.770272        -0.163421     
