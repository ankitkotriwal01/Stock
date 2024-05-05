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
    available_tickers = ["067290.KQ","126600.KQ","122870.KQ","088290.KQ","069510.KQ","057880.KQ","037460.KQ","036540.KQ","032500.KQ","950130.KQ","222800.KQ","171120.KQ","150840.KQ","143240.KQ","141080.KQ","121890.KQ","121800.KQ","121440.KQ","104830.KQ","104200.KQ","102210.KQ","101240.KQ","099440.KQ","099190.KQ","098660.KQ","097780.KQ","093920.KQ","091440.KQ","090730.KQ","090460.KQ","089010.KQ","085660.KQ","083650.KQ","083470.KQ","081580.KQ","081150.KQ","080420.KQ","080000.KQ","079950.KQ","078130.KQ","078020.KQ","068930.KQ","068790.KQ","068760.KQ","068270.KQ","068050.KQ","067000.KQ","065940.KQ","065680.KQ","065510.KQ","060720.KQ","060590.KQ","060540.KQ","060230.KQ","058820.KQ","058630.KQ","057030.KQ","056190.KQ","056000.KQ","054800.KQ","054540.KQ","054090.KQ","053160.KQ","052300.KQ","051370.KQ","049120.KQ","048550.KQ","046440.KQ","045890.KQ","044960.KQ","044490.KQ","044340.KQ","043610.KQ","041510.KQ","041460.KQ","041020.KQ","040610.KQ","039030.KQ","038880.KQ","038620.KQ","038060.KQ","038010.KQ","037370.KQ","036830.KQ","036710.KQ","036670.KQ","036220.KQ","036190.KQ","036010.KQ","035900.KQ","035610.KQ","034940.KQ","032800.KQ","031860.KQ","030530.KQ","026040.KQ","025270.KQ","024840.KQ","023460.KQ","022100.KQ","016600.KQ","013120.KQ","012620.KQ","011560.KQ","010280.KQ","009620.KQ","007770.KQ","006910.KQ","003800.KQ","014200.KQ","136540.KQ","092040.KQ","083660.KQ","033130.KQ","093190.KQ","068060.KQ","059100.KQ","025880.KQ","226440.KQ","200710.KQ","054210.KQ","033100.KQ","106240.KQ","025770.KQ","024830.KQ","038070.KQ","025900.KQ","013720.KQ","087220.KQ","021045.KQ","023600.KQ","232140.KQ","045100.KQ","066700.KQ","015750.KQ","217620.KQ","056090.KQ","039020.KQ","048870.KQ","082210.KQ","115180.KQ","101170.KQ","097800.KQ","046970.KQ","215360.KQ","115440.KQ","205100.KQ","193250.KQ","122640.KQ","219960.KQ","115960.KQ","138360.KQ","215090.KQ","235010.KQ","196170.KQ","117670.KQ","123750.KQ","065660.KQ","121600.KQ","094170.KQ","211270.KQ","054620.KQ","127710.KQ","067390.KQ","900110.KQ","090470.KQ","224110.KQ","182400.KQ","950110.KQ","200780.KQ","208710.KQ","217730.KQ","060900.KQ","207760.KQ","008470.KQ","206640.KQ","225530.KQ","049180.KQ","053300.KQ","900120.KQ","221610.KQ","900250.KQ","225650.KQ","160980.KQ","196490.KQ","215480.KQ","215580.KQ","140520.KQ","217270.KQ","113810.KQ","049520.KQ","230490.KQ","192080.KQ","187220.KQ","213420.KQ","225440.KQ","217600.KQ","173940.KQ","223310.KQ","221200.KQ","092870.KQ","185490.KQ","033290.KQ","189690.KQ","215100.KQ","192410.KQ","194510.KQ","063080.KQ","142280.KQ","187420.KQ","217190.KQ","049080.KQ","130740.KQ","206660.KQ","219580.KQ","215000.KQ","227950.KQ","208370.KQ","215380.KQ","076610.KQ","214680.KQ","219860.KQ","208870.KQ","900090.KQ","230240.KQ","218150.KQ","214870.KQ","010240.KQ","200470.KQ","221840.KQ","149980.KQ","217500.KQ","900180.KQ","900080.KQ","900130.KQ","226340.KQ","094840.KQ","200670.KQ","221950.KQ","145020.KQ","170030.KQ","189980.KQ","226360.KQ","230980.KQ","225430.KQ","068940.KQ","143160.KQ","220630.KQ","226350.KQ","114810.KQ","124500.KQ","225570.KQ","214270.KQ","208640.KQ","222390.KQ","232270.KQ","208350.KQ","221980.KQ","093320.KQ","226850.KQ","218710.KQ","067570.KQ","192440.KQ","071850.KQ","102940.KQ","224060.KQ","222080.KQ","050540.KQ","092070.KQ","046310.KQ","024910.KQ","008370.KQ","065530.KQ","053950.KQ","080010.KQ","091590.KQ","013310.KQ","064240.KQ","045060.KQ","104480.KQ","052220.KQ","005990.KQ","078070.KQ","002290.KQ","060560.KQ","138690.KQ","101390.KQ","091580.KQ","052260.KQ","109080.KQ","021650.KQ","014470.KQ","046390.KQ","075130.KQ","027830.KQ","133750.KQ","042520.KQ","051780.KQ","080520.KQ","015710.KQ","039240.KQ","052190.KQ","194610.KQ","080470.KQ","028150.KQ","119850.KQ","039200.KQ","177830.KQ","012790.KQ","084650.KQ","222980.KQ","017000.KQ","050110.KQ","204440.KQ","066910.KQ","033790.KQ","035200.KQ","080530.KQ","023760.KQ","141070.KQ","131090.KQ","030190.KQ","043650.KQ","065770.KQ","061970.KQ","038950.KQ","205470.KQ","191420.KQ","039440.KQ","037230.KQ","095340.KQ","039420.KQ","115310.KQ","053060.KQ","131970.KQ","039310.KQ","032820.KQ","096690.KQ","073110.KQ","079000.KQ","061460.KQ","086960.KQ","053870.KQ","038110.KQ","036690.KQ","033160.KQ","019010.KQ","119860.KQ","044060.KQ","026910.KQ","010470.KQ","212560.KQ","089030.KQ","032080.KQ","042370.KQ","090360.KQ","078600.KQ","096530.KQ","109860.KQ","041190.KQ","083310.KQ","067010.KQ","065150.KQ","085910.KQ","065690.KQ","046890.KQ","021320.KQ","109610.KQ","053350.KQ","058220.KQ","040420.KQ","094820.KQ","034950.KQ","204630.KQ","208140.KQ","050090.KQ","054920.KQ","073570.KQ","046210.KQ","008800.KQ","046940.KQ","155650.KQ","035080.KQ","036630.KQ","052290.KQ","033230.KQ","000250.KQ","024060.KQ","060300.KQ","014940.KQ","031390.KQ","130500.KQ","032580.KQ","041930.KQ","122690.KQ","041140.KQ","086830.KQ","053050.KQ","067770.KQ","215750.KQ","101330.KQ","036120.KQ","035460.KQ","024950.KQ","007370.KQ","171010.KQ","073070.KQ","013810.KQ","039230.KQ","060480.KQ","050320.KQ","064800.KQ","151860.KQ","095500.KQ","170920.KQ","182690.KQ","070300.KQ","013030.KQ","053260.KQ","065450.KQ","039740.KQ","063170.KQ","058610.KQ","119830.KQ","222810.KQ","032685.KQ","023900.KQ","067730.KQ","061040.KQ","037350.KQ","101670.KQ","065950.KQ","016920.KQ","074430.KQ","134780.KQ","002230.KQ","042500.KQ","043910.KQ","214450.KQ","004650.KQ","101680.KQ","049720.KQ","032750.KQ","111820.KQ","136510.KQ","074600.KQ","039670.KQ","049550.KQ","036420.KQ","043710.KQ","045970.KQ","017480.KQ","127160.KQ","043150.KQ","039840.KQ","060910.KQ","094860.KQ","100660.KQ","065130.KQ","051160.KQ","200130.KQ","041590.KQ","046140.KQ","158310.KQ","084180.KQ","048910.KQ","024660.KQ","066270.KQ","082850.KQ","028040.KQ","078650.KQ","140410.KQ","115480.KQ","090740.KQ","047920.KQ","032850.KQ","100700.KQ","138080.KQ","051980.KQ","192390.KQ","122350.KQ","019570.KQ","070590.KQ","043200.KQ","032960.KQ","039980.KQ","090850.KQ","084110.KQ","020180.KQ","021880.KQ","042040.KQ","078860.KQ","100090.KQ","094970.KQ","021040.KQ","036810.KQ","052900.KQ","054950.KQ","047080.KQ","033600.KQ","031310.KQ","056360.KQ","032940.KQ","047770.KQ","012860.KQ","024850.KQ","058450.KQ","019210.KQ","039290.KQ","105740.KQ","026150.KQ","131290.KQ","060310.KQ","064480.KQ","053450.KQ","032540.KQ","051380.KQ","067920.KQ","016170.KQ","078940.KQ","033560.KQ","019550.KQ","053660.KQ","087730.KQ","123570.KQ","018000.KQ","032860.KQ","083790.KQ","058470.KQ","052400.KQ","065560.KQ","086980.KQ","095910.KQ","138610.KQ","046070.KQ","058400.KQ","114190.KQ","065440.KQ","067990.KQ","073640.KQ","038680.KQ","023430.KQ","043360.KQ","041520.KQ","166480.KQ","082270.KQ","112040.KQ","018620.KQ","056730.KQ","065650.KQ","088390.KQ","086040.KQ","115530.KQ","040160.KQ","108380.KQ","027580.KQ","053270.KQ","077280.KQ","067080.KQ","079190.KQ","025440.KQ","091120.KQ","131390.KQ","026960.KQ","030520.KQ","131030.KQ","056080.KQ","066110.KQ","006140.KQ","095190.KQ","109820.KQ","007530.KQ","049950.KQ","056700.KQ","043340.KQ","106080.KQ","019660.KQ","089890.KQ","024800.KQ","178920.KQ","191410.KQ","141000.KQ","099410.KQ","159910.KQ","037950.KQ","160600.KQ","011370.KQ","090710.KQ","023770.KQ","051490.KQ","108230.KQ","083930.KQ","072870.KQ","137940.KQ","095610.KQ","050120.KQ","044780.KQ","203650.KQ","023890.KQ","032980.KQ","052460.KQ","019540.KQ","126880.KQ","063570.KQ","115500.KQ","060250.KQ","192250.KQ","045340.KQ","038340.KQ","005860.KQ","217820.KQ","048470.KQ","033050.KQ","194480.KQ","204620.KQ","085670.KQ","119610.KQ","066130.KQ","105550.KQ","042600.KQ","197210.KQ","102710.KQ","000440.KQ","046120.KQ","036930.KQ","073190.KQ","032620.KQ","101160.KQ","053590.KQ","066980.KQ","207930.KQ","037070.KQ","147830.KQ","046110.KQ","009730.KQ","052270.KQ","123420.KQ","001540.KQ","072770.KQ","036490.KQ","206560.KQ","131220.KQ","104040.KQ","022220.KQ","064520.KQ","036560.KQ","025870.KQ","032680.KQ","051360.KQ","096040.KQ","032190.KQ","047560.KQ","127120.KQ","114570.KQ","080160.KQ","078590.KQ","137400.KQ","089980.KQ","036800.KQ","043370.KQ","126700.KQ","007390.KQ","149940.KQ","063440.KQ","028080.KQ","123040.KQ","049070.KQ","187270.KQ","003100.KQ","100120.KQ","104540.KQ","019590.KQ","029480.KQ","071670.KQ","155960.KQ","065620.KQ","203690.KQ","066310.KQ","060570.KQ","031330.KQ","036000.KQ","038500.KQ","082660.KQ","068240.KQ","023790.KQ","042110.KQ","053610.KQ","053810.KQ","052860.KQ","051390.KQ","057540.KQ","051170.KQ","006920.KQ","014970.KQ","047820.KQ","114630.KQ","036030.KQ","059120.KQ","140860.KQ","091340.KQ","007820.KQ","213090.KQ","064260.KQ","048770.KQ","066670.KQ","065570.KQ","045510.KQ","062860.KQ","024880.KQ","054340.KQ","092730.KQ","032040.KQ","126640.KQ","099830.KQ","084990.KQ","096640.KQ","080440.KQ","043580.KQ","119500.KQ","060150.KQ","217810.KQ","030270.KQ","130580.KQ","004780.KQ","086900.KQ","092600.KQ","222420.KQ","006730.KQ","064760.KQ","036170.KQ","043290.KQ","090150.KQ","095270.KQ","053290.KQ","050860.KQ","073010.KQ","036500.KQ","037440.KQ","065350.KQ","020400.KQ","036180.KQ","032790.KQ","039560.KQ","121850.KQ","064550.KQ","122800.KQ","005710.KQ","011080.KQ","052770.KQ","101490.KQ","092130.KQ","088130.KQ","128660.KQ","100130.KQ","018310.KQ","086670.KQ","075970.KQ","086200.KQ","159580.KQ","009520.KQ","038390.KQ","064820.KQ","089530.KQ","131180.KQ","043090.KQ","086450.KQ","006050.KQ","037330.KQ","071280.KQ","198440.KQ","001840.KQ","043220.KQ","069080.KQ","120240.KQ","215200.KQ","067310.KQ","037400.KQ","050760.KQ","093380.KQ","049630.KQ","095300.KQ","030350.KQ","099660.KQ","066430.KQ","039340.KQ","095700.KQ","089150.KQ","026260.KQ","052330.KQ","067900.KQ","091970.KQ","085370.KQ","207720.KQ","068330.KQ","076080.KQ","139050.KQ","016100.KQ","054300.KQ","009300.KQ","033430.KQ","078140.KQ","054940.KQ","214430.KQ","038540.KQ","214310.KQ","205500.KQ","072020.KQ","083450.KQ","101000.KQ","058110.KQ","105330.KQ","078160.KQ","059090.KQ","214150.KQ","051500.KQ","092460.KQ","079970.KQ","106520.KQ","025550.KQ","064290.KQ","043260.KQ","137950.KQ","066790.KQ","112240.KQ","054040.KQ","065160.KQ","134580.KQ","218410.KQ","059210.KQ","079940.KQ","096630.KQ","204650.KQ","115450.KQ","236200.KQ","206400.KQ","023910.KQ","017680.KQ","039790.KQ","067160.KQ","060260.KQ","042420.KQ","014100.KQ","141020.KQ","027710.KQ","060370.KQ","138070.KQ","094190.KQ","042510.KQ","024740.KQ","036480.KQ","130960.KQ","038870.KQ","014190.KQ","139670.KQ","040910.KQ","078350.KQ","066410.KQ","054180.KQ","033320.KQ","053110.KQ","098120.KQ","204760.KQ","054670.KQ","097870.KQ","020710.KQ","104460.KQ","016670.KQ","123840.KQ","053700.KQ","093520.KQ","086520.KQ","111870.KQ","101400.KQ","049480.KQ","079650.KQ","089140.KQ","151910.KQ","014620.KQ","033340.KQ","106190.KQ","053800.KQ","039830.KQ","067280.KQ","083550.KQ","079370.KQ","219550.KQ","149950.KQ","012700.KQ","095660.KQ","041910.KQ","154040.KQ","066620.KQ","196700.KQ","084730.KQ","048830.KQ","078150.KQ","058420.KQ","018680.KQ","089230.KQ","019990.KQ","035890.KQ","099320.KQ","131370.KQ","065500.KQ","045520.KQ","092300.KQ","072520.KQ","204840.KQ","096610.KQ","052600.KQ","114450.KQ","109740.KQ","088800.KQ","098460.KQ","081970.KQ","064090.KQ","078340.KQ","054780.KQ","041960.KQ","093640.KQ","048430.KQ","039860.KQ","060380.KQ","033110.KQ","017250.KQ","084370.KQ","037340.KQ","225590.KQ","900070.KQ","180400.KQ","187790.KQ","190510.KQ","160550.KQ","126870.KQ","900100.KQ","215790.KQ","222040.KQ","080580.KQ","222110.KQ","087010.KQ","087600.KQ","189860.KQ","057500.KQ","900040.KQ","219130.KQ","019770.KQ","195990.KQ","142210.KQ","177350.KQ","072470.KQ","214370.KQ","175140.KQ","03663016.KQ","223040.KQ","220260.KQ","214180.KQ","131760.KQ"]

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
