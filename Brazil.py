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
    available_tickers = ["LAME4.SA","ABEV3.SA","VALE5.SA","SBSP3.SA","VALE3.SA","PETR4.SA","OIBR4.SA","BBDC4.SA","MRVE3.SA","ITUB4.SA","EMBR3.SA","CYRE3.SA","BTOW3.SA","BRKM5.SA","USIM3.SA","BVMF3.SA","BBDC3.SA","PRML3.SA","MRFG3.SA","JBSS3.SA","DTEX3.SA","CPLE6.SA","CPFE3.SA","CGAS5.SA","USIM5.SA","TAEE11.SA","RSID3.SA","PFRM3.SA","PCAR4.SA","CESP6.SA","BBAS3.SA","VLID3.SA","SNSY6.SA","SNSY3.SA","RPMG3.SA","RNGO11.SA","MRSA-DEB72B0.SA","JBDU4.SA","HOME34.SA","GRND3.SA","GEPA3.SA","TBLE3.SA","SMLE3.SA","REDE3.SA","PDGR3.SA","MMXM3.SA","KROT3.SA","EXXO34.SA","ELET3.SA","ECOR3.SA","XBOV11.SA","WEGE3.SA","TIFF34.SA","FIBR3.SA","FDXB34.SA","FBOK34.SA","WPLZ11B.SA","HGTX3.SA","LFFE3.SA","BBVJ11.SA","CEGR3.SA","JNJB34.SA","LFFE4.SA","JSRE11.SA","JPPC11.SA","HGJH11.SA","JSLG3F.SA","MCRJ11B.SA","JSLG-DEB63L1.SA","SJOS4F.SA","JSLG-DEB61B0.SA","JBDU3.SA","JPMC34.SA","JOPA4F.SA","MEND3.SA","MEND5.SA","TEKA3.SA","MYPK3.SA","BERK34F.SA","BERK34.SA","KLBN4.SA","ELEK3.SA","MYPK-DCA61L0.SA","MCDC34.SA","NATU3.SA","BSAN33.SA","TECN3.SA","NFLX34.SA","OIBR3.SA","CCRO3.SA","RUMO3.SA","PRIO3.SA","OSXB3.SA","ORCL34.SA","ODPV3.SA","GEOO34F.SA","GEOO34.SA","FDMO34.SA","CTIP3.SA","CSCO34F.SA","CPLE3.SA","CMIG4.SA","CBOP11.SA","AMZO34.SA","SULT3F.SA","NUTR3F.SA","FJTA11.SA","CPTP3B.SA","CEPE3F.SA","CBEE3F.SA","PTNT3F.SA","XPOM11.SA","BNBR3F.SA","OIBR-DEB92L0.SA","CEEB3F.SA","EKTR3F.SA","SNSL3F.SA","ECOO11.SA","OFSA3.SA","TKNO4.SA","JOPA4.SA","BMTO4.SA","OVSA-DEB31B0.SA","RUMO9.SA","SCLO3F.SA","BMTO3.SA","OPRE1B.SA","UGPA3.SA","TIMP3.SA","QUAL3.SA","SINQ11.SA","FVPQ11.SA","QCOM34.SA","FCCQ11.SA","QGEP3.SA","QCOM34F.SA","QVQP3B.SA","TWTR34.SA","GGBR4.SA","SEER3.SA","VIVT4.SA","UTEC34.SA","UPSS34.SA","UPAC34F.SA","UCAS3.SA","MGLU3.SA","GOAU4.SA","VISA34F.SA","VISA34.SA","VERZ34F.SA","PSVM11.SA","IDIV11.SA","ECOV-DEB21B0.SA","VRTA11.SA","VALE-DEB84B0.SA","ESUT11.SA","IBOV11.SA","AZEV4.SA","VALE-DEB81B0.SA","CRIV4.SA","SINC11L.SA","BRIV4.SA","MSRO3.SA","VALE-DEB84L0.SA","OVSA-DEB32L0.SA","XBOV11F.SA","ENEV3.SA","VALE-DEB83L1.SA","ECOV-DEB22L1.SA","VIVR3.SA","ECOV-DEB21L0.SA","GRLV11.SA","VERZ34.SA","VALE-DEB92B0.SA","WHRL4.SA","TWXB34F.SA","RNEW3.SA","MWET3.SA","SHOW3.SA","SPTW11.SA","KEPL11.SA","WUNI34F.SA","WTVP-CRI11L1.SA","WALM34.SA","RNEW2.SA","RNEW12.SA","KEPL3.SA","LINX3.SA","CTAX4.SA","CHVX34.SA","AGCX11.SA","TXRX4.SA","XBOV.SA","BDRX11.SA","FIXX11.SA","BRAX11.SA","INDX11.SA","CTAX3.SA","IGCX11.SA","XTED11.SA","NFLX34F.SA","DTEX-DCA11L0.SA","MLCX11.SA","HTMX11B.SA","XVTE5L.SA","XPCM11.SA","IEEX11.SA","TXRX3.SA","CHVX34F.SA","IBXX11.SA","TXRX3F.SA","DTEX-DCA11L1.SA","IFIX11.SA","XPTD11.SA","TTEX5L.SA","XRXB34.SA","XRXB34F.SA","IVBX11.SA","CTAX11.SA","XPGA11.SA","SNSY6F.SA","HSHY34F.SA","EBAY34.SA","DTCY3.SA","SNSY3F.SA","YPFL3.SA","COTY34F.SA","TUPY3.SA","SNSY5.SA","WMBY3F.SA","PABY11.SA","HSHY34.SA","EBAY34F.SA","BONY34F.SA","WMBY3.SA","FLRY3.SA","LILY34.SA","COTY34.SA","BONY34.SA","LILY34F.SA","CRUZ3.SA","MDLZ34F.SA","MDLZ34.SA","ARZZ3.SA","PFIZ34F.SA","PFIZ34.SA","ITSA4.SA","TGMA3.SA","PSSA3.SA","ITSA3.SA","GFSA3.SA","DASA3.SA","BAZA3.SA","ALPA4.SA","AAPL34F.SA","AAPL34.SA","MSPA4.SA","MTSA3F.SA","GEPA3F.SA","OGSA3.SA","MSPA4F.SA","CTSA4.SA","FJTA4.SA","CBMA4F.SA","CGRA3.SA","PTPA3F.SA","MDIA3.SA","IGTA3.SA","CTSA3.SA","GAFL-CRAA2L1.SA","MRSA5B.SA","MSPA3.SA","HAGA4.SA","MRSA3BF.SA","HAGA3.SA","MRSA5BF.SA","FESA4.SA","HETA3.SA","PTPA4.SA","EUCA3F.SA","PTPA4F.SA","CBMA3.SA","HETA3F.SA","FESA3.SA","CBMA3F.SA","TEKA4.SA","JOPA3.SA","CBMA4.SA","MRSA6B.SA","CAIA3B.SA","HETA4.SA","TEKA3F.SA","MRSA6BF.SA","GEPA4.SA","SFSA4.SA","ENMA6B.SA","CTKA3F.SA","CTKA3.SA","CTKA4.SA","EUCA3.SA","TCSA3.SA","CGRA4.SA","SUIA4L.SA","LUPA3.SA","MTSA3.SA","MRSA3B.SA","JOPA3F.SA","ENMA3B.SA","IGSA5L.SA","GAFL-CRAA2B0.SA","ENMA3BF.SA","PTPA3.SA","EUCA4.SA","FJTA3.SA","FRTA3.SA","CSNA3.SA","ALPA3.SA","MTSA4.SA","BPHA3.SA","BEMA3.SA","COCA34F.SA","TEXA34.SA","ABTT34F.SA","BPFF11.SA","PMSP13B.SA","ABCB10.SA","ABTT34.SA","COCA34.SA","ABCB10F.SA","ABCP11.SA","ABCB10L.SA","TEXA34F.SA","ABCB4.SA","ABCB2.SA","ACNB34.SA","ACNB34F.SA","RBRA-CRI98L1.SA","GAIA-CRI5JB0.SA","ECOA-CRA74L1.SA","ECOA-CRA73L0.SA","EALT3.SA","RBRA-CRI77L0.SA","GAIA-CRI40L1.SA","BOVA11.SA","ECOA-CRA68L1.SA","RBRA-CRI1XL0.SA","EALT4F.SA","AETA-CRI10L1.SA","RBRA-CRI81L0.SA","BCIA11.SA","EALT3F.SA","CTBA11B.SA","GAIA-CRI48B0.SA","RBRA-CRI07B0.SA","ECOA-CRA74B0.SA","GAIA-CRI48L0.SA","RBRA-CRI94L0.SA","RBRA-CRI96L0.SA","RBRA-CRI77B0.SA","RBRA-CRI97L1.SA","RBRA-CRI99L0.SA","GAIA-CRI5IB0.SA","RBRA-CRI98B0.SA","RBRA-CRI68L1.SA","RBRA-CRI44L1.SA","GAIA-CRI5BB0.SA","EALT4.SA","SULA11.SA","GAIA-CRI5BL0.SA","RBRA-CRI80L1.SA","AETA-CRI10L0.SA","RBRA-CRI44L0.SA","RBRA-CRI70B0.SA","GAIA-CRI5IL0.SA","RBRA-CRI93L1.SA","ECOA-CRA72L1.SA","ECOA-CRA72L0.SA","RBRA-CRI1XB0.SA","GAIA-CRI35B0.SA","GAIA-CRI47L1.SA","GAIA-CRI47B0.SA","RBRA-CRIA2B0.SA","GAIA-CRI780B.SA","RBRA-CRIA2L1.SA","RBRA-CRI90L0.SA","ECOA-CRA74L0.SA","ECOA-CRA68L0.SA","GAIA-CRI5JL0.SA","GAIA-CRI470B.SA","ECOA-CRA73L1.SA","RBRA-CRI90L1.SA","THRA11B.SA","RBRA-CRI77L1.SA","GAIA-CRI48L1.SA","RBRA-CRIA2L0.SA","FLMA11.SA","RBRA-CRI68L0.SA","GAIA-CRI40B0.SA","RBRA-CRI07L1.SA","RBRA-CRI93L0.SA","ECOA-CRA73B0.SA","RBRA-CRI97B0.SA","ECOA-CRA68B0.SA","GAIA-CRI5BL1.SA","EDGA11B.SA","RBRA-CRI94L1.SA","RBRA-CRI94B0.SA","RBRA-CRI90B0.SA","ATSA11B.SA","RESA-DEB13B0.SA","IGTA-DEB41L1.SA","RESA-DEB11L0.SA","TRIA-DEB21L0.SA","GFSA-DEB82L1.SA","CALI4.SA","LBRA-DEB11L0.SA","RESA-DEB12B0.SA","IGTA-DEB42L0.SA","BTTL3.SA","MRSA-DEB72L0.SA","RESA-DEB12L1.SA","LBRA-DEB11B0.SA","R2:BTTL3S.SA","BRGE3.SA","BRGE7.SA","BRGE8.SA","OVSA-DEB31L0.SA","BESA-DEB12L1.SA","OVSA-DEB31L1.SA","BESA-DEB12L0.SA","RPTA-DEB22L0.SA","BESA-DEB11L0.SA","IGTA-DEB41B0.SA","BRGE12.SA","BTTL4.SA","CALI3.SA","RESA-DEB11B0.SA","TRIA-DEB21L1.SA","BRGE5.SA","RPTA-DEB21B0.SA","BESA-DEB110B.SA","GFSA-DEB82L0.SA","TRIA-DEB21B0.SA","IGTA-DEB42B0.SA","GFSA-DEB82B0.SA","TRIA-DEB22B0.SA","MRSA-DEB710B.SA","FRTA1.SA","MRSA-DEB72L1.SA","RESA-DEB13L0.SA","IGTA-DEB21L0.SA","RESA-DEB13L1.SA","RPTA-DEB22L1.SA","RPTA-DEB21L1.SA","OGSA-DCA320B.SA","TRIA-DEB22L1.SA","OVSA-DEB32L1.SA","BRGE11.SA","TRIA-DEB22L0.SA","BRGE6.SA","TIET-DEB41B0.SA","TIET-DEB42L0.SA","TIET4.SA","AELP3F.SA","TIET-DEB43L0.SA","AEFI11.SA","GETI3.SA","TIET-DEB41L1.SA","TIET11.SA","TIET-DEB43B0.SA","PMSP11B.SA","TIET3.SA","AELP3.SA","GETI4.SA","AFLU3.SA","AFLT3.SA","AFLU5.SA","AFLU5F.SA","AFLT3F.SA","AFLU3F.SA","ANDG3B.SA","AGRO3.SA","VAGR3.SA","AGEN33.SA","GAFL-CRA01L0.SA","GAFL-CRA02L0.SA","GAFL-CRA31B0.SA","AGRU-DEB21L1.SA","UNAG-FIDS10B.SA","GAFL-CRA31L1.SA","AGEN33F.SA","SAAG11.SA","CASN3.SA","AGTE7L.SA","CASN4.SA","GAFL-CRA81L0.SA","FAGR-FID010B.SA","FPAB11.SA","AGPR5L.SA","SLCE3.SA","CVCB3.SA","GAFL-CRA810B.SA","GAFL-CRA02L1.SA","AGBC6L.SA","GAFL-CRA11L1.SA","FAGR-FID01B0.SA","GAFL-CRA01B0.SA","DAGB33.SA","GAFL-CRA1DB0.SA","AGSA5L.SA","AGVE5L.SA","EMAE4.SA","GAFL-CRA1DL1.SA","AGRU-DEB210B.SA","GAFL-CRA11L0.SA","AGVE6L.SA","AHEB3.SA","AHEB3F.SA","AHEB6.SA","AHEB5.SA","AHEB5F.SA","GOLL4.SA","TAXA4L.SA","TAXA161.SA","TAXA17.SA","TAXA63.SA","TAXA106.SA","TAXA345.SA","TAXA129.SA","TAXA303.SA","TAXA310.SA","TAXA210.SA","TAXA35.SA","TAXA59.SA","TAXA19.SA","TAXA31L.SA","TAXA20L.SA","TAXA148.SA","TAXA22.SA","TAXA143.SA","TAXA302.SA","TAXA47.SA","TAXA212.SA","TAXA295.SA","TAXA74.SA","TAXA50.SA","TAXA165.SA","TAXA58L.SA","TAXA260.SA","TAXA32.SA","TAXA123.SA","TAXA69.SA","TAXA265.SA","TAXA41.SA","TAXA362.SA","TAXA109.SA","TAXA232.SA","TAXA242.SA","TAXA319.SA","TAXA262.SA","TAXA113.SA","TAXA170.SA","TAXA85.SA","TAXA256.SA","TAXA193.SA","TAXA104.SA","TAXA21L.SA","TAXA86.SA","TAXA86L.SA","TAXA42.SA","TAXA361.SA","TAXA246.SA","TAXA307.SA","TAXA311.SA","TAXA24.SA","TAXA146.SA","TAXA304.SA","TAXA263.SA","TAXA171.SA","TAXA321.SA","TAXA29.SA","TAXA88L.SA","TAXA332.SA","TAXA71.SA","TAXA342.SA","TAXA87.SA","TAXA43L.SA","TAXA344.SA","TAXA221.SA","TAXA350.SA","TAXA247.SA","TAXA339.SA","TAXA200.SA","TAXA142.SA","TAXA16.SA","TAXA287.SA","TAXA65.SA","TAXA250.SA","TAXA45L.SA","TAXA215.SA","TAXA202.SA","TAXA70L.SA","TAXA36L.SA","TAXA364.SA","TAXA90.SA","TAXA141.SA","TAXA75.SA","TAXA189.SA","TAXA58.SA","TAXA145.SA","TAXA251.SA","TAXA329.SA","TAXA192.SA","TAXA78.SA","TAXA312.SA","TAXA149.SA","TAXA294.SA","TAXA282.SA","TAXA57.SA","TAXA341.SA","TAXA116.SA","TAXA128.SA","TAXA44L.SA","TAXA158.SA","TAXA37.SA","TAXA328.SA","TAXA203.SA","TAXA228.SA","TAXA183.SA","TAXA283.SA","TAXA172.SA","TAXA164.SA","TAXA138.SA","TAXA249.SA","TAXA64L.SA","TAXA73L.SA","TAXA248.SA","TAXA71L.SA","TAXA290.SA","TAXA351.SA","TAXA365.SA","TAXA359.SA","TAXA76.SA","TAXA110.SA","TAXA49L.SA","TAXA18L.SA","TAXA244.SA","TAXA155.SA","TAXA39L.SA","TAXA79L.SA","TAXA261.SA","TAXA69L.SA","TAXA285.SA","TAXA60.SA","TAXA105.SA","TAXA211.SA","TAXA135.SA","TAXA225.SA","TAXA84L.SA","TAXA100.SA","TAXA85L.SA","TAXA322.SA","TAXA198.SA","TAXA114.SA","TAXA67.SA","TAXA130.SA","TAXA80.SA","TAXA90L.SA","TAXA201.SA","TAXA305.SA","TAXA26L.SA","TAXA313.SA","TAXA340.SA","TAXA118.SA","TAXA38.SA","TAXA6L.SA","TAXA337.SA","TAXA178.SA","TAXA296.SA","TAXA357.SA","TAXA194.SA","TAXA79.SA","TAXA91.SA","TAXA207.SA","TAXA360.SA","TAXA355.SA","TAXA34L.SA","TAXA185.SA","TAXA157.SA","TAXA77.SA","TAXA88.SA","TAXA94L.SA","TAXA163.SA","TAXA224.SA","TAXA92L.SA","TAXA343.SA","TAXA96L.SA","TAXA17L.SA","TAXA117.SA","TAXA235.SA","TAXA57L.SA","TAXA147.SA","TAXA356.SA","TAXA126.SA","TAXA234.SA","TAXA274.SA","TAXA98.SA","TAXA18.SA","TAXA68L.SA","TAXA349.SA","TAXA308.SA","TAXA5L.SA","TAXA245.SA","TAXA236.SA","TAXA363.SA","TAXA36.SA","TAXA213.SA","TAXA293.SA","TAXA190.SA","TAXA179.SA","TAXA83.SA","TAXA136.SA","LATM33.SA","TAXA233.SA","TAXA53.SA","TAXA227.SA","TAXA41L.SA","TAXA222.SA","TAXA196.SA","TAXA334.SA","TAXA267.SA","TAXA209.SA","TAXA238.SA","TAXA177.SA","TAXA353.SA","TAXA336.SA","TAXA27.SA","TAXA150.SA","TAXA354.SA","TAXA258.SA","TAXA318.SA","TAXA315.SA","TAXA28L.SA","TAXA127.SA","TAXA95L.SA","TAXA152.SA","TAXA205.SA","TAXA99.SA","TAXA125.SA","TAXA42L.SA","TAXA252.SA","TAXA324.SA","TAXA167.SA","TAXA63L.SA","TAXA254.SA","TAXA231.SA","TAXA180.SA","TAXA191.SA","TAXA346.SA","TAXA97L.SA","TAXA55.SA","TAXA175.SA","TAXA284.SA","TAXA77L.SA","TAXA219.SA","TAXA320.SA","TAXA281.SA","TAXA23L.SA","TAXA55L.SA","TAXA217.SA","TAXA352.SA","TAXA62.SA","TAXA184.SA","TAXA187.SA","TAXA84.SA","TAXA31.SA","TAXA62L.SA","TAXA279.SA","TAXA0L.SA","TAXA134.SA","TAXA291.SA","TAXA214.SA","TAXA70.SA","TAXA48L.SA","TAXA96.SA","TAXA169.SA","TAXA30.SA","TAXA20.SA","TAXA240.SA","TAXA50L.SA","TAXA330.SA","TAXA218.SA","TAXA151.SA","TAXA115.SA","TAXA108.SA","TAXA237.SA","TAXA82.SA","TAXA47L.SA","TAXA32L.SA","TAXA168.SA","TAXA24L.SA","TAXA131.SA","TAXA162.SA","TAXA61.SA","TAXA56L.SA","TAXA140.SA","TAXA65L.SA","TAXA333.SA","TAXA48.SA","TAXA174.SA","TAXA338.SA","TAXA33L.SA","TAXA54L.SA","TAXA220.SA","TAXA316.SA","TAXA139.SA","TAXA195.SA","TAXA325.SA","TAXA35L.SA","TAXA347.SA","TAXA259.SA","TAXA74L.SA","TAXA229.SA","TAXA51L.SA","TAXA253.SA","TAXA230.SA","TAXA91L.SA","TAXA273.SA","TAXA286.SA","TAXA306.SA","TAXA67L.SA","TAXA73.SA","TAXA72.SA","TAXA66L.SA","TAXA43.SA","TAXA348.SA","TAXA133.SA","TAXA27L.SA","TAXA272.SA","TAXA49.SA","TAXA37L.SA","TAXA111.SA","TAXA309.SA","TAXA16L.SA","TAXA29L.SA","TAXA102.SA","TAXA30L.SA","TAXA173.SA","TAXA81L.SA","TAXA326.SA","TAXA271.SA","TAXA277.SA","TAXA78L.SA","TAXA76L.SA","TAXA40.SA","TAXA112.SA","TAXA103.SA","TAXA241.SA","TAXA327.SA","TAXA243.SA","TAXA335.SA","TAXA289.SA","TAXA2L.SA","TAXA276.SA","TAXA314.SA","GOLL10.SA","TAXA301.SA","TAXA317.SA","TAXA25L.SA","TAXA166.SA","TAXA270.SA","TAXA239.SA","IBRA11.SA","TAXA33.SA","TAXA176.SA","TAXA51.SA","TAXA61L.SA","TAXA80L.SA","TAXA52.SA","TAXA107.SA","TAXA95.SA","TAXA28.SA","TAXA132.SA","TAXA186.SA","TAXA280.SA","TAXA87L.SA","TAXA92.SA","TAXA156.SA","TAXA275.SA","TAXA89.SA","TAXA300.SA","TAXA137.SA","TAXA68.SA","TAXA288.SA","TAXA56.SA","TAXA121.SA","TAXA46L.SA","TAXA25.SA","TAXA64.SA","TAXA94.SA","TAXA23.SA","TAXA44.SA","TAXA124.SA","TAXA358.SA","TAXA153.SA","TAXA38L.SA","TAXA46.SA","TAXA52L.SA","TAXA119.SA","TAXA292.SA","TAXA159.SA","TAXA299.SA","TAXA26.SA","TAXA66.SA","TAXA81.SA","TAXA160.SA","TAXA323.SA","TAXA83L.SA","TAXA181.SA","TAXA268.SA","TAXA199.SA","TAXA188.SA","TAXA257.SA","TAXA72L.SA","TAXA22L.SA","TAXA297.SA","TAXA331.SA","TAXA39.SA","TAXA120.SA","TAXA54.SA","TAXA197.SA","TAXA208.SA","TAXA269.SA","TAXA19L.SA","TAXA82L.SA","TAXA93.SA","TAXA97.SA","TAXA298.SA","TAXA93L.SA","TAXA206.SA","TAXA278.SA","TAXA144.SA","TAXA223.SA","TAXA45.SA","TAXA34.SA","TAXA182.SA","TAXA255.SA","TAXA264.SA","TAXA21.SA","TAXA122.SA","TAXA75L.SA","TAXA59L.SA","TAXA216.SA","TAXA204.SA","TAXA98L.SA","TAXA99L.SA","TAXA89L.SA","TAXA53L.SA","TAXA60L.SA","TAXA40L.SA","TAXA154.SA","TAXA226.SA","TAXA101.SA","TAXA266.SA","ALSC3.SA","CSAB4F.SA","ALUP11.SA","RPAD6.SA","BRGE5F.SA","BRGE6F.SA","BRGE12F.SA","ITAG11.SA","APTI4.SA","APTI3.SA","RPAD3F.SA","TAEE3.SA","MEAL3.SA","PEAB4.SA","ALLF6L.SA","BAUH4.SA","RPAD3.SA","BRIV3.SA","CSAB4.SA","CSAB3F.SA","APTI4F.SA","PEAB3.SA","FAMB11B.SA","GOOG35F.SA","BRGE7F.SA","TAEE4.SA","CRIV3F.SA","BRIV3F.SA","VIGR3.SA","MEAL9.SA","GOOG34F.SA","APTI3F.SA","BRGE8F.SA","BRIV4F.SA","CRIV3.SA","CSAB3.SA","PEAB3F.SA","CRIV4F.SA","RPAD5F.SA","ALMI11B.SA","RPAD5.SA","AMGN34.SA","AMAR3.SA","AXPB34F.SA","AXPB34.SA","LAME3.SA","AMZO34F.SA","LCAM3.SA","BOAC34.SA","LAME-DCA51L0.SA","CBEE3.SA","BOAC34F.SA","AMGN34F.SA","STEN-DEB31L1.SA","ANHB-DEB61B0.SA","ANHB-DEB41L0.SA","ANCR11B.SA","ANHB-DEB61L0.SA","ANHB-DEB42L0.SA","FAED11B.SA","ANHB-DEB51B0.SA","BPHA11.SA","ANIM3.SA","ANHB-DEB41B0.SA","STEN-DEB31L0.SA","STEN-DEB31B0.SA","FJTA12.SA","ANHB-DEB42B0.SA","ANHB-DEB51L1.SA","STEN-DEB32B0.SA","AQLL11.SA","ARTR3.SA","FJTA10.SA","MOAR3.SA","MOAR3F.SA","FJTA9.SA","ARCN5L.SA","ARMT34F.SA","ARMT34.SA","ASCP-DEB14B0.SA","ASCP-DEB12L1.SA","ASCP-DEB14L1.SA","ASCP-DEB11L1.SA","ASCP-DEB12B0.SA","ASCP-DEB13L1.SA","ASCP-DEB12L0.SA","ESUD11.SA","ATTB34.SA","VSPT3F.SA","ATTB34F.SA","FIGS11.SA","ATOM3.SA","AVON34F.SA","AVON34.SA","VULC3.SA","AZEV3F.SA","AZGT5L.SA","AZEV3.SA","SANB4.SA","SANB3.SA","TOYB3.SA","TELB4.SA","SUZB5.SA","DAYC4.SA","BSLI3.SA","BMEB4.SA","BGIP4.SA","BICB4.SA","BPAN4.SA","CAMB4.SA","CAMB4F.SA","IMAT11.SA","TELB3F.SA","CRBD-DEB12B0.SA","BALM4.SA","PEPB34.SA","IBMB34F.SA","IBMB34.SA","HPQB34.SA","BBTG11.SA","BBSE3.SA","LMTB34.SA","BBVH-FIDS1B0.SA","KHCB34.SA","BMYB34F.SA","METB34F.SA","BBSD.SA","BBPO11.SA","BBRC11.SA","PEPB34F.SA","RNDP11.SA","TWXB34.SA","JNJB34F.SA","BBVH-FID01B0.SA","HONB34F.SA","BBIM11.SA","DISB34.SA","DISB34F.SA","KMBB34F.SA","LMTB34F.SA","BBRK3.SA","SBUB34.SA","DOWB34F.SA","FMXB34.SA","BBFI11B.SA","BBDC2.SA","HONB34.SA","BBDC1.SA","HPQB34F.SA","DOWB34.SA","TGTB34.SA","SBUB34F.SA","BMYB34.SA","FMXB34F.SA","TGTB34F.SA","FDXB34F.SA","KMBB34.SA","BBSD11.SA","METB34.SA","SANB11.SA","BRSR5.SA","MATB.SA","BRSR6.SA","BNBR3.SA","PIBB11.SA","IDVL4.SA","FIIB11.SA","MATB11.SA","BMIN4.SA","BRSR3.SA","BMIN3.SA","BPAR3.SA","IDVL10.SA","PIBB.SA","IDVL3.SA","RBCB11.SA","BCRI11.SA","BGIP3.SA","WMRB11B.SA","NCHB11B.SA","BCFF11B.SA","IVVB11.SA","IDVL9.SA","BDLL3F.SA","BDLS-DEB31L1.SA","BDLS-DEB41B0.SA","BDLS-DEB41L0.SA","BDLS-DEB110B.SA","BDLS-DEB310B.SA","BDLL4F.SA","BDLS-DEB11L1.SA","BDLS-DEB31B0.SA","BDLL4.SA","BDLS-DEB11L0.SA","BDLL3.SA","BDLS-DEB51L0.SA","BDLS-DEB41L1.SA","BDLS-DEB11B0.SA","BEEF3.SA","FIGE3.SA","FIGE3F.SA","FIGE4F.SA","FIGE4.SA","BEES4.SA","PBEL3B.SA","BFRE11.SA","BFRE12.SA","BGIP4F.SA","BGIP3F.SA","IMOB11.SA","BIOM3.SA","BSEV3.SA","BMKS3.SA","BICB3.SA","TENE7.SA","TENE7L.SA","TENE5.SA","TENE5F.SA","BMLC11B.SA","BMIN3F.SA","BMIN10.SA","BMTO3F.SA","UTIP11.SA","CSMO11.SA","BMIN9.SA","BNDP-DEB62L1.SA","BNDP-DEB62B0.SA","BNDP-DEB53L0.SA","BNFS11.SA","PDGR11.SA","BNDP-DEB63L0.SA","BNDP-DEB53B0.SA","BNDP-DEB61L0.SA","BNDP-DEB62L0.SA","BNDP-DEB61B0.SA","BOXP34.SA","BOVA.SA","BOBR4.SA","BOEI34F.SA","RBBV11.SA","BOBR3.SA","BOEI34.SA","BOXP34F.SA","BPAR3F.SA","BPAT33F.SA","BPAT33.SA","LIGT3.SA","BRML3.SA","BRFS3.SA","TPIS3.SA","SLBG34.SA","SHUL4.SA","SHUL3.SA","RLOG3.SA","RENT3.SA","RAPT4.SA","RANI3.SA","PLAS3.SA","PETR3.SA","PATI3.SA","MTIG4.SA","MSFT34.SA","MSBR34.SA","MOSC34F.SA","MMMC34.SA","LREN3.SA","LBRN34F.SA","HYPE3.SA","HALI34F.SA","HALI34.SA","GUAR4.SA","GSGI34F.SA","GSGI34.SA","GGBR3.SA","ETER3.SA","EQTL3.SA","ELPL4.SA","ELET6.SA","EKTR4.SA","CZLT33.SA","CTNM4.SA","CSAN3.SA","COLG34F.SA","CLSC3.SA","CIEL3.SA","CATP34.SA","CALI3F.SA","BRPR3.SA","BRKM3.SA","BRAP4.SA","SPRI6.SA","RBCS-CRI2PL0.SA","RBCS-CRI97B0.SA","UPAC34.SA","OPHF11B.SA","EEEL4F.SA","BSCS-CRIC1B0.SA","MERC3.SA","BSCS-CRIT1B0.SA","PDGS-CRI33L0.SA","IDNT3.SA","CPTS11B.SA","ENGI4.SA","MRCK34.SA","ELEK3F.SA","CGAS-DEB43B0.SA","IGNM11.SA","HYPE-DEB33L1.SA","CELP3.SA","BVLS-DEB21B0.SA","BSCS-CRIZ3L0.SA","SBSP-DEB7BL1.SA","MULT3.SA","BVLS-DEB41L1.SA","SLED3.SA","TOYB4.SA","TPIS-DEB41B0.SA","GPIV33.SA","TIBR6.SA","PDGR9.SA","VIVT-DEB43B0.SA","CELP5F.SA","BSCS-CRIG1L1.SA","CRBD-DEB11B0.SA","CSCO34.SA","TWTR34F.SA","BVLS-DEB21L0.SA","ECOO.SA","ISEE11.SA","VALE-DEB82L1.SA","BAHI3.SA","PDGS-CRI14L1.SA","MSCD34.SA","RBCS-CRI82B0.SA","RBCS-CRI86B0.SA","CLSC4.SA","RBCS-CRI85B0.SA","CTGP34F.SA","EVEN3.SA","PRCF-FID01B0.SA","ENGI-DEB73B0.SA","SAIC11B.SA","PNVL4F.SA","FISD11.SA","PMSP12BL.SA","TEPE-DEB13B0.SA","PNVL4.SA","CEOC11B.SA","BSCS-CRIS8B0.SA","BSCS-CRIH70B.SA","BSCS-CRIS8L0.SA","CMGD-DEB31L1.SA","ISUS.SA","SBSP-DEB7BL0.SA","SCLO4F.SA","MCDC34F.SA","MOBI.SA","CXRI11.SA","CEEB5F.SA","TCNO4.SA","CTBC-DEB21L0.SA","LBRN34.SA","RCSL3F.SA","FBMC4F.SA","OCTS-CRA310B.SA","CORR4F.SA","GOAU3.SA","LREN-DEB42L0.SA","KLBN-DCA61L0.SA","TRPL4.SA","MNPR3.SA","UTIL11.SA","LHER4F.SA","ORCL34F.SA","PPHT5L.SA","DUQE4.SA","LREN-DEB42B0.SA","RCSL1.SA","VOES-DEB41L1.SA","TGLT32F.SA","CGAS-DEB42L0.SA","BSCS-CRII5L0.SA","ICO211.SA","SULT4.SA","OCTS-CRA31B0.SA","MGIP-DEB31L0.SA","DUQE3.SA","SCLO4.SA","SNSL3.SA","BSCS-CRIC0L0.SA","RBPD11.SA","FSPE11.SA","BSCS-CRIT1L0.SA","BSCS-CRIO6L0.SA","MBRF11.SA","CRPG6.SA","CMCS34.SA","PDGS-CRI13L0.SA","RADL3.SA","PDGS-CRI37L0.SA","TRIS3.SA","PLRI11.SA","CTNM3F.SA","SGPS3.SA","CSMG3.SA","ENMT3.SA","RBRD11.SA","RANI4.SA","FIIP11B.SA","BRCS-CRI1AL0.SA","SDIL11.SA","ENGI9.SA","ELDO11B.SA","CORR3F.SA","DHER34.SA","BRPR-DEB12L1.SA","PCAR3.SA","RBCS-CRI040B.SA","VALE-DEB81L0.SA","BSCS-CRII4L0.SA","BSCS-CRI79B0.SA","BRKM6.SA","ITEC3.SA","USIM6F.SA","CELP6F.SA","BRML-DEB41L0.SA","RBCS-CRI91L0.SA","EKTR3.SA","SAPR4.SA","RBCS-CRI87L0.SA","FBSG5L.SA","BUET4.SA","PATI9.SA","BSCS-CRIJ1L0.SA","CMGT-DEB31L0.SA","BSCS-CRII9B0.SA","PINE4.SA","CESP5.SA","CCHI3.SA","KNRI11.SA","SCPF11.SA","UNID-DEB21L0.SA","COPH34.SA","CREM3.SA","MGEL4.SA","PLSC-CRI1CL1.SA","CTXT11.SA","BRML-DEB21L1.SA","MAPT4F.SA","RBCS-CRI2RL1.SA","TEPE-DEB11L0.SA","TRXL11.SA","BSCS-CRI460B.SA","MTAM6L.SA","BRPR-DEB11L1.SA","INEP-DCA61L0.SA","BRML-DEB21B0.SA","ENBR-DEB43L1.SA","RBCS-CRI84L1.SA","MSBR34F.SA","PDGR-DCA81B0.SA","CORR4.SA","BSCS-CRII50B.SA","BSCS-CRIG2B0.SA","CEPE5.SA","BSCS-CRII9L0.SA","SCLO3.SA","ENBR-DEB430B.SA","FCXO34F.SA","BSCS-CRIZ3B0.SA","BSCS-CRIO50B.SA","MERC4.SA","DHER34F.SA","RBCS-CRI73B0.SA","ELPL3.SA","ELPL-DEB1AL1.SA","BUET3.SA","PATI10.SA","SBSP-DEB7AL1.SA","DIRR3.SA","FEXC11B.SA","BSCS-CRIG2L1.SA","CRPG5.SA","SPRI6F.SA","CGAS-DEB43L1.SA","CCPR9.SA","CASN3F.SA","BZRS-CRI11L0.SA","PTNT3.SA","PCMR5L.SA","PRBC4.SA","FRES11.SA","EEEL3.SA","CPTP9B.SA","CEEB5.SA","BSCS-CRIO6L1.SA","BSCS-CRIG10B.SA","SMLL11.SA","MGIP-DEB31B0.SA","EBEN-DEB41L1.SA","MNDL3F.SA","CYRE-DEB22L1.SA","CMCS34F.SA","CEDO3.SA","RBCS-CRI85L0.SA","ITLC34F.SA","ITUB3.SA","TRPL3F.SA","LUXM4.SA","FBMC3.SA","BSCS-CRIT2L1.SA","SWET3F.SA","PDGS-CRI15L1.SA","CESP5F.SA","FIND11.SA","PLSC-CRI1CL0.SA","USBC34F.SA","BSCS-CRIZ4L0.SA","RNAR3.SA","HYPE-DEB33B0.SA","RBCS-CRI82L0.SA","RBCS-CRI030B.SA","BZRS-CRI21L0.SA","BSCS-CRIC1L1.SA","SOND3.SA","SAIP-DEB11L1.SA","COCE6F.SA","CGAS3.SA","VALE-DEB84L1.SA","BSCS-CRIJ0L1.SA","PLPF-FID01B0.SA","TGLT32.SA","MXRC11.SA","CRVD5L.SA","MTIG3.SA","CMGD-DEB32B0.SA","PDGR-DEB11B0.SA","BRAX.SA","IGBR3.SA","BSCS-CRIT4B0.SA","BSCS-CRIS7L1.SA","BSCS-CRII90B.SA","BSCS-CRIF9L0.SA","BSCS-CRI79L0.SA","BSCS-CRIH6B0.SA","BSCS-CRIS80B.SA","BSCS-CRIS7L0.SA","BSCS-CRIJ2L0.SA","BSCS-CRIT4L0.SA","BSCS-CRIT3L1.SA","BSCS-CRII40B.SA","BSCS-CRIO5L1.SA","BSCS-CRIG00B.SA","BSCS-CRIJ3L0.SA","BSCS-CRIJ0B0.SA","BSCS-CRIH6L1.SA","BSCS-CRI790B.SA","BSCS-CRIJ00B.SA","BSCS-CRIS70B.SA","BSCS-CRIJ3L1.SA","BSLI4F.SA","BSCS-CRIZ30B.SA","BSCS-CRIT3B0.SA","BSCS-CRIO60B.SA","BSCS-CRIF9B0.SA","BSCS-CRIZ4L1.SA","BSCS-CRII4B0.SA","BSCS-CRIZ4B0.SA","BSCS-CRI46L1.SA","BSCS-CRIG1B0.SA","BSCS-CRIF90B.SA","BSCS-CRIJ0L0.SA","BSLI3F.SA","BSLI4.SA","BSCS-CRI46L0.SA","BSCS-CRIT2L0.SA","BSCS-CRIG2L0.SA","BSCS-CRII5L1.SA","BSCS-CRIJ1B0.SA","BSCS-CRIT3L0.SA","BSCS-CRIT0B0.SA","BSCS-CRIF9L1.SA","BSCS-CRIG0L0.SA","BSCS-CRIO5L0.SA","BSCS-CRIS7B0.SA","BSCS-CRII5B0.SA","BSCS-CRIG0B0.SA","BSCS-CRIH7L0.SA","BRCR11.SA","BTGM11.SA","BURI5L.SA","BUET3F.SA","BVLS-DEB110B.SA","BVAR11.SA","BVLS-DEB12B0.SA","BVLS-DEB41B0.SA","BVLS-DEB42L0.SA","BVLS-DEB11B0.SA","BZRS-CRI11B0.SA","BZRS-CRI21B0.SA","USBC34.SA","ITLC34.SA","UTEC34F.SA","JPMC34F.SA","MOSC34.SA","MMMC34F.SA","CCXC3.SA","DOMC11.SA","TSNC11.SA","GWIC11.SA","CCHI4F.SA","CCHI4.SA","CCPR3.SA","CTBC-DEB21B0.SA","CTBC-DEB22L1.SA","CMGD-DEB33B0.SA","GPAR3.SA","CEPE6.SA","CMGT-DEB32B0.SA","CELP6.SA","COCE5.SA","CEBR6F.SA","CNES11B.SA","CEDO3F.SA","CELP7F.SA","CEPE3.SA","CMGT-DEB33B0.SA","COCE3.SA","COCE6.SA","CEED4F.SA","MAPT3F.SA","CELP5.SA","SUZB6.SA","CMGT-DEB31B0.SA","CEED4.SA","CMGD-DEB32L1.SA","CEBR6.SA","CEDO4F.SA","CMGD-DEB33L1.SA","CMGT-DEB33L0.SA","CEED3F.SA","CMGT-DEB32L0.SA","CLSC3F.SA","CLGN34.SA","RANI4F.SA","MAPT4.SA","PQDP11.SA","CEDO4.SA","VSPT3.SA","CMGD-DEB21L1.SA","CELP7.SA","CEBR5.SA","CEPE5F.SA","MAPT3.SA","CEBR3.SA","CESP3.SA","CEED3.SA","CEGR3F.SA","CEPE6F.SA","PMSP12B.SA","CMGD-DEB33L0.SA","CEBR3F.SA","CEBR5F.SA","CXCE11B.SA","CEEB3.SA","ELET5.SA","CGAS-DEB42L1.SA","CGAS-DEB33L0.SA","CGAS-DEB32B0.SA","CGAS-DEB43L0.SA","CGAS-DEB410B.SA","CGAS-DEB31L0.SA","CGAS-DEB31L1.SA","CGAS-DEB33L1.SA","CGAS-DEB430B.SA","CGAS-DEB32L0.SA","CGAS-DEB41L0.SA","CGAS-DEB31B0.SA","FNAM11.SA","CSRN5.SA","IMBI3.SA","HCRI11B.SA","CSRN6.SA","TRPL3.SA","SPXI11F.SA","ESUU11.SA","ESUU12.SA","CTGP34.SA","IMBI4.SA","FSTU11.SA","CTNM3.SA","LATR11B.SA","IFNC11.SA","FDES11.SA","FLRP11B.SA","NSLU11B.SA","SAPR3.SA","CSRN3.SA","MAXR11B.SA","PRVI3.SA","DOVL11B.SA","CMIG3.SA","CPLE5F.SA","CPLE5.SA","CPTE-DEB110B.SA","CPTP3BF.SA","CPRE3.SA","CREM3F.SA","TIBR5.SA","CRPG3.SA","RBVO11.SA","CRDE3.SA","CSRN3F.SA","CSRN6F.SA","HGRE11.SA","HGBS11.SA","CARD3.SA","HGLG11.SA","CSRN5F.SA","HGCR11.SA","CTNR11L.SA","CTVL5L.SA","LIXC3.SA","LIXC4.SA","LIXC3F.SA","CXTL11.SA","CYRE-DEB21L0.SA","SOND3F.SA","NORD3F.SA","SOND5.SA","SLED4.SA","SOND6F.SA","SOND6.SA","NORD3.SA","MEND6.SA","MEND6F.SA","MEND3F.SA","DBEN-DEB420B.SA","DBEN-DEBE6B0.SA","DBEN-DEB51B0.SA","DBEN-DEB51L0.SA","DBEN-DEB42L0.SA","NPPF-FID010B.SA","NPPF-FIDS10B.SA","DBEN-DEB42L1.SA","MSCD34F.SA","FIND.SA","PORD11.SA","SFND11.SA","UNID-DEB21B0.SA","ENMT4.SA","DHBI4F.SA","DHBI4.SA","DHBI3F.SA","DHBI3.SA","DIVO11.SA","DIVO.SA","PNVL3.SA","ENGI12.SA","IMBI4F.SA","FRES11F.SA","DOHL4.SA","RNEW1.SA","BEES3.SA","ENBR3.SA","BMEB3.SA","DOHL3F.SA","DOHL3.SA","IMBI3F.SA","DRIT11B.SA","GDBR34.SA","GDBR34F.SA","TAEE3F.SA","LFFE3F.SA","OPRE3B.SA","LEVE3.SA","COBE5B.SA","PINE3F.SA","REDE3F.SA","REDE4.SA","COBE3B.SA","OPSE3B.SA","NIKE34F.SA","EBEN-DEB41B0.SA","HOME34F.SA","NIKE34.SA","EBES5L.SA","ECOV-DEB22B0.SA","ECPR3.SA","KNRE11.SA","ECPR4F.SA","ECOV-DEB22L0.SA","ECPR4.SA","GOVE11.SA","FTCE11B.SA","ECPR3F.SA","GOVE.SA","TEPE-DEB13L0.SA","TEPE-DEB12L1.SA","VALE-DEB91L0.SA","TEPE-DEB14B0.SA","VALE-DEB92L0.SA","SEDU3.SA","EDFO11B.SA","TEPE-DEB13L1.SA","VALE-DEB83L0.SA","VALE-DEB82L0.SA","EEEL4.SA","PLAS3F.SA","MWET3F.SA","RBCS-CRI97L1.SA","PDGS-CRI35L1.SA","BRSR5F.SA","WTVR-CRI11L1.SA","PDGS-CRI35B0.SA","EKTR4F.SA","ELEK4.SA","LIPR3F.SA","LIPR3.SA","ELPL-DEB1AL0.SA","ELET5F.SA","SCAR3.SA","HBOR3.SA","EZTC3.SA","ENMT4F.SA","ENGI-DEB72B0.SA","ENGI-DEB72L0.SA","ENBR-DEB42L0.SA","RJCP3.SA","RCCS11.SA","JRDM11B.SA","FVBI11B.SA","OPRE9B.SA","MILS9.SA","ESTR4.SA","ESTR3F.SA","RDES11.SA","MILS3.SA","ESTR3.SA","ESTC3.SA","SPXI11.SA","ISUS11.SA","EURO11.SA","EXXO34F.SA","WFCO34F.SA","FBOK34F.SA","JHSF3.SA","WFCO34.SA","FBMC4.SA","TIFF34F.SA","FBMC3F.SA","MXRF11.SA","FCFL11B.SA","FSRF11.SA","TBOF11.SA","ONEF11.SA","GVFF11.SA","FINF11.SA","FCXO34.SA","FMOF11.SA","FDCS-CRI11L1.SA","RBDS11.SA","FDCS-CRI110B.SA","FDCS-CRI11L0.SA","FDMO34F.SA","FHER3.SA","FFCI11.SA","FGEN-DEB31L1.SA","FGEN-DEB31L0.SA","FIVN11.SA","REIT11B.SA","TRNT11B.SA","RBGS11.SA","MERC4F.SA","GWIR11.SA","FIRM5L.SA","NAFG4F.SA","FNOR11.SA","FONT6L.SA","FONT5L.SA","JFEN3.SA","FPOR11.SA","PARC3.SA","FRAS3.SA","FRIO3.SA","FTRT3B.SA","PRSV11.SA","KNCR11.SA","VLOL11.SA","RBPR11.SA","MFII11.SA","BRCP11.SA","NVHO11.SA","VPSI11.SA","SHPH11.SA","MTIG4F.SA","PGCO34F.SA","MAGG3.SA","JSLG3.SA","NAFG3.SA","NAFG3F.SA","MTIG3F.SA","PGCO34.SA","NAFG4.SA","JSLG-DEB62B0.SA","JSLG-DEB63L0.SA","JSLG-DEB62L0.SA","GSHP3.SA","USIM6.SA","GOOG34.SA","GOOG35.SA","GPCP3.SA","GUAR3.SA","HBTS5.SA","HBTS5F.SA","COPH34F.SA","LHER4.SA","LHER3F.SA","LHER3.SA","NEMO5.SA","HTAL7L.SA","SPRI3F.SA","SPRI5.SA","PATI4F.SA","SPRI3.SA","ENGI3.SA","POSI3.SA","CALI4F.SA","RDNI3F.SA","RDNI3.SA","TERI3F.SA","PATI3F.SA","ROMI3.SA","SPRI5F.SA","PRVI3F.SA","PATI4.SA","TERI3.SA","IBXL11.SA","WUNI34.SA","WTPI-CRI020B.SA","ICON11.SA","WTPI-CRI02L1.SA","WTPI-CRI02L0.SA","ENGI11.SA","WTPI-CRI02B0.SA","ENGI-DEB76B0.SA","PATI1.SA","ENGI-DEB75L1.SA","ENGI-DEB72L1.SA","IDVL3F.SA","ENGI-DEB52L0.SA","ENGI-DEB74L1.SA","ENGI-DEB71B0.SA","ENGI-DEB74L0.SA","IGCT11.SA","LPSB3.SA","RAPT3.SA","MYPK-DEB7AL0.SA","MYPK11.SA","MYPK3F.SA","ENGI10.SA","SMAL11F.SA","SMAL.SA","SMAL11.SA","ITEC3F.SA","ITTB11L.SA","MLFT3F.SA","MLFT3.SA","MLFT4.SA","SJOS4.SA","SJOS3.SA","SJOS3F.SA","MRCK34F.SA","MILK33.SA","KLBN-DCA61L1.SA","KLBN3.SA","KLBN-DCA61B0.SA","KLBN11.SA","MGEL3F.SA","MGEL3.SA","RCSL4.SA","MNDL3.SA","WHRL3.SA","RCSL3.SA","LTEL3B.SA","RSUL4.SA","PTBL3.SA","BRML-DEB41L1.SA","TRPL-DEB12B0.SA","BRML-DEB21L0.SA","BRML-DEB22B0.SA","BRML-DEB22L0.SA","BRML-DEB12L1.SA","BRML-DEB12L0.SA","BRML-DEB12B0.SA","BRML-DEB22L1.SA","LLIS3.SA","SPRT3B.SA","LREN-DEB51L1.SA","LREN-DEB42L1.SA","SPRT9BF.SA","LOGN3.SA","SPRT3BF.SA","MRSA-DEB71B0.SA","LUXM3.SA","LUXM4F.SA","LUXM3F.SA","BRKM6F.SA","MAOR3B.SA","MAOR4B.SA","PMAM3.SA","RBCS-CRI2RL0.SA","RBCS-CRI03L0.SA","RBCS-CRI87L1.SA","RBCS-CRI04B0.SA","RBCS-CRI2YB0.SA","RBCS-CRI2QL1.SA","RBCS-CRI2RB0.SA","WALM34F.SA","PRSN11B.SA","RBCS-CRI03B0.SA","RBCS-CRI85L1.SA","RBCS-CRI73L1.SA","SCNR5L.SA","MCHV5L.SA","TIBR3.SA","MSFT34F.SA","MMXM11.SA","MNHT5L.SA","MPLU3.SA","PSVM11F.SA","ENMT3F.SA","MWET4.SA","CASN4F.SA","TRPN3.SA","BRIN3.SA","WSON33.SA","COLN-DEB42B0.SA","COLN-DEB43L0.SA","COLN-DEB41L0.SA","ENBR-DEB41L0.SA","TPIS-DEB42L0.SA","VIVR-DCA41B0.SA","ENBR-DEB410B.SA","SBSP-DEB7CB0.SA","SBSP-DEB7AB0.SA","VIVR-DCA41L0.SA","UCAS3F.SA","ENBR-DEB420B.SA","SBSP-DEB7BB0.SA","SCAR3F.SA","BRPR-DEB12B0.SA","ENBR-DEB43L0.SA","BRPR-DEB11B0.SA","PDGR-DEB11L1.SA","BRIN9.SA","NUTR3.SA","SMTO3.SA","POMO4.SA","TKNO3F.SA","TKNO3.SA","TCNO3.SA","POMO3.SA","OCTS-CRA31L0.SA","OGXP3.SA","OIBR-DEB91L1.SA","BALM3F.SA","SAPR3F.SA","INET3F.SA","RJCP3F.SA","MERC3F.SA","BMEB3F.SA","OSEC-CRA24L0.SA","OSEC-CRA24L1.SA","HOOT4.SA","UPSS34F.SA","STBP11.SA","INEP4.SA","UNIP3.SA","SUZB6F.SA","UNIP5.SA","TEMP3.SA","UNIP6.SA","CATP34F.SA","WTVP-CRI11B0.SA","INEP-DCA610B.SA","INEP-DCA61B0.SA","INEP-DCA71B0.SA","INEP-DCA61L1.SA","PDGS-CRI13B0.SA","PDGS-CRI14B0.SA","PDGS-CRI37L1.SA","INEP-DCA71L1.SA","SAIP-DEB11L0.SA","INEP-DCA71L0.SA","PEPL6L.SA","PTNT4.SA","PFRM1.SA","SULT4F.SA","BALM4F.SA","RDTR3.SA","SSBR3.SA","VVAR4.SA","VVAR3.SA","RCST6L.SA","VVAR11.SA","RCTA6L.SA","RDVT-DEB11L1.SA","RDVT-DEB11B0.SA","RLOG1.SA","RNEW11.SA","RNEW4.SA","BRCS-CRI1AB0.SA","BRCS-CRI1AL1.SA","BRCS-CRI71L1.SA","SLBG34F.SA","SGAS4.SA","SGAS3.SA","SNST-DEB21L1.SA","SNST-DEB21L0.SA","SNST-DEB21B0.SA","SULT3.SA","SWET3.SA","VIVT3.SA","INET3.SA","TBCC4L.SA","TCTN5L.SA","VIVT-DEB43L1.SA","VIVT-DEB43L0.SA","TEMP3L.SA","TOTS3.SA","VLBN6L.SA","BESA-DEB120B.SA","BESA-DEB11B0.SA","TELB3.SA","BALM3.SA","BRAP3.SA","COLG34.SA","INEP3.SA","CAIU4L.SA","CAMC5L.SA","CAMC7L.SA","ENZM4L.SA","TEMP11L.SA","USIM11.SA"]

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
