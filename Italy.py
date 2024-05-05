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
    available_tickers = ["AZM.MI","AST.MI","AE.MI","A2A.MI","BMPS.MI","UBI.MI","PMI.MI","BZU.MI","EOAN.MI","DNN.MI","DMN.MI","DAL.MI","SPO.MI","SIE.MI","SAP.MI","DBK.MI","DAI.MI","CPR.MI","BPSO.MI","BIM.MI","ALV.MI","TAS.MI","PEL.MI","MUV2.MI","LD.MI","ENEL.MI","MN.MI","EXO.MI","CED.MI","BPE.MI","PRT.MI","FILA.MI","FDE.MI","EUK.MI","ERG.MI","ENI.MI","EGPW.MI","VITA.MI","TOT.MI","FNC.MI","VIV.MI","MTF.MI","JUVE.MI","FDA.MI","ALU.MI","G.MI","LUX.MI","GSP.MI","NRST.MI","HER.MI","CEM.MI","ANIM.MI","KI.MI","MSK.MI","MB.MI","RCS.MI","MT.MI","MARR.MI","MONC.MI","MOL.MI","M7IT.MI","CNHI.MI","NICE.MI","STM.MI","PHIA.MI","NET.MI","RACE.MI","NR.MI","S24.MI","ORA.MI","ON.MI","DANR.MI","PRY.MI","POPR.MI","PLT.MI","PC.MI","REY.MI","TITR.MI","REC.MI","LR.MI","BSRP.MI","STEFR.MI","UCG.MI","YSFT.MI","SRS.MI","TOD.MI","BZUR.MI","USRA.MI","UNI.MI","UCGR.MI","CTIC.MI","ZV.MI","VAS.MI","TV.MI","YVI.MI","VE.MI","WMC.MI","INW.MI","BMW.MI","XPR.MI","YNAP.MI","YIV.MI","YRM.MI","YSF.MI","ZUC.MI","ESCO.MI","MZB.MI","ZUCR.MI","ACE.MI","ACS.MI","ACO.MI","ACA.MI","CDR.MI","ADB.MI","AEF.MI","AGN.MI","TYA.MI","AGL.MI","A.MI","AGS.MI","ARE.MI","MASI.MI","DTE.MI","BB.MI","RWE.MI","OJM.MI","AHO.MI","ARN.MI","APE.MI","ALBA.MI","AMP.MI","AMB.MI","ATH.MI","STS.MI","ASSI.MI","CASS.MI","ASR.MI","AT.MI","ASC.MI","ATL.MI","SIS.MI","FCA.MI","AXEL.MI","AXA.MI","BOE.MI","BMED.MI","BANZ.MI","PRO.MI","CRG.MI","BP.MI","BGN.MI","BASF.MI","BAN.MI","B.MI","IF.MI","BDBR.MI","BDB.MI","BCM.MI","BC.MI","BNS.MI","BET.MI","BEC.MI","BE.MI","BEST.MI","BFE.MI","BF.MI","BSS.MI","BIE.MI","BIA.MI","BIO2.MI","BLUE.MI","BLU.MI","BLZ.MI","BM.MI","BNP.MI","BO.MI","BOMI.MI","BOR.MI","BRI.MI","IB.MI","DIB.MI","BRE.MI","BST.MI","CARR.MI","MIC.MI","CC.MI","RIC.MI","CMB.MI","PAN.MI","CE.MI","CLT.MI","CERV.MI","CFP.MI","MSU.MI","CHL.MI","CIA.MI","CIR.MI","CLF.MI","CLG.MI","CLA.MI","CLE.MI","CNP.MI","CRGR.MI","CRR.MI","CVAL.MI","CSP.MI","DA.MI","DAN.MI","DGT.MI","DIS.MI","DIA.MI","DM.MI","DLC.MI","DLG.MI","DMA.MI","ECK.MI","ECA.MI","ES.MI","EDNR.MI","POL.MI","EEMS.MI","EIT.MI","ELC.MI","ELN.MI","ELIN.MI","ELAB.MI","EM.MI","EMC.MI","FTL.MI","ENV.MI","ENT.MI","TEF.MI","SANT.MI","ETH.MI","EXSY.MI","FARM.MI","FKR.MI","PSF.MI","FBK.MI","FCT.MI","SFER.MI","FED.MI","TFI.MI","LFG.MI","FIC.MI","FM.MI","FNM.MI","GLF.MI","SANF.MI","GLE.MI","RNO.MI","FUL.MI","GAB.MI","GAMB.MI","GALA.MI","GEO.MI","GE.MI","SGR.MI","SG.MI","GGP.MI","GGTV.MI","PGR.MI","GO.MI","LMG.MI","IKGR.MI","IIG.MI","LVMH.MI","IES.MI","IGD.MI","IGV.MI","IIN.MI","IKF.MI","IKG.MI","IMA.MI","SAL.MI","SALR.MI","IMS.MI","IP.MI","IRE.MI","IRC.MI","ISPR.MI","ISP.MI","ISG.MI","ISGS.MI","SRN.MI","STEF.MI","SRG.MI","SO.MI","PR.MI","PINF.MI","PIA.MI","IT.MI","COF.MI","TME.MI","TXT.MI","TRN.MI","TIT.MI","TIS.MI","TIP.MI","SSL.MI","SPMR.MI","SPM.MI","SES.MI","SAVE.MI","SAB.MI","RN.MI","PRL.MI","MS.MI","MON.MI","MLM.MI","MCH.MI","ITM.MI","IND.MI","INC.MI","COV.MI","LIT.MI","PLTE.MI","RAT.MI","MEC.MI","SPA2.MI","ITMR.MI","SII.MI","USRB.MI","CAD.MI","ENG.MI","NOE.MI","MTV.MI","MIT.MI","SITI.MI","DEA.MI","MBY.MI","PRI.MI","CALT.MI","PITE.MI","PQ.MI","AUTME.MI","ROS.MI","TBM.MI","UNIP.MI","SFL.MI","MAIL.MI","TBS.MI","SNA.MI","MTH.MI","PRS.MI","PST.MI","TES.MI","CAI.MI","SB.MI","VLA.MI","RWAY.MI","TER.MI","MBR.MI","LVEN.MI","KRE.MI","MCK.MI","ME.MI","MSP.MI","LUVE.MI","PCP.MI","SRI.MI","TECN.MI","RM.MI","VLS.MI","SOL.MI","US.MI","IWB.MI","WIG.MI","VIN.MI","PRM.MI","NPI.MI","ITW.MI","OVS.MI","SSB.MI","OLI.MI","IVS.MI","KER.MI","TEN.MI","TEW.MI","INGA.MI","UNA.MI","NOKIA.MI","OR.MI","BAY.MI","ENGI.MI"]

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
