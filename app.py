from flask import Flask, render_template, request
import yfinance as yf

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/stock-lookup", methods=["GET", "POST"])
def stock_lookup():
    stock_data = None
    error = None

    if request.method == "POST":
        ticker = request.form.get("ticker").upper()
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            if "longName" not in info:
                raise ValueError("Invalid ticker")

            stock_data = {
                "name": info["longName"],
                "price": info.get("currentPrice", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "sector": info.get("sector", "N/A"),
            }

        except Exception as e:
            error = "Invalid ticker or API error."

    return render_template(
        "stock_lookup.html",
        stock_data=stock_data,
        error=error
    )



@app.route('/trending')
def trending():
    return render_template('trending.html')


@app.route('/ai-lab')
def ai_lab():
    return render_template('ai_lab.html')


if __name__ == "__main__":
    app.run(debug=True)
