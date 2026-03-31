# F1 Portfolio Optimizer

A Python-based portfolio optimization tool that uses live prediction market data from Polymarket to construct and analyze betting portfolios for the **2026 Formula 1 Drivers' Championship**.

---

## Overview

This project fetches real-time probability data from Polymarket and helps users:

* Select drivers to include in a portfolio
* Allocate capital optimally based on probabilities
* Analyze expected returns
* Evaluate downside risk
* Compare multiple exposure strategies

---

## Key Features

### Live Data Extraction

* Scrapes Polymarket event data
* Extracts driver-specific probabilities dynamically

### Driver Selection System

* Displays all available drivers with probabilities
* Allows custom portfolio construction via driver codes

### Capital Allocation Engine

* Allocates capital proportionally based on probabilities
* Ensures efficient portfolio distribution

### Risk Tier Modeling

Four investment strategies:

| Tier | Name          | Protection | Exposure |
| ---- | ------------- | ---------- | -------- |
| 1    | Conservative  | 50%        | 50%      |
| 2    | Balanced      | 30%        | 70%      |
| 3    | Growth        | 10%        | 90%      |
| 4    | Full Exposure | 0%         | 100%     |

---

## How It Works

1. Fetch HTML from Polymarket event page
2. Extract embedded JSON data (`__NEXT_DATA__`)
3. Parse driver probabilities
4. Assign driver codes
5. User selects drivers
6. Capital is allocated proportionally
7. Returns and risks are calculated across tiers

---

## Mathematical Logic

### Allocation Formula

Allocation = Capital × (Driver Probability / Total Probability)

### Gross Multiple

1 / Total Probability

### Profit

Exposed Capital × (Gross Multiple - 1)

### Net Profit

Gross Profit - Fees

---

## Example Output

Below is a real sample run of the tool:

### Input

* **Capital:** $1000
* **Selected Drivers:** RUS, ANT, LEC

---

### Portfolio Structure

====================================
PORTFOLIO STRUCTURE
====================================

Total Probability Covered: 83.25%
Gross Multiple (if fully exposed): 1.2012x

Capital Deployment Across Drivers:
------------------------------------
RUS (George Russell): $546.55
ANT (Kimi Antonelli): $385.59
LEC (Charles Leclerc): $67.87

---

### Tier Analysis

#### 🟢 Conservative Strategy

* Protection: 50%
* Exposure: 50%
* Net Return: **6.54%**
* Final Value: **$1065.39**
* Worst Case: **-50%**

---

#### 🟡 Balanced Strategy

* Protection: 30%
* Exposure: 70%
* Net Return: **10.56%**
* Final Value: **$1105.63**
* Worst Case: **-70%**

---

#### 🔵 Growth Strategy

* Protection: 10%
* Exposure: 90%
* Net Return: **15.39%**
* Final Value: **$1153.92**
* Worst Case: **-90%**

---

#### 🔴 Full Exposure

* Protection: 0%
* Exposure: 100%
* Net Return: **18.11%**
* Final Value: **$1181.08**
* Worst Case: **-100%**

---

### Key Insights

* Higher exposure → higher returns, but significantly higher downside risk
* Conservative strategy preserves capital but limits upside
* Full exposure maximizes returns but risks total loss
* Balanced strategy offers a strong middle-ground risk/reward profile

---

## Risk vs Return Visualization

You can extend this project using matplotlib to visualize:

* Return vs Risk tradeoff
* Capital allocation distribution
* Tier comparison

### Example Graph Code

```python
import matplotlib.pyplot as plt

tiers = ["Conservative", "Balanced", "Growth", "Full"]
returns = [6.54, 10.56, 15.39, 18.11]

plt.plot(tiers, returns)
plt.xlabel("Strategy")
plt.ylabel("Expected Return (%)")
plt.title("Risk vs Return Profile")
plt.show()
```

---

## Tech Stack

* Python
* requests
* BeautifulSoup
* pandas
* JSON parsing

---

## Installation

Clone the repository:

git clone https://github.com/your-username/polymarket-f1-analyzer.git
cd polymarket-f1-analyzer

Install dependencies:

pip install -r requirements.txt

---

## Usage

Run the script:

python main.py

Then:

1. Enter total capital
2. Select drivers using codes (e.g., VER, NOR, LEC)
3. View portfolio allocation and analysis

---

## Project Structure

polymarket-f1-analyzer/
│
├── main.py
├── README.md
├── requirements.txt
└── .gitignore

---

## Limitations

* Depends on Polymarket page structure (may break if site updates)
* Assumes probabilities are accurate and efficient
* No transaction costs beyond modeled fees

---

## Future Improvements

* [ ] Export results to CSV
* [ ] Add interactive graphs
* [ ] Build web dashboard (Streamlit / Flask)
* [ ] Add historical tracking
* [ ] Automate periodic data fetching

---

## License

This project is licensed under the MIT License.

---

## Disclaimer

This project is for educational and analytical purposes only.
It does not constitute financial or betting advice.

---

## Author

Built by Manas Jagdale
