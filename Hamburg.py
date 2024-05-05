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
    available_tickers = ["5TR.HM","WDP.HM","UYN.HM","UBK.HM","TTB.HM","TPE.HM","SZU.HM","SWA.HM","SOO1.HM","SKB.HM","SAX.HM","R6C3.HM","QCE.HM","P1Z.HM","OSR.HM","O2D.HM","O1BC.HM","LIN.HM","KRN.HM","ISR.HM","ILM1.HM","HHX.HM","HGL3.HM","GME.HM","GFT.HM","VVD.HM","VODI.HM","TJY.HM","SON1.HM","NKN.HM","FUJ1.HM","CMC.HM","TKD.HM","NISA.HM","CNN1.HM","JAF.HM","JO3.HM","JEN.HM","JFB.HM","NEC1.HM","HDM.HM","MYM.HM","KNIA.HM","KEL.HM","GRU.HM","AKS.HM","AFR.HM","CH8.HM","NTA.HM","NFC.HM","O3P.HM","NOL.HM","OEM.HM","QSC.HM","QBI.HM","TYI.HM","QIN.HM","QD4.HM","QIA.HM","QA9.HM","QFP.HM","QOU.HM","QCI.HM","QLG.HM","SWJ.HM","CHV.HM","BAC.HM","ALU.HM","YHO.HM","WMT.HM","UTC1.HM","USX1.HM","TL0.HM","SYM.HM","SRB.HM","PAE.HM","IBM.HM","HC5.HM","FMC1.HM","DWD.HM","CRIH.HM","CIS.HM","CH1A.HM","CG3.HM","B1C.HM","AUD.HM","ATD.HM","APC.HM","AOL1.HM","7PV.HM","PU11.HM","MEO3.HM","VX1.HM","VAS.HM","VOS.HM","VOL3.HM","VIH.HM","RWE3.HM","EUK3.HM","BBDB.HM","WSV2.HM","JUN3.HM","SII.HM","BIU2.HM","WSU.HM","WFM.HM","DWNI.HM","WEG1.HM","WDI.HM","WDL.HM","WMB.HM","MWB.HM","WJB.HM","3DW.HM","EW1.HM","WAC.HM","W1M.HM","WHC.HM","WUW.HM","W1D.HM","BIW.HM","FLW.HM","XPK.HM","XKI.HM","FG5.HM","XEUA.HM","RDO.HM","XMY.HM","XER.HM","XONA.HM","XD4.HM","UMG.HM","XIX.HM","XCA.HM","XA6.HM","O3B.HM","YG12.HM","0YYA.HM","YSN.HM","A60.HM","YP1.HM","YTR.HM","WPP.HM","YZA.HM","YM1.HM","ZVL.HM","ZJS1.HM","ZAL.HM","TIM.HM","EUZ.HM","ZPFK.HM","ZEG.HM","AFX.HM","ZO1.HM","T9Z.HM","ZEF.HM","ZIL2.HM","ZFIN.HM","AAQ.HM","AAD.HM","AAGN.HM","AAP.HM","ARL.HM","ABEA.HM","ABJ.HM","ABL.HM","ABEC.HM","ABA.HM","ABR.HM","AB1.HM","ACR.HM","ACWN.HM","E7S.HM","ACT.HM","ERCA.HM","AD2.HM","TEV.HM","HBC2.HM","SOCA.HM","AHS.HM","AV4A.HM","GS7A.HM","IOY.HM","OEL.HM","ADI1.HM","ADL.HM","ADB.HM","HAM.HM","ADD.HM","EDG.HM","ADN1.HM","APM.HM","CVLB.HM","ADV.HM","AMD.HM","GAZ.HM","AEC1.HM","A44.HM","AEI.HM","1Z7.HM","OAE.HM","MTX.HM","AEP.HM","AEND.HM","AEK.HM","EK7.HM","5BM.HM","EBGK.HM","AGX.HM","PSC.HM","FFM.HM","CDZ.HM","1PL.HM","OFL.HM","L1AK.HM","MSGL.HM","FO4N.HM","NAB.HM","BUF.HM","B9V.HM","SE3.HM","GTK.HM","BHEK.HM","TAV.HM","I3C.HM","I8CK.HM","WIB.HM","GA2.HM","EBS.HM","M7T.HM","AGV.HM","5RP.HM","BGZ.HM","SCI.HM","MDQ.HM","ALG.HM","NAK.HM","DG6.HM","7KT.HM","MMH.HM","HSRN.HM","AHLA.HM","OC3.HM","3SQ1.HM","AHOF.HM","AIR.HM","AINN.HM","SIA1.HM","AIL.HM","AIXA.HM","MJS.HM","AJ4.HM","AK3.HM","AK7.HM","T1W.HM","ATF.HM","ALS.HM","E7T.HM","DUL.HM","PHM7.HM","ALD.HM","WMC1.HM","CGE.HM","ALV.HM","AOX.HM","AOMD.HM","NGLB.HM","AMZ.HM","AMG.HM","BMT.HM","AM3D.HM","FDK.HM","NCB.HM","SCL.HM","ITK.HM","AZ2.HM","AOD.HM","OAB.HM","AOF.HM","7AA.HM","AP2.HM","DP4B.HM","APO.HM","ARO.HM","ERT.HM","GIX.HM","SAZ.HM","ARRB.HM","ARR1.HM","ASME.HM","ASG.HM","HEH.HM","DIC.HM","SLL.HM","RAD.HM","OMV.HM","IMO.HM","FAA.HM","AUS.HM","RAW.HM","CMBT.HM","SAC.HM","PKL.HM","EBO.HM","ROI.HM","AU9.HM","SOBA.HM","SANT.HM","TA1.HM","O2C.HM","OEWA.HM","AUV.HM","FA6.HM","HJI.HM","SIH.HM","BJ9.HM","6ME.HM","32Z.HM","PV3.HM","SWQ.HM","KXT.HM","PG1.HM","4SE.HM","BHP1.HM","NMA.HM","O5A.HM","LYI.HM","FMK.HM","GMK.HM","UV7.HM","AV7.HM","AVI.HM","AVP.HM","AWM.HM","AXA.HM","SPR.HM","BCY.HM","B5A.HM","BHU.HM","BTL.HM","NAGE.HM","BYW6.HM","BAS.HM","BM1.HM","BST.HM","BBY.HM","DBK.HM","BAYN.HM","BBZA.HM","BOY.HM","BB2.HM","BB6.HM","BCLN.HM","BC8.HM","BCO.HM","BDT.HM","CHK.HM","BEI.HM","WCMK.HM","BFV.HM","ECK.HM","BRYN.HM","GBQ.HM","BRH.HM","3RB.HM","NVJN.HM","DBAN.HM","BGR.HM","BIL.HM","BHM.HM","3BH.HM","SBH.HM","ETG.HM","IDP.HM","BIJ.HM","GBF.HM","SBS.HM","BIO3.HM","BIO.HM","PDL.HM","C6T.HM","RYS1.HM","BLH.HM","BLON.HM","RI1.HM","CTH.HM","OYD.HM","S9A.HM","BMSA.HM","SN6.HM","SO7.HM","MVL.HM","EBZ.HM","BNP.HM","BNR.HM","BVB.HM","VIB3.HM","BOU1.HM","BYG.HM","DB1.HM","BOSS.HM","BOF.HM","BPE.HM","BPE5.HM","BRS.HM","BRM.HM","BSD2.HM","BSL.HM","BSN.HM","BTQ.HM","B7B.HM","BUOB.HM","WBAG.HM","BWB.HM","BY6.HM","MPCK.HM","T3W1.HM","CBK.HM","CCC3.HM","D2B.HM","CEK.HM","CTNK.HM","CEV.HM","UNI3.HM","CSH.HM","CWC.HM","CE2.HM","C9J.HM","CLS1.HM","CEA.HM","M4MI.HM","CGN.HM","CGM.HM","EZ5.HM","CHL.HM","CMW.HM","16T.HM","NESR.HM","LMI.HM","SVJ.HM","RHO.HM","SR9.HM","CLRN.HM","DCH1.HM","0UB.HM","UHR.HM","KABN.HM","HLBN.HM","IKF.HM","GEY.HM","CTX.HM","CHP.HM","CIE1.HM","TRVC.HM","2CK.HM","UR9.HM","PC6.HM","WI4.HM","LI9.HM","HIFH.HM","CNWK.HM","SHX.HM","CNF.HM","CPW.HM","CPA.HM","CRA1.HM","CRG.HM","LVT.HM","CRN3.HM","CSC.HM","CSX.HM","CXR.HM","EVD.HM","CTO.HM","CTM.HM","CTP2.HM","CUR.HM","CVL.HM","CVV.HM","CVC1.HM","DAM.HM","DAR.HM","DAI.HM","DC4.HM","DCO.HM","DRI.HM","DRE2.HM","PDA.HM","HEN.HM","KWS.HM","SHF.HM","MRK.HM","SIE.HM","IXX.HM","S92.HM","HGL.HM","HNL.HM","RSL2.HM","STB1.HM","MXH.HM","GMM.HM","GGS.HM","UTDI.HM","8S9.HM","TTK.HM","SYT.HM","LEO.HM","MGN.HM","SYZ.HM","MDN.HM","GWI1.HM","DGR.HM","GUI.HM","EOT.HM","DSZ.HM","DIE.HM","DLG.HM","NOVC.HM","VWS.HM","GIL.HM","DNQ.HM","PMOX.HM","DPW.HM","HDD.HM","DRM.HM","RHO5.HM","DRW3.HM","DRW8.HM","DSM2.HM","DTE.HM","LHA.HM","EFF.HM","DUP.HM","R6C.HM","D2MN.HM","DUE.HM","DXBA.HM","GDX.HM","D5I.HM","DYH.HM","DY2.HM","ESY.HM","EJT1.HM","EBA.HM","ECQ.HM","EDD3.HM","E2F.HM","EDL.HM","VEH.HM","H5E.HM","EIN3.HM","EJD.HM","EKT.HM","SND.HM","EMR.HM","GEC.HM","ELK.HM","ELG.HM","9EM.HM","FEV.HM","LPK.HM","HLT.HM","LLY.HM","ELVA.HM","TUIJ.HM","EMP.HM","GZF.HM","MVV1.HM","EOAN.HM","LSE.HM","ERCB.HM","ERMK.HM","ESL.HM","IXD1.HM","ESF.HM","TNE5.HM","ENA.HM","REP.HM","KBU.HM","IBE1.HM","DEQ.HM","EUCA.HM","EUK2.HM","EV4.HM","WE7.HM","EVK.HM","EVT.HM","E3X1.HM","EXJ.HM","4XS.HM","PEO.HM","FAS.HM","FB2A.HM","NWT.HM","FDX.HM","FEW.HM","FRU.HM","2FE.HM","F1T.HM","2FI.HM","LJ9.HM","NOA3.HM","FIE.HM","FXI.HM","FMNB.HM","FMV.HM","FME.HM","FNTN.HM","L1OA.HM","FRS.HM","FVJ.HM","TFA.HM","FPE.HM","FPE3.HM","LOR.HM","SNW.HM","HMI.HM","SGE.HM","MOH.HM","LAG.HM","CAR.HM","FRA.HM","NLM.HM","VAC.HM","PEU.HM","TOTB.HM","PPX.HM","FTE.HM","FWQ.HM","FZ9.HM","7SE.HM","LK9.HM","GFJ.HM","GAD.HM","LLD.HM","TCO.HM","RRU.HM","TPA.HM","SSUN.HM","SSU.HM","GD2.HM","HYU.HM","G1A.HM","GSC1.HM","MYD.HM","GXI.HM","8GM.HM","GFK.HM","GIS.HM","GIB.HM","GLW.HM","GLJ.HM","8GC.HM","GS7.HM","GLK.HM","GO5.HM","GOB.HM","ORY.HM","GOS.HM","NYH.HM","TTU.HM","6GI.HM","H9Y.HM","07R.HM","CO0.HM","RHI.HM","HAB.HM","HAE.HM","HAL.HM","HAW.HM","HNR1.HM","HLAG.HM","HBM.HM","HBH.HM","HBC1.HM","HXCK.HM","HDI.HM","SNH.HM","HNK1.HM","HEI.HM","HMSB.HM","SST.HM","HSY.HM","HLE.HM","HS2.HM","HEN3.HM","HG1.HM","HHFA.HM","HLG.HM","LHL.HM","TLW.HM","NWD.HM","IO5A.HM","I8D.HM","HLS.HM","KPI1.HM","TTI.HM","SLW.HM","KD8.HM","NSE.HM","HNIB.HM","7HP.HM","2HP.HM","HVB.HM","HYW.HM","HYQ.HM","HYF.HM","NOH1.HM","IO0.HM","I7O.HM","IES.HM","2M6.HM","IFX.HM","IHCB.HM","IKB.HM","SCY.HM","PQL.HM","TLG.HM","TEG.HM","LEG.HM","IRP.HM","ISH2.HM","IS7.HM","TQI.HM","ENI.HM","ITN.HM","ITU.HM","ENL.HM","PIL3.HM","SNM.HM","IUI1.HM","JNP.HM","JNJ.HM","SRP.HM","MFZ.HM","TSE1.HM","TOM.HM","SFT.HM","JUB.HM","JYA.HM","KBC.HM","KB7.HM","KCN.HM","KCO.HM","KDR.HM","KEP1.HM","KGX.HM","WOSB.HM","KLA.HM","KMLK.HM","KPN.HM","KSC.HM","KSB.HM","SDF.HM","KSB3.HM","KTF.HM","KU2.HM","VH1.HM","LXS.HM","OLB.HM","LAR.HM","4SL.HM","ULC.HM","PRZ.HM","LNSX.HM","LEI.HM","LO3.HM","LTEC.HM","TGH.HM","K1R.HM","MLL.HM","RRTL.HM","STM.HM","SFQ.HM","LUK.HM","M2L.HM","M5S.HM","MDO.HM","MCP.HM","MCH.HM","MDG1.HM","6MK.HM","MEO.HM","COP.HM","MF8.HM","MHH.HM","TCD.HM","RSM.HM","MSF.HM","SMHN.HM","MLP.HM","MMM.HM","4QX.HM","MOR.HM","MTLA.HM","N1M.HM","TMW.HM","MOO.HM","MQG.HM","MTE.HM","MUB.HM","MUM.HM","MUE.HM","M4N.HM","MUV2.HM","6MU.HM","MV3.HM","MY3.HM","MZX.HM","NN6.HM","LI5.HM","N7E.HM","NDX1.HM","NDA.HM","PNG.HM","NEM.HM","OPP.HM","NEP.HM","NMM.HM","NSN.HM","NFS.HM","NPL.HM","NKE.HM","WIN.HM","PHI1.HM","TNTC.HM","TPL.HM","RSH.HM","SGM.HM","NST.HM","TMR.HM","NOEJ.HM","NOT.HM","NV9.HM","NS7.HM","NSU.HM","NVD.HM","OBS.HM","OHB.HM","PUB.HM","ORC.HM","B5Z.HM","3O1.HM","OSP2.HM","O4B.HM","OXR.HM","UPAB.HM","PCX.HM","2PP.HM","PA8.HM","PGN.HM","PAH3.HM","SRWA.HM","PUR.HM","PBB.HM","PCE1.HM","PCS.HM","PEP.HM","CHU.HM","PER.HM","PT8.HM","P4Q.HM","SGJH.HM","P1M.HM","PFV.HM","PFE.HM","PS4.HM","R66.HM","PNE3.HM","PO0.HM","POQ.HM","UP7.HM","PRA.HM","PZ9.HM","PSM.HM","PSAN.HM","PUM.HM","PWO.HM","RAA.HM","RTN1.HM","RMB.HM","RR5.HM","RCMN.HM","RH8.HM","RHK.HM","RHM.HM","RUC.HM","RIB.HM","RITN.HM","RSTA.HM","RIO1.HM","L9G.HM","RKET.HM","RNL.HM","RR3.HM","RWL.HM","RSO.HM","RTC.HM","RTHA.HM","RUB.HM","RWE.HM","RW4.HM","RY6.HM","SRT.HM","SCM.HM","G24.HM","SN2.HM","SHA.HM","S4A.HM","SLT.HM","SFM1.HM","SIT4.HM","SXTN.HM","VZS.HM","S8N.HM","BRX.HM","3P51.HM","P3G.HM","A9W1.HM","H2W1.HM","SGL.HM","SGN.HM","SW1.HM","UG6.HM","SNG.HM","SZZ.HM","SIQ.HM","SIX3.HM","WAF.HM","SIS.HM","SIX2.HM","SIN.HM","SKYD.HM","SK1A.HM","COZ.HM","UNS1.HM","SOW.HM","SWVK.HM","SOT.HM","SAG.HM","SQU.HM","SRT3.HM","SSK.HM","SY9.HM","CAP.HM","STP.HM","SUR.HM","SXL.HM","SY1.HM","SYV.HM","LIO1.HM","UMS.HM","SZG.HM","TLX.HM","TTFB.HM","TC1.HM","TII.HM","TGT.HM","TKA.HM","17T.HM","TIN.HM","TTC.HM","TSTA.HM","TTR1.HM","TUI1.HM","TUR.HM","TWR.HM","UB5.HM","UBL.HM","UCA1.HM","USE.HM","UNH.HM","UNP.HM","U9V.HM","UUY.HM","VRS.HM","VFP.HM","V3V.HM","3V64.HM","WRF.HM","VVU.HM","VNA.HM","VOW3.HM","VOW.HM","VSC.HM","V33.HM","VT9.HM","BMW3.HM","MAN3.HM","WCH.HM","WL6.HM","WYR.HM","ADS.HM","TRH1.HM","BAG.HM","3B7.HM","BEZ.HM","BMW.HM","COK.HM","CAT1.HM","C6G.HM","CON.HM","1Z8.HM","1COV.HM","DEX.HM","DE1.HM","DEZ.HM","FIV.HM","FRE.HM","GRR.HM","G7P.HM","HOT.HM","C9T.HM","INH.HM","INL.HM","INP.HM","LTC.HM","MAK.HM","M5Z.HM","MAN.HM","M4I.HM","MED.HM","M9K.HM","P2W.HM","PRG.HM","PRU.HM","SAP.HM","SEE.HM","2S7.HM","ST5.HM","PA9.HM","COM.HM"]

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
