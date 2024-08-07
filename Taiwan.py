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
    available_tickers = ["1589.TW","5906.TW","2354.TW","2601.TW","2498.TW","8429.TW","5285.TW","3653.TW","4763.TW","9136.TW","3673.TW","5264.TW","3665.TW","8411.TW","6451.TW","5871.TW","4141.TW","2637.TW","1590.TW","1525.TW","8467.TW","6405.TW","4999.TW","3042.TW","2904.TW","1307.TW","6271.TW","6277.TW","2884.TW","2330.TW","2888.TW","2317.TW","1452.TW","2486.TW","2303.TW","2062.TW","1773.TW","1513.TW","1466.TW","1314.TW","9935.TW","9904.TW","8103.TW","3617.TW","2891.TW","2886.TW","2488.TW","2475.TW","2454.TW","2409.TW","2392.TW","2382.TW","2355.TW","2325.TW","1503.TW","1323.TW","1102.TW","9926.TW","8110.TW","8039.TW","6505.TW","6176.TW","6115.TW","5434.TW","4906.TW","3380.TW","3056.TW","3037.TW","3028.TW","2881.TW","2845.TW","2618.TW","2536.TW","2499.TW","2489.TW","2448.TW","2428.TW","2404.TW","2360.TW","2337.TW","2332.TW","2308.TW","2301.TW","1904.TW","1802.TW","1708.TW","1236.TW","1217.TW","1101.TW","2423.TW","911622.TW","8222.TW","1568.TW","9188.TW","4958.TW","4142.TW","2634.TW","1626.TW","4545.TW","9110.TW","911612.TW","6449.TW","1337.TW","5269.TW","9106.TW","911608.TW","1786.TW","1783.TW","1522.TW","5259.TW","1103.TW","911611.TW","1735.TW","1309.TW","8150.TW","2002.TW","2231.TW","5519.TW","910861.TW","911616.TW","6251.TW","5225.TW","9105.TW","8341.TW","9157.TW","5243.TW","00653L.TW","00652.TW","00654R.TW","5288.TW","910708.TW","2642.TW","6442.TW","2712.TW","1516.TW","1722.TW","3532.TW","2228.TW","912398.TW","4755.TW","9802.TW","1312A.TW","6456.TW","4952.TW","3559.TW","913889.TW","4551.TW","910801.TW","1338.TW","911626.TW","3706.TW","8404.TW","1905.TW","910322.TW","031261.TW","4190.TW","031863.TW","6431.TW","2239.TW","8427.TW","1262.TW","2236.TW","6415.TW","5215.TW","1592.TW","4984.TW","4557.TW","1340.TW","2115.TW","4935.TW","4977.TW","2923.TW","4144.TW","6422.TW","4912.TW","3588.TW","2506.TW","5538.TW","8454.TW","911868.TW","5907.TW","6464.TW","4916.TW","6452.TW","6412.TW","2855.TW","4968.TW","8463.TW","2731.TW","8443.TW","2611.TW","912000.TW","031021.TW","2002A.TW","4930.TW","2913.TW","4934.TW","4555.TW","3432.TW","4976.TW","2929.TW","4536.TW","6443.TW","9945.TW","9939.TW","9937.TW","9908.TW","9907.TW","8926.TW","6286.TW","6239.TW","6214.TW","6206.TW","6201.TW","6168.TW","6155.TW","6153.TW","6145.TW","5608.TW","5533.TW","4746.TW","4733.TW","4133.TW","3607.TW","3605.TW","3598.TW","3591.TW","3579.TW","3576.TW","3545.TW","3504.TW","3481.TW","3419.TW","3057.TW","3035.TW","3034.TW","3026.TW","3025.TW","3022.TW","3019.TW","3018.TW","3010.TW","2915.TW","2911.TW","2906.TW","2905.TW","2903.TW","2887.TW","2882.TW","2820.TW","2609.TW","2608.TW","2606.TW","2605.TW","2603.TW","2530.TW","2495.TW","2478.TW","2457.TW","2456.TW","2438.TW","2437.TW","2429.TW","2419.TW","2406.TW","2383.TW","2379.TW","2377.TW","2374.TW","2353.TW","2352.TW","2347.TW","2342.TW","2338.TW","2331.TW","2328.TW","2327.TW","2323.TW","2321.TW","2313.TW","2311.TW","2227.TW","2207.TW","2101.TW","2012.TW","2010.TW","2006.TW","1809.TW","1808.TW","1731.TW","1614.TW","1605.TW","1582.TW","1541.TW","1533.TW","1521.TW","1447.TW","1444.TW","1326.TW","1316.TW","1313.TW","1232.TW","1219.TW","9955.TW","9944.TW","9943.TW","9941.TW","9934.TW","9929.TW","9928.TW","9927.TW","9925.TW","9924.TW","9919.TW","9918.TW","9914.TW","9911.TW","8422.TW","8271.TW","8261.TW","8163.TW","8114.TW","8081.TW","8072.TW","8046.TW","8016.TW","6702.TW","6605.TW","6409.TW","6289.TW","6281.TW","6257.TW","6243.TW","6235.TW","6209.TW","6205.TW","6197.TW","6192.TW","6184.TW","6166.TW","6152.TW","6141.TW","6139.TW","6117.TW","5531.TW","5525.TW","5522.TW","5521.TW","5484.TW","5471.TW","4994.TW","4960.TW","4956.TW","4938.TW","4904.TW","4526.TW","4164.TW","4108.TW","4106.TW","3701.TW","3698.TW","3694.TW","3682.TW","3679.TW","3669.TW","3622.TW","3584.TW","3583.TW","3573.TW","3557.TW","3550.TW","3533.TW","3519.TW","3515.TW","3501.TW","3454.TW","3443.TW","3406.TW","3383.TW","3356.TW","3296.TW","3231.TW","3189.TW","3149.TW","3130.TW","3094.TW","3090.TW","3058.TW","3052.TW","3046.TW","3045.TW","3044.TW","3032.TW","3031.TW","3008.TW","3003.TW","3002.TW","2912.TW","2908.TW","2890.TW","2885.TW","2852.TW","2849.TW","2847.TW","2832.TW","2816.TW","2812.TW","2707.TW","2706.TW","2701.TW","2617.TW","2547.TW","2545.TW","2543.TW","2542.TW","2535.TW","2534.TW","2528.TW","2514.TW","2511.TW","2504.TW","2493.TW","2492.TW","2485.TW","2483.TW","2477.TW","2468.TW","2467.TW","2466.TW","2462.TW","2461.TW","2455.TW","2451.TW","2449.TW","2444.TW","2443.TW","2442.TW","2441.TW","2431.TW","2426.TW","2424.TW","2420.TW","2413.TW","2412.TW","2402.TW","2401.TW","2397.TW","2395.TW","2393.TW","2390.TW","2388.TW","2385.TW","2371.TW","2369.TW","2368.TW","2365.TW","2364.TW","2363.TW","2362.TW","2361.TW","2359.TW","2357.TW","2356.TW","2329.TW","2324.TW","2305.TW","2302.TW","2201.TW","2105.TW","2103.TW","2034.TW","2029.TW","2025.TW","2023.TW","2022.TW","2017.TW","2015.TW","1909.TW","1907.TW","1903.TW","1810.TW","1789.TW","1737.TW","1734.TW","1725.TW","1724.TW","1720.TW","1717.TW","1714.TW","1712.TW","1711.TW","1707.TW","1701.TW","1617.TW","1612.TW","1611.TW","1609.TW","1603.TW","1583.TW","1560.TW","1537.TW","1535.TW","1530.TW","1529.TW","1527.TW","1526.TW","1519.TW","1514.TW","1507.TW","1506.TW","1475.TW","1463.TW","1460.TW","1459.TW","1457.TW","1455.TW","1454.TW","1443.TW","1441.TW","1439.TW","1438.TW","1436.TW","1423.TW","1417.TW","1402.TW","1339.TW","1325.TW","1319.TW","1315.TW","1310.TW","1303.TW","1301.TW","1234.TW","1227.TW","1220.TW","1216.TW","1215.TW","2405.TW","1704.TW","2520.TW","2434.TW","3164.TW","1608.TW","2851.TW","6269.TW","1517.TW","1730.TW","2501.TW","1762.TW","3051.TW","3059.TW","6164.TW","2615.TW","9942.TW","9917.TW","2102.TW","2453.TW","2373.TW","910482.TW","1532.TW","4737.TW","9103.TW","3054.TW","1713.TW","1442.TW","2891A.TW","8021.TW","2548.TW","1210.TW","3518.TW","4919.TW","9910.TW","8131.TW","2027.TW","1419.TW","6215.TW","2450.TW","3033.TW","8464.TW","2312.TW","2028.TW","6128.TW","3312.TW","2850.TW","3229.TW","6133.TW","2348.TW","8215.TW","1618.TW","2316.TW","3702.TW","6116.TW","2439.TW","6005.TW","2206.TW","3413.TW","3535.TW","9940.TW","3038.TW","4104.TW","2471.TW","3048.TW","2612.TW","1726.TW","9933.TW","6172.TW","2610.TW","2901.TW","2727.TW","1471.TW","3596.TW","1324.TW","4725.TW","3474.TW","1233.TW","2049.TW","6504.TW","1736.TW","2436.TW","2414.TW","5203.TW","6216.TW","3704.TW","1902.TW","1733.TW","3305.TW","2376.TW","2007.TW","4532.TW","2030.TW","9902.TW","8105.TW","5706.TW","3494.TW","5305.TW","2480.TW","1538.TW","1312.TW","2367.TW","2108.TW","6177.TW","2408.TW","2614.TW","6131.TW","3016.TW","3017.TW","6196.TW","1539.TW","2474.TW","1231.TW","9905.TW","9931.TW","1558.TW","3437.TW","2496.TW","5007.TW","2607.TW","1110.TW","2838.TW","3014.TW","3049.TW","1446.TW","9906.TW","1445.TW","4137.TW","911619.TW","03034P.TW","1817.TW","1304.TW"]

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
