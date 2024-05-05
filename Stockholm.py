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
    available_tickers = ["WIHL.ST","VOLV-B.ST","SCA-A.ST","SAS.ST","REZT.ST","PACT.ST","LUND-B.ST","HLDX.ST","ECEX.ST","CLAS-B.ST","BILL.ST","BBTO-B.ST","AXFO.ST","XANO-B.ST","SAND.ST","MQ.ST","LUPE.ST","KINV-B.ST","DUNI.ST","BEIJ-B.ST","VBG-B.ST","SKA-B.ST","SAAB-B.ST","RUSF.ST","NOTE.ST","NOMI.ST","NIBE-B.ST","LIAB.ST","JM.ST","ITAB-B.ST","HUSQ-B.ST","HEXA-B.ST","FEEL.ST","COIC.ST","BMAX.ST","BEIA-B.ST","ASSA-B.ST","AF-B.ST","ZZ-B.ST","SVED-B.ST","SEAM.ST","ODLO.ST","MEDF.ST","KDEV.ST","ETX.ST","ERICB.ST","ERIC-B.ST","EPIS-B.ST","ENRO.ST","ELAN-B.ST","BELE.ST","FPIP.ST","FIRE.ST","FING-B.ST","BALD-B.ST","SENS.ST","HM-B.ST","RECY-B.ST","NMAN.ST","AZA.ST","SIVE.ST","IJ.ST","KNOW.ST","KARO.ST","KOPY.ST","KAMBI.ST","KAHL.ST","KLIC-B.ST","KLOV-PREF.ST","MOB.ST","MEDA-A.ST","QFRO.ST","NOLA-B.ST","NCC-B.ST","AKSOO.ST","WWASAO.ST","WEIFAO.ST","SSOO.ST","SKBNO.ST","ORI.ST","NSP-B.ST","NRSO.ST","NOVE.ST","NOKI.ST","NODO.ST","NN-B.ST","NGQ.ST","NET-B.ST","ORX.ST","OPCO.ST","STE-R.ST","STE-A.ST","SOBI.ST","SAVOS.ST","OS.ST","OEM-B.ST","ODD.ST","LUCE.ST","FOI-B.ST","AOI.ST","OP-PREF.ST","GOIL-PREF.ST","QLRO.ST","QUICK.ST","QBNK.ST","PAR.ST","TREL-B.ST","TOBII.ST","TLSN.ST","TEL2B.ST","TEL2-B.ST","UFLX-B.ST","UNIB-SDB.ST","PFE.ST","VITR.ST","VOLV-A.ST","ELV.ST","EOLU-B.ST","FLNGO.ST","VNIL-SDB.ST","NEVI-B.ST","VVLO.ST","VICP-B.ST","VERI.ST","VNV-SDB.ST","NILS.ST","STVA-B.ST","WESC.ST","WALL-B.ST","WISE.ST","WILSO.ST","NEWA-B.ST","WRLO.ST","XVIVO.ST","XINT.ST","XXLO.ST","XTRA.ST","XBRANE.ST","63649.ST","OCYO.ST","YILD-B.ST","ZETA.ST","ZALO.ST","ZENZIP.ST","ZENI.ST","AAK.ST","AAP-B.ST","SWOL-B.ST","SEMC.ST","PROB.ST","LOOM-B.ST","LATO-B.ST","INDT.ST","ICA.ST","IAR-B.ST","GUNN.ST","GENI.ST","CTT.ST","CATE.ST","BOL.ST","BEGR.ST","AXIS.ST","ARCM.ST","ANOT.ST","ALFA.ST","ACTI.ST","ABB.ST","TRMO.ST","TRAN-B.ST","TEL2-A.ST","TAGM-B.ST","SYSR.ST","SWEC-B.ST","SWEC-A.ST","SVOL-B.ST","SSAB-B.ST","SSAB-A.ST","SOF-B.ST","SKF-B.ST","SINT.ST","SECU-B.ST","SEB-A.ST","SEAB-B.ST","RROS.ST","RNBS.ST","PRCO-B.ST","PEAB-B.ST","PCELL.ST","NDA-SEK.ST","NCC-A.ST","NAXS.ST","MSON-A.ST","MSC-B.ST","MPEN.ST","MISE.ST","MIDW-A.ST","MELK.ST","MEKO.ST","MCAP.ST","MAV.ST","LIFCO-B.ST","IVISYS.ST","INVE-B.ST","INSP.ST","IMMU.ST","IFS-A.ST","IFOX.ST","HUFV-C.ST","HTRO.ST","HMS.ST","HMED.ST","HMB.ST","HIFA-B.ST","HEMF.ST","GRNG.ST","GHUS-B.ST","GETI-B.ST","GENO.ST","FXI.ST","FPAR.ST","EWRK.ST","ENDO.ST","ELUX-A.ST","ELTEL.ST","ELOS-B.ST","ELN.ST","EKTA-B.ST","EFFN.ST","DOM.ST","DMYD-B.ST","DIGN.ST","DIAH.ST","DEFL-B.ST","CRAD-B.ST","CORE.ST","CONS-B.ST","CONF.ST","COMH.ST","CLA-B.ST","CI-B.ST","CCOR-B.ST","CBA.ST","CAT-A.ST","CAST.ST","CAPIO.ST","BRG-B.ST","BRE2.ST","BRAV.ST","BORG.ST","BIOT.ST","BINV.ST","BILI-A.ST","BETS-B.ST","BAHN-B.ST","ATCO-B.ST","ATCO-A.ST","ASCO.ST","AQER.ST","ALIG.ST","AGIS.ST","SKIS-B.ST","ARCOMA.ST","ADVE.ST","ICTA-B.ST","BWL.ST","SPRINT.ST","SPAG.ST","NOVU.ST","AQ.ST","KONT.ST","ECC.ST","TROAX.ST","SANION.ST","PETRO.ST","SEAL.ST","PART.ST","ALZ.ST","ME.ST","HEMF-PREF.ST","MAT.ST","HEBA-B.ST","KARE.ST","APTA.ST","HIQ.ST","ECO-B.ST","MVIR-B.ST","AGES-B.ST","MAXK.ST","MYFC.ST","LAGR-B.ST","CLX.ST","RAIL.ST","OASM.ST","MIR.ST","CASO.ST","BURE.ST","ADDT-B.ST","SEZI.ST","SWED-A.ST","POLY.ST","INVE-A.ST","PROF-B.ST","DORO.ST","SHOT.ST","AMNO.ST","CBTT-B.ST","PLUN.ST","RESP.ST","HQ.ST","PMED.ST","VRG-B.ST","HOFI.ST","EURI-B.ST","SAFE.ST","RAY-B.ST","CLAV.ST","LEX.ST","TETY.ST","FPAR-PREF.ST","GABA.ST","PRIME.ST","ENVI-B.ST","CLS-B.ST","PFAM.ST","ORES.ST","SLEEP.ST","POLYG.ST","CAPAC.ST","GENE.ST","MSAB-B.ST","KAN.ST","MANG.ST","OPUS.ST","DEDI.ST","SAGA-A.ST","KLOV-B.ST","RATO-A.ST","AXON.ST","CINN.ST","PREV-B.ST","PALS-B.ST","SJR-B.ST","NTEK-B.ST","DENT.ST","HANZA.ST","USE-B.ST","NUE.ST","BAYN.ST","KLAR.ST","SKF-A.ST","OPTI.ST","COMBI.ST","MPOS.ST","TOURN.ST","TRI.ST","AROC.ST","RATO-B.ST","SF.ST","NVP.ST","SCST.ST","SEB-C.ST","TRAN-A.ST","ATT.ST","IMPC.ST","DGC.ST","LIDDS.ST","SKMO.ST","DELARK.ST","MULQ.ST","TCT.ST","CAMX.ST","BOTX.ST","OV.ST","HOME-B.ST","MTG-A.ST","SVIK.ST","SPOR.ST","ROOT.ST","EUCI.ST","AMBI.ST","ORTI-B.ST","ORE.ST","NANEXA.ST","LAMM-B.ST","RECI-B.ST","DIOS.ST","CHER-B.ST","BUFAB.ST","BRIG.ST","HELIO.ST","AXIC-A.ST","ALON-B.ST","SYNT.ST","KLOV-A.ST","AMH2-B.ST","CANTA.ST","GWS.ST","ALTE.ST","BIM.ST","NFO.ST","SAGA-B.ST","ORTI-A.ST","ORT-B.ST","HUFV-A.ST","SAPIAB.ST","DEMI-B.ST","SAS-PREF.ST","SES.ST","INWI.ST","BTS-B.ST","CEFO-B.ST","SAGA-PREF.ST","SBOK.ST","AKEL-PREF.ST","CAPE.ST","DRIL.ST","AMAST-PREF.ST","BOUL.ST","PLED.ST","COOR.ST","PHAL.ST","MODI.ST","AVT-B.ST","JLT.ST","MTG-B.ST","HUM.ST","WTG.ST","HAV-B.ST","NOBI.ST","LATF-B.ST","STIL.ST","GHP.ST","NP3.ST","GOIL.ST","DOXA.ST","PARA.ST","RAST.ST","TEONE.ST","JOSA.ST","CSEC.ST","PCOM-B.ST","AXAO.ST","FOLLI.ST","NNH.ST","EMP-B.ST","EMOT.ST","THULE.ST","ABSO.ST","BACTI-B.ST","PB.ST","AVEN.ST","WAYS.ST","AVEG-B.ST","REDS.ST","AXON-BTA.ST","VIT-B.ST","NICO.ST","WNT.ST","MROX-B.ST","IS.ST","ELEC.ST","IDL-B.ST","FNMA-PREF.ST","ACM.ST","IFS-B.ST","GCOR.ST","NOCH.ST","SPIFFX.ST","INTU.ST","FOUT.ST","KAPIAB.ST","TIKS.ST","HEGR.ST","DEX.ST","ONG.ST","BONG.ST","GARO.ST","REJL-B.ST","ECOM.ST","ALM-PREF.ST","CTEC.ST","RATO-PREF.ST","ENRO-PREF.ST","PREC.ST","BESQ.ST","NDX.ST","MOBI.ST","OBOYA-B.ST","ENEA.ST","ABE.ST","JAYS.ST","MIND.ST","FAG.ST","EURO.ST","SWMA.ST","ABFAST-B.ST","DOME.ST","SERT.ST","VSEC.ST","CAMP.ST","POOL-B.ST","SVOL-A.ST","NETI-B.ST","MEAB-B.ST","RLS.ST","TRAC-B.ST","VIG.ST","MROX-A.ST","MACK-B.ST","BIOG-B.ST","HUSQ-A.ST","SPEC.ST","DIST.ST","COLL.ST","ARCT.ST","SPIRA.ST","IMMNOV.ST","ORGC.ST","NEXAM.ST","MSON-B.ST","CRED-A.ST","VIVO.ST","EVO.ST","VICP-PREF.ST","ACRI.ST","CLBIO.ST","DUST.ST","SDOS.ST","KENH.ST","TRANS.ST","MEDR-B.ST","SCIB.ST","ALPH.ST","IPL.ST","CHAL-B.ST","SHEL-B.ST","DURC-B.ST","IVSO.ST","CEAB.ST","WIFOG.ST","HOVD.ST","CORE-PREF.ST","TRUE-B.ST","WINT.ST","CEVI.ST","ALM.ST","ELUX-B.ST","HYCO.ST","PHI.ST","AHA.ST","NICA.ST","ODEN.ST","HAMLET.ST","MRG.ST","EQL.ST","DMAB-B.ST","TWW.ST","RTIM-B.ST","MAG.ST","AMAST.ST","TOL.ST","PIL.ST","IDOGEN.ST","NOBINA.ST","LOVI.ST","AJA-B.ST","OP.ST","MIDW-B.ST","CAT-B.ST","PROE-B.ST","FABG.ST","IMINT.ST","UTG.ST","TORSAB.ST","SGLD.ST","NMGO.ST","GREAT.ST","BETT.ST","AUTO.ST","GJAB.ST","PHLOG.ST","RBASE.ST","A1M.ST","KABE-B.ST","LLSW-B.ST","TRAD.ST","LINKAB.ST","TOBIN-PREF.ST","PREBON.ST","ABI.ST","BULTEN.ST","VICO.ST","BALD-PREF.ST","ENZY.ST","SOLT.ST","ACAN-B.ST","PRIC-B.ST","PLAZ-B.ST","BRAIN.ST","STEF-B.ST","G5EN.ST","HEART.ST","LEO.ST","HPOL-B.ST","MINEST.ST","BONAS.ST","ALIF-B.ST","ANOD-B.ST","ADDV-B.ST","AFGO.ST","AGORA-PREF.ST","AGORA-B.ST","TAGR.ST","DDM.ST","88867.ST","SCA-B.ST","SECT-B.ST","HOLM-B.ST","HOLM-A.ST","AKVAO.ST","INDU-C.ST","ARP.ST","REHA-B.ST","SDET.ST","KLED.ST","INDU-A.ST","63624.ST","AKPSO.ST","63625.ST","ALIV.ST","ALNX.ST","ALLG-B.ST","ALIV-SDB.ST","ATEL-A.ST","AMSCO.ST","AMNO-TR.ST","ANGL.ST","AQUAO.ST","ARISE.ST","BONO.ST","AZN.ST","NANOO.ST","MULTIO.ST","NOMO.ST","ITXO.ST","RENOO.ST","SOFFO.ST","EIOFO.ST","GSFO.ST","AUSSO.ST","LSGO.ST","HAVIO.ST","DATO.ST","OLTO.ST","THINO.ST","SALMO.ST","WBULKO.ST","PSIO.ST","FARO.ST","EPRO.ST","PHOO.ST","NORO.ST","HNBO.ST","GODO.ST","EKOO.ST","BRGO.ST","PROTCTO.ST","PENO.ST","BLOO.ST","STORMO.ST","VARDIAO.ST","DOFO.ST","HEXO.ST","ENTRAO.ST","CAM-B.ST","IOXO.ST","NELO.ST","NEXTO.ST","VEIO.ST","KOGO.ST","RECSOLO.ST","VISTINO.ST","GROO.ST","WWIO.ST","KITO.ST","KIDO.ST","TELIOO.ST","RISHO.ST","HYARDO.ST","SBOO.ST","KVAERO.ST","PCIBO.ST","BERGENO.ST","BIONORO.ST","ASETEKO.ST","WWIBO.ST","MCGO.ST","BOUVETO.ST","SPUO.ST","BIRDO.ST","ATCOA.ST","ATLA-NOKO.ST","ATRLJ-B.ST","71200.ST","AUR.ST","AVMO.ST","AVANCEO.ST","AWDRO.ST","AXIC-TR-A.ST","IBT-B.ST","NDA.ST","BEO-SDB.ST","KARO-TR.ST","BIOTECO.ST","BIGG-B.ST","HBCO.ST","PXXS-SDB.ST","BEF-SDB.ST","JINO.ST","SNIO.ST","GOGLO.ST","NOFO.ST","BWOO.ST","HLNGO.ST","DBP-B.ST","BRIN-B.ST","OBAB.ST","SNM.ST","SMF.ST","67272.ST","CCC.ST","CE.ST","MIC-SDB.ST","SCAB.ST","CLS-TR-B.ST","CLS-BTA-B.ST","CLINE-B.ST","CTM.ST","DESSCO.ST","CYBE.ST","PDRO.ST","SBXO.ST","DCAR-B.ST","LUC.ST","NAPAO.ST","PCAT.ST","63626.ST","SEVDRO.ST","EASY-B.ST","ELUXB.ST","88833.ST","VEMF-SDB.ST","ENQ.ST","EOS.ST","ERIC-A.ST","NETG.ST","EVERY-A.ST","STER.ST","NXTMS.ST","NOKIA-SEK.ST","NFAB.ST","FOOT-PREF.ST","81268.ST","STWK.ST","BAKKAO.ST","FROO.ST","SLOTT-B.ST","SLOTT-A.ST","FUNCOMO.ST","NIOO.ST","OLDM.ST","GETIB.ST","63648.ST","GPG-PREF.ST","63635.ST","RLS-TR.ST","RLS-BTA.ST","LUG.ST","GOGL-RO.ST","KOPY-BTA-1.ST","SHBA.ST","63631.ST","HANC-PREF-A.ST","SHB-B.ST","SHB-A.ST","HEIM-PREF.ST","HTRO-BTA.ST","SIVE-BTA.ST","SIVE-TR.ST","HUBR-B.ST","HUSQB.ST","63632.ST","IDEXO.ST","IS-BTA.ST","IMS.ST","IMNP.ST","ITAL-SDB.ST","JOJK.ST","KINV-A.ST","KINB.ST","K2A-PREF.ST","89289.ST","SIOFFO.ST","NLAB.ST","LUXO-SDB.ST","LUMI-SDB.ST","TAGM-BTA-B.ST","TILO.ST","MIR-BTA.ST","DEMI-BTA-B.ST","MTGB.ST","MUNK1S.ST","MYCR.ST","NATTO.ST","NAVAO.ST","NJOB.ST","NIL-B.ST","NICO-BTA.ST","63637.ST","OTSO.ST","ODFO.ST","88790.ST","63640.ST","75076.ST","NORTHO.ST","63642.ST","63647.ST","63634.ST","71203.ST","110075.ST","PPG-PREFO.ST","TTSO.ST","REACHO.ST","63644.ST","ODFBO.ST","88881.ST","SRBANKO.ST","SCIO.ST","OASM-BTA.ST","ORT-TR-B.ST","ORT-BTA-B.ST","PAPI.ST","PNDX-B.ST","VICP-A.ST","RAKPO.ST","PEXA-B.ST","PEGRO-PREF.ST","PMED-BTA.ST","PMED-TR.ST","TETY-IL.ST","PIL-BTA.ST","PIL-TR.ST","PLED-BTA.ST","PLUN-BTA.ST","VOLO-PREF.ST","PRIME-PREF-B.ST","RHOVAC.ST","DEFL-TR-B.ST","TAGM-TR-B.ST","SAVOS-TR.ST","MIR-TR.ST","WESC-TR.ST","PLED-TR.ST","RXS-PREF.ST","SDOS-BTA.ST","SCC-B.ST","SDIP-PREF.ST","SWEDA.ST","SKAB.ST","SKFB.ST","SNTC.ST","SSABA.ST","STORY-B.ST","VSSAB-B.ST","TAUR-B.ST","TBDY.ST","TIEN.ST","TRELB.ST","TWW-SDB-A.ST","VSD-B.ST","VOLVB.ST","203.ST","WESC-BTA.ST","TWW-SDB-B.ST","ADDV-A.ST","SEBA.ST","63641.ST","COPP-B.ST","HOGK-PREF-A.ST","INISS-B.ST","INVEB.ST","PLAY.ST","SAS-NOKO.ST","SAVOS-BTA.ST","SECUB.ST","SEZI-BTA.ST","STAR-A.ST","STAR-B.ST"]

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
