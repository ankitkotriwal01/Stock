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
    available_tickers = ["ATLN.VX","ROG.VX","FHZN.SW","AAPL.SW","RO.SW","AMS.SW","ABBN.VX","CSGN.VX","VW-V.SW","DUFN.SW","BCGE.SW","VWS.SW","OXDEX.SW","OXDB1.SW","OSR.SW","KU2.SW","HEN.SW","EVE.SW","ZURN.VX","LONN.VX","GEBN.VX","UBSG.VX","GIVN.VX","USIN.SW","TEMN.SW","ROL.SW","MIKN.SW","BALN.VX","ALLN.SW","YPSN.SW","VATN.SW","VAHN.SW","UBXN.SW","SLOG.SW","STMN.SW","SOON.VX","SMET.SW","SLHN.VX","SFZN.SW","SCHPE.SW","SCHP.VX","SANN.SW","BAER.VX","NIN.SW","JEN.SW","JFN.SW","JKS.SW","BCJ.SW","TOSH.SW","JPM.SW","GRKP.SW","SGKN.SW","BLKB.SW","OXKBC.SW","SDF.SW","GMCR.SW","SYNN.VX","NESN.VX","NOVN.VX","SREN.VX","GALN.VX","CFR.VX","STL.SW","OTI.SW","RY.SW","O2D.SW","OXCON.SW","POST.SW","OXSY1.SW","OXDUE.SW","OXLXS.SW","OXCOP.SW","ORCL.SW","QCOM.SW","QIHU.SW","QIA.SW","QSC.SW","SGSN.VX","SCMN.VX","UHR.VX","SCTY.SW","PFE.SW","MDLZ.SW","GOOGL.SW","CL.SW","BHI.SW","VPB.SW","EPH.SW","VALE.SW","GSV.SW","VFC.SW","VOE.SW","VIB3.SW","NEWN.SW","VW.SW","VZ.SW","DRW3.SW","NEV.SW","KORS.SW","VILN.SW","HEN3.SW","RWE3.SW","PAH3.SW","BCVN.SW","PWTN.SW","SLW.SW","WMN.SW","WBA.SW","DWNI.SW","WDI.SW","OXGWI1.SW","GWI1.SW","WKBN.SW","OXO1BC.SW","O1BC.SW","XRX.SW","XOM.SW","XONE.SW","YRI.SW","YHOO.SW","YAR.SW","YELP.SW","YY.SW","MY.SW","YUM.SW","YGE.SW","ZWM.SW","ZIL2.SW","ZAG.SW","ZAL.SW","ZEHN.SW","ZBH.SW","GOLI.SW","ZG.SW","AFX.SW","OXAFX.SW","ZC.SW","ZMS.SW","TIM.SW","ZNGA.SW","ZUGN.SW","ZUBN.SW","METN.SW","OXZO1.SW","ZO1.SW","ARL.SW","AAM.SW","AAD.SW","AA.SW","ABX.SW","ABBV.SW","ABBNE.SW","ABF.SW","ABT.SW","ANF.SW","ACUN.SW","ATLNE.SW","AC.SW","ACA.SW","AMD.SW","ADBE.SW","BABA.SW","VJET.SW","TTM.SW","DANG.SW","HQCL.SW","BIDU.SW","ADXN.SW","RESOL.SW","ADEN.VX","ADS.SW","TEVA.SW","JASO.SW","ADENE.SW","NTES.SW","ADVN.SW","TSL.SW","AEVS.SW","AEM.SW","MTX.SW","AGN.SW","AFGN.SW","AF.SW","STLN.SW","IMPN.SW","BION.SW","TECN.SW","SWTQ.SW","SPSN.SW","PM.SW","LISN.SW","LIFE.SW","IPS.SW","INRN.SW","GBMN.SW","GAV.SW","GAM.SW","CYTN.SW","BSLN.SW","BARN.SW","ALSN.SW","DCN.SW","CPGN.SW","SAHN.SW","DESN.SW","ALPH.SW","MOBN.SW","SCHN.SW","CLTN.SW","BIOEE.SW","ALPNE.SW","PSPN.SW","LUKN.SW","EMSN.SW","IFCN.SW","STGN.SW","ELMN.SW","CALN.SW","SUN.SW","MCHN.SW","ORON.SW","MBTN.SW","EMMN.SW","CASNE.SW","AGFB.SW","TIBN.SW","CLXN.SW","HUBN.SW","VBSN.SW","AGS.SW","ESUN.SW","UHRN.SW","BC.SW","GUR.SW","BANB.SW","CPHN.SW","RIEN.SW","PEL.SW","BRKN.SW","TOHN.SW","BBN.SW","PAXN.SW","UHRNE.SW","MASN.SW","CPEN.SW","ALPN.SW","EDHN.SW","VET.SW","BEAN.SW","REPI.SW","LLB.SW","VONN.SW","TAMN.SW","BAYN.SW","PEHN.SW","ALTN.SW","LOHN.SW","MYRN.SW","BLIN.SW","IHSN.SW","BCHN.SW","LISP.SW","BUCN.SW","HELN.SW","ASCN.SW","EEII.SW","DAE.SW","VLRT.SW","LINN.SW","OFN.SW","FORN.SW","REPP.SW","WIE.SW","COM.SW","BVZN.SW","CASN.SW","SHPNE.SW","SIN.SW","FORNE.SW","STRN.SW","COTN.SW","KUNN.SW","KARN.SW","GATE.SW","VZN.SW","HUE.SW","WARN.SW","KOMN.SW","VALN.SW","AIXA.SW","AI.SW","AIRN.SW","DAL.SW","AIG.SW","AIRE.SW","AIR.SW","AKZ.SW","ALU.SW","ALO.SW","MO.SW","ALV.SW","AOX.SW","ALXN.SW","AMGN.SW","PAA.SW","BATS.SW","AXP.SW","BAC.SW","AMZN.SW","ANDR.SW","LLY.SW","SLB.SW","AU.SW","APGN.SW","MT.SW","SAZ.SW","ARYN.VX","ARIA.SW","ADM.SW","CADN.SW","ARM.SW","UA.SW","DIC.SW","ASM.SW","ASML.SW","AZN.SW","ASG.SW","SBO.SW","EBS.SW","VER.SW","OMV.SW","BWO.SW","IIA.SW","RBI.SW","RHI.SW","ROS.SW","ATS.SW","MMK.SW","CWI.SW","O2C.SW","T.SW","TKA.SW","LNZ.SW","CS.SW","SPR.SW","BPDG.SW","BA.SW","BALNE.SW","BAX.SW","BB.SW","BBDB.SW","BBY.SW","BC8.SW","BDX.SW","BDT.SW","DBAN.SW","PROX.SW","BEKN.SW","BPOST.SW","BEI.SW","OXBEI.SW","BELL.SW","BLT.SW","BHP.SW","HEB.SW","OXGBF.SW","GBF.SW","BIIB.SW","BIO3.SW","SGMO.SW","SBS.SW","BKW.SW","CBA.SW","RBS.SW","BLK.SW","BLD.SW","BX.SW","BMY.SW","BMPS.SW","OXBMW.SW","BMW3.SW","BMW.SW","BNR.SW","BNP.SW","OXBNP.SW","BOBNN.SW","BVB.SW","BOSS.SW","EN.SW","DB1.SW","BOSN.SW","BP.SW","BSKP.SW","BTO.SW","BVN.SW","BYW6.SW","CPENE.SW","CAI.SW","CARLB.SW","CAP.SW","PTK.SW","CCO.SW","CDI.SW","CDE.SW","CMBN.SW","SCAB.SW","CWC.SW","UN.SW","CELG.SW","CEV.SW","CERN.SW","CFT.SW","CGG.SW","LEON.SW","HREN.SW","EFGN.SW","DOKA.SW","CHD.SW","SFPF1.SW","WIHN.SW","LOGN.SW","PLAN.SW","KNIN.VX","PEDU.SW","SIK.VX","PRFN.SW","GMI.SW","30318277.SW","SYNNE.SW","PUBN.SW","UBSNE.SW","HBMN.SW","SRCG.SW","OERL.SW","PGHN.SW","CICN.SW","DOW.SW","SIAT1.SW","CVX.SW","NBEN.SW","SCHNE.SW","SREA1.SW","RSPF1.SW","SQN.SW","SGSNE.SW","HBLN.SW","C.SW","CIE.SW","CSCO.SW","CLN.VX","CMCSA.SW","CNC.SW","SEV.SW","CRM.SW","CSIQ.SW","EVD.SW","CTSH.SW","OXEVD.SW","DAN.SW","DAI.SW","DHR.SW","DSY.SW","DBK.SW","DDD.SW","DD.SW","CONT.SW","HD.SW","OXSAP.SW","COMPG.SW","OXNOEJ.SW","PUM.SW","TLX.SW","TEG.SW","NEMA.SW","MEO.SW","DGC.SW","DG.SW","DIS.SW","COLOB.SW","NZYMB.SW","DKSH.SW","PNDORA.SW","NOVOB.SW","GIL.SW","PMOX.SW","DPW.SW","DRI.SW","HDD.SW","DSM.SW","OXLHA.SW","DTE.SW","LHA.SW","DUFN.VX","RDSA.SW","DUE.SW","EBAY.SW","EDP.SW","RLD.SW","EDR.SW","EW.SW","EDF.SW","EI.SW","SNE.SW","LPK.SW","GE.SW","ELD.SW","EMR.SW","EMC.SW","FCEL.SW","NUS.SW","EOAN.SW","EO.SW","ERF.SW","ERICB.SW","ESRX.SW","GET.SW","DEQ.SW","EVT.SW","EVK.SW","HLEE.SW","EXPE.SW","FB.SW","WFC.SW","FCX.SW","FDX.SW","FEYE.SW","RACE.SW","FTON.SW","FFI.SW","FMS.SW","NOKIA.SW","FME.SW","FNV.SW","FNTN.SW","FVI.SW","WFM.SW","F.SW","FPE3.SW","FP.SW","MC.SW","ML.SW","MMB.SW","OXFME.SW","KER.SW","FR.SW","GOE.SW","LOCAL.SW","RI.SW","FRA.SW","KN.SW","UBI.SW","ENGI.SW","POM.SW","VIE.SW","ING.SW","SAF.SW","FRE.SW","FSLR.SW","GFMN.SW","GAMEE.SW","GFJ.SW","MRW.SW","TCG.SW","SRP.SW","RGSE.SW","OXG1A.SW","G1A.SW","GIS.SW","GEBNE.SW","GMT.SW","OXGXI.SW","GLE.SW","HTM.SW","GM.SW","GXI.SW","FI-N.SW","GFK.SW","GILD.SW","GLJ.SW","SBB.SW","GLUU.SW","GSK.SW","GLW.SW","GLKBN.SW","GMM.SW","GPRO.SW","GT.SW","KG.SW","G.SW","GOB.SW","GS.SW","PGM.SW","GPR.SW","HAL.SW","HAB.SW","HOG.SW","HNR1.SW","HBMNE.SW","HBH3.SW","KHC.SW","OXHEN3.SW","OXHEI.SW","HL.SW","HEID.SW","HEI.SW","HMB.SW","HHFA.SW","HIAG.SW","LEN.SW","CHT.SW","SOONE.SW","ISN.SW","OXKD8.SW","HOCN.SW","TTI.SW","MOZN.SW","ONVO.SW","SLT.SW","INH.SW","HPQ.SW","HYG.SW","NHY.SW","IMG.SW","IBM.SW","MDT.SW","IFX.SW","SHLTN.SW","LEG.SW","P1Z.SW","IMB.SW","IONS.SW","IPH.SW","IRBT.SW","ISP.SW","ISRG.SW","TIT.SW","NWRN.SW","SPM.SW","UCG.SW","SKIN.SW","PRP.SW","ENI.SW","IT.SW","ENEL.SW","JCP.SW","OXJEN.SW","JNJ.SW","SOFB.SW","SONC.SW","MAELI.SW","SHA.SW","TOYMO.SW","JUNGH.SW","KNDI.SW","KBC.SW","TKBP.SW","KCO.SW","KGX.SW","KPO.SW","KO.SW","KRN.SW","OXSDFG.SW","KUD.SW","KWS.SW","LXS.SW","LVS.SW","LMN.SW","LHN.VX","LEO.SW","LECN.SW","LEHN.SW","OXLING.SW","LLOY.SW","LMT.SW","LNKD.SW","COPN.SW","SFQ.SW","RTL.SW","MAN.SW","MCD.SW","MCP.SW","NCM.SW","NEM.SW","MLP.SW","MMM.SW","TSLA.SW","MOLN.SW","MOR.SW","PMI.SW","MS.SW","MRK.SW","MSFT.SW","MUV2.SW","MU.SW","MYL1.SW","SNBN.SW","NDA.SW","NDX1.SW","NDASEK.SW","NESNE.SW","WAC.SW","NFLX.SW","NKE.SW","NIHN.SW","WIN.SW","PHI.SW","INO.SW","TMO.SW","RDN.SW","PN6.SW","SBM.SW","NOEJ.SW","TEL.SW","NOVNEE.SW","NVDA.SW","ODHN.SW","OR.SW","ORA.SW","ORMP.SW","OXDTE.SW","OXADS.SW","OXDPW.SW","OXMRK.SW","OXRWE.SW","OXDBK.SW","OXFNTN.SW","OXEOAN.SW","OXFIE.SW","UNP.SW","UPS.SW","PCLN.SW","PEP.SW","WPL.SW","UG.SW","PEAN.SW","PFV.SW","PG.SW","VRTX.SW","REGN.SW","VRX.SW","PLUG.SW","PSEC.SW","PSM.SW","PSAN.SW","PUB.SW","PYPL.SW","RAA.SW","RB.SW","RCO.SW","RHK.SW","RHM.SW","RIO.SW","RIOP.SW","RIGN.SW","RNO.SW","RSTI.SW","RUS.SW","RWE.SW","SAX.SW","SNDK.SW","SBUX.SW","SCZ.SW","SCR.SW","TFS.SW","SFPN.SW","SFSN.SW","SGL.SW","SW1.SW","SSO.SW","SIX2.SW","SVM.SW","SW.SW","S92.SW","SOW.SW","SWVK.SW","SPLS.SW","SRT3.SW","SYK.SW","CAS.SW","SZU.SW","SUR.SW","SU.SW","SPWR.SW","SWEDA.SW","UHRE.SW","SY1.SW","SYNNEE.SW","SZG.SW","THO.SW","TTK.SW","TXN.SW","TK.SW","TWX.SW","TLSN.SW","TMUS.SW","TRV.SW","TRIP.SW","TSCO.SW","TUI1.SW","TWTR.SW","UIS.SW","UL.SW","UNH.SW","UTDI.SW","GRPN.SW","UTX.SW","VLA.SW","VK.SW","VCH.SW","VIV.SW","V.SW","VNA.SW","VOS.SW","VOD.SW","WCH.SW","WMT.SW","WYNN.SW","AUTN.SW","BAP.SW","BARC.SW","BAS.SW","B5A.SW","COK.SW","CA.SW","CAT.SW","COP.SW","CON.SW","DE.SW","DEZ.SW","ENPH.SW","FIE.SW","HOT.SW","INVN.SW","LIN.SW","M5Z.SW","MA.SW","MER.SW","PARG.SW","SPCE.SW","SAN.SW","SAP.SW","SPEX.SW","SPLK.SW","COMD.SW","INTC.SW"]

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
