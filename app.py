# app.py – FINAL GOD MODE (Short + Long Combined Score) – 100% WORKING
from flask import Flask, render_template, request
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

# Your watchlist (unchanged)
MY_WATCHLIST = [
    "DKNG","TSSI","MARA","TTD","CRWV","SOUN","BABA","BBAI","RIVN","ACMR","VOO","META",
    "NVDA","AMD","SMCI","PLTR","TSLA","HOOD","COIN","UPST","SOFI","AVGO","LLY","NVO",
    "TSM","ASML","AAPL","MSFT","GOOGL","AMZN","ARM","QCOM","INTC","MU","SNOW","CRWD",
    "NOW","CRM","ADBE","ORCL","DELL","HPE","ANET","CSCO","PANW","FTNT","ZS","NET","DDOG",
    "HIMS","VKTX","CRSP","BEAM","REGN","VRTX","JNJ","PFE","MRK","ABBV","AMGN","BMY",
    "MDT","BSX","GEHC","OSCR","TEM","ISRG","DXCM","PODD","NIO","XPEV","LI","LCID",
    "ENPH","FSLR","RUN","FLNC","BE","PLUG","VST","CEG","NEE","AES","SHLS","SQ","PYPL",
    "AFRM","RBLX","SHOP","MELI","NU","IBKR","SCHW","RIOT","CELH","MNST","WMT","COST",
    "HD","PDD","JD","NKE","LULU","SE","CAT","DE","LMT","RTX","BA","GE","HON","RKLB",
    "LUNR","ASTS","ALB","SQM","MP","FCX"
]

def score_stock(ticker):
    try:
        s = yf.Ticker(ticker)
        info = s.info
        if not info.get("longName"):
            return None

        h = s.history(period="5y", interval="1d")
        if h.empty or len(h) < 200:
            return None

        price = h["Close"].iloc[-1]
        ath = h["Close"].max()
        dist_from_ath = (price - ath) / ath
        two_y_ago_price = h["Close"].iloc[-504] if len(h) >= 504 else h["Close"].iloc[0]
        cagr_2y = (price / two_y_ago_price) ** (1/2) - 1

        # Short-term 6 months
        h6 = h["Close"][-126:]
        high_6m = h6.max()
        low_6m = h6.min()
        dist_6m = (price - high_6m) / high_6m
        near_bottom = (price - low_6m) / (high_6m - low_6m)

        # RSI & Volume
        delta = h["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        vol_ratio = h["Volume"].iloc[-10:].mean() / h["Volume"].rolling(50).mean().iloc[-1]

        # Fundamentals
        fcf = info.get("freeCashflow", 0)
        rev_growth = info.get("revenueGrowth", 0)
        inst_own = info.get("heldPercentInstitutions", 0)
        short_ratio = info.get("shortRatio", 0)
        target_price = info.get("targetMeanPrice", price)
        upside = (target_price / price) - 1
        forward_pe = info.get("forwardPE") or 999
        market_cap = info.get("marketCap", 0)

        if forward_pe > 80 or market_cap < 1.5e9:
            return None

        # SHORT-TERM BOUNCE SCORE
        short_score = 0
        short_score += abs(dist_6m) * 600
        short_score += (1 - near_bottom) * 300
        short_score += max(0, (40 - rsi)) * 8
        short_score += max(0, (1 - vol_ratio)) * 400
        if short_ratio and short_ratio > 15:
            short_score += 350

        # LONG-TERM MONSTER SCORE
        long_score = 0
        long_score += abs(dist_from_ath) * 700
        long_score += max(0, -cagr_2y) * 900
        if rev_growth > 0.15: long_score += 500
        if fcf and fcf > 0: long_score += 450
        if inst_own > 0.7: long_score += 400
        if upside > 1.0: long_score += 500
        if short_ratio and short_ratio > 20: long_score += 300

        return {
            "ticker": ticker,
            "name": info.get("longName", ticker)[:28],
            "price": f"${price:,.2f}",
            "dip_ath": f"{dist_from_ath*100:+.1f}% ATH",
            "dip_6m": f"{dist_6m*100:+.1f}% 6m",
            "rsi": round(rsi, 1),
            "short_score": round(short_score),
            "long_score": round(long_score),
            "upside": f"{upside*100:+.1f}%",
            # GOD MODE COMBINED SCORE (this is what we sort by)
            "god_score": round(short_score + long_score)
        }
    except Exception as e:
        print(f"Error {ticker}: {e}")
        return None


@app.route('/', methods=["GET", "POST"])
def dashboard():
    added = None

    if request.method == "POST":
        ticker = request.form.get("add_ticker", "").strip().upper()
        if ticker and 1 <= len(ticker) <= 6 and ticker not in MY_WATCHLIST:
            MY_WATCHLIST.append(ticker)
            added = ticker

    # SCORE & SORT BY GOD MODE
    results = [score_stock(t) for t in MY_WATCHLIST]
    results = [r for r in results if r]
    results = sorted(results, key=lambda x: -x["god_score"])

    top = results[:6]
    watch = results[6:]
    for i, stock in enumerate(top):
        stock["rank"] = i + 1

    return render_template("dashboard.html",
                           top=top,
                           watch=watch,
                           added=added,
                           time=datetime.now().strftime("%H:%M:%S"))


# Keep your other routes
@app.route('/stock-lookup')
def stock_lookup(): return render_template('stock_lookup.html')

@app.route('/trending')
def trending(): return render_template('trending.html')

@app.route('/ai-lab')
def ai_lab(): return render_template('ai_lab.html')

if __name__ == "__main__":
    app.run(debug=True)