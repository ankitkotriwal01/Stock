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
    available_tickers = ["3264.TWO","5489.TWO","3211.TWO","T0502Y.TWO","6210.TWO","1580.TWO","8299.TWO","8076.TWO","6261.TWO","6107.TWO","3452.TWO","8091.TWO","6219.TWO","5426.TWO","5205.TWO","721827.TWO","721663.TWO","6114.TWO","5251.TWO","4502.TWO","3191.TWO","1594.TWO","722527.TWO","72425P.TWO","5701.TWO","3548.TWO","722005.TWO","T2006Y.TWO","721803.TWO","T2003Y.TWO","722025.TWO","722172.TWO","722770.TWO","722528.TWO","4559.TWO","723175.TWO","3322.TWO","721745.TWO","721828.TWO","8418.TWO","722046.TWO","4193.TWO","72480P.TWO","1787.TWO","722604.TWO","6247.TWO","3636.TWO","722690.TWO","5266.TWO","4980.TWO","6540.TWO","4417.TWO","8936.TWO","8406.TWO","6554.TWO","6242.TWO","6238.TWO","4971.TWO","4745.TWO","4157.TWO","3664.TWO","2732.TWO","1256.TWO","722277.TWO","722279.TWO","6125.TWO","722061.TWO","722431.TWO","721910.TWO","5383.TWO","5905.TWO","1565.TWO","5312.TWO","4120.TWO","3363.TWO","3362.TWO","6426.TWO","6233.TWO","8349.TWO","6188.TWO","4736.TWO","3213.TWO","6101.TWO","3218.TWO","4803.TWO","3307.TWO","5347.TWO","8092.TWO","722778.TWO","722331.TWO","5529.TWO","5013.TWO","4953.TWO","4113.TWO","1742.TWO","6259.TWO","721819.TWO","3086.TWO","722760.TWO","3078.TWO","6134.TWO","6170.TWO","8925.TWO","722762.TWO","6118.TWO","3662.TWO","3152.TWO","4922.TWO","3374.TWO","5490.TWO","8942.TWO","4802.TWO","8421.TWO","3171.TWO","5213.TWO","9957.TWO","72346P.TWO","723017.TWO","722968.TWO","722893.TWO","722791.TWO","722732.TWO","722708.TWO","722662.TWO","722586.TWO","722115.TWO","722112.TWO","722054.TWO","721845.TWO","721623.TWO","721622.TWO","721609.TWO","6482.TWO","5508.TWO","5345.TWO","4711.TWO","4533.TWO","3276.TWO","3207.TWO","2235.TWO","72444P.TWO","722665.TWO","T0567Y.TWO","T0508Y.TWO","722731.TWO","722666.TWO","722529.TWO","721949.TWO","722682.TWO","722132.TWO","T0504Y.TWO","721783.TWO","722065.TWO","4703.TWO","721608.TWO","6220.TWO","722895.TWO","721948.TWO","721782.TWO","723273.TWO","723178.TWO","722786.TWO","721798.TWO","72441P.TWO","722593.TWO","721979.TWO","722775.TWO","723274.TWO","722827.TWO","722767.TWO","T0506Y.TWO","721755.TWO","722776.TWO","723038.TWO","6275.TWO","721996.TWO","722885.TWO","721867.TWO","722615.TWO","722788.TWO","722888.TWO","4907.TWO","721869.TWO","722630.TWO","722837.TWO","722934.TWO","722839.TWO","2221.TWO","722494.TWO","722836.TWO","721786.TWO","722561.TWO","722130.TWO","722466.TWO","722021.TWO","2599.TWO","722715.TWO","72353P.TWO","5216.TWO","4734.TWO","722574.TWO","722749.TWO","722944.TWO","722828.TWO","6423.TWO","722842.TWO","722889.TWO","722677.TWO","722942.TWO","722588.TWO","721785.TWO","721946.TWO","722224.TWO","722886.TWO","721884.TWO","9962.TWO","721784.TWO","722589.TWO","72442P.TWO","723275.TWO","722790.TWO","721870.TWO","722225.TWO","723179.TWO","722575.TWO","722743.TWO","721880.TWO","72382P.TWO","722632.TWO","722829.TWO","72473P.TWO","72431P.TWO","721924.TWO","722572.TWO","722970.TWO","721621.TWO","72370P.TWO","721691.TWO","3531.TWO","723077.TWO","722533.TWO","722465.TWO","722711.TWO","722789.TWO","722114.TWO","6124.TWO","2726.TWO","722766.TWO","722531.TWO","722663.TWO","6418.TWO","4430.TWO","722986.TWO","722631.TWO","722709.TWO","8390.TWO","722675.TWO","722053.TWO","722884.TWO","72372P.TWO","721544.TWO","723272.TWO","722113.TWO","722250.TWO","722590.TWO","722710.TWO","721725.TWO","722733.TWO","72443P.TWO","722591.TWO","72499P.TWO","721756.TWO","721670.TWO","72505P.TWO","722240.TWO","4562.TWO","722239.TWO","72310P.TWO","721995.TWO","721883.TWO","5474.TWO","9961.TWO","72478P.TWO","72412P.TWO","4530.TWO","722530.TWO","722787.TWO","72504P.TWO","722177.TWO","722532.TWO","722454.TWO","4102.TWO","721723.TWO","722453.TWO","722519.TWO","722748.TWO","6194.TWO","721818.TWO","721994.TWO","72500P.TWO","722985.TWO","6023.TWO","721669.TWO","72477P.TWO","722576.TWO","721553.TWO","2067.TWO","722614.TWO","8435.TWO","3581.TWO","4544.TWO","3553.TWO","8932.TWO","8176.TWO","4543.TWO","1780.TWO","3628.TWO","6511.TWO","8071.TWO","3236.TWO","8121.TWO","3126.TWO","3492.TWO","5240.TWO","5536.TWO","6403.TWO","8255.TWO","3434.TWO","6455.TWO","5209.TWO","3438.TWO","5491.TWO","3071.TWO","3516.TWO","3260.TWO","8086.TWO","8938.TWO","4160.TWO","5227.TWO","6287.TWO","3564.TWO","1599.TWO","3414.TWO","6507.TWO","4609.TWO","6526.TWO","3615.TWO","3538.TWO","3693.TWO","6174.TWO","8024.TWO","3162.TWO","4553.TWO","4702.TWO","8054.TWO","3627.TWO","4558.TWO","3526.TWO","8478.TWO","6187.TWO","8155.TWO","5386.TWO","5601.TWO","6204.TWO","5272.TWO","8438.TWO","6241.TWO","6411.TWO","3188.TWO","6546.TWO","4760.TWO","5233.TWO","3585.TWO","4188.TWO","3595.TWO","8049.TWO","2241.TWO","6138.TWO","3646.TWO","6276.TWO","3528.TWO","6477.TWO","1259.TWO","6533.TWO","6291.TWO","3587.TWO","5210.TWO","1785.TWO","6560.TWO","8281.TWO","6570.TWO","4908.TWO","3690.TWO","3594.TWO","3217.TWO","6171.TWO","8921.TWO","6432.TWO","4173.TWO","6485.TWO","3169.TWO","3064.TWO","4939.TWO","6240.TWO","6113.TWO","6475.TWO","8038.TWO","5878.TWO","6279.TWO","5274.TWO","4542.TWO","4707.TWO","8082.TWO","4974.TWO","6109.TWO","6465.TWO","6179.TWO","8097.TWO","8074.TWO","6198.TWO","5392.TWO","6103.TWO","4735.TWO","3479.TWO","3597.TWO","3088.TWO","6292.TWO","6530.TWO","6148.TWO","8401.TWO","722883.TWO","6517.TWO","8325.TWO","240602.TWO","3379.TWO","6236.TWO","4726.TWO","4114.TWO","4107.TWO","1784.TWO","4183.TWO","4127.TWO","4154.TWO","4181.TWO","4155.TWO","4911.TWO","4743.TWO","6445.TWO","6458.TWO","4728.TWO","4109.TWO","1258.TWO","3176.TWO","3118.TWO","4161.TWO","8432.TWO","4105.TWO","8933.TWO","1569.TWO","4130.TWO","4740.TWO","4171.TWO","1799.TWO","4195.TWO","3659.TWO","4131.TWO","3566.TWO","4535.TWO","4116.TWO","8433.TWO","4415.TWO","5349.TWO","5863.TWO","3299.TWO","4177.TWO","6472.TWO","6538.TWO","7402.TWO","4556.TWO","8929.TWO","8930.TWO","1816.TWO","4523.TWO","3325.TWO","72369P.TWO","4990.TWO","722440.TWO","72503P.TWO","723063.TWO","722136.TWO","721913.TWO","721709.TWO","722899.TWO","T1612Y.TWO","723268.TWO","72357P.TWO","721857.TWO","72520P.TWO","6217.TWO","3323.TWO","6127.TWO","4123.TWO","5310.TWO","8042.TWO","6022.TWO","5511.TWO","4721.TWO","4205.TWO","1597.TWO","6603.TWO","4546.TWO","6510.TWO","4303.TWO","8923.TWO","5523.TWO","1777.TWO","722810.TWO","6509.TWO","72546P.TWO","8084.TWO","6534.TWO","723040.TWO","722854.TWO","4706.TWO","3345.TWO","5704.TWO","723078.TWO","1586.TWO","4111.TWO","6265.TWO","3631.TWO","4528.TWO","3313.TWO","3310.TWO","3332.TWO","6160.TWO","5864.TWO","5301.TWO","1587.TWO","6527.TWO","4944.TWO","6532.TWO","3377.TWO","3672.TWO","5286.TWO","4744.TWO","6548.TWO","3541.TWO","6566.TWO","5432.TWO","5276.TWO","8437.TWO","3168.TWO","4804.TWO","3521.TWO","5403.TWO","8455.TWO","3657.TWO","3577.TWO","3089.TWO","4716.TWO","9960.TWO","5304.TWO","3671.TWO","2596.TWO","5324.TWO","3252.TWO","6140.TWO","6173.TWO","5609.TWO","1818.TWO","3687.TWO","6180.TWO","4153.TWO","3290.TWO","6523.TWO","T3714Y.TWO","1598.TWO","8351.TWO","4138.TWO","8928.TWO","911613.TWO","8905.TWO","6227.TWO","8409.TWO","3633.TWO","5228.TWO","6425.TWO","3485.TWO","3523.TWO","6462.TWO","3556.TWO","5291.TWO","6211.TWO","3552.TWO","6228.TWO","5317.TWO","8182.TWO","8111.TWO","6245.TWO","4995.TWO","8085.TWO","3297.TWO","8041.TWO","3652.TWO","3128.TWO","5498.TWO","3520.TWO","5381.TWO","6135.TWO","4947.TWO","8289.TWO","6237.TWO","6266.TWO","5395.TWO","4909.TWO","8068.TWO","8171.TWO","T1010Y.TWO","6203.TWO","8487.TWO","3484.TWO","6156.TWO","3268.TWO","3206.TWO","8032.TWO","8287.TWO","3529.TWO","9950.TWO","5299.TWO","1333.TWO","8941.TWO","6126.TWO","3411.TWO","6288.TWO","3707.TWO","3675.TWO","6264.TWO","2926.TWO","5351.TWO","3567.TWO","5506.TWO","3647.TWO","6436.TWO","8934.TWO","6496.TWO","2734.TWO","5903.TWO","5015.TWO","8462.TWO","4513.TWO","T1012Y.TWO","T1001Y.TWO","2748.TWO","2061.TWO","3291.TWO","5859.TWO","4961.TWO","722966.TWO","721844.TWO","722258.TWO","4951.TWO","8913.TWO","722903.TWO","722628.TWO","721912.TWO","3554.TWO","722779.TWO","722051.TWO","721923.TWO","1260.TWO","7443.TWO","3483.TWO","5465.TWO","6298.TWO","4510.TWO","4159.TWO","5514.TWO","8906.TWO","4923.TWO","4207.TWO","4413.TWO","5321.TWO","2641.TWO","T0314Y.TWO","T0313Y.TWO","722504.TWO","721843.TWO","722341.TWO","722627.TWO","722977.TWO","723096.TWO","722746.TWO","722063.TWO","722862.TWO","722433.TWO","4429.TWO","722102.TWO","722507.TWO","72364P.TWO","6024.TWO","8383.TWO","721988.TWO","721658.TWO","722734.TWO","722580.TWO","5102.TWO","722745.TWO","722050.TWO","72319P.TWO","721771.TWO","72363P.TWO","T2501Y.TWO","723016.TWO","722505.TWO","1815.TWO","723097.TWO","722861.TWO","722104.TWO","4402.TWO","723013.TWO","722860.TWO","721657.TWO","721616.TWO","722033.TWO","723056.TWO","2724.TWO","8917.TWO","2916.TWO","5443.TWO","6441.TWO","8908.TWO","3083.TWO","3293.TWO","4991.TWO","6104.TWO","5384.TWO","6479.TWO","6221.TWO","6130.TWO","6026.TWO","3691.TWO","5355.TWO","3610.TWO","5262.TWO","8067.TWO","6151.TWO","4168.TWO","4551.TWO","4187.TWO","4198.TWO","8066.TWO","3428.TWO","6553.TWO","5009.TWO","2636.TWO","5475.TWO","3499.TWO","6481.TWO","3272.TWO","4506.TWO","8472.TWO","4987.TWO","4503.TWO","3178.TWO","6512.TWO","6529.TWO","4730.TWO","3680.TWO","6488.TWO","6218.TWO","3202.TWO","4432.TWO","8354.TWO","6453.TWO","5283.TWO","4175.TWO","8937.TWO","1781.TWO","3658.TWO","1776.TWO","3609.TWO","4139.TWO","3551.TWO","3522.TWO","6190.TWO","T4720Y.TWO","3284.TWO","1268.TWO","5220.TWO","3642.TWO","1788.TWO","6208.TWO","5439.TWO","8446.TWO","722629.TWO","3688.TWO","722493.TWO","722515.TWO","722434.TWO","2730.TWO","6559.TWO","4194.TWO","4406.TWO","4924.TWO","722032.TWO","722863.TWO","722738.TWO","4805.TWO","6487.TWO","6508.TWO","722759.TWO","5328.TWO","722981.TWO","1593.TWO","T1249Y.TWO","722739.TWO","5295.TWO","T1201Y.TWO","722805.TWO","5481.TWO","6163.TWO","5212.TWO","6457.TWO","2897.TWO","8050.TWO","8040.TWO","3372.TWO","3611.TWO","6486.TWO","5438.TWO","3227.TWO","3555.TWO","2035.TWO","1566.TWO","4741.TWO","7421.TWO","3685.TWO","6161.TWO","3147.TWO","722659.TWO","72305P.TWO","722410.TWO","723083.TWO","5820.TWO","4550.TWO","721892.TWO","722500.TWO","721705.TWO","T2005Y.TWO","T2004Y.TWO","722004.TWO","721638.TWO","72498P.TWO","721891.TWO","722409.TWO","722910.TWO","721537.TWO","722268.TWO","3230.TWO","72303P.TWO","722911.TWO","721859.TWO","72496P.TWO","721916.TWO","722619.TWO","722714.TWO","72312P.TWO","722058.TWO","72538P.TWO","6552.TWO","4925.TWO","3629.TWO","4747.TWO","6468.TWO","3543.TWO","5284.TWO","5294.TWO","2063.TWO","2721.TWO","6803.TWO","8107.TWO","722197.TWO","722150.TWO","722193.TWO","722162.TWO","722764.TWO","721769.TWO","722459.TWO","722152.TWO","72371P.TWO","72528P.TWO","722624.TWO","722814.TWO","722427.TWO","72368P.TWO","722929.TWO","722151.TWO","721987.TWO","722235.TWO","72491P.TWO","72335P.TWO","722455.TWO","722432.TWO","721985.TWO","722236.TWO","722984.TWO","72367P.TWO","721842.TWO","722275.TWO","721941.TWO","722156.TWO","72318P.TWO","721686.TWO","72490P.TWO","721595.TWO","723091.TWO","72426P.TWO","722189.TWO","722191.TWO","722696.TWO","72386P.TWO","722270.TWO","721937.TWO","723284.TWO","723286.TWO","72427P.TWO","722931.TWO","722625.TWO","722272.TWO","72385P.TWO","721984.TWO","721983.TWO","722228.TWO","721853.TWO","721655.TWO","72451P.TWO","722460.TWO","722813.TWO","722909.TWO","721840.TWO","722011.TWO","721940.TWO","722962.TWO","722695.TWO","722303.TWO","721935.TWO","722988.TWO","722479.TWO","722100.TWO","722457.TWO","72489P.TWO","722542.TWO","721531.TWO","722716.TWO","721597.TWO","721839.TWO","722274.TWO","722271.TWO","722989.TWO","723090.TWO","722229.TWO","722543.TWO","721855.TWO","722503.TWO","722626.TWO","722752.TWO","72515P.TWO","722157.TWO","722458.TWO","722718.TWO","722234.TWO","721986.TWO","72405P.TWO","721656.TWO","722199.TWO","722987.TWO","723073.TWO","721614.TWO","721767.TWO","722430.TWO","722280.TWO","72428P.TWO","721814.TWO","723092.TWO","721530.TWO","72302P.TWO","722802.TWO","72511P.TWO","722196.TWO","722501.TWO","722502.TWO","72296P.TWO","722983.TWO","722697.TWO","722538.TWO","722694.TWO","722456.TWO","722908.TWO","722960.TWO","722139.TWO","722242.TWO","722195.TWO","723089.TWO","722406.TWO","721770.TWO","723031.TWO","722160.TWO","722539.TWO","722623.TWO","6122.TWO","6516.TWO","3093.TWO","4527.TWO","2639.TWO","5306.TWO","2733.TWO","1757.TWO","1752.TWO","8477.TWO","5206.TWO","8916.TWO","4420.TWO","3287.TWO","1591.TWO","6514.TWO","2738.TWO","4762.TWO","2924.TWO","8426.TWO","8423.TWO","4966.TWO","6541.TWO","8444.TWO","3346.TWO","3068.TWO","5703.TWO","3081.TWO","6207.TWO","8420.TWO","5603.TWO","5410.TWO","5230.TWO","5364.TWO","8127.TWO","8490.TWO","5464.TWO","4972.TWO","1795.TWO","6290.TWO","4401.TWO","4997.TWO","5530.TWO","4979.TWO","5267.TWO","6535.TWO","3527.TWO","721739.TWO","721901.TWO","72550P.TWO","72506P.TWO","722583.TWO","722936.TWO","4541.TWO","722879.TWO","722940.TWO","722412.TWO","722938.TWO","721848.TWO","5902.TWO","722937.TWO","9951.TWO","72439P.TWO","72533P.TWO","722482.TWO","72486P.TWO","722220.TWO","722499.TWO","722581.TWO","72293P.TWO","722780.TWO","722044.TWO","72522P.TWO","721652.TWO","721823.TWO","722568.TWO","723009.TWO","722550.TWO","722824.TWO","723045.TWO","723099.TWO","3563.TWO","722822.TWO","722935.TWO","72547P.TWO","721953.TWO","721778.TWO","3224.TWO","72324P.TWO","721779.TWO","722914.TWO","2064.TWO","721903.TWO","72348P.TWO","721717.TWO","721688.TWO","3294.TWO","721641.TWO","723025.TWO","721957.TWO","721718.TWO","4962.TWO","722980.TWO","722094.TWO","723133.TWO","723006.TWO","723004.TWO","721690.TWO","721902.TWO","722423.TWO","722309.TWO","722480.TWO","721716.TWO","721571.TWO","4419.TWO","3122.TWO","722621.TWO","723005.TWO","2739.TWO","8122.TWO","4128.TWO","3491.TWO","5450.TWO","6244.TWO","4540.TWO","6223.TWO","2740.TWO","3507.TWO","4950.TWO","6407.TWO","5460.TWO","4941.TWO","6547.TWO","5314.TWO","4431.TWO","4712.TWO","4732.TWO","3630.TWO","3558.TWO","6143.TWO","5202.TWO","8147.TWO","8234.TWO","3512.TWO","3317.TWO","3444.TWO","8927.TWO","6542.TWO","6419.TWO","6494.TWO","3066.TWO","6483.TWO","4174.TWO","5011.TWO","2741.TWO","6569.TWO","8044.TWO","8458.TWO","3666.TWO","4166.TWO","3441.TWO","4903.TWO","4933.TWO","4729.TWO","8034.TWO","4129.TWO","723033.TWO","723180.TWO","4554.TWO","8080.TWO","3570.TWO","3097.TWO","3632.TWO","1760.TWO","4965.TWO","5480.TWO","6446.TWO","5211.TWO","6491.TWO","3067.TWO","4180.TWO","6551.TWO","4162.TWO","4191.TWO","8450.TWO","T2520Y.TWO","5248.TWO","6185.TWO","3131.TWO","1570.TWO","5904.TWO","4714.TWO","6105.TWO","6545.TWO","4973.TWO","4529.TWO","6167.TWO","3537.TWO","1813.TWO","8935.TWO","6550.TWO","8109.TWO","3489.TWO","722216.TWO","722217.TWO","723281.TWO","722289.TWO","8053.TWO","721759.TWO","5277.TWO","722307.TWO","722319.TWO","723085.TWO","721893.TWO","8083.TWO","721860.TWO","721747.TWO","722321.TWO","721631.TWO","723280.TWO","6129.TWO","722290.TWO","721932.TWO","721632.TWO","722322.TWO","721593.TWO","722028.TWO","721731.TWO","8924.TWO","721896.TWO","5242.TWO","722680.TWO","3429.TWO","721809.TWO","721757.TWO","721692.TWO","721930.TWO","722317.TWO","722226.TWO","721971.TWO","5238.TWO","8028.TWO","6498.TWO","6489.TWO","5488.TWO","5315.TWO","6568.TWO","2237.TWO","3592.TWO","3373.TWO","3228.TWO","5256.TWO","2743.TWO","5512.TWO","3306.TWO","4121.TWO","6027.TWO","8048.TWO","6186.TWO","5493.TWO","5876.TWO","6195.TWO","5302.TWO","721576.TWO","721802.TWO","722777.TWO","722900.TWO","721698.TWO","722394.TWO","72295P.TWO","72376P.TWO","72446P.TWO","722747.TWO","722871.TWO","723102.TWO","3105.TWO","722667.TWO","722526.TWO","721625.TWO","72320P.TWO","72396P.TWO","3219.TWO","722584.TWO","5425.TWO","722953.TWO","6016.TWO","723086.TWO","722817.TWO","722134.TWO","723278.TWO","723051.TWO","722108.TWO","72468P.TWO","722169.TWO","722522.TWO","722041.TWO","722488.TWO","722263.TWO","722444.TWO","721654.TWO","8410.TWO","722922.TWO","722995.TWO","72337P.TWO","72342P.TWO","721704.TWO","721559.TWO","722448.TWO","723081.TWO","722906.TWO","721915.TWO","6492.TWO","4416.TWO","8485.TWO","4806.TWO","4305.TWO","6506.TWO","8403.TWO","8291.TWO","5455.TWO","5356.TWO","3288.TWO","722640.TWO","722294.TWO","723075.TWO","722783.TWO","722449.TWO","722264.TWO","722099.TWO","721653.TWO","722723.TWO","6435.TWO","722013.TWO","722038.TWO","722120.TWO","722447.TWO","722525.TWO","722785.TWO","722782.TWO","723181.TWO","722875.TWO","721702.TWO","722639.TWO","72352P.TWO","722304.TWO","722679.TWO","722523.TWO","722720.TWO","722097.TWO","722067.TWO","722509.TWO","721754.TWO","721735.TWO","722047.TWO","722486.TWO","722147.TWO","722014.TWO","722947.TWO","722175.TWO","722657.TWO","722218.TWO","722636.TWO","721852.TWO","721700.TWO","T2506Y.TWO","6121.TWO","722951.TWO","3490.TWO","722678.TWO","722991.TWO","721547.TWO","722596.TWO","722721.TWO","721683.TWO","722074.TWO","722820.TWO","722306.TWO","722638.TWO","721826.TWO","72524P.TWO","722471.TWO","722124.TWO","722963.TWO","722876.TWO","722925.TWO","722512.TWO","722418.TWO","721684.TWO","4433.TWO","72316P.TWO","722816.TWO","721761.TWO","723052.TWO","721878.TWO","72397P.TWO","722849.TWO","722118.TWO","722490.TWO","722949.TWO","722992.TWO","721764.TWO","722127.TWO","722489.TWO","721604.TWO","723034.TWO","722149.TWO","722846.TWO","3511.TWO","72445P.TWO","721928.TWO","722176.TWO","721753.TWO","721734.TWO","721821.TWO","722952.TWO","722850.TWO","722125.TWO","721908.TWO","5483.TWO","722305.TWO","721960.TWO","722148.TWO","722773.TWO","723035.TWO","722265.TWO","722446.TWO","72514P.TWO","722844.TWO","721962.TWO","722417.TWO","721605.TWO","722291.TWO","722122.TWO","722145.TWO","721927.TWO","722948.TWO","722656.TWO","721961.TWO","722637.TWO","722598.TWO","721607.TWO","722993.TWO","722511.TWO","721736.TWO","722702.TWO","722173.TWO","72456P.TWO","722098.TWO","721992.TWO","721964.TWO","3466.TWO","6473.TWO","6222.TWO","3259.TWO","3530.TWO","6577.TWO","6111.TWO","5016.TWO","5478.TWO","2643.TWO","6231.TWO","6146.TWO","8431.TWO","5457.TWO","2719.TWO","8266.TWO","8179.TWO","3360.TWO","2066.TWO","3681.TWO","3390.TWO","2720.TWO","4304.TWO","4547.TWO","5516.TWO","6154.TWO","1819.TWO","6490.TWO","5278.TWO","4921.TWO","3289.TWO","8279.TWO","5309.TWO","6123.TWO","6575.TWO","8099.TWO","6558.TWO","4192.TWO","3402.TWO","3150.TWO","2640.TWO","6467.TWO","722994.TWO","6246.TWO","8496.TWO","722797.TWO","722737.TWO","6020.TWO","723269.TWO","4905.TWO","6609.TWO","722736.TWO","5353.TWO","722742.TWO","5520.TWO","6274.TWO","722832.TWO","6549.TWO","722750.TWO","3357.TWO","6428.TWO","3095.TWO","6021.TWO","6434.TWO","8931.TWO","722795.TWO","4152.TWO","1336.TWO","4186.TWO","3221.TWO","8436.TWO","4169.TWO","3339.TWO","8065.TWO","8064.TWO","6284.TWO","4163.TWO","3623.TWO","3073.TWO","5344.TWO","3184.TWO","3684.TWO","3580.TWO","3303.TWO","4738.TWO","2633.TWO","3540.TWO","6567.TWO","3144.TWO","6199.TWO","6536.TWO","9949.TWO","5468.TWO","6248.TWO","4147.TWO","5271.TWO","5487.TWO","1585.TWO","3388.TWO","6556.TWO","3226.TWO","2745.TWO","6521.TWO","TPCGI.TWO","5348.TWO","2230.TWO","6469.TWO","5604.TWO","3426.TWO","T4706Y.TWO","6493.TWO","8329.TWO","2729.TWO","6150.TWO","2233.TWO","5289.TWO","722585.TWO","3285.TWO","4752.TWO","722095.TWO","721542.TWO","721749.TWO","722040.TWO","72537P.TWO","72552P.TWO","722001.TWO","722003.TWO","72399P.TWO","3354.TWO","722857.TWO","72359P.TWO","722045.TWO","8056.TWO","722547.TWO","8440.TWO","723266.TWO","8491.TWO","722034.TWO","722007.TWO","6499.TWO","723267.TWO","72555P.TWO","6263.TWO","3674.TWO","722582.TWO","723023.TWO","723067.TWO","3625.TWO","6250.TWO","3151.TWO","8284.TWO","4967.TWO","72330P.TWO","8047.TWO","8088.TWO","8481.TWO","2718.TWO","3505.TWO","3391.TWO","3092.TWO","6234.TWO","5452.TWO","3508.TWO","3349.TWO","722386.TWO","2735.TWO","6429.TWO","722002.TWO","72299P.TWO","722898.TWO","721780.TWO","722438.TWO","722996.TWO","6518.TWO","3318.TWO","72449P.TWO","5222.TWO","722600.TWO","722758.TWO","722467.TWO","72373P.TWO","722187.TWO","72381P.TWO","2736.TWO","72571P.TWO","722918.TWO","4739.TWO","722116.TWO","72331P.TWO","722902.TWO","722184.TWO","722556.TWO","722077.TWO","721742.TWO","6182.TWO","721535.TWO","6572.TWO","723055.TWO","722186.TWO","72314P.TWO","721545.TWO","722439.TWO","4170.TWO","722379.TWO","722834.TWO","4969.TWO","3562.TWO","4134.TWO","6471.TWO","6562.TWO","3689.TWO","3141.TWO","4150.TWO","8277.TWO","3321.TWO","6539.TWO","1814.TWO","3603.TWO","3455.TWO","8115.TWO","4184.TWO","3624.TWO","4197.TWO","722869.TWO","723121.TWO","721951.TWO","8240.TWO","5201.TWO","721610.TWO","8424.TWO","6272.TWO","4949.TWO","4538.TWO","3265.TWO","8077.TWO","5245.TWO","5287.TWO","3138.TWO","3324.TWO","1595.TWO","721906.TWO","5340.TWO","3074.TWO","8415.TWO","5244.TWO","5263.TWO","3163.TWO","721744.TWO","722017.TWO","72542P.TWO","722019.TWO","722751.TWO","721791.TWO","723059.TWO","722957.TWO","72298P.TWO","721999.TWO","722267.TWO","721838.TWO","721613.TWO","722018.TWO","721627.TWO","721976.TWO","722901.TWO","72307P.TWO","722856.TWO","72417P.TWO","722056.TWO","721727.TWO","721662.TWO","722727.TWO","723061.TWO","72471P.TWO","723060.TWO","T1609Y.TWO","72495P.TWO","721628.TWO","721626.TWO","72494P.TWO","72540P.TWO","72509P.TWO","721536.TWO","722043.TWO","722897.TWO","72450P.TWO","723062.TWO","72461P.TWO","72530P.TWO","72553P.TWO","72344P.TWO","72458P.TWO","721811.TWO","72365P.TWO","722919.TWO","72334P.TWO","72487P.TWO","722646.TWO","722042.TWO","722185.TWO","72407P.TWO","722546.TWO","723177.TWO","722545.TWO","722376.TWO","721975.TWO","721837.TWO","722920.TWO","8359.TWO","6416.TWO","8059.TWO","5258.TWO","723048.TWO","72483P.TWO","721887.TWO","T3735Y.TWO","72464P.TWO","722867.TWO","722241.TWO","72379P.TWO","722866.TWO","722577.TWO","72525P.TWO","72355P.TWO","722941.TWO","72423P.TWO","72465P.TWO","721858.TWO","721694.TWO","723095.TWO","T3701Y.TWO","72306P.TWO","722804.TWO","721533.TWO","721943.TWO","722182.TWO","722441.TWO","722973.TWO","722873.TWO","721836.TWO","722374.TWO","723188.TWO","72551P.TWO","722395.TWO","721888.TWO","723012.TWO","72535P.TWO","721944.TWO","722974.TWO","723047.TWO","4946.TWO","5014.TWO","4427.TWO","3637.TWO","722599.TWO","721611.TWO","722689.TWO","722167.TWO","722641.TWO","3430.TWO","722298.TWO","6147.TWO","721693.TWO","6404.TWO","8096.TWO","722595.TWO","72325P.TWO","72484P.TWO","722700.TWO","721849.TWO","722907.TWO","72481P.TWO","722801.TWO","72413P.TWO","722170.TWO","722215.TWO","72482P.TWO","72351P.TWO","722117.TWO","722812.TWO","6401.TWO","6144.TWO","6212.TWO","8358.TWO","8093.TWO","4549.TWO","723069.TWO","722259.TWO","721772.TWO","722904.TWO","722219.TWO","723026.TWO","721922.TWO","721543.TWO","722287.TWO","72429P.TWO","722237.TWO","3413.TWO","4117.TWO","3431.TWO","8069.TWO","8087.TWO","8043.TWO","723283.TWO","722492.TWO","722491.TWO","6015.TWO","4126.TWO","3114.TWO","5398.TWO","3085.TWO","8183.TWO","4172.TWO","3232.TWO","3205.TWO","3644.TWO","6175.TWO","5229.TWO","5255.TWO","722481.TWO","722411.TWO","722939.TWO","723166.TWO","72361P.TWO","722535.TWO","721775.TWO","722105.TWO","723185.TWO","722536.TWO","722262.TWO","721824.TWO","72532P.TWO","721617.TWO","72308P.TWO","722681.TWO","721918.TWO","722692.TWO","721899.TWO","723008.TWO","721527.TWO","72332P.TWO","72517P.TWO","72350P.TWO","721897.TWO","72360P.TWO","721980.TWO","72349P.TWO","722693.TWO","72519P.TWO","721777.TWO","722647.TWO","723103.TWO","72479P.TWO","722882.TWO","72415P.TWO","722283.TWO","721796.TWO","721549.TWO","4151.TWO","721898.TWO","72414P.TWO","722128.TWO","72476P.TWO","721773.TWO","722728.TWO","723066.TWO","722622.TWO","72544P.TWO","72518P.TWO","722691.TWO","722864.TWO","722414.TWO","3663.TWO","722221.TWO","72336P.TWO","721568.TWO","722425.TWO","722978.TWO","722422.TWO","722756.TWO","721952.TWO","722979.TWO","721674.TWO","721847.TWO","722012.TWO","722171.TWO","722424.TWO","723030.TWO","722261.TWO","721817.TWO","722296.TWO","722300.TWO","723029.TWO","722052.TWO","722060.TWO","722008.TWO","721687.TWO","722059.TWO","721834.TWO","721832.TWO","8197.TWO","4103.TWO","721861.TWO","722744.TWO","721804.TWO","721862.TWO","722180.TWO","721713.TWO","722075.TWO","722905.TWO","722913.TWO","722483.TWO","721970.TWO","722269.TWO","722318.TWO","722227.TWO","721748.TWO","4534.TWO","721972.TWO","721558.TWO","722107.TWO","72374P.TWO","722179.TWO","72388P.TWO","722251.TWO","722385.TWO","722315.TWO","721633.TWO","722076.TWO","72304P.TWO","72333P.TWO","722384.TWO","72395P.TWO","722252.TWO","72300P.TWO","721758.TWO","722912.TWO","721831.TWO","721830.TWO","722316.TWO","723002.TWO","6270.TWO","2928.TWO","6438.TWO","6417.TWO","3465.TWO","8489.TWO","4167.TWO","3115.TWO","8416.TWO","4537.TWO","3546.TWO","6229.TWO","6294.TWO","3117.TWO","1264.TWO","8465.TWO","4135.TWO","8079.TWO","8476.TWO","4136.TWO","3234.TWO","6158.TWO","6169.TWO","5371.TWO","1584.TWO","3498.TWO","5253.TWO","3678.TWO","3601.TWO","4754.TWO","6461.TWO"]

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
