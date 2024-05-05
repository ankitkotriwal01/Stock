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
    available_tickers = ["PHOL-R.BK","PACE.BK","TAE.BK","WHAPF.BK","TPCH.BK","JUBILE.BK","JTS.BK","JMT-R.BK","JASIF.BK","JCT.BK","JWD.BK","JMART.BK","NPK-R.BK","KTC.BK","KTC-R.BK","KTB.BK","KGI.BK","KC.BK","KASET.BK","KPNPF.BK","KWC-R.BK","POMPUI.BK","NEP-R.BK","UPA-R.BK","QHPF.BK","QLT-R.BK","QH.BK","QTC-R.BK","Q-CON-R.BK","QHOP.BK","QLT.BK","QHHR.BK","QH-R.BK","QTC.BK","Q-CON.BK","SPRC-R.BK","SVH.BK","UWC-R.BK","UPF-R.BK","UNIQ.BK","VIBHA.BK","VARO.BK","VIH.BK","WIN-R.BK","TWPC-R.BK","WR.BK","WHA.BK","WHABT.BK","TWS.BK","WG.BK","WORLD-R.BK","WHART.BK","WIIK.BK","SPA-R.BK","XO-R.BK","XO.BK","YUASA.BK","YCI.BK","YUASA-R.BK","YNP-R.BK","YCI-R.BK","YNP.BK","ZMICO-R.BK","ZMICO.BK","AAV.BK","AAV-R.BK","ABPIF.BK","ABICO-R.BK","ABICO.BK","EA-R.BK","ABC-R.BK","EA.BK","ABC.BK","ACD-R.BK","ACAP-R.BK","ACC-R.BK","ACC.BK","ACAP.BK","AJD.BK","ADAM-R.BK","ADVANC.BK","ADVANC-R.BK","ADVA42P1602A.BK","AEONTS-R.BK","AEC-R.BK","AEONTS.BK","AEC.BK","AFC.BK","AF.BK","AF-R.BK","AFC-R.BK","TAE-R.BK","AGE.BK","AGE-R.BK","AHC.BK","AH-R.BK","AH.BK","AHC-R.BK","EFORL.BK","AIRA-R.BK","AIT-R.BK","AIRA.BK","NOK-R.BK","AIE-R.BK","BA-R.BK","EFORL-R.BK","AIE.BK","BA.BK","AI-R.BK","NOK.BK","AI.BK","AIT.BK","AJD-R.BK","AJ-R.BK","AJ.BK","AKR-R.BK","AKP.BK","AKP-R.BK","AKR.BK","ALUCON-R.BK","ALUCON.BK","AMANAH.BK","AMARIN.BK","AMATAV-R.BK","AMANAH-R.BK","AMATA.BK","AMATA-R.BK","AMATAV.BK","AMATAR.BK","AMC-R.BK","AMC.BK","AMARIN-R.BK","CTARAF.BK","CSS.BK","HPF.BK","TREIT.BK","ANAN.BK","TLGF.BK","TNPF.BK","CSS-R.BK","LHPF.BK","ANAN-R.BK","AOT.BK","AOT-R.BK","AP.BK","APCS.BK","APURE.BK","APURE-R.BK","APX.BK","AP-R.BK","APCO.BK","APX-R.BK","APCO-R.BK","APCS-R.BK","AQUA.BK","AQ.BK","AQUA-R.BK","AQ-R.BK","ARIP-R.BK","ARROW-R.BK","ARROW.BK","ARIP.BK","ASP.BK","ASIAN.BK","BLA-R.BK","ASCON.BK","ASP-R.BK","ASEFA-R.BK","PMTA-R.BK","ASK.BK","AS.BK","ASIMAR-R.BK","UPA.BK","ASEFA.BK","BLA.BK","ASK-R.BK","AS-R.BK","ASIA-R.BK","ASIA.BK","PMTA.BK","ASIMAR.BK","PCA.BK","PCA-R.BK","ASIAN-R.BK","J.BK","SCBLIF.BK","J-R.BK","ATP30-R.BK","ATP30.BK","AUCT.BK","AUCT-R.BK","AYUD.BK","AYUD-R.BK","BAY.BK","BRC.BK","BBL.BK","BBL-R.BK","BCP.BK","BCH-R.BK","BCH.BK","BCP-R.BK","BDMS.BK","BDMS-R.BK","BECL.BK","BEM.BK","BEAUTY-R.BK","BEC-R.BK","BFIT.BK","BFIT-R.BK","BGT.BK","BGT-R.BK","BH-R.BK","BH.BK","BIGC.BK","BIG-R.BK","BIG.BK","BIGC-R.BK","BJC.BK","BJC-R.BK","BJCHI.BK","BJCHI-R.BK","BKI-R.BK","BKD.BK","BKI.BK","BKD-R.BK","BKKCP.BK","BLAND-R.BK","BLISS.BK","BLAND.BK","BLISS-R.BK","BMCL.BK","BOL-R.BK","BOL.BK","BROCK-R.BK","BROOK.BK","BRR-R.BK","BROCK.BK","BSM-R.BK","BSBM.BK","BSM.BK","BSBM-R.BK","BTS.BK","BTC.BK","BTC-R.BK","BTS-R.BK","BTNC-R.BK","BTNC.BK","BTSGIF.BK","CMR.BK","SBPF.BK","CMR-R.BK","BRR.BK","BUI.BK","BUI-R.BK","BWG.BK","BWG-R.BK","GCAP.BK","IFS-R.BK","CBG-R.BK","CBG.BK","CCET-R.BK","CCN-R.BK","CCN.BK","CCP-R.BK","CCP.BK","CCET.BK","CEN-R.BK","CENTEL.BK","LHSC.BK","CEI.BK","CEI-R.BK","CPICO.BK","TUCC-R.BK","TUCC.BK","CEN.BK","CENTEL-R.BK","CFRESH-R.BK","CFRESH.BK","CGD.BK","CGD-R.BK","CGH.BK","CGH-R.BK","CHG.BK","CHG-R.BK","CHUO.BK","CHUO-R.BK","CHOW.BK","CIMBT.BK","U-R.BK","MJLF.BK","CIG.BK","CIG-R.BK","CIMBT-R.BK","CITY-R.BK","CI-R.BK","CI.BK","CITY.BK","CKP.BK","CK.BK","CK-R.BK","CKP-R.BK","CMO.BK","CM-R.BK","CM.BK","CMO-R.BK","CNT.BK","CNT-R.BK","CNS.BK","CPALL-R.BK","CPL-R.BK","CPH.BK","CPI.BK","CPR-R.BK","CPN.BK","CPALL.BK","CPF-R.BK","CPN-R.BK","CPL.BK","CPH-R.BK","CRYSTAL.BK","CPI-R.BK","CPF.BK","CPR.BK","CPNCG.BK","CPNRF.BK","CPTGF.BK","CRANE.BK","CRANE-R.BK","CSP-R.BK","CSR.BK","CSP.BK","CSL-R.BK","CSR-R.BK","CSL.BK","CSC-R.BK","CSC.BK","CTW-R.BK","CTW.BK","CWT-R.BK","CWT.BK","DAII-R.BK","DAII.BK","DCON.BK","DCC-R.BK","DCC.BK","DCORP-R.BK","DCORP.BK","DCON-R.BK","DELTA.BK","PHOL.BK","SANKO.BK","DIMET.BK","DIMET-R.BK","TVD-R.BK","DIF.BK","SANKO-R.BK","TVD.BK","DNA-R.BK","DNA.BK","CHO-R.BK","CHO.BK","DRACO.BK","DRT.BK","DRT-R.BK","DRACO-R.BK","DSGT.BK","DSGT-R.BK","DTAC.BK","DTCI-R.BK","DTC.BK","DTAC-R.BK","DTCPF.BK","DTC-R.BK","DTCI.BK","EASTW.BK","EASON.BK","EPG-R.BK","ECF.BK","EPG.BK","EARTH-R.BK","EASON-R.BK","EARTH.BK","EASTW-R.BK","ECF-R.BK","ECL-R.BK","ECL.BK","NINE-R.BK","NINE.BK","EE.BK","EE-R.BK","EGCO.BK","EGATIF.BK","EGCO-R.BK","EIC-R.BK","UOB8TF.BK","EIC.BK","SCI.BK","SCI-R.BK","EMC-R.BK","EMC.BK","PTG.BK","T.BK","EPCO.BK","EPCO-R.BK","MGE.BK","ERW.BK","ERW-R.BK","ERWPF.BK","IMPACT.BK","ESTAR.BK","LHHOTEL.BK","S-R.BK","ESSO.BK","S.BK","ESTAR-R.BK","ESSO-R.BK","MIT.BK","UREKA.BK","UREKA-R.BK","EVER-R.BK","EVER.BK","SGF-R.BK","FANCY.BK","FANCY-R.BK","SGF.BK","FER.BK","FER-R.BK","NFC.BK","RP-R.BK","RP.BK","NFC-R.BK","FE-R.BK","FE.BK","FIRE.BK","FVC.BK","TMILL.BK","TMILL-R.BK","FMT.BK","FMT-R.BK","FNS.BK","FNS-R.BK","FOCUS-R.BK","FPI.BK","FSMART-R.BK","SFP-R.BK","POMPUI-R.BK","TFG-R.BK","FPI-R.BK","TKN.BK","FORTH-R.BK","FOCUS.BK","TFG.BK","FSMART.BK","TKN-R.BK","SFP.BK","FORTH.BK","FSS-R.BK","FSS.BK","SSTSS.BK","URBNPF.BK","M-STOR.BK","TLOGIS.BK","POPF.BK","FUTUREPF.BK","SSPF.BK","TIF1.BK","TRIF.BK","GOLDPF.BK","SCBSET.BK","UNIPF.BK","MIPF.BK","FVC-R.BK","GC.BK","GCAP-R.BK","GC-R.BK","GEL-R.BK","LPH.BK","GEL.BK","GENCO-R.BK","GENCO.BK","LPH-R.BK","GFPT-R.BK","GFPT.BK","GIFT-R.BK","GIFT.BK","GJS.BK","GJS-R.BK","GL-R.BK","UAC-R.BK","GLOW-R.BK","GPSC-R.BK","GLOW.BK","GPSC.BK","VGI-R.BK","STHAI.BK","SCAN.BK","GLOBAL-R.BK","GL.BK","STHAI-R.BK","VGI.BK","GLAND-R.BK","UAC.BK","GLOBAL.BK","SCAN-R.BK","GLAND.BK","SUTHA.BK","SUTHA-R.BK","GOLD.BK","GOLD-R.BK","PCSGH-R.BK","ICHI.BK","GRAMMY.BK","GSTEL.BK","GSTEL-R.BK","GTB-R.BK","GTB.BK","GUNKUL.BK","GUNKUL-R.BK","GYT-R.BK","GYT.BK","HANA.BK","HTECH.BK","HTECH-R.BK","THL-R.BK","THL.BK","HANA-R.BK","HFT.BK","HFT-R.BK","HMPRO.BK","HMPRO-R.BK","HOTPOT.BK","HPT.BK","HPT-R.BK","HTC.BK","HTC-R.BK","HYDRO.BK","HYDRO-R.BK","ICC-R.BK","ICC.BK","ICHI-R.BK","IEC.BK","IEC-R.BK","IFEC-R.BK","IFEC.BK","IFS.BK","IHL.BK","IHL-R.BK","ILINK.BK","ILINK-R.BK","IRPC-R.BK","IRPC.BK","IRCP.BK","IRC-R.BK","IRCP-R.BK","IRC.BK","ITD-R.BK","ITD.BK","IT.BK","IT-R.BK","LIT.BK","LIT-R.BK","IVL.BK","IVL-R.BK","JAS-R.BK","JAS.BK","JCT-R.BK","JCP.BK","JMART-R.BK","JMT.BK","JSP.BK","JSP-R.BK","JTS-R.BK","JUTHA-R.BK","JUTHA.BK","JUBILE-R.BK","JWD-R.BK","KAMART.BK","KASET-R.BK","KTIS.BK","KTIS-R.BK","KAMART-R.BK","KBS.BK","KBANK-R.BK","KBANK.BK","KBS-R.BK","KCE-R.BK","KCM-R.BK","KCM.BK","KCAR.BK","KC-R.BK","KCE.BK","KCAR-R.BK","KDH.BK","KDH-R.BK","KGI-R.BK","K-R.BK","KIAT-R.BK","K.BK","KIAT.BK","KKP.BK","KKP-R.BK","KKC-R.BK","KKC.BK","NPK.BK","KOOL.BK","KOOL-R.BK","KSL-R.BK","KSL.BK","KTP.BK","KTECH-R.BK","KTB-R.BK","KTECH.BK","KWC.BK","LALIN-R.BK","LANNA-R.BK","LALIN.BK","LANNA.BK","LDC.BK","LDC-R.BK","LEE.BK","TTLPF.BK","MTLS-R.BK","MTLS.BK","LEE-R.BK","LH-R.BK","LHBANK-R.BK","LHBANK.BK","LHK.BK","LHK-R.BK","LH.BK","TMI-R.BK","SR-R.BK","SPVI.BK","SPCG.BK","SMPC.BK","PPP.BK","MEGA.BK","COLOR.BK","PTG-R.BK","SYMC.BK","INSURE-R.BK","SPA.BK","NDR.BK","TTCL.BK","SAWAD-R.BK","SR.BK","SPVI-R.BK","MONO.BK","SCN.BK","SMART.BK","NUSA-R.BK","THANA.BK","HOTPOT-R.BK","LOXLEY.BK","LOXLEY-R.BK","NCL-R.BK","WICE-R.BK","WICE.BK","NCL.BK","LPN-R.BK","LPN.BK","LRH-R.BK","LRH.BK","LST.BK","LST-R.BK","LUXF.BK","LVT-R.BK","LVT.BK","MALEE-R.BK","PM-R.BK","MAJOR-R.BK","MANRIN.BK","MANRIN-R.BK","MACO.BK","MATI.BK","MAX.BK","PCSGH.BK","MBKET.BK","MBAX.BK","MBK.BK","MBK-R.BK","MBKET-R.BK","MBAX-R.BK","MCS.BK","MC-R.BK","MCOT.BK","MCOT-R.BK","MCS-R.BK","MC.BK","MDX.BK","MDX-R.BK","METCO.BK","PLANB-R.BK","2S.BK","2S-R.BK","MFEC-R.BK","MFC-R.BK","M-II.BK","MNIT.BK","MFEC.BK","MFC.BK","SMT.BK","MINT.BK","MJD.BK","MJD-R.BK","M.BK","MK.BK","MK-R.BK","M-R.BK","ML.BK","ML-R.BK","MNIT2.BK","MNRF.BK","MONTRI.BK","MONO-R.BK","MOONG-R.BK","PIMO-R.BK","MODERN.BK","MODERN-R.BK","MOONG.BK","PIMO.BK","MPIC-R.BK","MPG.BK","MPIC.BK","MPG-R.BK","MSC-R.BK","MSC.BK","MTI.BK","MTI-R.BK","NYT-R.BK","NBC.BK","NYT.BK","NBC-R.BK","NCH.BK","NC.BK","NCH-R.BK","NC-R.BK","NDR-R.BK","NEWS.BK","NEW.BK","NEP.BK","NEWS-R.BK","NEW-R.BK","NKI.BK","NKI-R.BK","NMG-R.BK","NMG.BK","NNCL-R.BK","NNCL.BK","NOBLE-R.BK","NOBLE.BK","NPP.BK","NPP-R.BK","NSI.BK","NSI-R.BK","NTV-R.BK","NTV.BK","NUSA.BK","NWR-R.BK","NWR.BK","OCEAN-R.BK","OCC.BK","OCEAN.BK","OCC-R.BK","SIRIP.BK","OGC.BK","OGC-R.BK","OHTL-R.BK","OHTL.BK","SEAOIL.BK","VPO-R.BK","SEAOIL-R.BK","OISHI.BK","OISHI-R.BK","VPO.BK","OTO.BK","OTO-R.BK","ORI.BK","ORI-R.BK","PPF.BK","SINGHA.BK","SPWPF.BK","PJW.BK","PAF.BK","PAP-R.BK","PB.BK","PB-R.BK","PDI-R.BK","PDG.BK","PDG-R.BK","PDI.BK","PERM-R.BK","PERM.BK","PE.BK","SPRC.BK","PE-R.BK","PF.BK","PF-R.BK","PG.BK","PG-R.BK","PICO-R.BK","PICO.BK","PJW-R.BK","PK-R.BK","PK.BK","PLE.BK","PPS.BK","RICHY.BK","PLAT.BK","PM.BK","POLAR-R.BK","SMC.BK","POLAR.BK","TPOLY-R.BK","PSTC-R.BK","TPCH-R.BK","TPOLY.BK","PSTC.BK","POST-R.BK","POST.BK","SAWAD.BK","PPM.BK","PPS-R.BK","PPP-R.BK","PPM-R.BK","PRG-R.BK","TRS-R.BK","PRG.BK","PR-R.BK","PRAKIT-R.BK","TLHPF.BK","PRECHA-R.BK","SLP.BK","SLP-R.BK","PRAKIT.BK","PR.BK","PREB.BK","PRIN-R.BK","PSL-R.BK","PS.BK","PS-R.BK","PSL.BK","PTT.BK","PTTE06P1602A.BK","PTL.BK","PTTEP-R.BK","PTTEP.BK","PTTGC.BK","PTL-R.BK","PT-R.BK","PTT-R.BK","PTTGC-R.BK","PT.BK","PACE-R.BK","TSR.BK","SAFARI.BK","PLAT-R.BK","TSI-R.BK","TNP.BK","TMI.BK","MEGA-R.BK","TT-R.BK","SMT-R.BK","WHA-R.BK","COM7.BK","INSURE.BK","ROCK.BK","SPCG-R.BK","TACC.BK","THANA-R.BK","COM7-R.BK","COLOR-R.BK","TMC.BK","TSE.BK","WORLD.BK","VTE.BK","SENA-R.BK","RWI-R.BK","VI-R.BK","SAPPE.BK","TT&T-R.BK","WINNER.BK","WP-R.BK","S11-R.BK","UWC.BK","COL.BK","WP.BK","TNP-R.BK","WINNER-R.BK","VTE-R.BK","TSE-R.BK","GREEN-R.BK","TPROP.BK","TAKUNI.BK","SMPC-R.BK","TTCL-R.BK","SAFARI-R.BK","BRC-R.BK","TWPC.BK","TACC-R.BK","SAPPE-R.BK","ROCK-R.BK","CHOW-R.BK","FIRE-R.BK","RICHY-R.BK","TSR-R.BK","PLANB.BK","TMC-R.BK","TAKUNI-R.BK","VI.BK","SYMC-R.BK","TVT-R.BK","SMART-R.BK","SCN-R.BK","VIH-R.BK","TVT.BK","TSI.BK","SENA.BK","BEAUTY.BK","RWI.BK","WR-R.BK","S11.BK","COL-R.BK","ADAM.BK","TU-R.BK","PYLON-R.BK","PYLON.BK","RAM-R.BK","RATCH-R.BK","RAM.BK","RATCH.BK","RCI-R.BK","RCL-R.BK","RCI.BK","RCL.BK","RICH.BK","RICH-R.BK","RML-R.BK","RML.BK","ROH.BK","ROH-R.BK","ROJNA.BK","ROJNA-R.BK","ROBINS-R.BK","ROBINS.BK","RPC.BK","RPC-R.BK","RS.BK","RS-R.BK","SAT.BK","SAM-R.BK","SALEE-R.BK","SAM.BK","SABINA.BK","SAMART.BK","SAMTEL.BK","SAWANG.BK","SALEE.BK","SAT-R.BK","SCC.BK","SCB.BK","SCG.BK","SCC-R.BK","SCP-R.BK","SCCC-R.BK","SCCC.BK","SC-R.BK","SCG-R.BK","SCP.BK","SCB-R.BK","SC.BK","SF-R.BK","SF.BK","SGP.BK","SGP-R.BK","SHANG-R.BK","SHANG.BK","SINGER-R.BK","SIRI-R.BK","SIAM.BK","SIMAT-R.BK","SITHAI-R.BK","SIM.BK","SITHAI.BK","SIAM-R.BK","SIMAT.BK","SIM-R.BK","SIS.BK","SIRI.BK","SINGER.BK","SIS-R.BK","SKR.BK","SKR-R.BK","SMK-R.BK","SMIT-R.BK","SMG-R.BK","SMK.BK","SMIT.BK","SMM.BK","SMG.BK","SMM-R.BK","SNP.BK","SNP-R.BK","SNC.BK","SNC-R.BK","SOLAR.BK","SORKON.BK","SOLAR-R.BK","SPORT.BK","SPPT-R.BK","SPI-R.BK","SPORT-R.BK","SPALI-R.BK","SPACK-R.BK","SPG.BK","SPI.BK","SPC-R.BK","SPC.BK","SRICHA.BK","SRICHA-R.BK","SST-R.BK","SSSC-R.BK","SSI-R.BK","SSF.BK","SSC-R.BK","SSC.BK","SSI.BK","SSSC.BK","SSTPF.BK","SST.BK","SSF-R.BK","STEC-R.BK","STANLY.BK","STAR.BK","STEC.BK","STPI-R.BK","STAR-R.BK","STA.BK","STA-R.BK","SUSCO.BK","SUPER.BK","SUPER-R.BK","SUSCO-R.BK","SUC-R.BK","SUC.BK","SVI-R.BK","SVOA-R.BK","SVI.BK","SVH-R.BK","SVOA.BK","SWC.BK","SWC-R.BK","SYNEX.BK","SYNTEC-R.BK","SYNEX-R.BK","SYNTEC.BK","TAPAC.BK","TAPAC-R.BK","TASCO.BK","TASCO-R.BK","TBSP.BK","TBSP-R.BK","TCAP.BK","TCCC-R.BK","TCOAT-R.BK","TCB-R.BK","TC-R.BK","TCMC-R.BK","TCC-R.BK","TCIF.BK","TCB.BK","TCAP-R.BK","TC.BK","TCJ-R.BK","TCMC.BK","TCCC.BK","TCJ.BK","TCC.BK","TCOAT.BK","TEAM.BK","TFI.BK","TFUND.BK","TF-R.BK","TFI-R.BK","TFD-R.BK","TFD.BK","TF.BK","TGCI.BK","TGCI-R.BK","TGROWTH.BK","TGPRO-R.BK","TGPRO.BK","INTUCH.BK","TU.BK","TTW.BK","TRUE.BK","TMT.BK","TKT.BK","TKS-R.BK","TK-R.BK","THAI.BK","TIW-R.BK","SAUCE-R.BK","TPA-R.BK","TKS.BK","TNH.BK","BAFS-R.BK","TPP.BK","SPACK.BK","PRANDA-R.BK","L&E-R.BK","TNDT.BK","PATO-R.BK","TRT.BK","LIVE.BK","MILL-R.BK","TMW-R.BK","TVI.BK","TNITY.BK","BAFS.BK","DEMCO.BK","TOP-R.BK","TUF.BK","TMD-R.BK","UV-R.BK","TPAC.BK","BAT-3K-R.BK","UMS.BK","THE-R.BK","SE-ED-R.BK","SEAFCO-R.BK","SEAFCO.BK","MAJOR.BK","UKEM.BK","TLUXE.BK","TPAC-R.BK","LTX-R.BK","WACOAL-R.BK","MATCH.BK","TIW.BK","SPG-R.BK","TH-R.BK","TIPCO.BK","TTI.BK","GRAND.BK","TICON.BK","TNL.BK","TWP.BK","TWFP.BK","INET.BK","TNH-R.BK","TVO-R.BK","A.BK","TRT-R.BK","MATI-R.BK","MATCH-R.BK","UKEM-R.BK","TSC.BK","UTP-R.BK","TTA.BK","THREL-R.BK","TR.BK","TPC.BK","F&D.BK","UBIS-R.BK","F&D-R.BK","TTL-R.BK","TWZ.BK","TVI-R.BK","TYCN.BK","S-&-J-R.BK","TEAM-R.BK","TPA.BK","U.BK","TMD.BK","TRC.BK","THRE-R.BK","GBX-R.BK","UOBKH.BK","UP-R.BK","INOX.BK","TT.BK","SAUCE.BK","TWZ-R.BK","TSTE-R.BK","T-R.BK","PL-R.BK","TKT-R.BK","TNPC-R.BK","TLUXE-R.BK","VIBHA-R.BK","TOPP.BK","THAI-R.BK","TOG.BK","INOX-R.BK","S-&-J.BK","GRAND-R.BK","VNT.BK","E-R.BK","TTW-R.BK","TIP-R.BK","UPOIC.BK","TSF.BK","SAMTEL-R.BK","TNPC.BK","TTL.BK","WAVE-R.BK","VNG-R.BK","UVAN-R.BK","UT-R.BK","TRC-R.BK","UEC-R.BK","THANI.BK","PRIN.BK","KYE.BK","SPPT.BK","STANLY-R.BK","TSTE.BK","TRUBB.BK","TIC-R.BK","TISCO-R.BK","TIPCO-R.BK","TIC.BK","TICON-R.BK","TIP.BK","TISCO.BK","TK.BK","TMT-R.BK","TMB-R.BK","TMB.BK","TMW.BK","TNL-R.BK","TNDT-R.BK","TNITY-R.BK","TOP.BK","TOG-R.BK","TOPP-R.BK","TPIPL.BK","TPCORP.BK","TPP-R.BK","TPC-R.BK","TPBI-R.BK","TPIPL-R.BK","TPCORP-R.BK","TPBI.BK","TRUBB-R.BK","TRS.BK","TSC-R.BK","TSTH.BK","TSTH-R.BK","TSF-R.BK","TTI-R.BK","TTTM-R.BK","TTA-R.BK","TTTM.BK","TUF-R.BK","TVO.BK","TWP-R.BK","TYCN-R.BK","UBIS.BK","UEC.BK","UMI-R.BK","UMS-R.BK","UMI.BK","UNIQ-R.BK","UOBKH-R.BK","UPF.BK","UPOIC-R.BK","UP.BK","UT.BK","UTP.BK","UVAN.BK","UV.BK","VARO-R.BK","VNT-R.BK","VNG.BK","PRO.BK","WAVE.BK","PRO-R.BK","WACOAL.BK","WG-R.BK","WIIK-R.BK","WIN.BK","WORK-R.BK","WORK.BK","BANPU-R.BK","BANPU.BK","BAT-3K.BK","BAY-R.BK","BEC.BK","BEM-R.BK","BROOK-R.BK","CHARAN.BK","CHARAN-R.BK","CHOTI.BK","CHOTI-R.BK","CNS-R.BK","DELTA-R.BK","DEMCO-R.BK","THIF.BK","GBX.BK","GRAMMY-R.BK","GREEN.BK","INTUCH-R.BK","KYE-R.BK","LIVE-R.BK","LTX.BK","MACO-R.BK","MAKRO.BK","MAKRO-R.BK","MALEE.BK","MAX-R.BK","METCO-R.BK","MIDA.BK","MIDA-R.BK","MILL.BK","MINT-R.BK","PAE-R.BK","PAE.BK","PAF-R.BK","PAP.BK","PATO.BK","PLE-R.BK","PRANDA.BK","PRECHA.BK","PREB-R.BK","PRINC-R.BK","PRINC.BK","SABINA-R.BK","SAMCO-R.BK","SAMART-R.BK","SAMCO.BK","SAWANG-R.BK","SORKON-R.BK","SPALI.BK","SPF.BK","STPI.BK","THANI-R.BK","THCOM-R.BK","THCOM.BK","THE.BK","THIP-R.BK","THIP.BK","THREL.BK","THRE.BK","TRU.BK","TRUE-R.BK","TRU-R.BK","INET-R.BK"]

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
