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
    available_tickers = ["ARN.V","BOE.V","AQ.V","ALN.V","FLY.V","APO.V","AAC.V","SPX.V","LA.V","KWA.V","EOG.V","AUV.V","ATC.V","AOT.V","AN.V","AMX.V","ALY.V","ALL-H.V","AGO.V","AGM.V","AGE.V","ABR.V","ABE.V","EME.V","SRK.V","KBG.V","VRS.V","PHM.V","MOO.V","XI.V","ROG.V","FPC.V","CGC.V","LVL.V","JAG.V","GQC.V","BFD.V","ZMD.V","VPT.V","TGM.V","SVT.V","SPN.V","SPF.V","SAH.V","RX.V","RNK.V","RMK.V","PEX.V","OIL.V","NXE.V","NVX.V","MLR.V","IZN.V","IFA.V","NK.V","EQT.V","EIL.V","BRM.V","BKM.V","BG.V","ZEN.V","XYL.V","VMY-H.V","VPY.V","VPO-H.V","MAO.V","VGO.V","VGN.V","USO.V","UBN.V","TUS.V","TSG.V","TII.V","TE.V","SVV.V","SV.V","SRA.V","SOI.V","SNF.V","SLC.V","SFM.V","SDX.V","SBW.V","RJ.V","REC.V","QGR.V","PSH.V","PRG.V","PRB.V","PLC.V","PGS.V","PGM.V","PFM.V","PDP.V","ORX.V","OPS.V","OGI.V","NWN.V","NGC.V","NEV.V","NCG.V","NBU.V","MMA.V","MLN.V","MBO.V","MBG.V","LSI.V","LND.V","LMR.V","LGO.V","KGL.V","JZR.V","JAX.V","INT.V","INM.V","IMM.V","IGX.V","HVG.V","HTR.V","HPY.V","HMX.V","GPH.V","GBB.V","FSW.V","ESU.V","ENA.V","ELS.V","ELN.V","DVN.V","DSR.V","CLH.V","CIO.V","DNX.V","PMD.V","NDR.V","MMO.V","LMD.V","GZD.V","DYA.V","DVR.V","DVC-H.V","DV.V","DSY.V","DIG-H.V","DEQ.V","DEF.V","DAU.V","CYP.V","ADK.V","DXE.V","SQD.V","SDZ.V","SDV-H.V","NED.V","MDV.V","LDM.V","KZD.V","JP.V","IDL.V","IDC.V","GOM.V","GOE.V","GBD.V","FGF.V","FGD.V","EGD.V","DEX.V","VVC.V","ESK.V","XL.V","TYP.V","PEH.V","NXX.V","NKW.V","MAT.V","EWS.V","EPO.V","ENW.V","EKG.V","SWE.V","WSE.V","TMG.V","TIN.V","SXL.V","SSV.V","PZE.V","SNS.V","SKX.V","SKK.V","RMT.V","EDE.V","Q-A.V","PTP.V","PRD.V","POE.V","PMI.V","ORC-B.V","NUK.V","NSP.V","NOU.V","NEM.V","MEP.V","MEI.V","MD.V","MCE.V","LE.V","KUB.V","KLE.V","HWK-A.V","PPE.V","FVR.V","EXO.V","EXG.V","EVR.V","EVM.V","EUU.V","ETF.V","ESS.V","ERG.V","ELO.V","ELI.V","EEL.V","ED-UN.V","EBN.V","EAS.V","EAG.V","CWV.V","CRE.V","CFY.V","CFL.V","CE.V","BMK.V","BOW.V","BFS.V","AZM.V","AVN.V","AER.V","ZEE.V","XEL.V","WTR.V","WGX-H.V","WEL.V","WCE.V","WBE.V","WAR.V","VUX.V","VUI.V","VRD.V","VEL.V","VIO.V","FYL.V","FFP.V","RUF-U.V","PYD.V","IFR.V","FSN.V","FMS.V","FGH.V","FFF.V","FBI.V","FBF.V","FAM.V","AFS-H.V","UMF-A.V","SOG.V","VCI.V","SPA.V","GOD.V","VIT.V","MJS.V","GWA.V","GKX.V","CKG.V","GBN.V","CDX.V","BVA.V","BUS.V","BTV.V","WKG.V","WDG.V","TNR.V","THM.V","TGX.V","SVG.V","SUG.V","SSN.V","SKP.V","SGX.V","RGI.V","RDU.V","AGX.V","PGO-H.V","PGK.V","OY.V","OOO.V","NRT.V","NCX.V","MDO.V","MAC.V","LQD.V","LGN.V","VHO.V","PRH.V","LHR.V","HTC.V","HOP.V","HMT.V","HEO.V","GNH.V","GHR.V","CHC.V","AHI.V","HN.V","WON-H.V","TUF.V","JOC.V","JMC.V","JVL-H.V","JTR.V","JTC.V","JSP.V","JRI.V","JOR.V","JML.V","JFC.V","JET.V","JAU.V","JDL.V","FTJ-H.V","PJT.V","JNX.V","KFG.V","WKM.V","KZX.V","KNA.V","KMT.V","KLH.V","KCC.V","KAM.V","PNG.V","NOL-H.V","KWF.V","KWC-H.V","KTN.V","KSK.V","KNX.V","KNO-H.V","KG.V","KEK.V","KM.V","KLG.V","KDR.V","GKL.V","CKR.V","KXM.V","VAL.V","SFT.V","RM.V","PTR.V","PML.V","NNP.V","MIO.V","URC.V","TWM.V","TTD.V","TAC.V","SRL.V","MRV.V","BCM.V","ZON.V","XIM.V","UCU.V","ORS.V","SRO.V","SMY.V","SMN.V","RST.V","RML.V","REX.V","QMC.V","PPX.V","SMP.V","NNO.V","MVN.V","MUN.V","MTO.V","MOX.V","MIR.V","MHC-H.V","MGC.V","MFS.V","MEK.V","MED.V","MDL.V","LMS.V","POI.V","VID.V","UNO.V","TNC.V","SAT.V","NOW.V","ORO.V","NZN.V","NSY.V","NIC.V","NCI.V","SUP.V","SS.V","SFD.V","PFN.V","NRL.V","NZZ.V","NZ.V","NWX.V","NW.V","NVT.V","NVI.V","NU.V","NTY.V","NTS.V","NTR.V","NTE.V","NSX.V","NST.V","NS.V","NRN.V","NQ.V","NPH.V","NPA.V","NOV.V","NOT.V","NOR.V","NOB.V","NNX.V","NNN.V","NMX.V","NL.V","NIR.V","NIK.V","NGM.V","NET.V","NEE.V","CKK.V","OOI.V","OCN.V","IOG.V","CO.V","XOP.V","WAI.V","TOO.V","SAN.V","SAO.V","OYL.V","OX.V","OSS.V","OPW.V","OPA.V","ONE.V","ON.V","ODN.V","OCO.V","GOP.V","FO.V","CUO.V","COT.V","COO.V","AOS.V","IO.V","ORR.V","NAA.V","OMR-H.V","POC.V","OBN.V","PHO.V","TSP.V","PKS.V","QI.V","QHR.V","QST.V","QQ.V","QPT.V","QIS.V","QIC.V","GQ.V","QAI-H.V","Q-B.V","QTA.V","CQM.V","QF.V","QXP.V","QMX.V","QIC-U.V","QIT.V","LAQ.V","QRO-H.V","QZM.V","QRO.V","RW.V","BRI.V","B.V","TLR.V","YO.V","XND.V","WRR.V","VRB.V","TRA.V","TPN.V","TBR.V","SYS.V","SXR.V","SSE.V","SIE.V","SCO.V","RI.V","RYU.V","RVA.V","RRL.V","RRI.V","RKR.V","REO.V","RBE.V","RB.V","PTC.V","LK.V","IRC.V","GUL.V","GUG.V","GTA.V","GRV.V","GPG.V","GNT.V","GGL.V","CXD.V","CSQ.V","CPS.V","CN.V","CGP.V","CCE.V","CBI.V","CBA.V","BTR.V","BRS.V","BGD.V","WPR.V","AVZ.V","AUU.V","AU.V","ATI.V","ASN.V","BRA.V","ALI.V","ADR-H.V","AYN.V","WRP.V","WZR.V","WPQ.V","WMR.V","WIL.V","VSR.V","VAX.V","ULT.V","UC.V","UBR.V","TWR.V","TSN.V","TRC.V","TME.V","TK.V","TM.V","SWN.V","TCC.V","SRI.V","SQA.V","SWR.V","TMT-H.V","SLK.V","SLG.V","SKE.V","SIP.V","SI.V","SGU.V","RZZ.V","RTM.V","RVV.V","RVL.V","RUP.V","TRU.V","TLT.V","SIO.V","TWD.V","TNG.V","UGD.V","UTY.V","UNI.V","ULI.V","UG.V","MU.V","GAZ-UN.V","FDC.V","CVV.V","BYU.V","BW.V","YVI.V","VQS.V","PLL.V","GV.V","CLV.V","CBS.V","VV.V","VTT.V","VTI.V","VML.V","VGD.V","VEG-H.V","VCV.V","VRY.V","SVO.V","SMV-H.V","PVX.V","MVA-P.V","LVH.V","ITT.V","GZZ.V","GSV.V","EV.V","DVI.V","CZ.V","CZ-H.V","CVN.V","CDC.V","CBV.V","BLV.V","AZN.V","VVI-H.V","BAV-H.V","TVE.V","VVN.V","CVC-P.V","AQE-H.V","BVE.V","VOL.V","PPV-H.V","ATV.V","ETV-H.V","GGS.V","VXL.V","PSV.V","CMT.V","MQV-H.V","VCR-H.V","GVY.V","VIS.V","FCV.V","AQE.V","SLV.V","PGV.V","IVC.V","AMN-P.V","VFX.V","MPS.V","WT-H.V","WP.V","WML.V","WLV.V","WEE.V","WED.V","WCC.V","WAN.V","PAW.V","MGW.V","IDW.V","EW.V","DWS.V","BMW.V","BWR.V","AWI.V","WRY.V","WLF.V","WR.V","WHM.V","CWG-H.V","WIF-H.V","WHY.V","WEB.V","YFI.V","XBC.V","XX.V","XME.V","XIA.V","XCX.V","XAU.V","XCP.V","LIX.V","DAP-U.V","XE.V","XTT.V","XTM.V","YEL.V","YOO.V","YAK.V","YTY.V","YTC-H.V","ZC.V","ZFR.V","CZX.V","CNZ.V","ZIM.V","ZNC-H.V","ZAO.V","ZIM-H.V","ZCC.V","ZAD.V","ZUM.V","ZOR-P.V","ZMS.V","ZKL.V","ZTE.V","AAT.V","AAO.V","AAU.V","AAZ.V","AAX.V","AA.V","AAP-P.V","AAU-H.V","AAN.V","AA-H.V","AAD.V","AAP.V","NAI.V","ABZ.V","ABM.V","ABS.V","ABU.V","AB-H.V","ABI.V","AME.V","ABL.V","ABN.V","ABQ-H.V","AXE.V","AT.V","ART.V","AKR.V","AKM.V","ACU.V","ACL.V","ACS.V","FAS.V","CII-H.V","CWN.V","MIA-P.V","APD-P.V","ACE-H.V","ACK.V","ACY-H.V","RAP-P.V","ARI.V","ACN.V","ACH.V","APC.V","IB.V","AUA.V","ANT-H.V","AXI.V","ADL.V","ADI.V","ADG.V","ADD.V","ADE.V","AQS.V","AE-A.V","AEN.V","AEC.V","AEX.V","AEL.V","EAM.V","AGG.V","AFY.V","AFR.V","AFM.V","NFK.V","WAF.V","NFK-H.V","AUR.V","AFE.V","AGQ.V","BVO.V","AGH.V","AGC.V","AGB.V","AGA-H.V","AGL.V","AGD.V","FSH.V","SAI.V","AGV.V","AGY.V","AHU.V","AHS.V","AHP.V","AHC.V","AHR.V","AHO-H.V","AII.V","IQ.V","AIX.V","AXN-H.V","AIN-H.V","AIS-H.V","AKC-P.V","AKH.V","MAI.V","AZX.V","ALP.V","ALH.V","ALE.V","AL.V","ASX.V","ALM.V","APN.V","ALD.V","AXC.V","AMO.V","ALZ.V","ANE.V","ALR.V","ALQ.V","ATU.V","ALV.V","ANZ.V","ALG.V","ARH.V","ALZ-H.V","APT.V","AVX.V","NTC.V","MLY.V","FEM.V","AMY.V","AMU.V","AML.V","AMK.V","AMG.V","AMT-H.V","LAT.V","AVC.V","AMT.V","NAN.V","AMZ.V","AM-H.V","RRR-UN.V","RAB.V","AXG.V","AVE.V","ANF.V","ANG.V","RYP-H.V","ARY.V","URA.V","CA.V","DDD-H.V","ATE.V","RHA.V","ANK.V","EXC.V","NOG.V","BEE.V","MON.V","OMM.V","ARA.V","ANB.V","AOZ.V","APV.V","APL.V","APA.V","APE.V","AQM.V","AQC.V","AQC-H.V","ASL.V","NAR.V","GRG.V","AWS.V","ARS.V","ARD.V","ARC.V","A.V","ATX.V","SA.V","ARW.V","ARB-H.V","ARU.V","RPT.V","ARB.V","ARK.V","GAR.V","SCO-H.V","ARR.V","ASG.V","AST.V","ASM.V","ASC.V","ASE.V","AXA.V","BAY.V","TAR.V","FA.V","ASB-H.V","NOW-H.V","ASQ.V","-H.V","ATY.V","ATM.V","ATG.V","ATW.V","BOC.V","TTO-H.V","AVA.V","AUG.V","AUX.V","AVT.V","AVM.V","AVD.V","VVA.V","AVU.V","TPC.V","VIV.V","AWE.V","AXQ.V","AXM.V","AYQ-H.V","AYB-H.V","AYQ-A.V","BOZ.V","BAT.V","BAJ.V","PST.V","PBM.V","IBH.V","HBE.V","HBY.V","FBX.V","EBY.V","DBL.V","BSH.V","BHS.V","BGM.V","BCN.V","BGS.V","BRO-H.V","BAL-H.V","BGL.V","BOZ-H.V","GCO.V","CPA.V","BBB.V","SNR.V","SM.V","MCU.V","GSI.V","CFB.V","COD.V","BBM-H.V","BBI.V","BPC.V","EQ.V","MC.V","KAY.V","IMU.V","JFI.V","TQC-P.V","CD.V","PTK.V","BCT.V","SMS.V","MTS.V","MIT.V","INP.V","GSP.V","COV.V","BUL.V","BCU.V","BCK.V","BCG.V","BCF.V","BCC.V","CEB.V","EXX.V","BPE.V","NAV.V","VBI.V","BCR-H.V","VBI-H.V","BCU-H.V","BCO-H.V","GBR.V","BCO.V","JDN.V","BCP-H.V","DAN.V","CCP-H.V","SRC.V","SPY.V","PKT.V","PHI.V","GXM.V","GWM.V","CMB.V","TES.V","SHO-H.V","PLR.V","BDC.V","VCV-H.V","OGO.V","RLV.V","HPL.V","SSS.V","SHO-P.V","KE-H.V","BP-H.V","EGX.V","VLC-H.V","RNP.V","NXO.V","GLD.V","EET.V","GDM.V","SRQ-H.V","MRL.V","KE.V","TIM.V","LBC.V","BZ.V","BRZ.V","BRL.V","BKR.V","BEY.V","BEX.V","BEW.V","BER.V","BEN.V","BTC.V","BEA.V","BET.V","BEL.V","GB.V","WBR.V","SBG-H.V","BED.V","IBC.V","SEB.V","SIC.V","LPC.V","TAN.V","PEM.V","MJX.V","-P.V","CZH.V","NSC.V","LPS.V","GDN.V","DEC.V","BFK-P.V","SWR-H.V","DE.V","SJL.V","MWI-UN.V","PH-P.V","BFF.V","NGN.V","IES.V","BFT.V","MGZ-H.V","RHR.V","BFM.V","ROY-H.V","PLY.V","BGG.V","BGE.V","WOW-P.V","MGI.V","REP-H.V","CUT.V","IEX.V","BGA.V","IEX-H.V","OXI-H.V","EMS-P.V","DSS.V","EGT.V","RCR.V","EEN.V","EXS.V","RMD.V","FUU.V","EL.V","CZY.V","CSN.V","BIT.V","BHR.V","BSP.V","MML.V","MYR.V","TAJ.V","BHT.V","IRR.V","PHC.V","RRS.V","VMI-H.V","LEN.V","PHC-H.V","CSN-H.V","VMI.V","IVQ-P.V","BHK.V","MRS.V","SNV.V","TKK.V","TIR-H.V","BHV.V","GPE.V","LIR.V","CYX.V","SGB.V","SBM.V","MBI.V","BTM-H.V","BQE.V","BIO.V","EBM.V","SVS.V","LBL.V","BTT.V","KNE.V","BTI.V","SOR.V","MOR.V","CIN.V","MNP.V","EMO.V","-UN.V","RPN.V","TCO.V","SYR-H.V","CHY-H.V","CNC.V","MRB.V","MOM.V","RHC.V","RCK.V","PBR.V","LET.V","DSF.V","CMX.V","CKZ-H.V","CAC.V","BOR.V","PPZ-H.V","ROC.V","KAP.V","WEY.V","DJI.V","GAL.V","BKD.V","PPI.V","SEW.V","JCO.V","GRC.V","WST.V","TCX.V","PXA.V","PE.V","MBS.V","DIA.V","BXR.V","BSR.V","BSG-H.V","BPL.V","BLR.V","BLN.V","BLT.V","BVD-UN.V","GOI-H.V","CEP-P.V","ICM.V","KGC.V","MCK.V","BLM.V","NIP.V","EEC.V","MRX-H.V","TIL.V","BMM.V","GPY.V","BSK.V","BLL-H.V","TRM.V","LMG.V","GLK.V","CGW.V","BRU.V","BM.V","CDB.V","RMG.V","PHL-H.V","EMT.V","NHK.V","CWC.V","BMR-H.V","BMA.V","BML.V","BME.V","TEP-UN.V","RUF-UN.V","RTI.V","PDM.V","MOC.V","MCI.V","IML.V","GR.V","GMV.V","DVG.V","DMC-P.V","CYM.V","CPE-H.V","CLI.V","TRX.V","NVV.V","BNL-H.V","FRN.V","EXU.V","PPA.V","CUG.V","CWM.V","IOU.V","HBY-H.V","COR.V","WMT.V","UC-H.V","FEO.V","CCY.V","CWS-H.V","BNR.V","IDM.V","BOB.V","BPU.V","BOL.V","MTB.V","GGG.V","REL.V","PMA.V","HRP.V","HDA.V","DMG-H.V","CKT.V","BUF.V","UHO.V","PMR.V","SMO.V","CBM-H.V","KYS-H.V","SAE.V","CAY.V","SUS-A.V","SAE-H.V","SUS-U.V","NCR.V","LXE.V","MPG.V","LAB.V","FMX.V","EU.V","EHT.V","CNS.V","MEA-P.V","CLN-P.V","MCP-P.V","NGY-H.V","CEV.V","CPL.V","TPI.V","IKM.V","RYO.V","TKU.V","OLE-P.V","HEC.V","SDC.V","ROE.V","HGO.V","NXS.V","MVP.V","MRO.V","MAP-P.V","GVG.V","BWN.V","RDX.V","CEY-H.V","MLM.V","GPL.V","UBS-H.V","NFR.V","RCZ.V","GPS.V","TTM.V","TON.V","STO.V","MPL.V","CTP-H.V","SE.V","SFX.V","EQG.V","PED-H.V","TGV.V","FMM.V","MMC-P.V","MZI.V","HEM.V","POR.V","PDQ.V","PCR.V","HVV.V","GI.V","GCX.V","JUB.V","TNO-H.V","SG.V","NYX.V","MJN.V","KCK.V","BTU-H.V","TNO.V","NM.V","BTL.V","NX.V","MNR-H.V","CCU.V","DNI.V","IS.V","GPV.V","NTH-H.V","BUD.V","CBX.V","SN.V","MXR.V","MNY.V","NSY-H.V","STI.V","FUR.V","RSL.V","GRS-H.V","GGC.V","VLR-H.V","COB-U.V","KMI.V","RRC.V","RCT.V","TPA-H.V","MQR.V","SOF.V","CXV.V","KMI-H.V","EOR.V","ES.V","RLY-P.V","TUO.V","GTB.V","ELT.V","EGA.V","STS-H.V","RDM.V","TLK.V","LTG.V","PGE.V","MTE.V","IVS.V","FAU-H.V","CNG.V","CIT-H.V","ECH-H.V","MZA-H.V","RYR.V","ECH.V","ICU.V","MSD.V","USS.V","NTQ.V","DTS.V","FF.V","VIE-P.V","TTR.V","SUF-A.V","SYN.V","RPX.V","CSC.V","PLU.V","PPP.V","WAV.V","CRF.V","SIM.V","RAK.V","PP.V","MGS.V","LHC.V","HIT.V","GSH.V","GDX.V","FEN.V","FAN.V","EYC.V","ERC.V","ELM.V","COU.V","CEL.V","CDA.V","CC-H.V","NEL-UN.V","EPR.V","EMH.V","SPZ.V","REQ-P.V","MU-H.V","LRN.V","SEI.V","CNH.V","SZM.V","RCU.V","FAC.V","CVA.V","CIP-H.V","MSP.V","GPM.V","PRJ.V","LLC.V","CPM.V","GBE.V","HNC.V","IFD.V","NCA.V","PSL.V","HA.V","CX.V","SGW.V","DUG.V","OEE.V","BYN.V","PTA.V","PA.V","MI.V","SIL.V","UI.V","KR.V","PVF.V","OEG.V","MGL.V","BYM-H.V","NIM.V","ROL-P.V","FFC-H.V","KNG.V","CEC.V","TCA.V","MV.V","CEI.V","PIT-H.V","PSC-P.V","GHE-P.V","DRN-H.V","ECT.V","PDA-H.V","ELC.V","IMR.V","DVA.V","CVB-H.V","NGE.V","CEL-H.V","MKT.V","FCF.V","REZ.V","RCG.V","SSP.V","CT.V","RIR.V","SCG.V","CTN.V","STE.V","ISS.V","CRC.V","SC.V","MMX.V","CUC.V","NNA.V","MCX.V","CEA.V","CRD.V","SC-H.V","CTG-H.V","GMZ.V","PRN.V","RZ.V","WMM.V","FMK-P.V","NGZ.V","ITG.V","ERA.V","GIS.V","OLA.V","PYR.V","CXB.V","CNX.V","TCI.V","SVI.V","SGE.V","SAY-H.V","ROX.V","PPK.V","PCI.V","NES.V","HMB.V","GSW.V","GRB.V","GNC.V","GIC.V","GCU.V","FCD-UN.V","DBV.V","CTM.V","CRS.V","CPC.V","CNO.V","CKB.V","CJC.V","CGD.V","CDN.V","CCK.V","CCD.V","CCB.V","CAU-H.V","CAP.V","CAF.V","CAD.V","RCC-H.V","FSC-H.V","CRU.V","CBG.V","CBJ.V","CBE.V","CCC.V","CDG.V","CDE.V","CZO.V","CVX.V","CTZ.V","CMM.V","CEM.V","CEO-H.V","CFO.V","CFM.V","CGT.V","CGM.V","CGE.V","MCG.V","CMV.V","CH.V","CTO.V","CKC-H.V","CKC.V","CY.V","CXG-A.V","CL-H.V","CSX.V","RII-B.V","CL.V","CLX.V","NFD-A.V","NVM.V","PNE.V","EYE-A.V","CLD.V","RJX-A.V","CLZ.V","CMU.V","CMD.V","CMJ.V","CML.V","CMI.V","CNP.V","CPV.V","CPP.V","CQR.V","CQC.V","CRB.V","WCX.V","CRX.V","CYF.V","CWG.V","CRV.V","C-H.V","CST.V","CSO.V","CSV.V","CSG.V","CSG-H.V","CSL.V","CTI.V","DEV-H.V","CUU.V","CWQ.V","CWQ-H.V","CUI.V","CUV.V","CV-H.V","CVR.V","CXX.V","CXO.V","CXM.V","CXE-H.V","DAL.V","DAI-H.V","DMR.V","DAM-H.V","DYU-H.V","DCY.V","DLT.V","MIX.V","DFI.V","DGM.V","DGO.V","DHR.V","DVT.V","DOS.V","DMA.V","DMI.V","KDI.V","PAN.V","MVD-H.V","DLV.V","DLS.V","DOT.V","DOX.V","DPH.V","DRV.V","DRC-H.V","DXX.V","DYG.V","RD.V","SEG-H.V","ERL-H.V","ESB-H.V","EWK.V","GER.V","ERN.V","LL.V","EPL.V","ECC.V","ECR.V","EDW.V","CHN.V","EDG.V","EFT.V","ELY.V","EMX.V","EMR.V","EMB-H.V","EMB.V","EPT.V","EM-H.V","TZR.V","TVL.V","RED.V","MQL.V","MCW.V","MCR.V","LNE.V","HRE.V","HME.V","INA.V","FEE.V","ENS.V","COQ.V","NWE.V","POP.V","MAH.V","SXE.V","FSI-H.V","KIV.V","EOX.V","EPX-H.V","EPK.V","IEI.V","GUF.V","PRV-UN.V","ESV.V","EST.V","ESE.V","EUO.V","EUK.V","TNA.V","EVC-H.V","SOP.V","SDE.V","PUM.V","MSA.V","MIN.V","LME.V","GIT.V","GFN.V","FNC.V","EY.V","SNL-H.V","GEA.V","NQE.V","PX.V","GGY.V","MFX.V","PMX.V","IXI.V","FLX.V","GRX-H.V","MTZ.V","TYE.V","GEA-H.V","GUN.V","SPT.V","LRA.V","SNL.V","DEX-H.V","THX.V","KAR.V","TQY.V","PXI.V","FEX.V","TOE.V","KAS.V","GEG.V","ORC-A.V","FMR.V","FAV-H.V","UMF-U.V","FG.V","FBR-H.V","FDR.V","FFM.V","FGC.V","FMG.V","KGF.V","FI.V","FLO-H.V","FNR.V","FTI.V","FOM.V","RUN.V","GFP.V","FRI.V","FTR.V","PTF.V","FWK.V","GGI.V","GG.V","GRY-H.V","GTO-H.V","LG.V","GLW.V","GRI.V","GAE.V","GCR.V","GCC-H.V","GDE-A.V","GCN.V","GTC.V","GMA.V","GEM.V","GXR.V","GVW-H.V","GFK.V","GFM-H.V","IGP.V","GOK.V","IGP-PA.V","GJB.V","PGZ.V","GLB.V","GMN.V","GMT-H.V","GN.V","GNG.V","GNF.V","ICG.V","GXS.V","GUM.V","GRM.V","TTG.V","TEM.V","SGN.V","SGM.V","SGC.V","RPR.V","RPM.V","RGD.V","PGC.V","MYA.V","MXI.V","MTU.V","NAC.V","MGG.V","HWY.V","GSS.V","GRZ.V","GP.V","GOG.V","TEN.V","GTG.V","SOC.V","ORG.V","SGA.V","RG.V","GST-H.V","PGX.V","PKL.V","RYG.V","RGC.V","LTA-H.V","TDC.V","RGZ.V","TDC-H.V","REN.V","LPK.V","GRO.V","NUG.V","SR-H.V","SCA.V","RAU-H.V","OPG.V","GRR.V","WGF.V","MAD.V","MAS.V","LAD.V","OPG-H.V","GSR.V","ORE.V","CAT.V","IGO.V","GPW.V","SPS-A.V","SGH.V","REK.V","NMG.V","LOY.V","LLG.V","GSA.V","GRK.V","GRA-H.V","GTD-H.V","GTP.V","GWQ.V","HTL.V","HRL.V","HBK.V","MDX.V","HRC.V","MT.V","VGL.V","MOB-UN.V","HJI.V","HXC.V","HRH.V","HMI.V","HI.V","HPI.V","THP.V","MHI.V","HLM.V","HML.V","MPT.V","HSR.V","HUA.V","ROB.V","HUD.V","IBT.V","ICO.V","IDI.V","IDH-H.V","IRI.V","IFX.V","IFM.V","IGD.V","JCI-H.V","ILA.V","ILC.V","IPT.V","IMA.V","IMT.V","IMI.V","PPM.V","IOT.V","IPD.V","IPC.V","IRO.V","NFE.V","ISD.V","ITM.V","IVI.V","IVX.V","IWG.V","JEN-H.V","JHC-H.V","JLR.V","JLR-H.V","JOR-H.V","KZN-H.V","KRS.V","KYU.V","KBT.V","KES.V","KHA-H.V","KHA.V","KS.V","KRM-H.V","KUT.V","KZZ.V","PLA.V","LTV.V","LES.V","LEA.V","LGR.V","SYL.V","RUM.V","LM.V","PBS.V","LJ.V","TLA.V","LRC.V","LOT.V","LRC-H.V","LOM.V","LRL.V","TSM.V","MNM.V","MCC.V","MAZ-H.V","MAE.V","MAM.V","MXX.V","MDE-H.V","MFM.V","MAN.V","MTH.V","MCS.V","MCA.V","MCM-A.V","TNK.V","SMD.V","SEK.V","PYT.V","MWX.V","MPH.V","MKR.V","MTC.V","MTX.V","LIO.V","MWC.V","MOE-H.V","MGP.V","SSI.V","SMI.V","SCZ.V","RUG.V","RMN.V","RMI.V","RDS.V","PRZ-H.V","PAL.V","MTM-H.V","MRZ.V","MMY.V","MMV.V","MIB.V","COL.V","UVN.V","RL.V","MSR.V","VZZ.V","SUI-H.V","SCM-H.V","VUL.V","MMS.V","TXR.V","MKA.V","MKN.V","MKU-H.V","MNX.V","MVW.V","SMM.V","M-PA.V","RMO.V","MOE.V","MOV-P.V","M.V","MOI.V","MTV.V","MVE-H.V","MVC-H.V","MXM.V","MXC-H.V","NAP.V","NVY.V","SNA.V","NXT.V","NBR.V","NBO-H.V","NCO.V","NCE.V","NE.V","NEO-H.V","VDO.V","NXG.V","NR.V","NER.V","NTN-H.V","NGH.V","NIO.V","NOX.V","NIA.V","NLL.V","NMD.V","NRZ-H.V","NRM.V","TGC.V","NVO.V","NXI-H.V","OAG.V","OKM-H.V","OCC.V","OCA-P.V","OVT.V","OEL-H.V","ODX-H.V","OEC.V","SCD.V","PCO.V","OLV.V","OML.V","OMN.V","OWI.V","ONV.V","OWI-H.V","OUP-H.V","PPC.V","PSP.V","PAK.V","PUC.V","PKS-H.V","PAW-H.V","RPP.V","PBA-H.V","PCS.V","PCQ.V","PCV.V","PDR-H.V","PKK.V","SNM.V","PRO.V","PNN.V","PFC.V","PEO.V","PEA.V","PNA.V","PTV.V","PET.V","PEP.V","SPK.V","PTG.V","PTE.V","PJX.V","PTX.V","PM.V","PNR-H.V","PZ.V","SBX.V","RSN-H.V","RP.V","PRR.V","RPC.V","BRN-PA.V","PRS-H.V","PRR-H.V","PTU.V","PUC-H.V","RTH.V","SNG.V","RBX.V","RDX-H.V","RRE.V","ROM.V","RGM.V","RER.V","SRE.V","RFC.V","RYE.V","RYS-H.V","SHL.V","RII-K.V","RRD-H.V","RK.V","RLS-H.V","RMC.V","RMR-H.V","RMR.V","RRK.V","STR-H.V","ROI.V","RRK-H.V","ROS-H.V","ROU.V","ROT.V","RSV.V","RSY.V","SHM.V","SCR.V","SCX-H.V","SDS.V","SVA.V","SGG.V","SGZ.V","SJR-A.V","SHI.V","SLY-H.V","SYI.V","SMB.V","SIR.V","SSG.V","SNN.V","SPD.V","SYH.V","SLM.V","SSC.V","SME.V","SNI-PA.V","SY.V","SOL.V","SOJ.V","SSA.V","SPP.V","SRJ.V","SQG.V","SRX.V","STH.V","STT.V","STA.V","STK-H.V","STC.V","SYC.V","INX.V","SPC.V","SUL.V","SWA.V","SYD.V","SYZ.V","TAU.V","TAW.V","TAE.V","TRO.V","TDR-H.V","TTZ.V","TEA.V","TGD.V","TGR.V","TGI-H.V","TIC.V","TIP-H.V","TIA-H.V","TXX.V","TLL-H.V","TTS.V","TMV.V","TRB.V","TRG-H.V","TRS.V","TVR.V","TSD.V","TUR.V","UFC.V","UQ.V","UN.V","USR.V","VAN.V","VYC.V","VQA.V","VDR.V","VLA.V","VMS.V","WHN.V","VLV.V","VVV.V","BRV-H.V","TWY.V","VPI.V","VR.V","WAS-H.V","WRI.V","WFG.V","WCB.V","WMK-H.V","ADZ.V","AUN.V","BMG.V","CHQ.V","REG.V","CHK-P.V","CNA.V","CNY.V","SPI.V","SAB-H.V","MII.V","ENG.V","ENP.V","ENS-H.V","FIX.V","GBL.V","SEV.V","PLO-H.V","TEG-H.V","TRC-H.V","THH.V","THG-H.V"]

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
