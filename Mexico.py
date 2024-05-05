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
    available_tickers = ["ASURB.MX","WALMEX.MX","MTN.MX","GOOG.MX","AMXL.MX","AAPL.MX","LALAB.MX","AZTECACPO.MX","ALFAA.MX","ADSK.MX","BIMBOA.MX","GRUMAB.MX","FEMSAUBD.MX","DIS.MX","KOFL.MX","ELEKTRA.MX","RDSB.MX","GMEXICOB.MX","CEMEXCPO.MX","RDSA.MX","PINFRA.MX","MEXCHEM.MX","MASECAB.MX","LABB.MX","ICHB.MX","ICA.MX","HOMEX.MX","HERDEZ.MX","HD.MX","GPH1.MX","GIGANTE.MX","GBMO.MX","FIBRAMQ12.MX","CMOCTEZ.MX","CHDRAUIB.MX","BAFARB.MX","AMD.MX","VALUEGFO.MX","SIMECB.MX","SIEN.MX","RCENTROA.MX","OMAB.MX","ODP.MX","LIVEPOL1.MX","INVEXA.MX","IDEALB-1.MX","HOGARB.MX","GMD.MX","GFNORTEO.MX","GEOB.MX","GCARSOA1.MX","FINN13.MX","FINAMEXO.MX","NEMAKA.MX","XOM.MX","PRU.MX","FSLR.MX","KHC.MX","CVS.MX","BHI.MX","JPM.MX","JNJ.MX","JCP.MX","GLENN.MX","STJN.MX","JCI.MX","JAH.MX","DECN.MX","JDN.MX","SINAN.MX","KO.MX","KUOA.MX","SLBN.MX","MMM.MX","SITESL.MX","NFLX.MX","TELN.MX","SIDN.MX","RIGN.MX","NVSN.MX","NVDA.MX","NOKN.MX","NKE.MX","POTN.MX","ORCL.MX","CULTIBAB.MX","BAC.MX","HOTEL.MX","TEMGBIAA.MX","ORN.MX","PINFRAL.MX","OHLMEX.MX","QSRN.MX","QIHUN.MX","QCOM.MX","Q.MX","CREAL.MX","SNEN.MX","TWX.MX","TOTN.MX","COST.MX","YHOO.MX","X.MX","VALEN.MX","UAL.MX","UA.MX","SCCO.MX","INTC.MX","GPS.MX","GILD.MX","CSCO.MX","CMG.MX","C.MX","BIDUN.MX","BCSN.MX","BBY.MX","BBBY.MX","BA.MX","ATVI.MX","AMZN.MX","ALUN.MX","AIG.MX","ABBN.MX","AA.MX","WU.MX","WHR.MX","V.MX","UTX.MX","ULN.MX","TWTR.MX","TSO.MX","TSLA.MX","TRV.MX","TMN.MX","TIN.MX","TGT.MX","TEVAN.MX","SYTN.MX","STT.MX","SNDK.MX","RGC.MX","PUKN.MX","PLD.MX","PHM.MX","PFE.MX","PBRN.MX","MU.MX","MS.MX","MON.MX","MO.MX","MGM.MX","MELIN.MX","MCD.MX","MA.MX","LYGN.MX","IP.MX","ILMN.MX","HYUDN.MX","GS.MX","GOOGL.MX","GM.MX","GGBN.MX","FCFS.MX","EN.MX","EMR.MX","EBAY.MX","DLTR.MX","DISH.MX","CVX.MX","CPLN.MX","COP.MX","CL.MX","CHK.MX","CBPX.MX","CAR.MX","BSBRN.MX","BRFSN.MX","BMY.MX","BBDN.MX","AZNN.MX","AXP.MX","AMGN.MX","VRXN.MX","VASCONI.MX","BOLSAA.MX","BBDBN.MX","VPKN.MX","SAVBMX1B.MX","BBVA.MX","SLN.MX","VESTA.MX","DGN.MX","BOKAN.MX","WMT.MX","WFTN.MX","WINN.MX","WEIRN.MX","WRLD.MX","AXTELCPO.MX","XLNX.MX","AGNN.MX","MCMN.MX","YOKUN.MX","BMEN.MX","YPFN.MX","GRAMN.MX","YGEN.MX","RYAN.MX","ZINCQ.MX","JMATN.MX","AAL.MX","AAUN.MX","ABT.MX","ABEVN.MX","ABXN.MX","0R87N.MX","ABBV.MX","ABI.MX","ACI.MX","ACCN.MX","ACOFN.MX","ACTIPATB.MX","ACTIPATA.MX","ACHN.MX","ACTINVRB.MX","AC.MX","FIBRAHD15.MX","ACXN.MX","HISN.MX","ACCELSAB.MX","ACNN.MX","ACTIPATFF.MX","ADM.MX","ADBE.MX","FPAFYN.MX","EDUN.MX","SHPGN.MX","CRHN.MX","CEON.MX","STON.MX","ADSN.MX","SIMON.MX","MRN.MX","CHTN.MX","CTRPN.MX","LFCN.MX","PNGAYN.MX","DRDN.MX","LKODN.MX","AEGN.MX","NBGGYN.MX","CNCON.MX","VIPSN.MX","JKSN.MX","TCEHYN.MX","CCUN.MX","CHUN.MX","ECN.MX","BAKN.MX","ORANN.MX","ARMHN.MX","ASXN.MX","VIVN.MX","JASON.MX","PBRAN.MX","OIBRN.MX","ENIN.MX","HQCLN.MX","NTTN.MX","NTESN.MX","SPILN.MX","SNPN.MX","SOLN.MX","TSLN.MX","KBN.MX","SSLN.MX","SBSN.MX","MTXN.MX","GAPB.MX","AEROMEX.MX","DBN.MX","AGUA.MX","AGKN.MX","AGLN.MX","AGNC.MX","CSN.MX","DAIN.MX","UBSN.MX","AHN.MX","DAL.MX","LUV.MX","AIN.MX","JBLU.MX","ATSG.MX","GOLN.MX","AKS.MX","AKEN.MX","ALSEA.MX","ALLEN.MX","ALSN.MX","ALPEKA.MX","BABAN.MX","ALVN.MX","AMXA.MX","PASAB.MX","AMFWN.MX","APH.MX","VRSK.MX","DWA.MX","ANTM.MX","APC.MX","LLY.MX","APOL.MX","APOLO10E.MX","APPSN.MX","APA.MX","ARTCK13-2.MX","ARTCK13.MX","ARYNN.MX","ARISTOSA.MX","ARA.MX","ARCON.MX","ASMLN.MX","ASCN.MX","T.MX","EBON.MX","AVN.MX","AVP.MX","AXBN.MX","AXAN.MX","AXIAN.MX","SAN.MX","GFREGIOO.MX","BNS.MX","DANHOS13.MX","USB.MX","BACHOCOB.MX","BBRYN.MX","BCHN.MX","BEVIDESB.MX","BEVIDESA.MX","BRKB.MX","INVEXCOBE.MX","BKGN.MX","INVEXCOBF.MX","BG.MX","BHPN.MX","BIIB.MX","CBPO.MX","PAPPEL.MX","FUNO11.MX","FIHO12.MX","FIBRAPL14.MX","BKIAN.MX","BLK.MX","BLD.MX","BMWM5N.MX","NCLHN.MX","INVEXCOBM.MX","BAPN.MX","BNPN.MX","BNRN.MX","BNN.MX","DB1N.MX","WBA.MX","BOSSN.MX","BPN.MX","CST.MX","BTN.MX","BURL.MX","BVNN.MX","IBM.MX","BXLT.MX","PROCORPA.MX","TCPTFN.MX","PROCORPB.MX","CBDN.MX","CBKN.MX","CC.MX","CCRN.MX","CDIN.MX","CERAMICB.MX","CLNXN.MX","CELG.MX","FBRN.MX","CERAMICD.MX","GCC.MX","FOX.MX","CFHSN.MX","CFRIN.MX","CGGN.MX","DOW.MX","LISPN.MX","CHS.MX","SCHW.MX","ROGN.MX","CIDMEGA.MX","CIEB.MX","KSU.MX","CTXS.MX","CIEAN.MX","HCITY.MX","CIGN.MX","FSHOP13.MX","TERRA13.MX","KIMBERB.MX","KIMBERA.MX","CLF.MX","CMRB.MX","CMCSA.MX","CMCN.MX","PROF-CPA1.MX","TEAKCPO.MX","LACOMERUBC.MX","LACOMERUB.MX","CPIN.MX","CPAN.MX","PROF-CPA2.MX","PROF-CPB2.MX","RCL.MX","NTE-IB1C.MX","CRM.MX","CTSH.MX","CONVERA.MX","FEMSAUB.MX","GFAMSAA.MX","VITROCPO.MX","SORIANAB.MX","SAREB.MX","EDOARDOB.MX","FINDEP.MX","COMERCIUB.MX","DINEB.MX","COMERCIUBC.MX","CABLECPO.MX","GFINBURO.MX","VITROA.MX","MAXCOMCPO.MX","MEDICAB.MX","URBI.MX","GISSAA.MX","AUTLANB.MX","SANMEXB.MX","COLLADO.MX","GPROFUT.MX","DINEA.MX","LAMOSA.MX","MINSAB.MX","MEGACPO.MX","HILASALA.MX","POCHTECB.MX","FRAGUAB.MX","CYDSASAA.MX","GFINTERO.MX","POSADASA.MX","SAB.MX","KUOB.MX","DATA.MX","DSYN.MX","DHR.MX","DD.MX","DDD.MX","FMEN.MX","DIDAN.MX","DO.MX","DEON.MX","WDC.MX","0QBON.MX","0JN9N.MX","DNOW.MX","DPWN.MX","RDYN.MX","DTEN.MX","DUFNN.MX","DVN.MX","STLD.MX","GD.MX","EBRON.MX","ECL.MX","EIN.MX","LIVEPOLC-1.MX","REEN.MX","EL.MX","ELEMENT.MX","GE.MX","SUN.MX","ELPN.MX","ERJN.MX","EMC.MX","ENELN.MX","SN.MX","ENGI.MX","EOANN.MX","ERICN.MX","CAFEN.MX","ITXN.MX","ESNTN.MX","COLN.MX","FAEN.MX","MRLN.MX","GRFPN.MX","ESRX.MX","IBEN.MX","TREN.MX","VISCN.MX","FERN.MX","MAPN.MX","TUBN.MX","POPN.MX","GCON.MX","REPSN.MX","IDRN.MX","OHLN.MX","GASN.MX","ENGN.MX","NHHN.MX","ETLN.MX","EVR.MX","HEEN.MX","PREN.MX","EXON.MX","EXC.MX","FB.MX","FFHN.MX","WFC.MX","FCAN.MX","FCX.MX","FDX.MX","RACEN.MX","FFIV.MX","FGEN.MX","FHIPO14.MX","GFMULTIO.MX","UNIFINA.MX","PNC.MX","COF.MX","FLEXN.MX","FLR.MX","FMTY14.MX","FIG.MX","WFM.MX","F.MX","FVIN.MX","MFRISCOA-1.MX","KERN.MX","TECN.MX","GLEN.MX","UGN.MX","MLN.MX","PUBN.MX","VALOFN.MX","COG.MX","GFAN.MX","GALPN.MX","PG.MX","GASIN.MX","IT.MX","KGFN.MX","FRES.MX","TSCON.MX","GBX.MX","MGGTN.MX","SMSNN.MX","GENTERA.MX","GENSEG.MX","GNW.MX","GGAN.MX","GGN.MX","GICSAB.MX","GIVNN.MX","GSKN.MX","HTZ.MX","GLW.MX","GNP.MX","GT.MX","TMMA.MX","TLEVISACPO.MX","GSANBORB-1.MX","HAL.MX","HBCN.MX","HEIN.MX","HPQ.MX","RMSN.MX","HGGN.MX","OPK.MX","HILASALB.MX","RH.MX","SCHPN.MX","HMCN.MX","HON.MX","HPE.MX","HSBCAHOA.MX","IENOVA.MX","MDTN.MX","SSYSN.MX","CALLN.MX","CHKPN.MX","IMTN.MX","IM.MX","IPON.MX","ISPN.MX","UCGN.MX","ITUBN.MX","SFLN.MX","PIAN.MX","SRGN.MX","JAVER.MX","KBR.MX","KBH.MX","KGXN.MX","KMX.MX","KPNN.MX","KSS.MX","UTSI.MX","MANUN.MX","LVS.MX","LB.MX","LEN.MX","LRN.MX","LEA.MX","LUK.MX","LMT.MX","LNKD.MX","TS.MX","LUPEN.MX","STAN.MX","MCN.MX","LYBN.MX","MPC.MX","MLM.MX","TSMN.MX","MRO.MX","MBTN.MX","MCK.MX","MUX.MX","MD.MX","MDLZ.MX","MRK.MX","MTG.MX","MGAN.MX","MSFT.MX","MKSN.MX","MKL.MX","MOS.MX","CHLN.MX","MONEXB.MX","MSI.MX","NSANYN.MX","MRWN.MX","MTUN.MX","MUV2N.MX","SITESA.MX","SBRAICP1.MX","INVEXCOA.MX","MIFIPCB.MX","INTERS2A.MX","VOLARA.MX","PE&OLES.MX","SBRAICPA2.MX","RLHA.MX","VECTMDA.MX","INTERS2M.MX","VALOR1FA.MX","INBUREXA.MX","CADUA.MX","INTERS2B.MX","SBRAICPB2.MX","INBUREXB.MX","SAVBMX1A.MX","VALUEV6B.MX","RASSINIA.MX","SPORTS.MX","VALOR3MB.MX","PV.MX","VALUEV6A.MX","RASSINICPO.MX","MIFIPCA.MX","NTE+USAA.MX","VALOR3MA.MX","VALOR1FB.MX","NOV.MX","NESNN.MX","NGN.MX","RANDN.MX","NOEJN.MX","NVON.MX","NUE.MX","INGN.MX","RYN.MX","ORLY.MX","TSUN.MX","UNP.MX","UGPN.MX","UPS.MX","PCLN.MX","PFCN.MX","PTRN.MX","PEP.MX","REGN.MX","VRTX.MX","PII.MX","PKXN.MX","PPG.MX","PSMT.MX","SEMN.MX","PYPL.MX","RDN.MX","RBN.MX","RCFN.MX","RION.MX","ROST.MX","SAPN.MX","SNYN.MX","SBUX.MX","SBRYN.MX","TMO.MX","SCTY.MX","SHW.MX","SKYN.MX","S.MX","SXSN.MX","SRE.MX","SRENN.MX","SSE.MX","SWC.MX","STZ.MX","SVU.MX","SVLCN.MX","UHRN.MX","SY1N.MX","TCKN.MX","TIF.MX","TIME.MX","TJX.MX","TXN.MX","TX.MX","TXT.MX","UNH.MX","VLO.MX","VRTV.MX","VZ.MX","VODN.MX","VOW3N.MX","WRK.MX","WTBN.MX","WITN.MX","WYNN.MX","ADPN.MX","BASN.MX","BAX.MX","BAYNN.MX","CAJN.MX","CNEN.MX","CAN.MX","CAT.MX","COO.MX","FRC.MX","FISV.MX","TRN.MX","INTU.MX","LINN.MX","M.MX","MAS.MX","MET.MX","PLL.MX","TEFN.MX","INCHN.MX"]

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
