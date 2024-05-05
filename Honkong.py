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
    available_tickers = ["0522.HK","0104.HK","0933.HK","0180.HK","6388.HK","0718.HK","0494.HK","0316.HK","0233.HK","0055.HK","0524.HK","0703.HK","0005.HK","2888.HK","1222.HK","0992.HK","0293.HK","0388.HK","0017.HK","0941.HK","0688.HK","0291.HK","0027.HK","0242.HK","0011.HK","0006.HK","0004.HK","0003.HK","3377.HK","2388.HK","1299.HK","0883.HK","0817.HK","0762.HK","0392.HK","0257.HK","0252.HK","1668.HK","0900.HK","0808.HK","0716.HK","0705.HK","0669.HK","0656.HK","0619.HK","0363.HK","0303.HK","0267.HK","0245.HK","0184.HK","0144.HK","0105.HK","0083.HK","0071.HK","0045.HK","0020.HK","0016.HK","0008.HK","8022.HK","2380.HK","1972.HK","1360.HK","1208.HK","1029.HK","0984.HK","0966.HK","0887.HK","0882.HK","0836.HK","0708.HK","0639.HK","0450.HK","0375.HK","0308.HK","0295.HK","0294.HK","0285.HK","0273.HK","0271.HK","0254.HK","0247.HK","0244.HK","0202.HK","0137.HK","0131.HK","0123.HK","0101.HK","0086.HK","0081.HK","0028.HK","0023.HK","0021.HK","0019.HK","0012.HK","0647.HK","0486.HK","1245.HK","0805.HK","8391.HK","1928.HK","0700.HK","2282.HK","0001.HK","3800.HK","1833.HK","1044.HK","3383.HK","3333.HK","2319.HK","0337.HK","3322.HK","3308.HK","2877.HK","2383.HK","1700.HK","1212.HK","1112.HK","0868.HK","0862.HK","0829.HK","0575.HK","0210.HK","3998.HK","3900.HK","3818.HK","2369.HK","2348.HK","2300.HK","2038.HK","2007.HK","1986.HK","1889.HK","1880.HK","1638.HK","1515.HK","1313.HK","1234.HK","1221.HK","1149.HK","1128.HK","1125.HK","1083.HK","1059.HK","0981.HK","0919.HK","0825.HK","0809.HK","0757.HK","0745.HK","0713.HK","0631.HK","0607.HK","0425.HK","0379.HK","0318.HK","0183.HK","8356.HK","8296.HK","8295.HK","8269.HK","8250.HK","8207.HK","8198.HK","8185.HK","8181.HK","8178.HK","8173.HK","8163.HK","8137.HK","8119.HK","8071.HK","8041.HK","8019.HK","8006.HK","8003.HK","6868.HK","3999.HK","3933.HK","3918.HK","3889.HK","3888.HK","3883.HK","3777.HK","3669.HK","3337.HK","3331.HK","3318.HK","3311.HK","2955.HK","2382.HK","2342.HK","2324.HK","2313.HK","2309.HK","2302.HK","2283.HK","2280.HK","2111.HK","1998.HK","1938.HK","1929.HK","1831.HK","1823.HK","1717.HK","1683.HK","1661.HK","1623.HK","1616.HK","1600.HK","1555.HK","1498.HK","1396.HK","1393.HK","1372.HK","1363.HK","1361.HK","1348.HK","1335.HK","1333.HK","1323.HK","1318.HK","1293.HK","1230.HK","1219.HK","1198.HK","1181.HK","1175.HK","1165.HK","1161.HK","1142.HK","1106.HK","1073.HK","1070.HK","1009.HK","1007.HK","0963.HK","0923.HK","0917.HK","0913.HK","0896.HK","0884.HK","0877.HK","0867.HK","0827.HK","0773.HK","0768.HK","0737.HK","0682.HK","0646.HK","0572.HK","0546.HK","0505.HK","0475.HK","0474.HK","0468.HK","0459.HK","0449.HK","0410.HK","0400.HK","0395.HK","0356.HK","0354.HK","0353.HK","0311.HK","0272.HK","0269.HK","0268.HK","0223.HK","0208.HK","0195.HK","0121.HK","0120.HK","0072.HK","0047.HK","0039.HK","0035.HK","0033.HK","8387.HK","8272.HK","8266.HK","8256.HK","8242.HK","8226.HK","8225.HK","8213.HK","8212.HK","8203.HK","8196.HK","8193.HK","8169.HK","8167.HK","8165.HK","8156.HK","8148.HK","8143.HK","8133.HK","8128.HK","8117.HK","8116.HK","8112.HK","8103.HK","8097.HK","8092.HK","8090.HK","8085.HK","8077.HK","8068.HK","8066.HK","8061.HK","8060.HK","8053.HK","8051.HK","8032.HK","8031.HK","8030.HK","8029.HK","8008.HK","8001.HK","6899.HK","6896.HK","6888.HK","6833.HK","6166.HK","8219.HK","3989.HK","3963.HK","3899.HK","3882.HK","3868.HK","3838.HK","3828.HK","3688.HK","3666.HK","3628.HK","3382.HK","3368.HK","3336.HK","3335.HK","3313.HK","2991.HK","2986.HK","2910.HK","2903.HK","2898.HK","2889.HK","2728.HK","2662.HK","2623.HK","2618.HK","2608.HK","2398.HK","2393.HK","2371.HK","2368.HK","2358.HK","2341.HK","2336.HK","2331.HK","2330.HK","2317.HK","2288.HK","2255.HK","2211.HK","2198.HK","2168.HK","2138.HK","2128.HK","2118.HK","2078.HK","2018.HK","2014.HK","1980.HK","1918.HK","1900.HK","1888.HK","1886.HK","1882.HK","1836.HK","1830.HK","1813.HK","1808.HK","1803.HK","1778.HK","1771.HK","1718.HK","1685.HK","1678.HK","1669.HK","1628.HK","1520.HK","1509.HK","1421.HK","1395.HK","1388.HK","1387.HK","1382.HK","1381.HK","1378.HK","1366.HK","1358.HK","1338.HK","1319.HK","1317.HK","1315.HK","1308.HK","1300.HK","1277.HK","1273.HK","1263.HK","1259.HK","1250.HK","1249.HK","1247.HK","1240.HK","1236.HK","1232.HK","1185.HK","1143.HK","1130.HK","1115.HK","1113.HK","1110.HK","1109.HK","1087.HK","1080.HK","1039.HK","1030.HK","1020.HK","1019.HK","1006.HK","0987.HK","0978.HK","0975.HK","0969.HK","0951.HK","0936.HK","0929.HK","0911.HK","0873.HK","0860.HK","0856.HK","0853.HK","0852.HK","0848.HK","0846.HK","0845.HK","0838.HK","0837.HK","0833.HK","0830.HK","0828.HK","0826.HK","0819.HK","0813.HK","0800.HK","0777.HK","0775.HK","0756.HK","0746.HK","0732.HK","0698.HK","0691.HK","0672.HK","0660.HK","0609.HK","0602.HK","0596.HK","0586.HK","0565.HK","0554.HK","0540.HK","0531.HK","0509.HK","0503.HK","0480.HK","0477.HK","0465.HK","0445.HK","0444.HK","0434.HK","0428.HK","0426.HK","0423.HK","0419.HK","0413.HK","0408.HK","0402.HK","0364.HK","0359.HK","0352.HK","0348.HK","0322.HK","0319.HK","0312.HK","0288.HK","0279.HK","0264.HK","0256.HK","0248.HK","0197.HK","0196.HK","0175.HK","0157.HK","0153.HK","0151.HK","0148.HK","0143.HK","0130.HK","0117.HK","0098.HK","0080.HK","0065.HK","2121.HK","8230.HK","8290.HK","8140.HK","0699.HK","8361.HK","2100.HK","0469.HK","8368.HK","1022.HK","8277.HK","2277.HK","2379.HK","1910.HK","2946.HK","0243.HK","6230.HK","6836.HK","6210.HK","1568.HK","1733.HK","1278.HK","0532.HK","3009.HK","3035.HK","3019.HK","3027.HK","2921.HK","0096.HK","4332.HK","170.HK","0595.HK","8390.HK","2941.HK","2936.HK","8380.HK","8389.HK","2935.HK","2928.HK","8376.HK","2937.HK","2930.HK","2927.HK","8385.HK","2926.HK","8107.HK","6288.HK","2366.HK","1205.HK","1201.HK","1184.HK","1127.HK","1098.HK","1001.HK","0878.HK","0861.HK","0758.HK","0724.HK","0723.HK","0702.HK","0641.HK","0618.HK","0617.HK","0506.HK","0385.HK","0297.HK","0212.HK","0209.HK","0166.HK","0142.HK","0135.HK","8400.HK","8306.HK","8228.HK","8089.HK","8079.HK","1224.HK","1218.HK","1174.HK","1168.HK","1139.HK","1123.HK","1063.HK","1047.HK","1045.HK","1041.HK","1038.HK","1031.HK","0999.HK","0979.HK","0970.HK","0912.HK","0908.HK","0897.HK","0889.HK","0859.HK","0751.HK","0710.HK","0709.HK","0687.HK","0659.HK","0657.HK","0636.HK","0610.HK","0577.HK","0551.HK","0535.HK","0529.HK","0510.HK","0493.HK","0491.HK","0485.HK","0479.HK","0467.HK","0396.HK","0372.HK","0343.HK","0341.HK","0336.HK","0334.HK","0330.HK","0307.HK","0296.HK","0286.HK","0255.HK","0240.HK","0234.HK","0232.HK","0213.HK","0211.HK","0207.HK","0179.HK","0163.HK","0139.HK","0129.HK","0113.HK","0100.HK","0093.HK","0092.HK","0075.HK","0052.HK","0046.HK","0029.HK","0009.HK","8375.HK","8351.HK","8279.HK","8270.HK","8265.HK","8192.HK","8176.HK","8175.HK","8159.HK","8153.HK","8150.HK","8131.HK","8108.HK","8086.HK","8081.HK","8080.HK","8048.HK","8047.HK","8037.HK","8033.HK","8005.HK","2340.HK","2327.HK","2326.HK","2323.HK","2322.HK","2088.HK","1556.HK","1447.HK","1431.HK","1371.HK","1223.HK","1200.HK","1193.HK","1191.HK","1189.HK","1188.HK","1180.HK","1170.HK","1169.HK","1166.HK","1141.HK","1118.HK","1114.HK","1094.HK","1091.HK","1079.HK","1052.HK","1051.HK","1050.HK","1046.HK","1043.HK","1037.HK","1013.HK","1010.HK","1005.HK","1004.HK","1003.HK","0993.HK","0989.HK","0986.HK","0983.HK","0982.HK","0959.HK","0952.HK","0934.HK","0925.HK","0922.HK","0907.HK","0905.HK","0903.HK","0899.HK","0898.HK","0891.HK","0888.HK","0875.HK","0869.HK","0858.HK","0855.HK","0834.HK","0818.HK","0812.HK","0803.HK","0789.HK","0771.HK","0765.HK","0764.HK","0761.HK","0755.HK","0738.HK","0730.HK","0726.HK","0721.HK","0720.HK","0717.HK","0715.HK","0711.HK","0693.HK","0686.HK","0683.HK","0681.HK","0678.HK","0677.HK","0676.HK","0675.HK","0665.HK","0662.HK","0661.HK","0635.HK","0628.HK","0622.HK","0621.HK","0613.HK","0603.HK","0601.HK","0590.HK","0583.HK","0582.HK","0581.HK","0526.HK","0517.HK","0500.HK","0498.HK","0487.HK","0482.HK","0451.HK","0430.HK","0418.HK","0417.HK","0404.HK","0403.HK","0399.HK","0397.HK","0393.HK","0391.HK","0389.HK","0387.HK","0384.HK","0367.HK","0366.HK","0365.HK","0342.HK","0340.HK","0333.HK","0332.HK","0328.HK","0327.HK","0315.HK","0306.HK","0292.HK","0275.HK","0262.HK","0251.HK","0239.HK","0230.HK","0224.HK","0221.HK","0214.HK","0205.HK","0190.HK","0188.HK","0182.HK","0176.HK","0173.HK","0164.HK","0159.HK","0147.HK","0146.HK","0136.HK","0127.HK","0125.HK","0110.HK","0106.HK","0102.HK","0084.HK","0079.HK","0073.HK","0069.HK","0063.HK","0062.HK","0061.HK","0059.HK","0057.HK","0053.HK","0043.HK","0041.HK","0025.HK","0024.HK","0022.HK","0007.HK","0701.HK","0643.HK","0109.HK","0864.HK","0476.HK","0679.HK","0305.HK","1163.HK","0339.HK","1120.HK","0620.HK","0645.HK","0155.HK","0835.HK","0377.HK","2940.HK","0684.HK","0787.HK","8109.HK","8172.HK","0149.HK","0927.HK","0854.HK","3300.HK","1207.HK","0638.HK","0754.HK","1152.HK","0261.HK","0132.HK","0198.HK","1215.HK","8082.HK","0563.HK","8078.HK","3839.HK","0530.HK","0547.HK","0058.HK","0725.HK","0550.HK","0460.HK","0651.HK","8016.HK","0685.HK","0894.HK","0810.HK","8021.HK","0655.HK","0938.HK","0519.HK","0996.HK","0997.HK","0512.HK","1229.HK","8386.HK","0642.HK","8076.HK","1132.HK","8393.HK","0495.HK","0759.HK","0015.HK","0433.HK","0114.HK","0167.HK","0497.HK","1682.HK","0310.HK","0940.HK","1999.HK","2902.HK","8083.HK","2886.HK","1192.HK","0851.HK","0030.HK","3813.HK","0673.HK","0508.HK","0750.HK","1131.HK","1663.HK","0289.HK","0472.HK","0904.HK","0126.HK","0990.HK","0116.HK","8202.HK","0398.HK","0760.HK","0169.HK","8317.HK","0736.HK","0231.HK","1199.HK","8100.HK","1082.HK","1049.HK","2908.HK","0585.HK","0592.HK","0910.HK","0571.HK","0412.HK","0767.HK","1028.HK","0088.HK","2904.HK","2975.HK","0611.HK","8166.HK","2343.HK","0406.HK","2983.HK","1225.HK","2917.HK","2882.HK","8046.HK","0204.HK","1332.HK","0689.HK","0499.HK","0544.HK","0566.HK","1105.HK","8120.HK","8186.HK","0626.HK","2186.HK","0199.HK","8075.HK","3363.HK","1104.HK","0943.HK","1262.HK","1064.HK","0948.HK","0589.HK","1187.HK","0909.HK","0627.HK","0729.HK","8271.HK","0616.HK","0632.HK","0241.HK","1213.HK","6108.HK","0578.HK","0567.HK","2668.HK","0593.HK","0078.HK","1076.HK","0704.HK","0186.HK","0152.HK","0138.HK","8239.HK","2916.HK","2997.HK","2944.HK","0918.HK","0630.HK","2900.HK","1182.HK","0085.HK","0321.HK","8130.HK","1124.HK","1159.HK","0674.HK","0731.HK","0706.HK","0431.HK","3886.HK","0346.HK","0298.HK","1196.HK","0432.HK","0082.HK","0276.HK","1220.HK","1160.HK","0915.HK","0162.HK","0380.HK","1768.HK","6828.HK","2123.HK","1298.HK","0371.HK","1060.HK","0378.HK","0355.HK","100.HK","8222.HK","8059.HK","8170.HK","8139.HK","8305.HK","1470.HK","8381.HK","8372.HK","8177.HK","2949.HK","2925.HK","8012.HK","2948.HK","8379.HK","8396.HK","8141.HK","2942.HK","2931.HK","2938.HK","8369.HK","2922.HK","2932.HK","8395.HK","2934.HK","8327.HK","1561.HK","2950.HK","8038.HK","2193.HK","8027.HK","8378.HK","2933.HK","8373.HK","1341.HK","2920.HK","8248.HK","2924.HK","2912.HK","2923.HK","2929.HK","0557.HK","0939.HK","1211.HK","0386.HK","3988.HK","2318.HK","1398.HK","0338.HK","0902.HK","0857.HK","0390.HK","8243.HK","8211.HK","6030.HK","2777.HK","2328.HK","1798.HK","0998.HK","0728.HK","0549.HK","0323.HK","8348.HK","3606.HK","3378.HK","3323.HK","2899.HK","2868.HK","2866.HK","2727.HK","2722.HK","2628.HK","2202.HK","2196.HK","2006.HK","1988.HK","1919.HK","1898.HK","1800.HK","1776.HK","1533.HK","1339.HK","1288.HK","1171.HK","1138.HK","1099.HK","1088.HK","1055.HK","1053.HK","0995.HK","0991.HK","0980.HK","0814.HK","0763.HK","0694.HK","0598.HK","0489.HK","0107.HK","0042.HK","8249.HK","8247.HK","8227.HK","8205.HK","8197.HK","8189.HK","8106.HK","8058.HK","8045.HK","6886.HK","6869.HK","6198.HK","6196.HK","3983.HK","3908.HK","3699.HK","3698.HK","3618.HK","3399.HK","3396.HK","3355.HK","3328.HK","2883.HK","2880.HK","2799.HK","2698.HK","2607.HK","2601.HK","2600.HK","2488.HK","2357.HK","2355.HK","2333.HK","2208.HK","1893.HK","1816.HK","1812.HK","1799.HK","1766.HK","1588.HK","1558.HK","1543.HK","1528.HK","1476.HK","1459.HK","1359.HK","1186.HK","1157.HK","1133.HK","1108.HK","1072.HK","1071.HK","1066.HK","1065.HK","1057.HK","1033.HK","0956.HK","0914.HK","0874.HK","0753.HK","0747.HK","0696.HK","0568.HK","0564.HK","0525.HK","0438.HK","0416.HK","0347.HK","0168.HK","0161.HK","6881.HK","8253.HK","8258.HK","3903.HK","0958.HK","1513.HK","3636.HK","1708.HK","1265.HK","8301.HK","2238.HK","1461.HK","6839.HK","0839.HK","1456.HK","0811.HK","3969.HK","0300.HK","8095.HK","1025.HK","8115.HK","1103.HK","1618.HK","1075.HK","3996.HK","8049.HK","3968.HK","6865.HK","1829.HK","1666.HK","0840.HK","0358.HK","1958.HK","1296.HK","6818.HK","3369.HK","1819.HK","6837.HK","0038.HK","6116.HK","6138.HK","0576.HK","8273.HK","0895.HK","1599.HK","0916.HK","8235.HK","1385.HK","2066.HK","2120.HK","0317.HK","3866.HK","0816.HK","1292.HK","1349.HK","1858.HK","0548.HK","8286.HK","8236.HK","1818.HK","0588.HK","0954.HK","1289.HK","0357.HK","0177.HK","2218.HK","0552.HK","0719.HK","2338.HK","1375.HK","0921.HK","0579.HK","3330.HK","1122.HK","2386.HK","1508.HK","0553.HK","2068.HK","1963.HK","1786.HK","0350.HK","8215.HK","3043.HK","3048.HK","6889.HK","8366.HK","6823.HK","6808.HK","6139.HK","3188.HK","3124.HK","3117.HK","3070.HK","3037.HK","2919.HK","2830.HK","2356.HK","1883.HK","1788.HK","1347.HK","1270.HK","1258.HK","1137.HK","1111.HK","1097.HK","0906.HK","0880.HK","0823.HK","0697.HK","0668.HK","0648.HK","0623.HK","0606.HK","0560.HK","0533.HK","0521.HK","0513.HK","0511.HK","0488.HK","0435.HK","0420.HK","0382.HK","0376.HK","0373.HK","0368.HK","0351.HK","0287.HK","0282.HK","0280.HK","0278.HK","0270.HK","0260.HK","0236.HK","0235.HK","0227.HK","0225.HK","0219.HK","0218.HK","0217.HK","0200.HK","0193.HK","0191.HK","0185.HK","0174.HK","0172.HK","0160.HK","0158.HK","0156.HK","0154.HK","0122.HK","0108.HK","0091.HK","0076.HK","0068.HK","0066.HK","0051.HK","0031.HK","0014.HK","0010.HK","0002.HK","3143.HK","8067.HK","3101.HK","8125.HK","3157.HK","0050.HK","0141.HK","0145.HK","3137.HK","0229.HK","3076.HK","0411.HK","0026.HK","3051.HK","3090.HK","87001.HK","0237.HK","3121.HK","3126.HK","2982.HK","0604.HK","0625.HK","8162.HK","3021.HK","3160.HK","2808.HK","0181.HK","2990.HK","3128.HK","1093.HK","0821.HK","3041.HK","0171.HK","3118.HK","0440.HK","0266.HK","3054.HK","1828.HK","0663.HK","2822.HK","0283.HK","0044.HK","0118.HK","3145.HK","3100.HK","3808.HK","3315.HK","0087.HK","0194.HK","0277.HK","3066.HK","3075.HK","0170.HK","2973.HK","3060.HK","3122.HK","2805.HK","3072.HK","1266.HK","0281.HK","0133.HK","8009.HK","3120.HK","3360.HK","3162.HK","0036.HK","0037.HK","0165.HK","3161.HK","3127.HK","0605.HK","0060.HK","0253.HK","0250.HK","3136.HK","0034.HK","1881.HK","3086.HK","0666.HK","0201.HK","0097.HK","3134.HK","0054.HK","2996.HK","3119.HK","2993.HK","3029.HK","0222.HK","0518.HK","3140.HK","0216.HK","1203.HK","8028.HK","0089.HK","0405.HK","2832.HK","3102.HK","3156.HK","6161.HK","0070.HK","0570.HK","3040.HK","2778.HK","3139.HK","0536.HK","8191.HK","2811.HK","1426.HK","3091.HK","3095.HK","3098.HK","3150.HK","3180.HK","3129.HK","0128.HK","0263.HK","2638.HK","1126.HK","1275.HK","0226.HK","0112.HK","3165.HK","3056.HK","2310.HK","3149.HK","3199.HK","0032.HK","2666.HK","3084.HK","0345.HK","0056.HK","3008.HK","0018.HK","3141.HK","1058.HK","0119.HK","3064.HK","1639.HK","0727.HK","0103.HK","3085.HK","3031.HK","3078.HK","2909.HK","2939.HK","3147.HK","3132.HK","0820.HK","3089.HK","3110.HK","2824.HK","8138.HK","0040.HK","3107.HK","3069.HK","8326.HK","0799.HK","1970.HK","1913.HK","2233.HK","2011.HK","0442.HK","1280.HK","1530.HK","2023.HK","1466.HK","0947.HK","2086.HK","8171.HK","1340.HK","1253.HK","1438.HK","2200.HK","1116.HK","2901.HK","6183.HK","1400.HK","8182.HK","2906.HK","1446.HK","8267.HK","1260.HK","0329.HK","3663.HK","0612.HK","1369.HK","1026.HK","6880.HK","8129.HK","1662.HK","1312.HK","2399.HK","8325.HK","6838.HK","8026.HK","2236.HK","8093.HK","0064.HK","6893.HK","8233.HK","1538.HK","0320.HK","0520.HK","0893.HK","8282.HK","8316.HK","2080.HK","1452.HK","1884.HK","8132.HK","1316.HK","2312.HK","0090.HK","2212.HK","1089.HK","1613.HK","8307.HK","1993.HK","1492.HK","8312.HK","8113.HK","0863.HK","0653.HK","2286.HK","0640.HK","8397.HK","8020.HK","3737.HK","2947.HK","3600.HK","0462.HK","1227.HK","8336.HK","1282.HK","6882.HK","2223.HK","8011.HK","1522.HK","8072.HK","1499.HK","2788.HK","2188.HK","8268.HK","1439.HK","1023.HK","0960.HK","8206.HK","8155.HK","8340.HK","1345.HK","0360.HK","0798.HK","6168.HK","1430.HK","0743.HK","1178.HK","0822.HK","1370.HK","1290.HK","8209.HK","2678.HK","1681.HK","8145.HK","1468.HK","6863.HK","6898.HK","1121.HK","0690.HK","1367.HK","8218.HK","1968.HK","8260.HK","8200.HK","1251.HK","3708.HK","3966.HK","2960.HK","3639.HK","2020.HK","2002.HK","0483.HK","2008.HK","1899.HK","1314.HK","1117.HK","1239.HK","1252.HK","1355.HK","2943.HK","1397.HK","1164.HK","1226.HK","8147.HK","8310.HK","8399.HK","1233.HK","6123.HK","8195.HK","3344.HK","0850.HK","1380.HK","3393.HK","0658.HK","0246.HK","2878.HK","8087.HK","1329.HK","0258.HK","3366.HK","2226.HK","0574.HK","0220.HK","2221.HK","1096.HK","0600.HK","3326.HK","1246.HK","0707.HK","0543.HK","1838.HK","0401.HK","8036.HK","0712.HK","2112.HK","1908.HK","1062.HK","1002.HK","1140.HK","6830.HK","0189.HK","1368.HK","2307.HK","1856.HK","1090.HK","8355.HK","1210.HK","1269.HK","1966.HK","8363.HK","1848.HK","3799.HK","2199.HK","2349.HK","3683.HK","0309.HK","1235.HK","2389.HK","2339.HK","8101.HK","3303.HK","1194.HK","1036.HK","1863.HK","8237.HK","2988.HK","3816.HK","0299.HK","2010.HK","0381.HK","0215.HK","2362.HK","0722.HK","3939.HK","1699.HK","0633.HK","3398.HK","3633.HK","0542.HK","1086.HK","1069.HK","1399.HK","0471.HK","1386.HK","0484.HK","0558.HK","8246.HK","1383.HK","80737.HK","1177.HK","1271.HK","0953.HK","2033.HK","0842.HK","6118.HK","0931.HK","3339.HK","2688.HK","2030.HK","0841.HK","1228.HK","1698.HK","0362.HK","0496.HK","8238.HK","1107.HK","1991.HK","2699.HK","1172.HK","0872.HK","1011.HK","2669.HK","8007.HK","2098.HK","1822.HK","1362.HK","8311.HK","1241.HK","0580.HK","8123.HK","1626.HK","8220.HK","8111.HK","0587.HK","2222.HK","0455.HK","0067.HK","1310.HK","8098.HK","8122.HK","0930.HK","0573.HK","3301.HK","8070.HK","1689.HK","8063.HK","2768.HK","8025.HK","2907.HK","0374.HK","0569.HK","1102.HK","8099.HK","0228.HK","0095.HK","8315.HK","0591.HK","1495.HK","3836.HK","2298.HK","1728.HK","1428.HK","8331.HK","2005.HK","0556.HK","1566.HK","1217.HK","0926.HK","2133.HK","8179.HK","1129.HK","2083.HK","0695.HK","1148.HK","2314.HK","1389.HK","0973.HK","3087.HK","3017.HK","2844.HK","2816.HK","3092.HK","3020.HK","3015.HK","3016.HK","3055.HK","3082.HK","3061.HK","3063.HK","3045.HK","3062.HK","3099.HK","3105.HK","3005.HK","3025.HK","3052.HK","3049.HK","3013.HK","3065.HK","3106.HK","3026.HK","3011.HK","3007.HK","3057.HK","2848.HK","3036.HK","1206.HK","0778.HK","1151.HK","1085.HK","0967.HK","1021.HK","1866.HK","1048.HK","0770.HK","2178.HK","0844.HK","1619.HK","1738.HK","0370.HK","2689.HK","0361.HK","0326.HK","0650.HK","8398.HK","0439.HK","0735.HK","0111.HK","0555.HK","2905.HK","1176.HK","0608.HK","0094.HK","1811.HK","2000.HK","0383.HK","1068.HK","0876.HK","0259.HK","0988.HK","1135.HK","0115.HK","0458.HK","0680.HK","0539.HK","0802.HK","0369.HK","0313.HK","0559.HK","1100.HK","0124.HK","0692.HK","0099.HK","3678.HK","2345.HK","1202.HK","3993.HK","6826.HK","1000.HK","1353.HK","0670.HK","6866.HK","3833.HK","3948.HK","2009.HK","0187.HK","1527.HK","1330.HK","2039.HK","1680.HK","1136.HK","0265.HK","0801.HK","1673.HK","0456.HK","0637.HK","2700.HK","0831.HK","1532.HK","1636.HK","8121.HK","1155.HK","1480.HK","8088.HK","2913.HK","2268.HK","2183.HK","2789.HK","1190.HK","6133.HK","0629.HK","0422.HK","1862.HK","2320.HK","0815.HK","3608.HK","0464.HK","3822.HK"]

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
