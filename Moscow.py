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
    available_tickers = ["MOEX.ME","HYDR.ME","DIXY.ME","IDVP.ME","DZRDP.ME","VRSBP.ME","RUAL.ME","OMSH.ME","JNOS.ME","CBOM.ME","OFCB.ME","JNOSP.ME","NKHP.ME","KUBE.ME","KROTP.ME","TGKO.ME","KTSBP.ME","KTSB.ME","KRSB.ME","KRKO.ME","KMAZ.ME","KLSB.ME","KCHEP.ME","KCHE.ME","KBTK.ME","HIMC.ME","MSNG.ME","MRKZ.ME","MOTZ.ME","MGNT.ME","NVTK.ME","NSVZ.ME","NMTP.ME","NLMK.ME","ODVA.ME","PRIN.ME","OMZZP.ME","ZMZNP.ME","QIWI.ME","VLHZ.ME","URKA.ME","SKYC.ME","SBER.ME","ROSN.ME","RASP.ME","PHOR.ME","GAZP.ME","ALNU.ME","AFLT.ME","AFKS.ME","ZMZN.ME","ZHIV.ME","YRSL.ME","YRSB.ME","YASH.ME","YAKG.ME","VSYD.ME","VJGZP.ME","VJGZ.ME","VGSBP.ME","URKZ.ME","URFD.ME","TTLK.ME","TRMK.ME","SZPR.ME","STSBP.ME","SIBN.ME","SELL.ME","SARE.ME","SAGOP.ME","SAGO.ME","VRSB.ME","VRAO.ME","RU000A0JUSX7.ME","VSMO.ME","WTCMP.ME","YNDX.ME","YKEN.ME","YKENP.ME","YRSBP.ME","ZILL.ME","ZVEZ.ME","ABRD.ME","AESL.ME","AGRO.ME","AKRN.ME","RU000A0JUGA0.ME","SIBG.ME","ALRS.ME","RU000A0JUHS0.ME","ALBK.ME","AMEZ.ME","UWGN.ME","APTK.ME","AQUA.ME","ARSA.ME","ARMD.ME","ASSB.ME","AVAZP.ME","AVAN.ME","AVAZ.ME","BANEP.ME","BANE.ME","BISVP.ME","BGDE.ME","RU000A0JUP71.ME","RU000A0JUUF0.ME","BISV.ME","BLNG.ME","BSPB.ME","CHZN.ME","CHMF.ME","CHKZ.ME","GRNT.ME","CLSBP.ME","EPLN.ME","CLSB.ME","CNTL.ME","DASB.ME","DALM.ME","DGBZ.ME","DIOD.ME","DVEC.ME","DZRD.ME","RU000A0JUA37.ME","RU000A0JVT35.ME","RU000A0JUXF4.ME","ELTZ.ME","MISB.ME","ENRU.ME","EONR.ME","RU000A0JUBX3.ME","RU000A0JUW49.ME","RU000A0JUTA3.ME","FESH.ME","FEES.ME","FORTP.ME","GAZAP.ME","GAZC.ME","GAZS.ME","GAZA.ME","GAZT.ME","GCHE.ME","RU000A0JUSU3.ME","KGKCP.ME","RU000A0JVEZ0.ME","KGKC.ME","GMKN.ME","GRAZ.ME","GTPR.ME","GTLC.ME","HALS.ME","HIMCP.ME","RUSI.ME","IGST.ME","IGSTP.ME","IRKT.ME","IRAO.ME","IRGZ.ME","ISKJ.ME","RU000A0JTXM2.ME","RU000A0JVPL6.ME","POLY.ME","TRNFP.ME","UTSY.ME","PLSM.ME","TANL.ME","NFAZ.ME","RUSP.ME","KAZTP.ME","KAZT.ME","KBSB.ME","KMEZ.ME","KOGK.ME","KROT.ME","KRSG.ME","KRKN.ME","KRKNP.ME","KUZB.ME","KZOS.ME","KZOSP.ME","LKOH.ME","LNTA.ME","LNZLP.ME","LNZL.ME","LPSB.ME","LSRG.ME","LSNG.ME","LSNGP.ME","LVHK.ME","MAGE.ME","MFGS.ME","MFGSP.ME","MFON.ME","MGVM.ME","MGNZ.ME","MGTS.ME","MGTSP.ME","MMBM.ME","MOBB.ME","MORI.ME","MRKY.ME","MRKP.ME","MRKS.ME","MRKV.ME","MRKK.ME","MRKU.ME","MRKC.ME","MRSB.ME","MSST.ME","MSRS.ME","MSTT.ME","MTSS.ME","MTLR.ME","MTLRP.ME","MUGS.ME","MUGSP.ME","MVID.ME","NAUK.ME","NKNCP.ME","NKSH.ME","NKNC.ME","NNSBP.ME","NNSB.ME","TAER.ME","OGKB.ME","OPIN.ME","OSMP.ME","OTCP.ME","PHST.ME","PIKK.ME","PLZL.ME","PMSB.ME","PMSBP.ME","PRMB.ME","PRIM.ME","RODNP.ME","TASBP.ME","PSBR.ME","RU000A0JUQZ6.ME","RBCM.ME","RDRB.ME","RGSS.ME","RKKE.ME","RLMNP.ME","RLMN.ME","RNAV.ME","ROSB.ME","ROST.ME","ROLO.ME","RSTIP.ME","RSTI.ME","RTSBP.ME","RTSB.ME","RTKM.ME","RTGZ.ME","RTKMP.ME","RUALR.ME","CHMK.ME","STSB.ME","TATNP.ME","MAGN.ME","RU000A0JQ5X1.ME","TUCH.ME","VZRZP.ME","UNKL.ME","SNGSP.ME","SNGS.ME","PRFN.ME","UNAC.ME","VSYDP.ME","USBN.ME","TASB.ME","RZSB.ME","TATN.ME","SELG.ME","TORSP.ME","CHGZ.ME","TUZA.ME","PRTK.ME","VZRZ.ME","UCSS.ME","TNSE.ME","MAGEP.ME","BRZL.ME","VRAOP.ME","LIFE.ME","SAREP.ME","SYNG.ME","PAZA.ME","VTRS.ME","KRSBP.ME","VTBR.ME","WTCM.ME","KRKOP.ME","SELGP.ME","TRCN.ME","UTAR.ME","UTII.ME","SBERP.ME","TORS.ME","MISBP.ME","SVAV.ME","VTGK.ME","UKUZ.ME","CHEP.ME","CNTLP.ME","VDSB.ME","MERF.ME","VGSB.ME","RUGR.ME","GZE1R.RG","BRV1R.RG","LJM1R.RG","RJR1R.RG","GRZ1R.RG","GRD1R.RG","VEF1R.RG","SMA1R.RG","VNF1R.RG","KA11R.RG","SCM1R.RG","KCM1R.RG","BAL1R.RG","OLF1R.RG","TMA1R.RG","VSS1R.RG","DPK1R.RG","LSC1R.RG","RKB1R.RG","RER1R.RG","BTE1R.RG","RRR1R.RG","LOK1R.RG","RAR1R.RG","TKB1R.RG","LTT1R.RG","SAF1R.RG"]

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
