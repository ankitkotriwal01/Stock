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
    available_tickers = ["001065.KS","096760.KS","001067.KS","089590.KS","005930.KS","000660.KS","055550.KS","034220.KS","036460.KS","017670.KS","010140.KS","005935.KS","004020.KS","003620.KS","001440.KS","000040.KS","128820.KS","097950.KS","088790.KS","086280.KS","066570.KS","051910.KS","042700.KS","042670.KS","032640.KS","020560.KS","015760.KS","011160.KS","011070.KS","011000.KS","009150.KS","008770.KS","008250.KS","006400.KS","005940.KS","005490.KS","004540.KS","002790.KS","000990.KS","185750.KS","161890.KS","138930.KS","138040.KS","133820.KS","129260.KS","128940.KS","123700.KS","120115.KS","119650.KS","105630.KS","103130.KS","102280.KS","097230.KS","085310.KS","081660.KS","069960.KS","066575.KS","060980.KS","058860.KS","052690.KS","047810.KS","047050.KS","044820.KS","042660.KS","039130.KS","035250.KS","034020.KS","027410.KS","027390.KS","025540.KS","023810.KS","019680.KS","019175.KS","018880.KS","018260.KS","017940.KS","017810.KS","015590.KS","012800.KS","012750.KS","012330.KS","010600.KS","010420.KS","010130.KS","010120.KS","009540.KS","009410.KS","009160.KS","008900.KS","007575.KS","007160.KS","007070.KS","006840.KS","006380.KS","005850.KS","005800.KS","005720.KS","005610.KS","005450.KS","005389.KS","005385.KS","005380.KS","004990.KS","004960.KS","004800.KS","004545.KS","004490.KS","004360.KS","004310.KS","004140.KS","003550.KS","003450.KS","003075.KS","002350.KS","002250.KS","002000.KS","001880.KS","001800.KS","001680.KS","001550.KS","001520.KS","001230.KS","001020.KS","000970.KS","000950.KS","000890.KS","000830.KS","000725.KS","000720.KS","000327.KS","000270.KS","000120.KS","016385.KS","000835.KS","068290.KS","020120.KS","014820.KS","003545.KS","009200.KS","007190.KS","002460.KS","051310.KS","039490.KS","000545.KS","500018.KS","005320.KS","001525.KS","005010.KS","068870.KS","001790.KS","009290.KS","005745.KS","192400.KS","036570.KS","011790.KS","550009.KS","214320.KS","051900.KS","001465.KS","003470.KS","75A511.KS","001620.KS","001740.KS","015020.KS","026890.KS","550014.KS","550003.KS","550010.KS","550004.KS","550005.KS","550006.KS","550007.KS","520001.KS","118000.KS","500019.KS","580004.KS","095570.KS","71301A1B.KS","530006.KS","183190.KS","085620.KS","71901A58.KS","152330.KS","530005.KS","500004.KS","500001.KS","590001.KS","500002.KS","570007.KS","570006.KS","530014.KS","001045.KS","011155.KS","001040.KS","097955.KS","011150.KS","000590.KS","112610.KS","520003.KS","520006.KS","520005.KS","520004.KS","500012.KS","500011.KS","530001.KS","500009.KS","002690.KS","004840.KS","155660.KS","210540.KS","737027S7.KS","570008.KS","530008.KS","530003.KS","530004.KS","500014.KS","530007.KS","500017.KS","500016.KS","530013.KS","500013.KS","500015.KS","530019.KS","530012.KS","570001.KS","500005.KS","159650.KS","006360.KS","123690.KS","213500.KS","58A598.KS","075580.KS","900050.KS","900140.KS","214330.KS","227840.KS","122900.KS","145210.KS","226320.KS","194370.KS","001060.KS","707017R9.KS","009440.KS","001390.KS","001940.KS","114090.KS","083420.KS","025850.KS","025000.KS","012200.KS","012030.KS","001750.KS","004370.KS","039570.KS","000080.KS","004365.KS","014910.KS","049770.KS","083380.KS","005180.KS","002600.KS","004450.KS","140890.KS","023150.KS","017370.KS","007980.KS","007570.KS","000215.KS","008700.KS","058850.KS","011500.KS","007197.KS","013570.KS","086790.KS","006805.KS","004690.KS","008110.KS","170900.KS","014160.KS","096775.KS","007210.KS","107590.KS","006390.KS","161000.KS","028260.KS","009190.KS","139480.KS","008420.KS","109070.KS","120110.KS","003920.KS","063160.KS","011200.KS","102260.KS","004560.KS","009270.KS","003419.KS","006405.KS","002100.KS","010770.KS","031440.KS","008260.KS","144620.KS","009275.KS","134380.KS","017390.KS","000300.KS","015350.KS","001720.KS","007340.KS","009320.KS","000325.KS","037560.KS","006110.KS","017900.KS","004920.KS","005257.KS","014680.KS","000700.KS","094280.KS","001140.KS","006040.KS","105560.KS","024070.KS","034730.KS","002030.KS","105840.KS","029780.KS","016710.KS","000810.KS","024900.KS","006260.KS","017550.KS","011300.KS","008500.KS","014580.KS","023530.KS","020150.KS","014825.KS","008600.KS","095720.KS","000087.KS","000540.KS","079660.KS","011280.KS","064960.KS","004770.KS","032350.KS","003465.KS","002550.KS","009680.KS","100220.KS","026940.KS","002360.KS","033920.KS","000520.KS","005820.KS","073240.KS","096770.KS","024090.KS","011810.KS","083600.KS","000105.KS","000430.KS","071840.KS","010690.KS","090430.KS","024720.KS","001130.KS","003200.KS","002795.KS","016090.KS","012205.KS","019180.KS","007690.KS","005680.KS","033530.KS","003300.KS","068875.KS","192530.KS","010955.KS","037710.KS","088350.KS","009970.KS","016590.KS","005620.KS","101060.KS","139200.KS","003410.KS","002410.KS","013367.KS","025820.KS","012690.KS","011720.KS","092630.KS","100250.KS","023350.KS","083590.KS","014915.KS","004380.KS","006880.KS","001780.KS","008040.KS","005950.KS","019490.KS","161390.KS","008775.KS","003720.KS","009415.KS","003830.KS","082640.KS","023960.KS","950010.KS","012600.KS","003560.KS","002787.KS","001527.KS","079430.KS","005255.KS","010780.KS","002300.KS","068400.KS","083610.KS","006200.KS","023000.KS","005500.KS","014285.KS","008350.KS","011700.KS","180640.KS","005750.KS","051905.KS","033240.KS","002270.KS","023450.KS","001500.KS","071055.KS","012450.KS","004985.KS","002780.KS","000650.KS","030200.KS","003535.KS","004200.KS","034310.KS","005390.KS","004415.KS","024110.KS","009830.KS","008560.KS","083370.KS","058730.KS","019685.KS","083620.KS","004740.KS","051915.KS","008930.KS","000030.KS","033180.KS","092230.KS","011390.KS","006650.KS","100840.KS","014530.KS","018500.KS","003280.KS","025530.KS","145270.KS","003240.KS","091090.KS","004980.KS","108670.KS","002840.KS","000370.KS","004105.KS","019300.KS","020760.KS","000210.KS","088980.KS","004830.KS","002810.KS","006890.KS","069260.KS","000547.KS","049800.KS","007860.KS","136490.KS","007310.KS","009140.KS","014830.KS","014990.KS","071320.KS","111770.KS","005250.KS","009470.KS","084690.KS","047040.KS","035000.KS","035150.KS","003010.KS","007110.KS","002005.KS","204320.KS","035420.KS","003680.KS","001630.KS","006125.KS","005725.KS","003220.KS","090080.KS","004565.KS","077500.KS","044380.KS","003540.KS","00781K.KS","081000.KS","033270.KS","002760.KS","002170.KS","008730.KS","001250.KS","009070.KS","000060.KS","005740.KS","071950.KS","000815.KS","004090.KS","000480.KS","009180.KS","030610.KS","005965.KS","003480.KS","090355.KS","017960.KS","064350.KS","011330.KS","018470.KS","126560.KS","009810.KS","004080.KS","009155.KS","103590.KS","002310.KS","000390.KS","002630.KS","001470.KS","000680.KS","004835.KS","530022.KS","034120.KS","072710.KS","002700.KS","000760.KS","092200.KS","006090.KS","005880.KS","090350.KS","005305.KS","008060.KS","015890.KS","001560.KS","003350.KS","010820.KS","153360.KS","082740.KS","003080.KS","078935.KS","015540.KS","023800.KS","071970.KS","001570.KS","093230.KS","033780.KS","006345.KS","015230.KS","012610.KS","093370.KS","003415.KS","010060.KS","005945.KS","002785.KS","000140.KS","007810.KS","012320.KS","007590.KS","002420.KS","083580.KS","003160.KS","093050.KS","011760.KS","078520.KS","102460.KS","011210.KS","000880.KS","009835.KS","019440.KS","010580.KS","093240.KS","010620.KS","000225.KS","000670.KS","104120.KS","003960.KS","030790.KS","058650.KS","001210.KS","002220.KS","089470.KS","090435.KS","036530.KS","083390.KS","013700.KS","120030.KS","001820.KS","011090.KS","001290.KS","004890.KS","013000.KS","140910.KS","016800.KS","005110.KS","001510.KS","032830.KS","003000.KS","530010.KS","005430.KS","014440.KS","015860.KS","090990.KS","006060.KS","012160.KS","005190.KS","069620.KS","003090.KS","015260.KS","011780.KS","006660.KS","214420.KS","001080.KS","003945.KS","004000.KS","011690.KS","009420.KS","069460.KS","002240.KS","145995.KS","069640.KS","004700.KS","002150.KS","031820.KS","025620.KS","163560.KS","006280.KS","003610.KS","001685.KS","001070.KS","004910.KS","003570.KS","032560.KS","019170.KS","021240.KS","079160.KS","003530.KS","008020.KS","001725.KS","090970.KS","003460.KS","001460.KS","071050.KS","000070.KS","016380.KS","72501A3B.KS","003940.KS","008000.KS","007280.KS","025560.KS","016450.KS","530017.KS","024890.KS","005810.KS","003120.KS","084870.KS","001770.KS","001275.KS","002210.KS","007630.KS","002070.KS","010640.KS","172580.KS","004130.KS","003780.KS","181710.KS","014710.KS","003475.KS","004970.KS","003580.KS","001420.KS","02826K.KS","004270.KS","035510.KS","004870.KS","025890.KS","121550.KS","013870.KS","001340.KS","011170.KS","002710.KS","000640.KS","007610.KS","084680.KS","031430.KS","004989.KS","000157.KS","053210.KS","028100.KS","74401722.KS","003547.KS","004170.KS","016580.KS","005830.KS","002880.KS","053690.KS","008870.KS","006370.KS","000075.KS","003555.KS","005030.KS","027740.KS","110570.KS","004135.KS","012170.KS","016880.KS","012510.KS","002025.KS","072130.KS","033660.KS","010100.KS","530018.KS","001530.KS","067830.KS","074610.KS","007660.KS","083570.KS","002140.KS","003490.KS","017180.KS","079550.KS","000400.KS","72503A3B.KS","72502A3B.KS","72504A3B.KS","138250.KS","530011.KS","03473K.KS","006120.KS","018670.KS","001745.KS","210980.KS","001515.KS","077970.KS","009310.KS","214390.KS","028670.KS"]

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
