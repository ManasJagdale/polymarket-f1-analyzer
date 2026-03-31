import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://polymarket.com/event/2026-f1-drivers-champion"

TIERS = {
    "1": {"name": "Conservative", "protection": 0.50, "fee": 0.35},
    "2": {"name": "Balanced", "protection": 0.30, "fee": 0.25},
    "3": {"name": "Growth", "protection": 0.10, "fee": 0.15},
    "4": {"name": "Full Exposure", "protection": 0.00, "fee": 0.10},
}

OFFICIAL_CODES = {
    "Max Verstappen": "VER",
    "Lewis Hamilton": "HAM",
    "Charles Leclerc": "LEC",
    "Lando Norris": "NOR",
    "Carlos Sainz": "SAI",
    "George Russell": "RUS",
    "Oscar Piastri": "PIA",
    "Fernando Alonso": "ALO",
    "Sergio Perez": "PER",
    "Esteban Ocon": "OCO",
    "Pierre Gasly": "GAS",
    "Yuki Tsunoda": "TSU",
    "Lance Stroll": "STR",
    "Valtteri Bottas": "BOT",
    "Zhou Guanyu": "ZHO",
    "Kevin Magnussen": "MAG",
    "Nico Hulkenberg": "HUL",
    "Alexander Albon": "ALB",
    "Logan Sargeant": "SAR",
    "Daniel Ricciardo": "RIC"
}

# ==========================================================
# DATA FETCHING
# ==========================================================

def fetch_html():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers, timeout=10)
    r.raise_for_status()
    return r.text

def extract_next_data(html):
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        raise ValueError("Could not find __NEXT_DATA__ script tag")
    return json.loads(script.string)

def find_event_markets(next_data):
    """Find markets data from the next_data JSON structure"""
    try:
        # Try to find markets in dehydrated queries
        queries = next_data.get("props", {}).get("pageProps", {}).get("dehydratedState", {}).get("queries", [])
        
        # Search through all queries to find one containing markets data
        for query in queries:
            state = query.get("state", {})
            data = state.get("data", {})
            
            # Check if this query has markets data
            if isinstance(data, dict) and "markets" in data:
                return data["markets"]
            
            # Also check nested structures
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict) and "markets" in value:
                        return value["markets"]
        
        # Alternative: Try to find markets in the page props directly
        page_props = next_data.get("props", {}).get("pageProps", {})
        if "markets" in page_props:
            return page_props["markets"]
        
        raise ValueError("Could not find markets data in the response")
        
    except Exception as e:
        print(f"Error finding markets: {e}")
        # Debug: print structure to help identify the correct path
        print("\nAvailable keys in next_data['props']['pageProps']:")
        page_props = next_data.get("props", {}).get("pageProps", {})
        print(list(page_props.keys())[:10])  # Show first 10 keys
        
        print("\nAvailable query types:")
        queries = next_data.get("props", {}).get("pageProps", {}).get("dehydratedState", {}).get("queries", [])
        for i, query in enumerate(queries):
            query_data = query.get("state", {}).get("data", {})
            if isinstance(query_data, dict):
                print(f"Query {i}: {list(query_data.keys())[:5]}")
        
        raise

def parse_drivers(markets):
    drivers = []

    for m in markets:
        question = m.get("question", "")

        if "be the 2026 F1 Drivers' Champion" in question and "Will " in question:
            name = question.replace("Will ", "").replace(" be the 2026 F1 Drivers' Champion?", "").strip()

            prices = m.get("outcomePrices")

            if isinstance(prices, str):
                try:
                    prices = json.loads(prices)
                except:
                    continue

            if prices and len(prices) > 0:
                try:
                    prob = float(prices[0])
                    if 0 < prob < 1:
                        drivers.append({"name": name, "probability": prob})
                except:
                    continue

    return drivers

# ==========================================================
# DRIVER CODE ASSIGNMENT
# ==========================================================

def generate_driver_codes(drivers):
    used_codes = set()

    for d in drivers:
        name = d["name"]

        if name in OFFICIAL_CODES:
            code = OFFICIAL_CODES[name]
        else:
            last = name.split()[-1]
            code = last[:3].upper()

        while code in used_codes:
            code = code[:2] + chr(ord(code[-1]) + 1)

        used_codes.add(code)
        d["code"] = code

    return drivers

# ==========================================================
# DRIVER SELECTION
# ==========================================================

def select_drivers(drivers):
    print("\nAvailable Drivers:\n")

    drivers_sorted = sorted(drivers, key=lambda x: x["probability"], reverse=True)

    for d in drivers_sorted:
        print(f"{d['code']} - {d['name']} ({round(d['probability']*100,2)}%)")

    selected = input("\nEnter driver codes separated by commas: ").upper()
    selected_codes = [x.strip() for x in selected.split(",")]

    chosen = [d for d in drivers if d["code"] in selected_codes]

    if not chosen:
        print("No valid drivers selected.")
        exit()

    return chosen

# ==========================================================
# ALLOCATION ENGINE
# ==========================================================

def allocation_engine(drivers, capital):
    df = pd.DataFrame(drivers)
    total_prob = df["probability"].sum()

    df["allocation"] = capital * (df["probability"] / total_prob)
    df["allocation"] = df["allocation"].round(2)

    return df, total_prob

# ==========================================================
# CORRECTED TIER CALCULATOR
# ==========================================================

def calculate_tier_metrics(capital, total_prob, tier):

    protection = tier["protection"]
    fee_rate = tier["fee"]

    exposure = 1 - protection

    exposed_capital = capital * exposure
    protected_capital = capital * protection

    gross_multiple = 1 / total_prob

    gross_profit = exposed_capital * (gross_multiple - 1)
    gross_return_pct = (gross_profit / capital) * 100

    fee_amount = gross_profit * fee_rate
    net_profit = gross_profit - fee_amount

    final_value = protected_capital + exposed_capital * gross_multiple - fee_amount
    net_return_pct = (net_profit / capital) * 100

    worst_case_value = protected_capital
    worst_case_pct = -((capital - worst_case_value) / capital) * 100

    return {
        "exposure": exposure,
        "protected_capital": protected_capital,
        "exposed_capital": exposed_capital,
        "gross_profit": gross_profit,
        "gross_return_pct": gross_return_pct,
        "fee_amount": fee_amount,
        "net_profit": net_profit,
        "net_value": final_value,
        "net_return_pct": net_return_pct,
        "worst_case_pct": worst_case_pct
    }

# ==========================================================
# MAIN
# ==========================================================

def main():

    print("\nFetching live probabilities...\n")

    try:
        html = fetch_html()
        next_data = extract_next_data(html)
        markets = find_event_markets(next_data)
        drivers = parse_drivers(markets)
        
        if not drivers:
            print("No drivers found. The page structure might have changed or no markets are available.")
            return
            
        drivers = generate_driver_codes(drivers)

        capital = float(input("Enter total capital: "))

        chosen_drivers = select_drivers(drivers)

        df, total_prob = allocation_engine(chosen_drivers, capital)

        print("\n====================================")
        print("PORTFOLIO STRUCTURE")
        print("====================================\n")

        print(f"Total Probability Covered: {round(total_prob*100,2)}%")
        print(f"Gross Multiple (if fully exposed): {round(1/total_prob,4)}x\n")

        print("Capital Deployment Across Drivers:")
        print("------------------------------------")
        for _, row in df.iterrows():
            print(f"{row['code']} ({row['name']}): ${row['allocation']}")

        print("\n====================================")
        print("TIER BREAKDOWN (Corrected Exposure Math)")
        print("====================================\n")

        for key, tier in TIERS.items():

            metrics = calculate_tier_metrics(capital, total_prob, tier)

            print(f"{tier['name']}")
            print(f"  Protection: {int(tier['protection']*100)}%")
            print(f"  Exposure: {int(metrics['exposure']*100)}%")
            print(f"  Fee Rate: {int(tier['fee']*100)}%")

            print(f"  Protected Capital: ${round(metrics['protected_capital'],2)}")
            print(f"  Exposed Capital: ${round(metrics['exposed_capital'],2)}")

            print(f"  Gross Return: {round(metrics['gross_return_pct'],2)}%")
            print(f"  Gross Profit: ${round(metrics['gross_profit'],2)}")

            print(f"  Fee Collected: ${round(metrics['fee_amount'],2)}")

            print(f"  Net Return: {round(metrics['net_return_pct'],2)}%")
            print(f"  Net Profit: ${round(metrics['net_profit'],2)}")
            print(f"  Final Portfolio Value: ${round(metrics['net_value'],2)}")

            print(f"  Worst Case Return: {round(metrics['worst_case_pct'],2)}%\n")

        print("Done.\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check if the URL is still valid")
        print("2. The Polymarket website might have changed its structure")
        print("3. Try running again - sometimes the API response varies")

if __name__ == "__main__":
    main()