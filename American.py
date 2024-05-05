
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
    available_tickers = ["ERC","AMPE","NOG","CVU","ASM","AE","HUSA","AWX","APT","AXN","UAMY","ADK","CH","AIRI","EAD","ATNM","AST","HRT","ECF","CIK","ISL","FAX","DIT","APHB","ERH","AKG","ACY","NEN","AXU","APP","ADGE","ACU","DLA","MZA","FEN","AUMN","AMS","ALN","AAMC","IF","ETF","AXX","WGA","SBI","IAF","FCO","ALTV","WRN","NZH","IGZ","VKI","NXZ","AVL","NVX","LAQ","GLV","AINC","AFCO","AAU","AUXO","NXK","IBO","HCAC","MHM","DFF","AIII","BWL-A","BTX","HEB","BDL","SYN","ROX","EVBN","BAA","NAVB","CANF","BKJ","BHB","PLX","BRN","BTG","BRG","NML","BONE","BDR","MHE","BVX","BTN","NHS","FWV","EIP","BCV","TOF","NBW","MAB","MIW","BZM","BGI","PBM","NTN","MVF","DHY","BPMX","BGSF","NBO","EVM","EMJ","EIM","BZC","NRO","ENX","EIV","BLE","BFY","NYH","BHV","NBH","EIO","EIA","ZBZX","COVR","BLJ","MTNB","LNG","CQP","VHC","GV","CRMD","CCF","NHC","IGC","CEF","SYRG","LEU","GORO","EMAN","DNN","CLM","TIS","XXII","TMP","SKY","CVM","PZG","MXC","ETAK","STRP","SEB","PLM","LSG","FPP","CRV","TPI","LODE","CIX","CAW","WYY","MCF","GBR","DXR","DGSE","ZBB","UEC","TRX","SGB","SGA","RWC","MVG","MSN","MGT","IEC","DPW","CVR","CUO","CFD","VTG","TGD","SIM","PRK","PED","MGH","MCZ","FSP","ESP","EPM","XRA","RBY","HLTH","GTU","GSV","CNR","VGZ","INTT","ERN","ENSV","CTP","CTO","CRF","CPHI","CET","MOC","IPB","GLQ","FTF","ERB","SDPI","DSS","EVV","NAK","VMM","VCF","DMF","DEJ","VFL","HNW","ISDR","DXI","YGRO","GST","GTE","UUUU","EOX","ELMD","YUMA","EVI","EGAS","EGI","RIF","JOB","EVO","REI","LLEX","EMI","XPL","REE","MMV","GRF","ENRJ","ELLO","CQH","EVP","EVJ","TIK","EVY","EMXX","CSCR","CEV","ESNC","URZ","PCG-PA","ENRJ-P","YUMA-PA","SCE-PD","EPM-PA","LTS","IFMI","PHF","FRS","RCG","FSI","UTG","UFAB","NPN","NJV","GLO","FRD","CTF","CCA","UTG-RWI","NGD","GSAT","GSS","GIG","SAND","GPL","GVP","HTM","GGN","GMO","GSB","WTT","GLOW","PLG","GLU","SSN","LGL","UWN","MDW","GRH","OSGB","HLM-P","GRH-PC","GGN-PB","HH","IMH","IHT","HMG","XTNT","SSY","THM","INFU","LBMH","PARR","CDOR","MHH","CRVP","TPHS","SENS","NHC-PA","MHR-PC","MSTX","TRXC","NG","ISR","TXMD","IDI","LOV","IBIO","RNN","RLGT","IMUC","NNVC","INUV","IMO","URG","TGC","ORM","NBY","JRJR","KIQ","KLDX","NSU","TAT","SPP","IG","LBY","TGB","LIQT","VNRX","CKX","TAS","SVLC","MEA","IDN","MGN","CMT","MLSS","MAG","MJCO","CRHM","RVM","NCQ","NSPR","NTIP","NSAT","ONP","IOT","OGEN","OCX","OSGB.A","PTN","PIP","PW","CFP","PFNX","QRM.A","ETF.A","RVP","REED","CVRS","TLR","STS","SIF","SVT","SLI","VISI","UUU","INS","UQM","TRT","GLU-PA","VSR","VII","VHC.A","WRN.A","WIL.A","WGA.A","XXII.A","XPL.A","XRA.A","YGRO.A","YUMA-PA.A","YUMA.A","ZTST","ZBB.A","AA-P","AAU.A","AA-P.A","AAMC.A","ACY.A","ACU.A","ADGE.A","ADK-PA.A","ADK-PA","AE.A","AINC.A","AIII.A","AIRI.A","AKG.A","ALN.A","ALTV.A","AMS.A","AMCO.A","AMPE.A","AMZG.A","ANV.A","APT.A","API.A","APTS.A","APP.A","AQQ.A","TKAT","AST.A","ASM.A","ASB-WT","ATL.A","ATNM.A","AVL.A","AWX.A","AXX.A","AXN.A","AXU.A","JPST","BCV.A","BDL.A","BDR.A","BIR-PA","BFY.A","BGSF.A","BGI.A","BHV.A","BHB.A","BTX-WI","BIR-PA.A","BKJ.A","BRG-PA","BLJ.A","BLE.A","BONE.A","IAF.A","BPS.A","BTX-WT","BTN.A","BTI.A","BTSTA-TEST","BTG.A","BTX.A","BVX.A","BWL-A.A","BZC.A","BZM.A","SCE-PE","SCE-PC","CCF.A","CCA.A","CET.A","CEV.A","CFD.A","CFP.A","CIX.A","CIK.A","CKX.A","CLM.A","CMT.A","CNR.A","CPHI.A","CQH.A","CQP.A","CRVP.A","CRF.A","VCF.A","CRMD.A","CRV.A","CSCR.A","CTP.A","CTF.A","CTO.A","PW-PA","CUR.A","CUO.A","CVU.A","CVSL.A","CVM-WT","CVM.A","CVR.A","DAKP.A","DFF.A","DGSE.A","DHY.A","DIT.A","DIVC.A","DLA.A","DMF.A","DNN.A","DPW.A","DSS.A","DXR.A","EAD.A","ECF.A","SCE-PB","EGI.A","EGAS.A","EIV.A","EIM.A","EIP.A","EIO.A","EIA.A","PCG-PG","PCG-PE","PCG-PD","PCG-PB","PCG-PH","PCG-PI","ELLO.A","ELMD.A","PCG-PC","EMXX.A","EMAN.A","EMI.A","EMJ.A","EOX.A","EPM-PA.A","EPM.A","ERB.A","ERN.A","ERC.A","ERH.A","ESP.A","ESTE.A","ESBA.A","ETAK.A","EVO.A","EVBN.A","EVI.A","EVP.A","EVV.A","EVY.A","EVJ.A","EVM.A","GST-PA","GST-PB","FAX.A","FBGX.A","FCO.A","FEN.A","FLGE.A","FMLP.A","FPI.A","FPP-WT","FPP.A","FRS.A","FSI.A","FSP.A","FTF.A","UTG-RI","FWV.A","GGN-PB.A","GGN.A","GIG.A","GLV.A","GLOW.A","GLO.A","GLU.A","GLU-PA.A","GLQ.A","GMO.A","GORO.A","GPL.A","GSB.A","GST.A","GST-PA.A","GSS.A","GSAT.A","GST-PB.A","GSV.A","GTE.A","GTU.A","GV.A","GVP.A","HCHC.A","HEB.A","HH.A","HLTH.A","HLM-P.A","HMG.A","HNW.A","HRT.A","HTM.A","MHR-PD","MHR-PE","HUSA.A","IBIO.A","IDN.A","IDI.A","IEC.A","IF.A","IFMI.A","IGC.A","IGC-WT","IG.A","IHT.A","IMUC.A","IMO.A","IMH.A","IOT.A","IPB.A","IRT.A","ISR.A","ISDR.A","ISL.A","ITI.A","JOB.A","JRS.A","KIQ.A","LAQ.A","LTS-PA","LBY.A","LBMH.A","LEI.A","LEU.A","LGL.A","LGL-WT","LNG.A","RLGT-PA","LODE.A","LOV.A","LSG.A","MCF.A","MCZ.A","MDM.A","MDW.A","MDGN-WT","MDGN.A","MGT.A","MGN.A","MGH.A","MHR-PE.A","MHE.A","MHR-PC.A","MHH.A","MHM.A","MHR-PD.A","MHW.A","MMV.A","MOC.A","MSN.A","MSC.A","MSTX.A","MVF.A","MVG.A","MXC.A","MZA.A","NAK.A","NAVB.A","NBO.A","NBH.A","NBY.A","NBW.A","NCQ.A","NCB.A","NEN.A","NG.A","NGD.A","NHS.A","NHC-PA.A","NHC.A","NJV.A","NMZ.A","NML.A","NNVC.A","NOG.A","NOM.A","NPN.A","NRO.A","NSAT.A","NSPR.A","NSU.A","NTN.A","NTIP.A","NVX.A","NVG.A","NXZ.A","NXK.A","NYV.A","NYH.A","NZF.A","NZH.A","OCX-WI","OESX.A","OGCP.A","OGEN.A","ONP.A","ONVO.A","ORM.A","PAL.A","PARR.A","PBM.A","PCG-PD.A","PCG-PH.A","PCG-PI.A","PCG-PE.A","PCG-PB.A","PCG-PC.A","PCG-PG.A","PCG-PA.A","PED.A","PFNX.A","PHF.A","PIP.A","PRK.A","PTN.A","PVCT.A","PW.A","PW-PA.A","PZG.A","RBY.A","RCG.A","RIC.A","RIF.A","RLGT-PA.A","RLGT.A","RNN.A","RODI.A","ROX.A","RVM.A","RVP.A","RWC.A","SAND.A","SBI.A","SCE-PE.A","SCE-PB.A","SCE-PC.A","SCE-PD.A","SDPI.A","SDA.A","SGB.A","SGA.A","SIF.A","SIM.A","SKY.A","SLI.A","SMHD.A","SMU.A","SSN.A","SSY.A","STS.A","STRP.A","SVBL.A","SVLC.A","SVT.A","SYN.A","SYRG.A","TAT.A","TAS.A","TGB.A","TGD.A","TGC.A","THM.A","TIS.A","TIK.A","TLR.A","TMP.A","TOF.A","TPI.A","TPLM.A","TRT.A","TRX.A","TXMD.A","UAMY.A","UEC.A","UQM.A","URZ.A","URG.A","UTG.A","UUUU.A","UUU.A","UWN.A","VFL.A","VGZ.A","VISI.A","VII.A","VKI.A","VMM.A","VNRX.A","VSR.A","VTG.A","WTT.A","WYY.A","ADK.A","AUMN.A","BAA.A","BRG.A","BRN.A","CAK.A","CANF.A","CAW.A","COVR.A","DEJ.A","ENRJ.A","ENRJ-P.A","ENSV.A","ENX.A","FISK.A","FRD.A","GBR.A","GRC.A","GRF.A","GRH-PC.A","GRH.A","HOMX.A","HOML.A","INFU.A","INFL.A","INS.A","INTT.A","INUV.A","LIQT.A","LTS.A","LTS-PA.A","MAB.A","MEA.A","MIW.A","PLG.A","PLM.A","PLX.A","REED.A","REE.A","REI.A","SARA.A","SEB.A","SPP.A","TRC-WT","TRXC.A"]

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
