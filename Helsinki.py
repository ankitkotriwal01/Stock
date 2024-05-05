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
    available_tickers = ["ZO1.HA","VWS.HA","USE.HA","TLG.HA","SZU.HA","SIX2.HA","SDF.HA","PFV.HA","O4B.HA","MRK.HA","MAK.HA","LIN.HA","KD8.HA","KBC.HA","GLJ.HA","VVU.HA","CNN1.HA","JEN.HA","JUN3.HA","EJR.HA","ZJS1.HA","KTF.HA","AHOF.HA","QIA.HA","PHI1.HA","HNM.HA","QCE.HA","QSC.HA","QCI.HA","AMZ.HA","XER.HA","SRB.HA","PHM7.HA","FB2A.HA","CIS.HA","AMG.HA","BMW3.HA","RWE3.HA","PAH3.HA","SIX3.HA","VOW.HA","DWNI.HA","WDL.HA","W9X.HA","WAC.HA","O1BC.HA","XONA.HA","XCA.HA","YHO.HA","ZAL.HA","ZEG.HA","ZIL2.HA","AFX.HA","TIM.HA","AAD.HA","ARL.HA","AB1.HA","ABJ.HA","ABEC.HA","ABR.HA","ABEA.HA","AHLA.HA","B1C.HA","ADV.HA","ADD.HA","AMD.HA","ADL.HA","TEV.HA","CVLB.HA","AEND.HA","A44.HA","MTX.HA","AEC1.HA","AGX.HA","ALG.HA","FO4N.HA","AIL.HA","AIXA.HA","AIR.HA","AINN.HA","AOMD.HA","ALU.HA","CGE.HA","ALV.HA","ALD.HA","ATW.HA","AOX.HA","AM3D.HA","NGLB.HA","NCB.HA","BMT.HA","SCL.HA","AOL1.HA","APC.HA","7AA.HA","SAZ.HA","A6T.HA","ARRB.HA","ARO.HA","ASME.HA","ASG.HA","DIC.HA","SOBA.HA","AUS.HA","OMV.HA","TWB.HA","O2C.HA","BHP1.HA","2FI.HA","GU8.HA","SPR.HA","AXA.HA","SKB.HA","COM.HA","BOY.HA","BBZA.HA","BC8.HA","BCY.HA","BCO.HA","BDT.HA","BEZ.HA","BEI.HA","DBAN.HA","BE8.HA","3RB.HA","42BA.HA","WCMK.HA","BRYN.HA","BIL.HA","BIO.HA","BIJ.HA","ETG.HA","IDP.HA","BIO3.HA","SBS.HA","GBF.HA","RYS1.HA","S9A.HA","BMSA.HA","BMW.HA","BNP.HA","BNR.HA","BVB.HA","BON.HA","VIB3.HA","DB1.HA","BOSS.HA","BPE5.HA","HAK.HA","BSN.HA","BSB.HA","BSD2.HA","BST.HA","BTQ.HA","BYW6.HA","CBK.HA","CBHD.HA","CCC3.HA","HF1.HA","UNI3.HA","CWC.HA","CLS1.HA","CEV.HA","CTNK.HA","CTM.HA","NESR.HA","CSX.HA","DCH1.HA","TRVC.HA","CMC.HA","CPA.HA","CRG.HA","CRIH.HA","CRA1.HA","CXR.HA","EVD.HA","CY2.HA","DSY1.HA","DAI.HA","DBK.HA","1COV.HA","SNG.HA","TTI.HA","MEO.HA","CAP.HA","LEG.HA","DRW8.HA","KWS.HA","MEO3.HA","H5E.HA","HBM.HA","EOAN.HA","PMOX.HA","TEG.HA","HG1.HA","SW1.HA","MLP.HA","DLG.HA","WDP.HA","GUI.HA","NOVC.HA","GIL.HA","DNQ.HA","DPW.HA","HDD.HA","DRW3.HA","DRI.HA","DTE.HA","LHA.HA","O2D.HA","DUP.HA","R6C3.HA","DUE.HA","R6C.HA","D5I.HA","EBA.HA","E2F.HA","EDL.HA","EG4.HA","SND.HA","GEC.HA","LPK.HA","LLY.HA","EMP.HA","ERCB.HA","REP.HA","IXD1.HA","TNE5.HA","ENA.HA","GTQ1.HA","ESL.HA","KBU.HA","IBE1.HA","EUK2.HA","EUCA.HA","EUK3.HA","DEQ.HA","EVK.HA","EV4.HA","EVT.HA","NWT.HA","2FE.HA","FRU.HA","FGR.HA","FME.HA","FNTN.HA","WFM.HA","FPE.HA","FPE3.HA","SGE.HA","RNL.HA","GZF.HA","FRA.HA","CAR.HA","PEU.HA","UBL.HA","LOR.HA","FTE.HA","HBC1.HA","3PNA.HA","RDEB.HA","SSU.HA","HYU.HA","SSUN.HA","GXI.HA","8GM.HA","G1A.HA","GWI1.HA","GSC1.HA","GBRA.HA","GFT.HA","GFK.HA","GGS.HA","GIB.HA","GIS.HA","GS7.HA","GMM.HA","GOS.HA","GOB.HA","HAB.HA","HLAG.HA","HNR1.HA","HAL.HA","HAW.HA","HBH.HA","HDI.HA","HLE.HA","HEI.HA","HEN.HA","HMSB.HA","HNK1.HA","HEN3.HA","HHFA.HA","HLG.HA","RHO.HA","SLT.HA","HVB.HA","HWSA.HA","HYQ.HA","IBM.HA","IES.HA","IF6N.HA","IFX.HA","P1Z.HA","TQI.HA","ENI.HA","ENL.HA","SNM.HA","JNJ.HA","SFT.HA","KWI.HA","SRP.HA","SHM.HA","TOM.HA","SON1.HA","RIC1.HA","KCO.HA","KFI1.HA","KGX.HA","KPN.HA","KRN.HA","KU2.HA","LXS.HA","OLB.HA","LEO.HA","LNSX.HA","OSR.HA","LLD.HA","STM.HA","RRTL.HA","SFQ.HA","MOH.HA","MAN.HA","MAN3.HA","MCH.HA","MDO.HA","MDN.HA","MDG1.HA","6MK.HA","NMM.HA","SMHN.HA","MSF.HA","MMM.HA","TL0.HA","MOR.HA","MPCK.HA","MUV2.HA","MVV1.HA","NDA.HA","NDX1.HA","NFC.HA","NSN.HA","NEM.HA","NKE.HA","WIN.HA","TPL.HA","TNTC.HA","INN.HA","SGM.HA","NOT.HA","NST.HA","NOEJ.HA","NOA3.HA","R3Q.HA","ORC.HA","PA9.HA","UNP.HA","PBB.HA","PEP.HA","PFE.HA","VX1.HA","PS4.HA","PNE3.HA","UP7.HA","PO0.HA","PSM.HA","PRG.HA","PRA.HA","PSAN.HA","PUM.HA","RAA.HA","RHK.HA","RHM.HA","RIB.HA","RSTA.HA","RIO1.HA","RKET.HA","RWE.HA","SAP.HA","SRT.HA","SZG.HA","G24.HA","SHA.HA","S4A.HA","SGL.HA","SGS.HA","SIE.HA","SII.HA","SKFB.HA","SK1A.HA","S92.HA","SNW.HA","SOW.HA","SOO1.HA","SWVK.HA","SQU.HA","SR9.HA","SRT3.HA","SSK.HA","SUR.HA","SUY1.HA","S9P2.HA","SY1.HA","TTK.HA","TLX.HA","TC1.HA","TKA.HA","TOTB.HA","TUI1.HA","UBK.HA","0UB.HA","UTDI.HA","UNH.HA","UTC1.HA","BAC.HA","VVD.HA","VFP.HA","3V64.HA","V6C.HA","VNA.HA","VOW3.HA","VOS.HA","VT9.HA","WSU.HA","WMT.HA","WCH.HA","WDI.HA","ADS.HA","AUD.HA","BAS.HA","B5A.HA","BAYN.HA","COK.HA","CAT1.HA","CHV.HA","CON.HA","COP.HA","DEX.HA","DEZ.HA","5E2.HA","FIE.HA","FRE.HA","HOT.HA","INH.HA","INL.HA","M5Z.HA","SAX.HA","TWR.HA"]

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

