import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
import requests
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup


# Function to format currency values
def filter_tickers(prefix, available_tickers):
    return [ticker for ticker in available_tickers if ticker.startswith(prefix.upper())]

def get_ticker_from_company_name(company_name):
    ticker = None
    url = f"https://finance.yahoo.com/quote/{company_name}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        ticker = soup.find('meta', property='og:tickersymbol')['content']
    except Exception as e:
        print(f"Error fetching ticker for {company_name}: {e}")
    return ticker

def get_trading_recommendation(stock_history):
    sma_50 = SMAIndicator(close=stock_history['Close'], window=50).sma_indicator()
    sma_200 = SMAIndicator(close=stock_history['Close'], window=200).sma_indicator()
    rsi = RSIIndicator(close=stock_history['Close']).rsi().iloc[-1]

    if sma_50.iloc[-1] > sma_200.iloc[-1] and rsi < 30:
        return "Buy"
    elif sma_50.iloc[-1] < sma_200.iloc[-1] and rsi > 70:
        return "Sell"
    else:
        return "Hold"
def get_stock_news(ticker):
    # Construct Google search URL for stock news
    url = f"https://www.google.com/search?q={ticker}+stock+news"

    # Send HTTP GET request and parse the response
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract news articles and their links
    news_articles = []

    for item in soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd'):
        title = item.get_text()
        # Find the parent 'a' tag and retrieve the 'href' attribute (URL)
        link = item.find_parent('a')['href']
        # Remove any unnecessary URL parameters added by Google
        clean_link = clean_google_news_link(link)
        # Append the article title and clean link to the list
        news_articles.append({'title': title, 'link': clean_link})

    return news_articles

def clean_google_news_link(link):
    # Extract the clean URL from the Google search result link
    clean_link = link.split('q=')[1].split('&sa=')[0]
    return clean_link


def get_investor_reports(ticker):
    url = f"https://www.google.com/search?q={ticker}+investor+report"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    reports = []

    for item in soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd'):
        title = item.get_text()
        link = item.find_parent('a')['href']
        clean_link = clean_google_report_link(link)
        reports.append({'title': title, 'link': clean_link})

    return reports

def get_peer_reports(ticker):
    url = f"https://www.google.com/search?q={ticker}+peer+report"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    reports = []

    for item in soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd'):
        title = item.get_text()
        link = item.find_parent('a')['href']
        clean_link = clean_google_report_link(link)
        reports.append({'title': title, 'link': clean_link})

    return reports

def clean_google_report_link(link):
    # Extract the clean URL from the Google search result link
    clean_link = link.split('q=')[1].split('&sa=')[0]
    return clean_link

def format_currency(value):
    if value == 'N/A':
        return value
    else:
        return f"${value:,.2f}"

# Function to format percentage values
def format_percentage(value):
    if value == 'N/A':
        return value
    else:
        return f"{value:.2f}%"

# Function to fetch stock data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    data = {
        'Name': info.get('shortName', 'N/A'),

        'Previous Close': format_currency(info.get('previousClose', 'N/A')),
        'Market Cap': format_currency(info.get('marketCap', 'N/A')),
        'Open Price': format_currency(info.get('regularMarketOpen', 'N/A')),
        'Average Price': format_currency(info.get('regularMarketPrice', 'N/A')),
        'Beta (1 year)': info.get('beta', 'N/A'),
        'Bid Price': format_currency(info.get('bid', 'N/A')),
        'Ask Price': format_currency(info.get('ask', 'N/A')),
        'PE Ratio (TTM)': info.get('trailingPE', 'N/A'),
        'EPS (TTM)': format_currency(info.get('trailingEps', 'N/A')),
        "Day's Range": format_currency(info.get('dayLow', 'N/A')) + ' - ' + format_currency(info.get('dayHigh', 'N/A')),
        '52 Week Range': format_currency(info.get('fiftyTwoWeekLow', 'N/A')) + ' - ' + format_currency(info.get('fiftyTwoWeekHigh', 'N/A')),
        '1 Year Target': format_currency(info.get('targetMeanPrice', 'N/A')),
        '52 Week Change (%)': format_percentage(info.get('52WeekChange', 'N/A')),
        'Earnings Date': info.get('earningsDate', 'N/A'),
        'Forward Dividend': format_currency(info.get('forwardDividendRate', 'N/A')),
        'Dividend Yield': format_percentage(info.get('dividendYield', 'N/A')),
        'Volume': info.get('volume', 'N/A'),
        'Ex-Dividend Date': info.get('exDividendDate', 'N/A'),
        'Enterprise Value': format_currency(info.get('enterpriseValue', 'N/A')),
        'Price/Earnings Ratio (Trailing)': info.get('trailingPE', 'N/A'),
        'Price/Earnings Ratio (Forward)': info.get('forwardPE', 'N/A'),
        'PEG Ratio': info.get('pegRatio', 'N/A'),
        'Price/Sales Ratio': info.get('priceToSalesTrailing12Months', 'N/A'),
        'Price/Book Ratio': info.get('priceToBook', 'N/A'),
        '50-Day Moving Average': format_currency(info.get('fiftyDayAverage', 'N/A')),
        '200-Day Moving Average': format_currency(info.get('twoHundredDayAverage', 'N/A')),
        'Enterprise Value/EBITDA': format_currency(info.get('enterpriseToEbitda', 'N/A')),
        'Profit Margin': format_percentage(info.get('profitMargins', 'N/A')),
        'Operating Margin': format_percentage(info.get('operatingMargins', 'N/A')),
        'Return on Assets': format_percentage(info.get('returnOnAssets', 'N/A')),
        'Return on Equity': format_percentage(info.get('returnOnEquity', 'N/A')),
        'Revenue': format_currency(info.get('totalRevenue', 'N/A')),
        'Revenue per Share': format_currency(info.get('revenuePerShare', 'N/A')),
        'Quarterly Revenue Growth': format_percentage(info.get('quarterlyRevenueGrowth', 'N/A')),
        'Gross Profit': format_currency(info.get('grossProfit', 'N/A')),
        'EBITDA': format_currency(info.get('ebitda', 'N/A')),
        'Diluted EPS': format_currency(info.get('trailingEps', 'N/A')),
        'Quarterly Earnings Growth': format_percentage(info.get('earningsQuarterlyGrowth', 'N/A')),
        'Total Cash (MRQ)': format_currency(info.get('totalCash', 'N/A')),
        'Total Cash Per Share (MRQ)': format_currency(info.get('totalCashPerShare', 'N/A')),
        'Total Debt (MRQ)': format_currency(info.get('totalDebt', 'N/A')),
        'Current Ratio (MRQ)': info.get('currentRatio', 'N/A'),
        'Book Value Per Share (MRQ)': format_currency(info.get('bookValue', 'N/A')),
        'Operating Cash Flow (TTM)': format_currency(info.get('operatingCashflow', 'N/A')),
        'Levered Free Cash Flow (TTM)': format_currency(info.get('freeCashflow', 'N/A')),
        'Share Statistics': format_currency(info.get('sharesOutstanding', 'N/A')),
        'Dividends & Splits': info.get('dividendsAndSplits', 'N/A'),
        'About Company': info.get('longBusinessSummary', 'N/A'),

    }
    return data

# Function to fetch historical stock data
def get_stock_data_history(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period='20y')
    return data

# Main function to run the app
def main():
    st.set_page_config(page_title='Stock Analysis App', layout="wide")

    # Custom CSS to set font to Times New Roman
    st.markdown(
        """
        <style>
        body {
            font-family: 'Times New Roman', Times, serif;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title('Single Stock Data')
    st.sidebar.title('Search')

    # Get user input for ticker symbols
    available_tickers = ["6599.KL","5099.KL","7579.KL","7162.KL","6432.KL","5014.KL","4162.KL","6947.KL","1023.KL","6012.KL","1066.KL","7113.KL","7052.KL","5347.KL","5101.KL","4707.KL","1295.KL","1155.KL","7164.KL","5218.KL","2445.KL","1619.KL","1171.KL","5216.KL","7277.KL","5141.KL","3026.KL","9806.KL","7773.KL","7206.KL","7182.KL","5227.KL","5176.KL","0820EA.KL","0138.KL","7107.KL","6939.KL","3689.KL","3522.KL","0128.KL","5398.KL","4715.KL","7088.KL","5199.KL","9997.KL","9679.KL","9385.KL","8362.KL","7323.KL","7293.KL","7235.KL","7121.KL","7110.KL","6351.KL","5819.KL","5260.KL","5252.KL","5236.KL","5156.KL","5095.KL","5080.KL","3301.KL","9598.KL","5161.KL","9083.KL","8648.KL","7223.KL","7152@BN.KL","7043.KL","6556@BN.KL","3522@BN.KL","8923@BN.KL","0024@BN.KL","9431.KL","5268.KL","8931.KL","4723.KL","5268@BN.KL","0058.KL","3441.KL","4383@BN.KL","7152.KL","2453.KL","9954.KL","9466.KL","8303.KL","7216.KL","7153.KL","7130.KL","6874.KL","6572.KL","5878.KL","5843.KL","5192.KL","5172.KL","5171.KL","5060.KL","5027.KL","3565.KL","3476.KL","3204.KL","3115.KL","0170.KL","5235SS.KL","5123.KL","8966.KL","7171.KL","5049.KL","4502.KL","1589.KL","6009.KL","7243.KL","7204.KL","5201@BN.KL","5201.KL","5159.KL","5126.KL","5065.KL","0172.KL","0040.KL","5255.KL","5243@BN.KL","0040@BN.KL","0053@BN.KL","3417.KL","7084.KL","7544@OM.KL","7544.KL","7084@BN.KL","7219.KL","4324.KL","3042.KL","5222.KL","0097.KL","0069.KL","0066@BN.KL","5049@BN.KL","0083.KL","5021.KL","8206.KL","7245.KL","5142.KL","5007.KL","4243.KL","0008.KL","7374.KL","9601@BN.KL","7203.KL","2976.KL","5098@BN.KL","1589@BN.KL","5260@DB.KL","8206@BN.KL","0103.KL","7226.KL","5007@BN.KL","5188@BN.KL","5238.KL","5267.KL","5156@BN.KL","0095.KL","0165.KL","5155.KL","5155@OM.KL","0165@BN.KL","5238@BN.KL","0095@BN.KL","5267@BN.KL","7184.KL","7178@BN.KL","7122@BN.KL","7066.KL","7003.KL","6742.KL","5584.KL","5048@BN.KL","4677.KL","2577.KL","0086.KL","4677@BN.KL","5048.KL","7020.KL","6742@BN.KL","7178.KL","0086@BN.KL","5062@BN.KL","0009.KL","7066@BN.KL","7003@BN.KL","3158@BN.KL","2577@BN.KL","7122.KL","5584@BN.KL","3158.KL","5159@BN.KL","5173.KL","5109.KL","7014.KL","7293@BN.KL","5062.KL","7028.KL","2283.KL","7078.KL","5131.KL","5131@BN.KL","2283@BN.KL","7028@BN.KL","7086.KL","5198.KL","7061@BN.KL","7086@BN.KL","0800EA.KL","7061.KL","0800EA@OM.KL","5198@BN.KL","7061@OM.KL","7120@BN.KL","5924.KL","5134.KL","7120.KL","7131.KL","5924@BN.KL","7191.KL","9148@BN.KL","0122@BN.KL","9148.KL","0122.KL","5139@BN.KL","5139.KL","7146.KL","0181.KL","6599@BN.KL","0181@BN.KL","5185.KL","5185@BN.KL","7315@BN.KL","7315.KL","5099@BN.KL","5014@BN.KL","7609.KL","2658@BN.KL","2658.KL","9326.KL","5115.KL","2488.KL","1163.KL","9814.KL","5116@BN.KL","5115@BN.KL","2674.KL","5116.KL","1163PA.KL","2488@BN.KL","1163@BN.KL","9326@BN.KL","5269.KL","0036.KL","5120@BN.KL","1015.KL","0166.KL","7051.KL","5127.KL","1007@BN.KL","1007.KL","5127@BN.KL","1015@BN.KL","5120.KL","1007PA.KL","2682.KL","4952@BN.KL","4162@BN.KL","7031@BN.KL","7031.KL","4952.KL","0166@BN.KL","7083.KL","3255.KL","0048.KL","4758.KL","5012@BN.KL","3255@BN.KL","9342.KL","5186@BN.KL","6556.KL","5012.KL","0048@BN.KL","5186.KL","4758@BN.KL","5194.KL","5088.KL","6432@BN.KL","5015@BN.KL","7090@BN.KL","5015.KL","7090.KL","0119.KL","5568.KL","5088@BN.KL","5226.KL","5226@BN.KL","0098@BN.KL","0098.KL","5210.KL","5210@BN.KL","7007.KL","7986.KL","6399.KL","7722.KL","0152.KL","7070@BN.KL","3239@BN.KL","0039@OM.KL","9954@BN.KL","0039.KL","7070.KL","0176@DB.KL","0822EA.KL","5166.KL","0173.KL","7054.KL","0152@BN.KL","0039@BN.KL","0135.KL","7162@BN.KL","7054@BN.KL","0105.KL","7129.KL","0176.KL","0150.KL","0135@BN.KL","7986@BN.KL","4057@BN.KL","0068.KL","0150@BN.KL","0143.KL","0826EA.KL","4057.KL","5166@BN.KL","7722@BN.KL","6399@BN.KL","0173@BN.KL","0159.KL","3239.KL","0159@BN.KL","7129@BN.KL","7048.KL","5130.KL","0072.KL","7099.KL","7181.KL","0072@BN.KL","5248.KL","5229.KL","7579@BN.KL","6888.KL","6888@BN.KL","5106@BN.KL","5106.KL","5021@BN.KL","2569.KL","2569@BN.KL","1295@BN.KL","7251@BN.KL","6602.KL","7165.KL","6114.KL","5263.KL","5251.KL","3743.KL","8613.KL","7595.KL","7253.KL","7249.KL","7237.KL","7214.KL","7213.KL","7211.KL","7207.KL","7186.KL","7108.KL","7105.KL","7079.KL","6262@BN.KL","6149.KL","5265.KL","5256.KL","5250.KL","5241.KL","5239.KL","5228.KL","5211.KL","5205.KL","5202.KL","5140.KL","5136.KL","5133.KL","5129.KL","5113.KL","5108.KL","5107.KL","5105.KL","4731.KL","4022.KL","2291.KL","1538.KL","1198.KL","0149@BN.KL","0081.KL","0055@BN.KL","0045.KL","0034.KL","5265@BN.KL","5219@BN.KL","7143@OM.KL","5190@BN.KL","4022@BN.KL","0154.KL","7889@BN.KL","5152.KL","2291@BN.KL","0180.KL","0161.KL","8419.KL","0074.KL","5211@BN.KL","4219.KL","5264.KL","8613@BN.KL","5149.KL","9474.KL","5157.KL","5254.KL","5237.KL","9776.KL","5149@BN.KL","7233.KL","0112@BN.KL","0158@BN.KL","5162@BN.KL","7212@BN.KL","5082@OM.KL","8532.KL","2259@BN.KL","5191.KL","5232.KL","0167@OM.KL","5253.KL","0116.KL","5208@BN.KL","6012@BN.KL","0056.KL","7161.KL","5160@BN.KL","5606PA.KL","0041.KL","5184@BN.KL","5184.KL","0118@BN.KL","5196.KL","2127.KL","0170@BN.KL","0112.KL","5219.KL","5216@BN.KL","0161@BN.KL","7168@BN.KL","3069OR.KL","5250@BN.KL","0156@BN.KL","5230.KL","5213@BN.KL","7137@OM.KL","0055.KL","0156.KL","5259@DB.KL","0060.KL","7079@BN.KL","9741@BN.KL","5835PA.KL","5204@BN.KL","5148@BN.KL","5182.KL","0123.KL","1058@OM.KL","4456@BN.KL","3794@BN.KL","0104.KL","9806@OM.KL","1198@BN.KL","3859.KL","5183.KL","9474@BN.KL","5200@BN.KL","5237@BN.KL","4715@BN.KL","2542@OM.KL","5208.KL","5189.KL","0080@BN.KL","7206PB.KL","9628.KL","5797@BN.KL","5167.KL","5078@BN.KL","0154@BN.KL","7240.KL","7206@BN.KL","0118.KL","0169@BN.KL","5242.KL","0034@BN.KL","1058.KL","7163@OM.KL","7149@OM.KL","9741.KL","7889.KL","5220.KL","3743@BN.KL","5197.KL","9458.KL","5213.KL","5249.KL","7246.KL","5078.KL","5401@BN.KL","5205@BN.KL","5181.KL","5225.KL","5195.KL","1368.KL","4723@BN.KL","7215.KL","5170.KL","5220@BN.KL","5241@BN.KL","5245.KL","7230.KL","4456.KL","5247.KL","5195@BN.KL","7229.KL","0178@BN.KL","5112.KL","5175.KL","7134.KL","5249@BN.KL","5094@BN.KL","0163.KL","0149.KL","3379PA.KL","2143@OM.KL","7105@BN.KL","4448P.KL","9377@OM.KL","0151.KL","5148.KL","5175@BN.KL","1147.KL","1023@BN.KL","7108@BN.KL","5401.KL","5228OR.KL","0157.KL","5161@BN.KL","7182@BN.KL","5274@BN.KL","5259.KL","9458@BN.KL","0167@BN.KL","5257.KL","5234.KL","3395.KL","7204@BN.KL","3794.KL","0045@BN.KL","5132.KL","5606PA@OM.KL","0081@BN.KL","2003@OM.KL","5171@BN.KL","0179@BN.KL","5246.KL","7029.KL","5274.KL","0069@BN.KL","7239.KL","5232@BN.KL","6769.KL","0140@BN.KL","5178.KL","0172@BN.KL","1147@BN.KL","0179.KL","5162.KL","5202@BN.KL","5209@BN.KL","6084@BN.KL","0104@BN.KL","5152@BN.KL","5273.KL","5264@BN.KL","0158.KL","5151.KL","0041@BN.KL","7222.KL","0066.KL","4731@BN.KL","7227.KL","7676@BN.KL","5146@BN.KL","1902@BN.KL","5168.KL","5263@BN.KL","0080.KL","5270.KL","7253@BN.KL","7073.KL","5170@BN.KL","9288.KL","8567.KL","7157.KL","7087.KL","7022.KL","6033.KL","5087.KL","5085.KL","4863.KL","2925.KL","2836.KL","1961.KL","0137.KL","9946.KL","9571.KL","9261.KL","8885.KL","8877@BN.KL","8877.KL","8745.KL","8591.KL","8583.KL","8494.KL","8478.KL","8346.KL","8311.KL","7811.KL","7765.KL","7668.KL","7247.KL","7241.KL","7225@BN.KL","7218.KL","7210.KL","7208.KL","7202.KL","7200@BN.KL","7183.KL","7174@BN.KL","7155.KL","7148.KL","7139.KL","7132.KL","7126.KL","7123.KL","7114.KL","7110@OM.KL","7091.KL","7089.KL","7085.KL","7082@BN.KL","7082.KL","7081.KL","7060.KL","7045.KL","7034.KL","7022@BN.KL","7018@BN.KL","7016.KL","7002.KL","6459.KL","6181.KL","5959.KL","5932.KL","5738.KL","5703.KL","5681.KL","5673.KL","5665.KL","5614.KL","5592.KL","5576.KL","5517.KL","5509.KL","5147@OM.KL","5141@BN.KL","5092@BN.KL","5092.KL","5084.KL","5082.KL","5041.KL","5024.KL","5018.KL","5006.KL","5001.KL","4634.KL","4596.KL","4405.KL","4197.KL","4081.KL","3905.KL","3778.KL","3557.KL","3514.KL","3336.KL","3182.KL","3107.KL","2828.KL","2224.KL","2097.KL","2062.KL","2054.KL","1929.KL","1724.KL","1597.KL","1503.KL","0175.KL","0106.KL","0091.KL","0078.KL","0059.KL","0043.KL","0010@BN.KL","0010.KL","3174.KL","4634@BN.KL","5091@BN.KL","7501@BN.KL","6912.KL","3948.KL","7081@BN.KL","0155@OM.KL","4286.KL","0120@BN.KL","0064.KL","2135.KL","9423.KL","0001.KL","2194.KL","4375@BN.KL","2097@BN.KL","2216.KL","7172@BN.KL","1899@BN.KL","7100.KL","2062@BN.KL","7141.KL","5622@BN.KL","7229@BN.KL","5077.KL","6807.KL","6238@BN.KL","6068.KL","9059@BN.KL","7117@BN.KL","0155.KL","5135@BN.KL","7106@BN.KL","5026@BN.KL","7114@BN.KL","7248@BN.KL","5754.KL","7106.KL","3662.KL","2836@BN.KL","5231.KL","9369.KL","7239@BN.KL","0029.KL","6203.KL","4243@BN.KL","0082@BN.KL","8079@BN.KL","5056.KL","5000.KL","0022@BN.KL","7218@OM.KL","5009@OM.KL","0049@BN.KL","1899.KL","8486.KL","5133@BN.KL","3298@BN.KL","3913.KL","7528@BN.KL","7160.KL","7197@BN.KL","3557@BN.KL","5054.KL","6904.KL","0083@BN.KL","5126@BN.KL","0103@BN.KL","3581@BN.KL","5168@BN.KL","8494@BN.KL","0091@BN.KL","9199@BN.KL","4464@BN.KL","6718@BN.KL","4359.KL","5258.KL","0102@BN.KL","7111.KL","9393.KL","5207@BN.KL","5079.KL","0007.KL","0084.KL","0168.KL","7172.KL","7179.KL","0043@BN.KL","0032.KL","7096@BN.KL","7137@BN.KL","5592@BN.KL","7158.KL","5073@BN.KL","0132@BN.KL","9334.KL","5035@BN.KL","5054@BN.KL","7139@BN.KL","3913@BN.KL","5789@BN.KL","5517@BN.KL","0021@BN.KL","8567@BN.KL","5606@BN.KL","9113.KL","7154.KL","4588@BN.KL","7191@BN.KL","8524.KL","7176.KL","3042@BN.KL","0026@BN.KL","7062.KL","8664.KL","9962@BN.KL","2453@BN.KL","6874@BN.KL","3026@BN.KL","5223.KL","5703@BN.KL","0175@DB.KL","3247@BN.KL","6521@BN.KL","5983@BN.KL","4936@OM.KL","7137.KL","5020.KL","0005.KL","4995@BN.KL","7163@BN.KL","7113@BN.KL","5112@BN.KL","6718.KL","5147.KL","8761.KL","5932@BN.KL","8893.KL","0102.KL","6076.KL","5125@BN.KL","8141@BN.KL","7013.KL","7005.KL","7173.KL","7219@BN.KL","2038.KL","5071.KL","0109@BN.KL","0168@BN.KL","2542.KL","0109.KL","9342@BN.KL","0050@BN.KL","5025.KL","5036.KL","7232.KL","8141PA.KL","9091.KL","7197.KL","2194@BN.KL","4006@BN.KL","7077.KL","3921.KL","8907.KL","0174@BN.KL","7205@BN.KL","5258@BN.KL","5105@BN.KL","7205.KL","4847.KL","6041.KL","7803.KL","5024@BN.KL","7173@BN.KL","0111.KL","3204@BN.KL","9873.KL","5037@BN.KL","0090.KL","0006@BN.KL","2224@BN.KL","5040@BN.KL","8982@BN.KL","5101@BN.KL","0108.KL","7199.KL","3417@BN.KL","4448@BN.KL","5649.KL","5005@BN.KL","0101@BN.KL","5183@BN.KL","9539.KL","7187.KL","5027@BN.KL","6076@BN.KL","7200.KL","7170.KL","5146.KL","5068.KL","3301@BN.KL","2828@BN.KL","0020@BN.KL","8044.KL","0174.KL","7247@BN.KL","5028.KL","0028.KL","7133@BN.KL","7180.KL","5065@BN.KL","7060@BN.KL","7854.KL","9334@BN.KL","3174@BN.KL","5000@BN.KL","7174.KL","7323@BN.KL","6971.KL","7128.KL","9407.KL","4375.KL","4944.KL","2429@BN.KL","7179@BN.KL","7085@BN.KL","6211@BN.KL","7208@BN.KL","0012@BN.KL","7528.KL","0094@BN.KL","5673@BN.KL","7193.KL","7277@BN.KL","2208@BN.KL","7227@BN.KL","5355.KL","2593.KL","8869@BN.KL","8761@BN.KL","6483@BN.KL","7213@BN.KL","2208.KL","5100.KL","7006.KL","7199@BN.KL","3573@BN.KL","5010.KL","0120.KL","1201@BN.KL","2135@BN.KL","0021.KL","8907@BN.KL","7017@BN.KL","0020.KL","8834@BN.KL","2968.KL","7773@BN.KL","7133.KL","9687.KL","9121@BN.KL","5657@BN.KL","0022.KL","6173.KL","5242@BN.KL","3247.KL","9997@BN.KL","1066@BN.KL","0051.KL","9792.KL","9792@BN.KL","7198@BN.KL","5028@BN.KL","5032.KL","5020@BN.KL","0110.KL","7103.KL","8192@BN.KL","7164@BN.KL","3514@BN.KL","7123@BN.KL","4286@BN.KL","1643@BN.KL","0059@BN.KL","4316@BN.KL","1082.KL","8141.KL","7221.KL","7033@BN.KL","2887@BN.KL","7160@BN.KL","2089@BN.KL","5053.KL","0101.KL","0037@BN.KL","7617.KL","8338.KL","2771.KL","0092@BN.KL","8443.KL","8745@BN.KL","3441@BN.KL","9881.KL","2445@BN.KL","7100@BN.KL","6033@BN.KL","0079.KL","7099@BN.KL","7223@BN.KL","0064@BN.KL","9717@BN.KL","7183@BN.KL","7080.KL","0136@BN.KL","5026.KL","8966@BN.KL","6139.KL","5253@DB.KL","0026.KL","3476@BN.KL","2054@BN.KL","5132@BN.KL","0075.KL","0126.KL","5236@BN.KL","5080@BN.KL","7095.KL","1694.KL","6254.KL","0007@BN.KL","6254@BN.KL","5145.KL","5100@BN.KL","0094.KL","7025.KL","7285@BN.KL","7053.KL","5069.KL","4596@BN.KL","9962.KL","8621.KL","5095@BN.KL","5047.KL","0128@BN.KL","7412.KL","7134@BN.KL","5072.KL","7111@BN.KL","4898.KL","2887.KL","9237@BN.KL","3034@BN.KL","0155@BN.KL","7943.KL","9938.KL","2143@BN.KL","7188@BN.KL","7089@BN.KL","1996@BN.KL","6548.KL","5711.KL","7094.KL","8931@BN.KL","0011.KL","2852.KL","7366.KL","5016@BN.KL","5819@BN.KL","7155@BN.KL","7027.KL","7025@BN.KL","8192.KL","5073.KL","4707@BN.KL","5113@BN.KL","9288@BN.KL","6238.KL","2593@BN.KL","7119.KL","8362@BN.KL","7010.KL","8869.KL","5878@BN.KL","7143.KL","3883@BN.KL","9393@BN.KL","3115@BN.KL","6491@BN.KL","9539@OM.KL","4995.KL","5071@BN.KL","0141.KL","7033.KL","5079@BN.KL","7218@BN.KL","0136.KL","7233@BN.KL","6459@BN.KL","1597@BN.KL","5371@BN.KL","7190.KL","3484.KL","5222@BN.KL","9407@BN.KL","5827.KL","0111@BN.KL","5606.KL","5102.KL","7207@BN.KL","9318@BN.KL","3034.KL","8478@BN.KL","6815.KL","0089.KL","5143.KL","7017@OM.KL","0032@BN.KL","0148.KL","7045@BN.KL","7006@BN.KL","0099.KL","5098.KL","1287.KL","0132.KL","3573.KL","5091.KL","7153@BN.KL","0100.KL","1929@BN.KL","2186.KL","3298.KL","6491.KL","5622.KL","7149.KL","5533@BN.KL","9199.KL","7055.KL","5614@BN.KL","7161@BN.KL","5347@BN.KL","0160@BN.KL","7188.KL","5158@BN.KL","8044@BN.KL","7439.KL","0160.KL","7935.KL","4936@BN.KL","3662@BN.KL","7668@BN.KL","1724@BN.KL","0022@OM.KL","7087@BN.KL","5040.KL","5053@BN.KL","5959@BN.KL","7211@BN.KL","0113.KL","0146@OM.KL","3018.KL","5886.KL","6297@BN.KL","5135.KL","0037.KL","5011.KL","5008.KL","3689@BN.KL","5005.KL","6637.KL","7052@BN.KL","5657.KL","6963@BN.KL","0070@BN.KL","7180@BN.KL","5087@BN.KL","7149@BN.KL","0065@BN.KL","3565@BN.KL","7501.KL","4502@BN.KL","7209@BN.KL","2739.KL","0001@BN.KL","4588.KL","9237.KL","0035.KL","6963.KL","7228.KL","3816.KL","5037.KL","7617@BN.KL","4219@BN.KL","6017@BN.KL","0147.KL","9008.KL","8583@BN.KL","9261@BN.KL","6297.KL","0038.KL","4006.KL","0092.KL","0138@BN.KL","7096.KL","7167@BN.KL","1783.KL","6998.KL","8834.KL","5035.KL","5835.KL","7189.KL","0023.KL","3336@BN.KL","8664@BN.KL","5142@BN.KL","5041@BN.KL","5145@BN.KL","4316.KL","0065.KL","2216@BN.KL","7226@BN.KL","2755.KL","8486@BN.KL","5231@BN.KL","3379@BN.KL","6139@BN.KL","7036@BN.KL","1171@BN.KL","0085.KL","5029.KL","9601.KL","5072@BN.KL","7047@BN.KL","9717.KL","3611@BN.KL","7145.KL","7216@BN.KL","8885@BN.KL","8338@BN.KL","0049.KL","7811@BN.KL","7036.KL","5009.KL","6181@BN.KL","5533.KL","5056@BN.KL","7201.KL","0029@BN.KL","7241@BN.KL","5252@DB.KL","7285.KL","0127@BN.KL","0133.KL","5038@BN.KL","5060@BN.KL","8117.KL","7231@BN.KL","3581.KL","7366@BN.KL","3948@BN.KL","0127.KL","0145.KL","4936.KL","0082.KL","5797.KL","5070@BN.KL","9091@BN.KL","7059.KL","4065.KL","7215@BN.KL","5125.KL","6009@BN.KL","7228@BN.KL","4065@BN.KL","7246@BN.KL","5096.KL","0050.KL","3395@BN.KL","9938@BN.KL","0025.KL","8273@BN.KL","0133@BN.KL","5681@BN.KL","0035@BN.KL","4383.KL","3905@BN.KL","0129.KL","7167.KL","7034@BN.KL","2739@BN.KL","9318.KL","7117.KL","6483.KL","4197@BN.KL","5075.KL","7250@BN.KL","5042.KL","5077@BN.KL","3069.KL","9865.KL","4847@BN.KL","6661.KL","7013@BN.KL","0099@BN.KL","3891.KL","5398@BN.KL","6173@BN.KL","5008@BN.KL","5085@BN.KL","7017.KL","0141@BN.KL","8311@BN.KL","8893@BN.KL","5355@BN.KL","2003.KL","0060@BN.KL","6378.KL","6211.KL","9059.KL","0038@BN.KL","0028@BN.KL","2305.KL","5070.KL","1818@BN.KL","6017.KL","5031.KL","0006.KL","1996.KL","5200.KL","4898@BN.KL","5102@BN.KL","8982.KL","3891@BN.KL","8346@BN.KL","7217.KL","3816@BN.KL","2755@BN.KL","7757.KL","5010@BN.KL","5207.KL","5001@BN.KL","5066.KL","4863@BN.KL","0100@BN.KL","5199@BN.KL","5038.KL","5107@BN.KL","5084@BN.KL","4324@BN.KL","1155@BN.KL","3069@BN.KL","8702.KL","1481.KL","1082@BN.KL","3182@BN.KL","2771@BN.KL","2143.KL","6815@BN.KL","2089.KL","1481@BN.KL","3883.KL","7018.KL","5031@BN.KL","0070.KL","6947@BN.KL","0084@BN.KL","0171.KL","7097.KL","7047.KL","9296.KL","5165.KL","6637@BN.KL","1643.KL","5011@BN.KL","0053.KL","7140.KL","5138.KL","9113@BN.KL","3018@BN.KL","9776@BN.KL","1201.KL","7757@BN.KL","7234.KL","8591@BN.KL","6521.KL","0058@BN.KL","7231.KL","0054.KL","0146.KL","1562@BN.KL","8273.KL","2542@BN.KL","0012.KL","7158@BN.KL","7145@BN.KL","7080@BN.KL","7115.KL","0023@BN.KL","7773@OM.KL","7140@BN.KL","7126@BN.KL","7095@BN.KL","3611.KL","9016.KL","2429.KL","7692.KL","8079.KL","5094.KL","7412@BN.KL","7195.KL","6971@BN.KL","0008@BN.KL","7071@BN.KL","1619@BN.KL","5022.KL","0005@BN.KL","7035@BN.KL","4944@BN.KL","5371.KL","9598@BN.KL","7692@BN.KL","5032@BN.KL","0054@BN.KL","9377.KL","1562.KL","7035.KL","7198.KL","5068@BN.KL","0002.KL","9571@BN.KL","5576@BN.KL","4081@BN.KL","4464.KL","9121.KL","3484@BN.KL","3921@BN.KL","6025.KL","5143@BN.KL","7471@BN.KL","0011@BN.KL","5789.KL","4448.KL","5081@OM.KL","7195@BN.KL","8443@BN.KL","4405@BN.KL","7169.KL","2852@BN.KL","7163.KL","1287@BN.KL","5983.KL","5104.KL","8621@BN.KL","5016.KL","3379.KL","9466@BN.KL","7471.KL","7498.KL","5214.KL","5150.KL","5229@BN.KL","5214@BN.KL","5090.KL","8133.KL","8133@BN.KL","1818.KL","5257@DB.KL","7076.KL","7076@BN.KL","8052.KL","0823EA@OM.KL","7209@OM.KL","0823EA.KL","5234@BN.KL","8125.KL","8176.KL","0824EA.KL","0131.KL","0825EA.KL","0824EA@OM.KL","0821EA.KL","5908@BN.KL","5908.KL","0116@BN.KL","0107.KL","5036@OM.KL","0107@BN.KL","1368@BN.KL","9075.KL","7004.KL","7004@BN.KL","8435@BN.KL","9822.KL","9822@BN.KL","5212.KL","5121.KL","5111.KL","5176@BN.KL","5081.KL","5110.KL","5227@BN.KL","5212@BN.KL","7249@BN.KL","9806@BN.KL","2984.KL","2984@BN.KL","8605.KL","7107@BN.KL","9172.KL","9172@BN.KL","5196@BN.KL","5243.KL","5209.KL","2607.KL","5187.KL","5158.KL","2127@BN.KL","7192.KL","7382.KL","7676.KL","5138@BN.KL","5225@BN.KL","8397.KL","7088@BN.KL","5169@BN.KL","5169.KL","5169PA.KL","5169PB.KL","6688.KL","5255@DB.KL","0162.KL","7201@BN.KL","0024.KL","2747.KL","8923.KL","6769@BN.KL","8672@BN.KL","8672.KL","2607@BN.KL","5247@BN.KL","6645.KL","5843@BN.KL","5191@BN.KL","5239@BN.KL","4235.KL","4235@BN.KL","8397@BN.KL","8095.KL","5916.KL","1651.KL","5180@BN.KL","1651@BN.KL","5916@BN.KL","5189@BN.KL","5180.KL","3867@BN.KL","3719.KL","0167.KL","5182@BN.KL","6114@OM.KL","5237@OM.KL","5123@BN.KL","5436.KL","3719@BN.KL","5436@BN.KL","0117.KL","0177.KL","6262.KL","4251.KL","0047@BN.KL","9695.KL","7050.KL","0017@BN.KL","5160.KL","3867.KL","0047.KL","4251@BN.KL","8435.KL","7050@BN.KL","0074@BN.KL","0096.KL","2879.KL","7251.KL","0018.KL","5188.KL","0153.KL","5245@BN.KL","1902.KL","7237@BN.KL","5272.KL","7248.KL","0117@BN.KL","0169.KL","0093@BN.KL","6084.KL","0140.KL","7186@BN.KL","1538@BN.KL","2976@BN.KL","2259.KL","7250.KL","9679@BN.KL","5246@BN.KL","5248@BN.KL","5190.KL","7212.KL","3859@BN.KL","7225.KL","7168.KL","5204.KL","5163.KL","7073@BN.KL","0177@BN.KL","7252.KL","7209.KL","3395OA.KL","0178.KL","7071.KL","8176@BN.KL","0093.KL","0017.KL"]

    # Get user input
    input_text = st.sidebar.text_input('Enter first three letters of the stock ticker:')
    selected_tickers = st.sidebar.multiselect('Select Tickers', available_tickers)


    for ticker in selected_tickers:
        if st.sidebar.button(f'Get Analysis for {ticker}'):
            # Display interactive chart
            st.subheader(f'Interactive Chart for {ticker}')

            stock_history = get_stock_data_history(ticker)

            # Calculate technical indicators
            sma_50 = SMAIndicator(close=stock_history['Close'], window=50).sma_indicator()
            sma_200 = SMAIndicator(close=stock_history['Close'], window=200).sma_indicator()
            rsi = RSIIndicator(close=stock_history['Close']).rsi()

            # Create candlestick trace
            candlestick = go.Candlestick(x=stock_history.index,
                                         open=stock_history['Open'],
                                         high=stock_history['High'],
                                         low=stock_history['Low'],
                                         close=stock_history['Close'],
                                         name='Candlestick')

            # Create SMA 50 and SMA 200 traces
            sma_50_trace = go.Scatter(x=stock_history.index, y=sma_50, mode='lines', name='SMA 50', line=dict(color='orange'))
            sma_200_trace = go.Scatter(x=stock_history.index, y=sma_200, mode='lines', name='SMA 200', line=dict(color='red'))

            # Create RSI trace
            rsi_trace = go.Scatter(x=stock_history.index, y=rsi, mode='lines', name='RSI', line=dict(color='green'))

            # Combine traces into data list
            data = [candlestick, sma_50_trace, sma_200_trace, rsi_trace]

            # Layout settings
            layout = {
                'title': f'{ticker} Interactive Chart',
                'xaxis_title': 'Date',
                'yaxis_title': 'Price',
                'hovermode': 'x unified'
            }

            # Create figure and plot
            fig = go.Figure(data=data, layout=layout)
            st.plotly_chart(fig)

            # Display stock information
            stock_data = get_stock_data(ticker)
            if stock_data:
                st.subheader(f'Stock Information for {ticker}')
                col1, col2 = st.columns(2)

                for key, value in stock_data.items():
                    col1.write(f"**{key}:**")
                    col2.write(value)

                # Display historical prices
                st.subheader(f'Historical Prices for {ticker}')
                st.write("Please consider $ as your local trading currency")
                st.line_chart(stock_history['Close'])

            stock_news = get_stock_news(ticker)
            if stock_news:
                st.subheader(f'Latest News for {ticker}')
                for article in stock_news:
                    st.markdown(f"[{article['title']}]({article['link']})")


            investor_reports = get_investor_reports(ticker)
            if investor_reports:
                st.subheader(f'Latest Investor Report for {ticker}')
                top_investor_report = investor_reports[0]
                st.markdown(f"[{top_investor_report['title']}]({top_investor_report['link']})")

            # Get peer reports
            peer_reports = get_peer_reports(ticker)
            if peer_reports:
                st.subheader(f'Latest Peer Report for {ticker}')
                top_peer_report = peer_reports[0]
                st.markdown(f"[{top_peer_report['title']}]({top_peer_report['link']})")

            trading_decision = get_trading_recommendation(stock_history)
            st.subheader(f'Technical Analysis Recommendation for {ticker}')
            st.write(f"Suggestion: {trading_decision}")


if __name__ == '__main__':
    main()
