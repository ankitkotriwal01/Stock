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
    available_tickers = ["VOW3.DU","IFX.DU","ESY.DU","WUW.DU","WUG3.DU","WF5A.DU","WAN.DU","V3V.DU","V33.DU","TXA.DU","TTO.DU","TTK.DU","TIS.DU","TIN.DU","TFA.DU","T2G.DU","SZZ.DU","SRT3.DU","SNG.DU","SKB.DU","SIS.DU","RHM.DU","QB7.DU","PLT.DU","PDEK.DU","P1Z.DU","NSA.DU","NEM.DU","M3E.DU","LPK.DU","KRN.DU","JUN3.DU","IWB.DU","HGJ.DU","HDI.DU","HDD.DU","HAW.DU","H2FA.DU","FAO2.DU","EVD.DU","ZM7.DU","XONA.DU","UBL.DU","VODI.DU","RY4C.DU","RDO.DU","XSZ.DU","XSC.DU","XKK.DU","UBE.DU","TDK.DU","NTT.DU","NBO.DU","MSI.DU","MEA.DU","MAT1.DU","KAJ.DU","JNP.DU","J2B.DU","IWJ.DU","HMO.DU","FJK.DU","8GC.DU","IOC.DU","FJI.DU","JEG.DU","SSM1.DU","S7E.DU","MMG.DU","FUR.DU","DPM.DU","HPE.DU","JYS1.DU","TQN.DU","UTN.DU","BGT.DU","0C2.DU","FR7.DU","TUO.DU","TO4.DU","V8H.DU","DSE.DU","HIK.DU","CAC1.DU","KHE.DU","SEH.DU","UNQ.DU","SPH1.DU","EAR.DU","I8U.DU","PIO.DU","KEI.DU","TKK1.DU","YOJ.DU","TOH.DU","SH0.DU","24W2.DU","DW1.DU","JAP.DU","HDM.DU","YI2A.DU","NPS.DU","MMO.DU","TYC1.DU","NFR.DU","K22.DU","SLS.DU","ISU.DU","TO7.DU","NEC1.DU","OLY1.DU","EII.DU","KPO.DU","SMO.DU","CTZ.DU","TAX.DU","MH6.DU","YOK.DU","MCN.DU","KUY.DU","YRB.DU","D4S.DU","MFZ.DU","JEM.DU","JBL.DU","0WP.DU","NYKA.DU","MIH.DU","DIP.DU","TZ6.DU","NI6.DU","JUD.DU","JAN.DU","SBW.DU","JIM.DU","TIE.DU","7SS.DU","SUA2.DU","KQ1.DU","KPN.DU","KOG.DU","KNIA.DU","KDB.DU","KBWA.DU","4A4B.DU","SGM.DU","PNK.DU","PMV.DU","PGS1.DU","NYT.DU","NVD.DU","NTH.DU","NRD.DU","NESM.DU","W8V.DU","ORC.DU","OMV.DU","OM6.DU","OJS1.DU","OCI1.DU","3O1.DU","G1V.DU","BN9.DU","OCO.DU","OC5.DU","QFSP.DU","QCI.DU","QDI.DU","QAN.DU","QIA.DU","LB3A.DU","IZ1.DU","QY6.DU","QIG.DU","QSC.DU","QAA.DU","QC9.DU","QS5.DU","QACL.DU","QS2A.DU","TR1.DU","TEKB.DU","RY4D.DU","BUY.DU","IDP.DU","GAP.DU","YCZ.DU","XER.DU","VHY.DU","VFP.DU","UWS.DU","UNVB.DU","UEI.DU","TX5.DU","TWR.DU","TF7A.DU","SSUN.DU","SSK.DU","SRB.DU","SOBA.DU","SGN.DU","SBNC.DU","SAPA.DU","RTS2.DU","RSI.DU","PPQ.DU","PG4.DU","PEP.DU","PCG.DU","NCR1.DU","MX4A.DU","MV9L.DU","MRO.DU","MOO.DU","LWE.DU","LCX.DU","ILT.DU","IER1.DU","HAR.DU","GRA.DU","GGK.DU","GAZ.DU","FB2A.DU","EW1.DU","ELAA.DU","DUBA.DU","DAP.DU","CY9A.DU","CTX.DU","CTO.DU","COZ.DU","CHV.DU","CAO.DU","AWC.DU","ASMF.DU","AS3.DU","AP2.DU","AOL1.DU","ALU.DU","BMW3.DU","KSB3.DU","RHT.DU","VA9.DU","VJ6.DU","FR4N.DU","VNA.DU","CVLA.DU","VNM.DU","WSV2.DU","BKS3.DU","V4S.DU","SHA.DU","MAN3.DU","SNC3.DU","VROS.DU","SIX3.DU","4BV.DU","VBK.DU","VLM.DU","VLX1.DU","VAT.DU","VMR1.DU","VOS.DU","VODJ.DU","VAC.DU","BVF.DU","LCR.DU","VBHK.DU","V1S.DU","DRW3.DU","W1I.DU","AB9.DU","WHA.DU","SII.DU","WUG.DU","WDL.DU","KWG.DU","WAF.DU","SMWN.DU","MWB.DU","DWNI.DU","WD5.DU","WFR.DU","WL6.DU","WF3.DU","WDI.DU","WIB.DU","WBC.DU","WE7.DU","WHC.DU","W8A.DU","NWT.DU","WDC.DU","WGF1.DU","ZEF.DU","VWS.DU","RKB.DU","WYR.DU","WMB.DU","WBAG.DU","XGR1.DU","FG5.DU","XOA1.DU","XMY.DU","RYSB.DU","B3SB.DU","XPH.DU","XLG.DU","O1BC.DU","XIX.DU","XNP.DU","XCI.DU","XCW.DU","XCQ.DU","XD4.DU","X0M.DU","XMF.DU","XTP.DU","XAE2.DU","XCN.DU","XCA.DU","XEB.DU","RTV.DU","YX3.DU","YHO.DU","YSN.DU","TGR.DU","IU2.DU","YIT.DU","YZA.DU","YSON.DU","AIB1.DU","M6O.DU","YIN.DU","YCP.DU","YTT.DU","YPH.DU","A60.DU","YKE.DU","YHA.DU","YOC.DU","YC5.DU","YG12.DU","G9Y.DU","RNY.DU","YB1.DU","LRH1.DU","ZSK.DU","ZGY.DU","ZIL2.DU","ZDO.DU","ZVX.DU","ZIM.DU","AFX.DU","T2R.DU","HIGA.DU","AOD1.DU","HZS.DU","ZYA.DU","EUZ.DU","ZEG.DU","ZO1.DU","ZFIN.DU","HAM1.DU","ZAS.DU","ZAL.DU","JMT2.DU","T9Z.DU","FJZ.DU","ZS3.DU","ZSV.DU","TIM.DU","ZDC.DU","EDGA.DU","AAZ.DU","AA9.DU","AAH3.DU","ARL.DU","AACA.DU","AAH.DU","AAGN.DU","AAP.DU","AAD.DU","AAQ.DU","AFT.DU","ABL.DU","ABJ.DU","AB1.DU","ABEC.DU","RSB.DU","ABR.DU","324.DU","ABW.DU","AYO2.DU","ABA.DU","AUC.DU","AIO.DU","ABEA.DU","ABG.DU","ABO.DU","AYO.DU","ABN.DU","ACWN.DU","ACOG.DU","33A.DU","ACOF.DU","B3K.DU","AJ3.DU","AIY.DU","ACJ.DU","ACBB.DU","AC5G.DU","ACR.DU","E7S.DU","ACE1.DU","ACT.DU","AHLA.DU","ADS.DU","ADP.DU","ADM.DU","ADJ.DU","NNIC.DU","HAM.DU","LUK.DU","SONA.DU","IWY1.DU","EDG.DU","ADN1.DU","KMB.DU","TRBA.DU","PJXA.DU","NOTA.DU","TATB.DU","ADL.DU","TEV.DU","ADD.DU","TUL1.DU","IFXA.DU","RTL.DU","DKA.DU","AMD.DU","FLN.DU","IOY.DU","IPH1.DU","ADE.DU","ADI1.DU","TTFB.DU","DTEA.DU","VAN.DU","DBSA.DU","A62.DU","MHSG.DU","N1N.DU","35V.DU","PJX.DU","NC2A.DU","SIEB.DU","ADC.DU","MGYA.DU","RPH.DU","APM.DU","CTMA.DU","VSJ.DU","CLV.DU","BHP.DU","NEH.DU","ADB.DU","TSFA.DU","AES.DU","AE4.DU","A44.DU","HE8.DU","AE9.DU","IT3A.DU","AEU.DU","AEE1.DU","MTX.DU","JUS1.DU","AEI.DU","AEC1.DU","AEND.DU","AEP.DU","AE6.DU","AJXA.DU","AFL.DU","AFF.DU","AFR.DU","AFO1.DU","H9W.DU","AGE.DU","LWD.DU","APQ.DU","INW1.DU","US5.DU","SGS.DU","MSGL.DU","LUM.DU","PM5V.DU","S26.DU","AGU.DU","BUF.DU","DBAN.DU","AG8.DU","AGX.DU","M7C.DU","SZ5.DU","RAR.DU","ALG.DU","SVQ.DU","VUA.DU","7KT.DU","MU4.DU","CB7.DU","0EK2.DU","FO4N.DU","ILM1.DU","AHOF.DU","AHE.DU","MJS.DU","SIA1.DU","INR.DU","CTY.DU","AIXA.DU","SWN.DU","A1G.DU","SDA.DU","AIL.DU","AINN.DU","AIR.DU","AI3A.DU","AJ91.DU","AJ4.DU","AJI.DU","AKU.DU","AK3.DU","KY7.DU","6MP.DU","AK2.DU","ANO.DU","ALV.DU","CGE.DU","AOX.DU","WMC1.DU","ALX.DU","AXP.DU","AOMD.DU","PHM7.DU","TQL1.DU","ECF.DU","ALS.DU","ATD.DU","ALE.DU","WMC.DU","ATF.DU","A1OS.DU","CSV.DU","ALD.DU","BMT.DU","A0T.DU","NAPN.DU","AMP.DU","AMT.DU","A4S.DU","AM3D.DU","PA2.DU","CCL.DU","AMI.DU","NCB.DU","AMZ.DU","AMK.DU","SZ7.DU","AMG.DU","RQ4.DU","NGLB.DU","AM8.DU","ITK.DU","DGW1.DU","AODC.DU","AZ2.DU","ANL.DU","W9X.DU","A58.DU","LHOG.DU","ANCA.DU","PZX.DU","BZY.DU","GPI1.DU","AOD.DU","FG1.DU","ANB.DU","SCL.DU","AOF.DU","9H6.DU","APC.DU","APA.DU","7AA.DU","APO.DU","APDA.DU","DP4B.DU","APS.DU","REB.DU","ARX.DU","ARN.DU","ERT.DU","8RC.DU","D2EN.DU","ARRB.DU","ART.DU","A6T.DU","SAZ.DU","U9R.DU","ARM.DU","ARO.DU","ARW.DU","HEH.DU","AYV1.DU","ASAA.DU","A5A.DU","02A1.DU","ASG.DU","0LC.DU","ASME.DU","DIC.DU","SHJ.DU","5AB.DU","PFI.DU","TA1.DU","SLL.DU","C8I.DU","EVN.DU","O2C.DU","SANT.DU","SEW.DU","EBO.DU","CMBT.DU","ROI.DU","PKL.DU","RAW.DU","O3P.DU","ODDB.DU","D7I.DU","TWB.DU","6W2.DU","OEWA.DU","VAS.DU","FAA.DU","UN9.DU","SAC.DU","LEN.DU","MYM.DU","ATU.DU","IMO.DU","BWO.DU","AXI.DU","RAD.DU","WOF.DU","AUS.DU","AU9.DU","COR.DU","BFC.DU","CSJ.DU","CDP.DU","FVJ.DU","RMY.DU","AZ5.DU","DQY.DU","CWW.DU","PV3.DU","ORL.DU","MY4.DU","BHP1.DU","UFW.DU","GKG.DU","G7P.DU","AV7.DU","AV3.DU","AVP.DU","AV6.DU","GU8.DU","AWT.DU","AWM.DU","AXA.DU","SPR.DU","AZU.DU","SEBA.DU","DBK.DU","BSP.DU","BSD2.DU","BAS.DU","BW3.DU","BKP2.DU","DVB.DU","BCY.DU","DTD2.DU","BPI.DU","BDSB.DU","BKKF.DU","HBM.DU","BBY.DU","BPD.DU","NDB.DU","BB2.DU","BBZA.DU","BBK.DU","BBVA.DU","BBDB.DU","BOY.DU","BBH.DU","4BE.DU","BCE1.DU","BC3.DU","ME1.DU","593.DU","BC8.DU","BCSA.DU","BPG.DU","POPD.DU","BCO.DU","BDT.DU","MOS.DU","BRH.DU","CHK.DU","BOX.DU","NVJN.DU","41B.DU","T4I.DU","BEZ.DU","EAI.DU","BRYN.DU","DJDA.DU","ECK.DU","BEI.DU","DHZ.DU","COF.DU","BE7.DU","SOL.DU","KSW.DU","NBG6.DU","E4S.DU","M12.DU","MA1.DU","13B.DU","EFC1.DU","MOB.DU","SVE.DU","USE.DU","BK8N.DU","BX7.DU","BSS.DU","UNC.DU","T6W.DU","TG4.DU","PKB.DU","BPS.DU","BIH.DU","HMU.DU","3B7.DU","BF5B.DU","BGR.DU","BGC.DU","BGPA.DU","BGS.DU","BH5.DU","BIL.DU","HUL.DU","BHU.DU","4B3.DU","CEPR.DU","RBQP.DU","ETG.DU","GBF.DU","BIO.DU","BIJ.DU","ELN.DU","BIO3.DU","PDL.DU","B8F.DU","BM8.DU","BIR.DU","SBS.DU","HBI.DU","EYW.DU","BIF.DU","BJEB.DU","BJ51.DU","SIPF.DU","RYS1.DU","SID.DU","BKAA.DU","C4C.DU","BOZA.DU","NBC.DU","NAL.DU","BKN.DU","C6T.DU","D1Y.DU","BLD.DU","B7E.DU","3EV.DU","BL8.DU","SWF.DU","RI1.DU","3IW.DU","HK51.DU","CBA.DU","BMSA.DU","S9A.DU","HLH.DU","SMIF.DU","LIUB.DU","ERE.DU","BM1.DU","DIN.DU","NBI.DU","BMW.DU","BNT1.DU","BNP.DU","BNE.DU","BNN.DU","BNR.DU","BOF.DU","BOSS.DU","BSX.DU","DB1.DU","VIB3.DU","BWJ.DU","GSH.DU","BYG.DU","BOU1.DU","HQK.DU","PBW.DU","BSY.DU","BO9.DU","BVB.DU","NB5.DU","BPE5.DU","BPE.DU","BRW1.DU","CS3.DU","LTD.DU","CB1A.DU","BSL.DU","BSB.DU","BST.DU","BSN.DU","BTQ.DU","BTBA.DU","BTL.DU","BTPC.DU","BTT.DU","BTU.DU","PJM.DU","BUZ1.DU","MABB.DU","HBY.DU","UCM.DU","TUB.DU","M6YA.DU","UCM1.DU","BWB.DU","BY6.DU","BYW6.DU","BYW.DU","RI4.DU","E4U.DU","DVC1.DU","CVC1.DU","CRC.DU","CJ5A.DU","48CA.DU","LAV.DU","E17.DU","POH1.DU","FKGC.DU","P2O.DU","FME.DU","PGZ.DU","EKS.DU","CCG.DU","SGL.DU","CAI.DU","T3W1.DU","CBHD.DU","CBGB.DU","RF6.DU","CBK.DU","C5S.DU","CCJ.DU","CCC3.DU","2GD.DU","RMEA.DU","PC8.DU","CQQ.DU","E01.DU","CDM1.DU","CWC.DU","CEW3.DU","UNI3.DU","RY8.DU","TIC.DU","CEZ.DU","CEV.DU","CXD.DU","CENB.DU","CYT.DU","CSH.DU","CEK.DU","CEA.DU","CLS1.DU","HOU.DU","CEDA.DU","CRE.DU","SCA.DU","CG3.DU","CE2.DU","CTNK.DU","M4M1.DU","TCM1.DU","LSRN.DU","C4F.DU","CF2.DU","CFC.DU","CGD.DU","CGZ.DU","CGM.DU","GDG.DU","CGN.DU","CGOB.DU","GIN.DU","CPW.DU","HLBN.DU","STD.DU","O5H.DU","CPM.DU","G2A.DU","ERO1.DU","ED4.DU","PGH1.DU","SLW.DU","HVX.DU","P2H.DU","SVJ.DU","CMN1.DU","RITN.DU","EAC.DU","CS1.DU","CU1.DU","HLG.DU","PHBN.DU","TOJ.DU","2FI.DU","EZQ.DU","CIT.DU","CPV.DU","CRU.DU","CPF.DU","LTH.DU","CIR.DU","CIE1.DU","TRVC.DU","CIS.DU","CJ6.DU","CKZA.DU","CXX.DU","CLH.DU","CLRN.DU","CLIQ.DU","HK2C.DU","CSG.DU","CMC.DU","CMR.DU","CMAB.DU","NC2B.DU","CHL.DU","PC6.DU","37C.DU","CRP.DU","CHU.DU","ICK.DU","SGJH.DU","TSI.DU","CPA.DU","CPP.DU","O5G.DU","SZ1.DU","CQMA.DU","PK0.DU","CRG.DU","CRA1.DU","CRIH.DU","CRZ.DU","BR6.DU","CRN3.DU","CS9.DU","CSX.DU","CSC.DU","CXR.DU","CSR.DU","CSUA.DU","CSF.DU","CTAA.DU","CTM.DU","CTP2.DU","CUR.DU","CUP.DU","CUM.DU","CUS.DU","CVK.DU","CVS.DU","CWB.DU","CYJ.DU","CY2.DU","T5O.DU","CYC.DU","5PS.DU","DAM.DU","DAR.DU","KE4.DU","DSY1.DU","DKI.DU","DDN.DU","D6H.DU","4DS.DU","DAL.DU","DAL3.DU","DWH.DU","DSN.DU","DAI.DU","TRL.DU","DNP.DU","DCS.DU","DC7.DU","DC6C.DU","DCH1.DU","DC6.DU","DCC.DU","DCO.DU","DOR.DU","D2T.DU","2GB.DU","MUB.DU","ELG.DU","FIE.DU","WAC.DU","EDL.DU","HNL.DU","IFS.DU","SWD.DU","SSS.DU","S4K.DU","VG0K.DU","SRT.DU","KSB.DU","GFK.DU","UUU.DU","ERMK.DU","GLJ.DU","NWX.DU","DMRE.DU","LUS.DU","TRX.DU","MT3.DU","SIX2.DU","IKB.DU","RMO.DU","IDT.DU","PEH.DU","BAYN.DU","MYRK.DU","G7B.DU","MDG1.DU","PRA.DU","UZU.DU","TTC.DU","KU2.DU","DGR.DU","NSU.DU","SFO.DU","NC5A.DU","PCS.DU","GMM.DU","L1OA.DU","KN1.DU","STB1.DU","TAE1.DU","SAG.DU","DEZ.DU","VSC.DU","SWVK.DU","RHK.DU","SYT.DU","98D.DU","UMS.DU","34D.DU","DLG.DU","DO1.DU","DIO.DU","GUI.DU","DIK.DU","WDP.DU","EOT.DU","DI6.DU","DIE.DU","T2V1.DU","NKT.DU","DS81.DU","TM2.DU","WDH.DU","LDB.DU","R90.DU","F6O1.DU","GE9.DU","TQ71.DU","NOVC.DU","D69.DU","NZM2.DU","DLL.DU","DL1C.DU","DLX.DU","GIL.DU","DMI.DU","DMB.DU","DNE.DU","DNQ.DU","DNO.DU","NBA.DU","DOV.DU","DT3.DU","DOD.DU","T97.DU","DPW.DU","DP5.DU","D9F2.DU","RDDA.DU","PAD.DU","RHO5.DU","DRI.DU","DRE2.DU","DRW8.DU","DR0.DU","DSM2.DU","DTE.DU","LHA.DU","O2D.DU","EFF.DU","R6C3.DU","019.DU","DUE.DU","D2MN.DU","TXC2.DU","R6C.DU","DUT.DU","DVY.DU","PDA.DU","RYE.DU","DWD.DU","GDX.DU","DY2.DU","DYH.DU","SD5.DU","ND3.DU","DYE.DU","DY6.DU","M59.DU","EJT1.DU","EAM.DU","ERL1.DU","EJR.DU","EBK.DU","EBA.DU","E4C.DU","ECJ.DU","ECX.DU","EDW.DU","E2F.DU","EIX.DU","EDC.DU","MDD.DU","EDP.DU","EFX.DU","EFGD.DU","EF3.DU","EGT.DU","EG4.DU","EIA.DU","EIN3.DU","EIS.DU","EIF.DU","H5E.DU","EJXB.DU","EKT.DU","LLY.DU","SND.DU","FEV.DU","EWI.DU","ELO.DU","FJE.DU","UEH.DU","MITA.DU","E8X.DU","GEC.DU","OKI.DU","ELX.DU","MIE1.DU","EMR.DU","FKA.DU","TPO.DU","RE2.DU","ELVA.DU","SCE.DU","EMQ.DU","EMH1.DU","TUIJ.DU","GZF.DU","TE5.DU","ENI.DU","2HP.DU","ENA.DU","ETY.DU","PSE.DU","EOAN.DU","EOAA.DU","EO5.DU","HPBK.DU","EQ6.DU","T9B.DU","TP5.DU","EQR.DU","EQS.DU","ERCB.DU","ERCA.DU","ER7.DU","TNE5.DU","ESL.DU","MES.DU","KBU.DU","GAN.DU","ESF.DU","GTQ1.DU","UFG.DU","T5R.DU","IDA.DU","FV01.DU","BAKA.DU","VIS.DU","IXD1.DU","HUA.DU","IBE1.DU","FCC.DU","HZJ.DU","UPR.DU","ESHB.DU","RWW.DU","VHM.DU","REP.DU","ETRA.DU","ETX.DU","E3B.DU","EUQ.DU","EUCA.DU","DEQ.DU","RO5K.DU","TNU3.DU","LCY.DU","EUX.DU","EVZ.DU","EVT.DU","EVK.DU","EV4.DU","NWJ.DU","PEO.DU","EXJ.DU","2TN.DU","E3X1.DU","NEX.DU","IC2.DU","EX9.DU","4XS.DU","EZ1.DU","FUC.DU","FVI.DU","FAS.DU","FAM1.DU","FCT.DU","UN3.DU","SES.DU","FDO.DU","FDX.DU","2FE.DU","FRU.DU","FGT.DU","FEW.DU","3KC.DU","FE7.DU","FFV.DU","FGR.DU","RN7.DU","A7A.DU","FMNB.DU","IFF.DU","FWV.DU","FLU.DU","FL4.DU","FXI.DU","FMV.DU","FMH.DU","FMQ.DU","FMC1.DU","FNG.DU","FNL.DU","FNTN.DU","HO7.DU","FSL.DU","FOT.DU","FRS.DU","WFM.DU","F2T.DU","FOO.DU","FOU1.DU","F5D.DU","FP3.DU","FPMB.DU","FPE3.DU","FPH.DU","FPE.DU","LRC.DU","FSE.DU","LOR.DU","MMT.DU","RNL.DU","HMI.DU","CAR.DU","FRYA.DU","THP.DU","3IC.DU","PER.DU","IY4.DU","SEJ1.DU","SJ7.DU","NXS.DU","FRK.DU","PPX.DU","UEN.DU","WIS.DU","LAG.DU","VVD.DU","RCF.DU","MCH.DU","FTE.DU","F3D.DU","FUH.DU","MFU.DU","T8F.DU","FUJ1.DU","GS2C.DU","NG4.DU","GZ5.DU","KW9A.DU","TOG.DU","SCF.DU","GEY.DU","GWK3.DU","TCG.DU","LSU1.DU","HGM.DU","HBC1.DU","RRU.DU","TLY.DU","RIO1.DU","KYC.DU","SCT.DU","IMI1.DU","1LGE.DU","HAY.DU","H5P.DU","NXG.DU","6CJ.DU","S4VC.DU","PQQB.DU","IJIA.DU","WHF4.DU","1LGD.DU","OMUB.DU","SSU.DU","HYU.DU","RLI.DU","GTN.DU","LDV.DU","G1A.DU","GRU.DU","MYD.DU","GWI1.DU","GME.DU","GSC1.DU","WWG.DU","GHH.DU","GSJ.DU","GXI.DU","GON.DU","LGI.DU","SGE.DU","GRM.DU","GBRA.DU","GEBK.DU","GPT.DU","GF8.DU","GFT.DU","GGS.DU","GHN.DU","GIS.DU","GIB.DU","GKS.DU","GKN.DU","1LG.DU","GS7.DU","GLW.DU","JO3.DU","8GS.DU","1LGC.DU","NI9.DU","T34.DU","IQ3.DU","5G5.DU","GTR.DU","32N.DU","KIN2.DU","GOS.DU","GOB.DU","GO5.DU","VN3A.DU","GOZ2.DU","CAJ.DU","GTT.DU","GWW.DU","HFF.DU","PND.DU","KY4.DU","HAE.DU","CO0.DU","H2R.DU","HAS.DU","HLAG.DU","H2V.DU","H11.DU","HNR1.DU","RHI.DU","HRS.DU","SVHH.DU","M8U2.DU","H9Y.DU","HAB.DU","HII.DU","HAL.DU","RHJ.DU","HBC2.DU","HBD1.DU","C0Q.DU","HBH.DU","HCW.DU","HXCK.DU","HCM.DU","HCL.DU","HC5.DU","I5G.DU","SNH.DU","HDJ0.DU","SIH.DU","S6M.DU","HJN1.DU","HEI.DU","HEZ.DU","KHNZ.DU","HXGB.DU","4H5.DU","HLE.DU","HEN.DU","HS2.DU","HNK1.DU","HMSB.DU","HEN3.DU","MBH3.DU","OTE.DU","IPO.DU","HSY.DU","HETA.DU","HG1.DU","HHFA.DU","WHI.DU","HIA1.DU","HJ1.DU","IO5A.DU","HKE.DU","SNO.DU","LHL.DU","TLW.DU","SWI.DU","93M.DU","KOA.DU","3M0.DU","HL9B.DU","WPOB.DU","NSE.DU","KD8.DU","SHRQ.DU","RHO.DU","ROH.DU","M3C.DU","KPI1.DU","TTI.DU","PNY.DU","HMT.DU","HNIB.DU","01H.DU","SFQ.DU","HP3.DU","7HP.DU","HRB.DU","HRPK.DU","HRZ.DU","TUBJ.DU","S1V.DU","HTH.DU","HU3.DU","HUM.DU","H9O1.DU","OTP.DU","HWSA.DU","NOH1.DU","HYQ.DU","HYF.DU","IAL.DU","IBM.DU","ICY.DU","ICM1.DU","IC8.DU","GBNA.DU","ICP.DU","INVN.DU","IDVA.DU","BABB.DU","KRZ.DU","2M6.DU","IES.DU","IL0A.DU","IEA.DU","STT.DU","IS8.DU","IFA.DU","IGQ5.DU","IHCB.DU","II8.DU","IJ7.DU","IKH.DU","OT5.DU","VOC.DU","OIL.DU","IL2.DU","WZM.DU","ILU.DU","IR3B.DU","PQL.DU","LEG.DU","IPJ1.DU","ITB.DU","IMU.DU","TLG.DU","TEG.DU","IPG.DU","TPIG.DU","ISH2.DU","4HP.DU","IS7.DU","ISR.DU","MOV.DU","LUXA.DU","TQI.DU","SPE.DU","UIPN.DU","ITA.DU","STNA.DU","TIQ1.DU","AUL.DU","ME9.DU","ITN.DU","ITU.DU","ENZ.DU","P4I.DU","URH.DU","S9L.DU","ENL.DU","SOAN.DU","I7N.DU","IT6.DU","IT1.DU","TOB.DU","SNM.DU","MDS.DU","MGG.DU","B8ZB.DU","MPI3.DU","PIL3.DU","IUI1.DU","IUR.DU","IVU.DU","IVSB.DU","IV4.DU","IVKA.DU","IVX.DU","IXX.DU","JAF.DU","32JN.DU","J9R.DU","JAT.DU","JB1.DU","JCP.DU","JCN.DU","A8A.DU","JEN.DU","PM6.DU","JFR.DU","JGE.DU","JJO.DU","JM2.DU","JNJ.DU","JY8.DU","MIB.DU","MTS1.DU","SFT.DU","SB3.DU","S19.DU","MZA.DU","N76.DU","NI3.DU","9TO.DU","KOM1.DU","MBI.DU","KAO.DU","KUO1.DU","SON1.DU","SHD.DU","MU1.DU","NKN.DU","RIC1.DU","SRP.DU","MARA.DU","OBA.DU","OJI.DU","MUI.DU","ND5.DU","SMM.DU","MIU.DU","SU2.DU","NTO.DU","TKD.DU","NTN.DU","NP7.DU","KIK.DU","NSK.DU","TIJ.DU","TMI.DU","KLI1.DU","LCJ.DU","TKM.DU","OKU.DU","TOR1.DU","TOS.DU","KYR.DU","PYV.DU","TOM.DU","TSQ.DU","KWI.DU","S3X.DU","CNN1.DU","MILA.DU","KIR.DU","TSE1.DU","MUJ.DU","RL2.DU","NGI.DU","DEN.DU","KST.DU","01T.DU","SUK.DU","NISA.DU","SUMA.DU","NSC.DU","N9L.DU","MZ8.DU","59M.DU","MTW.DU","JWG1.DU","KA8.DU","KPH.DU","TFBF.DU","KBH.DU","KBC.DU","KB7.DU","KB2.DU","KCN.DU","KCO.DU","KC4.DU","KDR.DU","KEL.DU","KEY.DU","KEK.DU","KEP1.DU","KFI1.DU","KGX.DU","KG0A.DU","KHP.DU","KIC.DU","3GK.DU","KMY.DU","WOSB.DU","KPR.DU","KLA.DU","VPK5.DU","PHIA.DU","K34.DU","KSC.DU","KTB1.DU","K1R.DU","SDF.DU","KTC.DU","KTF.DU","KWS.DU","TC2A.DU","LAB.DU","LXS.DU","LAR.DU","OLB.DU","LADA.DU","PRL.DU","4SL.DU","ULC.DU","LCO.DU","LEI.DU","LEO.DU","TAN.DU","LP1.DU","OSR.DU","LVCN.DU","LNSX.DU","LEC.DU","LX31.DU","LN3.DU","LNN.DU","LJ2.DU","LLD.DU","LM0.DU","LN1.DU","MLL.DU","LOM.DU","LO24.DU","TGH.DU","LTEC.DU","LO3.DU","LTR.DU","LPZB.DU","LSX.DU","LSPN.DU","LSPP.DU","LS4C.DU","RRTL.DU","LYV.DU","SOC.DU","TW11.DU","T6C.DU","STM.DU","MOH.DU","LVO.DU","LYI.DU","MGA.DU","MZX.DU","M3T.DU","MXI.DU","MF6.DU","M5Z.DU","MAN.DU","MTT.DU","MAQ.DU","MVL.DU","MBJ.DU","MBQ.DU","MBB.DU","US8A.DU","MDO.DU","MSN.DU","MCX.DU","MCK.DU","MCP.DU","MDN.DU","MEZ.DU","MQG.DU","8TM.DU","MED.DU","6MK.DU","SPM.DU","MHH.DU","MGI.DU","MGN.DU","RXM3.DU","MNSN.DU","MSF.DU","SMHN.DU","PGM.DU","M3B.DU","MLP.DU","MM2.DU","MMM.DU","MNMA.DU","MOR.DU","MZP.DU","MO7.DU","NY7.DU","TL0.DU","N1M.DU","MTLA.DU","D7Q1.DU","M09.DU","8MP.DU","TMW.DU","MPS.DU","MPRK.DU","MPCK.DU","MRK.DU","4I1.DU","MSQ.DU","MSAG.DU","MTZ.DU","MTE.DU","MTA.DU","MUV2.DU","MUQ.DU","MUM.DU","M4N.DU","MVV1.DU","MV3.DU","C1V.DU","MVIN.DU","MWZ.DU","MXH.DU","6MY.DU","MZ4.DU","NNGE.DU","N7E.DU","NBP.DU","N2F.DU","NAGE.DU","NAI.DU","LI5.DU","NAQ.DU","N7G.DU","NTG.DU","NO8.DU","NNS.DU","NB6.DU","NCYD.DU","NDA.DU","NDX1.DU","NXU.DU","NWL.DU","NTA.DU","NFC.DU","NPW1.DU","NEQ.DU","NMM.DU","ADV.DU","OD8.DU","NSN.DU","NEF.DU","NMA.DU","NESR.DU","NETK.DU","NFPH.DU","NFS.DU","NOU.DU","NKE.DU","WIN.DU","WER.DU","RSH.DU","TNTC.DU","OIC.DU","PHI1.DU","VNX.DU","INN.DU","OEM.DU","NN2.DU","SKT.DU","TMR.DU","R3Q.DU","NS7.DU","TEQ.DU","NRE.DU","NOA3.DU","OKL.DU","NOAA.DU","BAR.DU","NVV.DU","NOEJ.DU","NOT.DU","NTR.DU","SNY.DU","NUO.DU","SC2.DU","PYXA.DU","OMAX.DU","OBS.DU","OLG.DU","OBH.DU","OBD.DU","OPC.DU","OCN.DU","OCS1.DU","ODP.DU","ODE.DU","VVV3.DU","OEZ.DU","OFK.DU","OHB.DU","OHP.DU","HOJ.DU","TQW.DU","USS.DU","OORD.DU","P4O.DU","OS2.DU","OSP2.DU","UOF.DU","OUTA.DU","O4B.DU","OXR.DU","PA8.DU","PAH3.DU","PUR.DU","PGN.DU","PAE.DU","PBB.DU","PBY.DU","PCE1.DU","PCD1.DU","PCX.DU","PCU.DU","PD2.DU","PP21.DU","PJXB.DU","3PNA.DU","PT8.DU","P2F.DU","P13.DU","P4Q.DU","PKN.DU","PPJ.DU","WOPA.DU","PEU.DU","PES.DU","PHZ.DU","PFE.DU","PFV.DU","PGV.DU","PTCA.DU","HOZ.DU","PS4.DU","RGO.DU","VX1.DU","PWC.DU","PLEK.DU","PMTA.DU","PNP.DU","PNE3.DU","PNC1.DU","UP7.DU","POC.DU","PO0.DU","PU8.DU","PO9.DU","P9R.DU","PSM.DU","SQI.DU","PRU.DU","P7S.DU","PSAN.DU","PSU.DU","S4LA.DU","RN4.DU","PU4.DU","PUP.DU","PUM.DU","PU7.DU","TPE.DU","PWO.DU","PXR.DU","PYX.DU","PZS.DU","PZR.DU","RMB.DU","RAZB.DU","RAX.DU","RAA.DU","RTN1.DU","RGR1.DU","RGRA.DU","RC0.DU","RDEB.DU","RGB.DU","RH8.DU","RLV.DU","RSTA.DU","RIB.DU","RKQ.DU","RKET.DU","VO7.DU","RNWA.DU","RYC.DU","RSO.DU","RWC.DU","RPL.DU","RPU.DU","RSL2.DU","RSM.DU","RTO1.DU","RTC.DU","C9R.DU","RWE.DU","RWE3.DU","RWI.DU","34U.DU","SAX.DU","SNQB.DU","SBOA.DU","SBE.DU","SBJ.DU","SWA.DU","SK2.DU","S4A.DU","TN8.DU","SCM.DU","SDRC.DU","G24.DU","SHF.DU","SLT.DU","SHB3.DU","SWG.DU","SKNB.DU","SEE.DU","SFX.DU","F3C.DU","SFM1.DU","SFD1.DU","SUVN.DU","SGMR.DU","SGK1.DU","SIT4.DU","SHWK.DU","SHP5.DU","SW1.DU","SJ3.DU","SU1N.DU","SIQ.DU","SIK.DU","SIE.DU","SQX.DU","S9Y.DU","G3U.DU","SJ1.DU","SKYD.DU","SKFB.DU","SK1A.DU","SKWA.DU","SM1.DU","SM3.DU","S92.DU","SMPA.DU","SNW.DU","SPU.DU","8S9.DU","SW5.DU","TRIG.DU","F3A.DU","UNS1.DU","SOW.DU","99SC.DU","L5A.DU","SOT.DU","SPZI.DU","N4D.DU","SQU.DU","SR9.DU","STE.DU","USX1.DU","CAP.DU","9LMA.DU","SYK.DU","ST5.DU","WMT.DU","STP.DU","ENUR.DU","SY9.DU","SUR.DU","SUU.DU","TR4.DU","SZU.DU","SUY1.DU","SUL1.DU","ST7B.DU","S9P2.DU","UPAB.DU","SVKB.DU","SVT1.DU","S6N.DU","UHR.DU","SWM.DU","SWJ.DU","LIO1.DU","SY1.DU","SYM.DU","V3S.DU","VTY.DU","SYZ.DU","SYY.DU","SZG.DU","TWW.DU","TLX.DU","TKE.DU","TAEN.DU","TCO.DU","TC1.DU","TTR1.DU","TII.DU","LTC.DU","TLS.DU","UTC1.DU","TGT.DU","TL1.DU","TOC.DU","W3U.DU","TIF.DU","TJX.DU","TKA.DU","TLI.DU","TMJ.DU","TM5.DU","TOTB.DU","TPN.DU","TRS.DU","TZ1.DU","T6A.DU","TVD6.DU","TSTA.DU","TT1.DU","TUI1.DU","TUR.DU","TXT.DU","0UB.DU","UCA1.DU","USY1.DU","UUEC.DU","UNP.DU","UTDI.DU","UNH.DU","U6Z.DU","VA4.DU","VLE.DU","VG8.DU","VCX.DU","VR9.DU","VEO.DU","VEN.DU","BAC.DU","VRS.DU","VIH.DU","T3V1.DU","3V64.DU","VS1.DU","V6C.DU","VIU.DU","VVU.DU","VOW.DU","VOL1.DU","VQKA.DU","VT9.DU","WKM3.DU","STO3.DU","MEO3.DU","W4C.DU","WSOK.DU","WSU.DU","WCH.DU","WCMK.DU","42W.DU","WEG1.DU","WEU.DU","WIC.DU","WHR.DU","WID.DU","WIG1.DU","WKM.DU","CH1A.DU","WWR.DU","B1C.DU","SAO.DU","TR3.DU","AUD.DU","COM.DU","3BA.DU","B5A.DU","B8A.DU","3RB.DU","42BA.DU","BMM.DU","R1H.DU","BRM.DU","COO2.DU","COK.DU","RE0.DU","TEX.DU","CAT1.DU","CNWK.DU","COY.DU","CON.DU","COP.DU","1COV.DU","DEX.DU","EN3.DU","PRVA.DU","FIV.DU","FRA.DU","FRE.DU","M3K.DU","HOT.DU","INH.DU","HOS.DU","INL.DU","INP.DU","LIN.DU","MAK.DU","MA6.DU","M4I.DU","M3V.DU","MEO.DU","3MI.DU","PAR.DU","2PP.DU","PRG.DU","SAP.DU","S7MB.DU","SE4.DU","SEO.DU","STR.DU","3T4.DU","PA9.DU","CA3.DU","HO1.DU","G5N.DU"]

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
