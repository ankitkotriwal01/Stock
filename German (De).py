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
    available_tickers = ["ADS.DE","BAYN.DE","DAI.DE","WDI.DE","ALV.DE","LO3.DE","IVX.DE","RSTA.DE","VWS.DE","RKET.DE","NOEJ.DE","LSPN.DE","BVB.DE","SAZ.DE","SAPA.DE","RAD.DE","PNE3.DE","OSR.DE","O4B.DE","NDX1.DE","M6YA.DE","KSB.DE","KD8.DE","K1R.DE","G1A.DE","ERCA.DE","COP.DE","SKYD.DE","BAYA.DE","ARRB.DE","AP2.DE","AHLA.DE","ABJ.DE","AAD.DE","BMW.DE","BAS.DE","DBK.DE","DB1.DE","TGR.DE","BKN.DE","BEI.DE","VOW3.DE","SAP.DE","RWE.DE","SIE.DE","DTE.DE","VOW.DE","CON.DE","LHA.DE","HEN3.DE","FME.DE","DRI.DE","SDF.DE","MUV2.DE","HEI.DE","DPW.DE","YSN.DE","TTK.DE","TEG.DE","MOR.DE","MAN.DE","FRE.DE","FIE.DE","EOAN.DE","CBK.DE","VOS.DE","TKA.DE","SZU.DE","SZG.DE","SGL.DE","QSC.DE","PSM.DE","MRK.DE","LIN.DE","LEO.DE","KBC.DE","IS7.DE","CXU.DE","BPE.DE","BMW3.DE","ZAL.DE","WUG3.DE","VT9.DE","VIB3.DE","TUI1.DE","TFA.DE","T5O.DE","STO3.DE","SNG.DE","SMHN.DE","SIX2.DE","S92.DE","PRA.DE","RWE3.DE","RAA.DE","R6C3.DE","QYM.DE","PSAN.DE","PDA.DE","PAH3.DE","NEM.DE","NDA.DE","MTX.DE","MLP.DE","MLL.DE","MHH.DE","MAK.DE","LPK.DE","KU2.DE","KGX.DE","KCO.DE","JUN3.DE","IVU.DE","ISH2.DE","HHFA.DE","HEN.DE","HDI.DE","HAB.DE","GXI.DE","GMM.DE","FRA.DE","FNTN.DE","EVK.DE","EVD.DE","EV4.DE","ECK.DE","DWNI.DE","DTEA.DE","DIC.DE","DEZ.DE","DAR.DE","CSH.DE","COM.DE","COK.DE","CEA.DE","CE2.DE","BIO3.DE","BAF.DE","AR4.DE","AM3D.DE","4DS.DE","1PL.DE","ZO1.DE","ZIL2.DE","WUG.DE","WGF1.DE","VVV1.DE","V6C.DE","V3V.DE","V3S.DE","UTDI.DE","TTI.DE","TPN.DE","TLX.DE","TLG.DE","SZZ.DE","SYT.DE","SY1.DE","SWA.DE","SPM.DE","SLT.DE","SIS.DE","SHWK.DE","SHA.DE","SCE.DE","SAX.DE","RO5K.DE","RIB.DE","RHK.DE","R6C1.DE","R6C.DE","QB7.DE","PNG.DE","PS4.DE","PMOX.DE","PGN.DE","PFV.DE","P4O.DE","P1Z.DE","O2D.DE","NXU.DE","NXI.DE","NWX.DE","NSU.DE","NNS.DE","NN6.DE","N7G.DE","MXH.DE","MVV1.DE","MUM.DE","MU4.DE","MPCK.DE","MF6.DE","MEO.DE","MBQ.DE","MBB.DE","MAN3.DE","M5Z.DE","M3V.DE","LXS.DE","LNSX.DE","L1OA.DE","KWS.DE","KWG.DE","KRN.DE","JEN.DE","IXX.DE","ITN.DE","ISR.DE","INH.DE","IFX.DE","I7N.DE","HNL.DE","HLAG.DE","HDD.DE","HAW.DE","H2FA.DE","GWI1.DE","GSC1.DE","GLJ.DE","GIL.DE","GBF.DE","FVI.DE","FPH.DE","FPE3.DE","FPE.DE","ETG.DE","ERMK.DE","EBK.DE","E8X.DE","ENI1.DE","SSU.DE","GTQ1.DE","ERCB.DE","ENL.DE","BSD2.DE","RITN.DE","FOO.DE","FB2A.DE","WFM.DE","RIO1.DE","ZFIN.DE","RYS2.DE","HYU.DE","O5H.DE","BOSA.DE","ZJS1.DE","VODI.DE","TIM.DE","SLW.DE","RHO5.DE","RHO.DE","CNN1.DE","CMC.DE","TOM.DE","A8A.DE","8GC.DE","S7E.DE","SFT.DE","KNIA.DE","FMEA.DE","7KT.DE","2KD.DE","17E.DE","KA8.DE","SIEB.DE","TL0.DE","QIA.DE","NFC.DE","NOTA.DE","NOT.DE","NKE.DE","NESR.DE","APM.DE","OS3.DE","OKL.DE","OBH.DE","NOVA.DE","NGLB.DE","NESM.DE","O2C.DE","OUTA.DE","O5G.DE","LUK.DE","BIR.DE","B7J.DE","AOX.DE","ADV.DE","VVV3.DE","BSU.DE","QCI.DE","RSI.DE","T6UN.DE","SR9.DE","RWEA.DE","WHR.DE","VOW5.DE","LIN1.DE","GIS.DE","CNNA.DE","CHV.DE","CG3.DE","BAC.DE","ALVA.DE","ADM.DE","ZFI1.DE","UBRA.DE","VOW4.DE","UTC1.DE","UNP.DE","TATB.DE","TQIA.DE","TOMA.DE","TNE2.DE","TEV.DE","SWN.DE","SSK.DE","SRB.DE","SNW2.DE","RIOA.DE","REPA.DE","PRG.DE","PEP.DE","PCE1.DE","MUVB.DE","MMM.DE","LLY.DE","LLD2.DE","INP.DE","IDP.DE","HNRB.DE","HCL.DE","HBC2.DE","GS7A.DE","GRM.DE","GOS.DE","FMC1.DE","FDX.DE","EVTA.DE","DNQA.DE","DAP.DE","BRM.DE","BNPH.DE","BMWA.DE","BHU.DE","AXP.DE","ARRC.DE","WSV2.DE","VWA.DE","VSJ.DE","VIH.DE","EIN3.DE","DRW3.DE","VBH.DE","BBVA.DE","VAS.DE","OEWA.DE","VNX.DE","WOPA.DE","WIB.DE","BW6.DE","WFT.DE","WDL.DE","WCH.DE","MWB.DE","WIG1.DE","WUW.DE","PEH.DE","WEG1.DE","WSU.DE","NWT.DE","W8A.DE","WBAG.DE","WSOK.DE","4WM.DE","XMY.DE","XAE2.DE","O1BC.DE","XNH.DE","RNY.DE","IU2.DE","0YYA.DE","YCP.DE","YP1B.DE","OCI1.DE","RY4C.DE","YOC.DE","ZSB.DE","ZEG.DE","ZCT1.DE","FZM.DE","AFX.DE","ZM5N.DE","ZZMS.DE","EDGA.DE","ZM5.DE","EUZ.DE","Z1L.DE","ZEF.DE","6GX.DE","AAQ.DE","AAGN.DE","ARL.DE","MAC1.DE","HMSB.DE","ABR.DE","ABL.DE","ABA.DE","AB1.DE","ABEC.DE","TRIG.DE","SCA.DE","SWM.DE","4AB.DE","ABJA.DE","BWJ.DE","ACWN.DE","ACX.DE","E7S.DE","AJ3.DE","ACT.DE","ACP.DE","FLN.DE","APE.DE","ADN1.DE","ADL.DE","ADI1.DE","ADD.DE","TOTA.DE","ADS1.DE","IFXA.DE","BHP.DE","NOAA.DE","GAZ.DE","AENF.DE","AEI.DE","AEC1.DE","AFO1.DE","1AF.DE","L60.DE","DLX.DE","D6H.DE","CSY.DE","CRZ.DE","COR.DE","CLS1.DE","C8I.DE","C1V.DE","BST.DE","BOSS.DE","BNT1.DE","B8A.DE","AV7.DE","AUS.DE","AJ91.DE","AIXA.DE","A6T.DE","93M.DE","63DA.DE","5AB.DE","2GB.DE","02P.DE","LHAB.DE","DEX.DE","SCUN.DE","DRW8.DE","PT8.DE","H9W.DE","E4C.DE","BNR.DE","IMO.DE","M3B.DE","IS8.DE","KB7.DE","FYB.DE","UP7.DE","TIN.DE","CY1.DE","0UB.DE","G6P.DE","SWVK.DE","PQL.DE","OMV.DE","SANT.DE","DBAN.DE","DR0.DE","VSC.DE","BCLN.DE","CEW3.DE","DKG.DE","F3C.DE","RSL2.DE","G24.DE","S4A.DE","MCE.DE","RHO6.DE","HP3.DE","INW1.DE","PXL.DE","T3T1.DE","US5.DE","ART.DE","SUL1.DE","S4K.DE","BLON.DE","UHRN.DE","HYQ.DE","SK1A.DE","EMQ.DE","LSPP.DE","HWSA.DE","RAW.DE","HMU.DE","CY1K.DE","VROS.DE","VBHK.DE","NTG.DE","VBK.DE","BBZA.DE","SWJ.DE","GFIN.DE","TC1.DE","O3P.DE","VG8.DE","8S9.DE","GTK.DE","DPWA.DE","FGT.DE","PZS.DE","A1G.DE","HEIU.DE","ARO.DE","N2F.DE","HBH.DE","EBO.DE","SCO.DE","MNSN.DE","1COV.DE","G2A.DE","N1M.DE","M12.DE","B7E.DE","UHR.DE","HG1.DE","H5E.DE","M7U.DE","HRPK.DE","DAIC.DE","AU2.DE","A7A.DE","0NF.DE","B8F.DE","UHRA.DE","B5SK.DE","ECF.DE","GKS.DE","BWB.DE","WL6.DE","IFXN.DE","A5A.DE","WAF.DE","GBRA.DE","RCMN.DE","ALG.DE","CU1.DE","GRF.DE","CFC.DE","F2Y.DE","SMNK.DE","R1T.DE","AGJ.DE","DMRE.DE","FMEN.DE","D7S.DE","BWO.DE","T3T.DE","PBY.DE","FO4N.DE","T1L.DE","IFM.DE","AGE.DE","LO24.DE","ELB.DE","DWNN.DE","PHBN.DE","TUIJ.DE","KSC.DE","V33.DE","NC5A.DE","IWB.DE","SLL.DE","BEIA.DE","MSGL.DE","SMWN.DE","HXCK.DE","LIO1.DE","MUX.DE","BNN.DE","FLA.DE","KCC.DE","PBB.DE","3VZ1.DE","TTR1.DE","H9O1.DE","AZ2.DE","MDG1.DE","CNWK.DE","S3F.DE","SW1.DE","H8K.DE","SFD1.DE","M4N.DE","IKH.DE","PAL.DE","EMH1.DE","WL6J.DE","IC8.DE","MA1.DE","AHG1.DE","AIXB.DE","AIRA.DE","AIR.DE","AINN.DE","B5A.DE","SRT.DE","EUCA.DE","LUS.DE","H2R.DE","SRT3.DE","KSB3.DE","WINA.DE","ATF.DE","E2Z.DE","6LLN.DE","ANO.DE","CGEA.DE","1AG.DE","CGE.DE","ALU.DE","A1OS.DE","PA2.DE","AWC.DE","AMG.DE","BMT.DE","NGLD.DE","A8B.DE","SCL.DE","ITK.DE","FKR.DE","AOF.DE","RYA.DE","7AA.DE","OAL.DE","ARMA.DE","ERT.DE","U9R.DE","ARM.DE","BOY.DE","AT1.DE","ASG.DE","NK1A.DE","NOH1.DE","3P7.DE","ASMF.DE","FOH.DE","PND.DE","SOBA.DE","UP2.DE","SAC.DE","BFC.DE","FAA.DE","PV3.DE","CRA1.DE","CBA.DE","BHP1.DE","1CB.DE","FMK.DE","NHY.DE","EDO.DE","SPR.DE","AXAA.DE","AXA.DE","AZU.DE","LLD.DE","DTD2.DE","BYW6.DE","BPG.DE","BYW.DE","BSP.DE","BC8.DE","BCY.DE","BCY2.DE","BDT.DE","MOS.DE","BX7.DE","3RB.DE","WCMK.DE","BEZ.DE","USE.DE","NBG6.DE","BRH.DE","SVE.DE","BIL.DE","BIL1.DE","BIJ.DE","BTI.DE","BRB.DE","BIO.DE","BIW.DE","SBS.DE","BLQA.DE","S9A.DE","BTBA.DE","BMSA.DE","CLTV.DE","BPE5.DE","BRW1.DE","BSL.DE","BSDK.DE","BSND.DE","BTQ.DE","BTQA.DE","BTL.DE","P2G1.DE","BY6.DE","BY6A.DE","SMK.DE","PNX.DE","GR9.DE","CVC1.DE","CAP.DE","C3H1.DE","MHN2.DE","IWI.DE","GO5.DE","P01.DE","KIN2.DE","CBHD.DE","CWC.DE","RY8.DE","CEV.DE","CJ5A.DE","LTEC.DE","HLG.DE","GIN.DE","ED4.DE","CHL.DE","CTMA.DE","CSX.DE","GYC.DE","CLIQ.DE","CLRN.DE","CM3.DE","CMAB.DE","PC6.DE","CSX1.DE","CRIH.DE","CTM.DE","CUR.DE","CWW.DE","DAM.DE","C2U1.DE","3G8A.DE","9VD.DE","DCH1.DE","DCO.DE","DUE.DE","DIE.DE","DEQ.DE","DPB.DE","SIX3.DE","PA8.DE","WIN.DE","VNA.DE","STE.DE","GGS.DE","TFGC.DE","DGR.DE","DLG.DE","WDP.DE","IXD1.DE","2P6.DE","DIS.DE","GUI.DE","NOVC.DE","DNQ.DE","EFF.DE","R6C2.DE","DWD.DE","ESY.DE","EBA.DE","ECX.DE","EDL.DE","EDG.DE","EE1.DE","LEG.DE","EKT.DE","SSUN.DE","EWI.DE","ELG.DE","FEV.DE","ENLA.DE","EMP.DE","ENUR.DE","2HP.DE","EOAA.DE","MT4.DE","HPBK.DE","EQS.DE","ERCG.DE","2EM.DE","ERO1.DE","TNE5.DE","IBE1.DE","FV01.DE","ENA.DE","GAN.DE","KBU.DE","POPD.DE","REP.DE","EVT.DE","EXC.DE","2TN.DE","FAO2.DE","FRU.DE","2FE.DE","FOT.DE","FMV.DE","RPL.DE","FRS.DE","HO7.DE","FPMB.DE","FREA.DE","GOB.DE","FTE1.DE","TCO.DE","PES.DE","HBC1.DE","GS7.DE","TFGB.DE","2IV.DE","SGE1.DE","GHH.DE","GME.DE","GFT.DE","GFK.DE","GHG.DE","GLW.DE","GM2.DE","5G5.DE","INN.DE","GSJ.DE","6GI.DE","HAR.DE","HAE.DE","HAL.DE","HNR1.DE","HBM.DE","HLE.DE","HEZ.DE","KHNZ.DE","LHL.DE","MYRK.DE","HLBN.DE","7HP.DE","IO0.DE","2M6.DE","IES.DE","RY4B.DE","ITB.DE","I3M.DE","ITA.DE","TQIR.DE","PIL3.DE","P4I.DE","MDS.DE","ENI.DE","TQI1.DE","PIL2.DE","TQI.DE","URH.DE","KEL.DE","KMY.DE","KPNB.DE","SKB.DE","KSW.DE","KTF.DE","NNND.DE","ULC.DE","TLA.DE","LHL1.DE","LEI.DE","RNP.DE","2NY1.DE","LKI.DE","TGH.DE","LOM.DE","LSX.DE","RRTL.DE","SFQ.DE","3W9K.DE","SEN.DE","ADJ.DE","M4I.DE","MTT.DE","MZX.DE","MT3.DE","MBK.DE","MDN.DE","MEO3.DE","RNM.DE","MED.DE","NMK.DE","MGN.DE","WELA.DE","UMD.DE","MZP.DE","4I1.DE","S5GM.DE","MSAG.DE","MUB.DE","NNGE.DE","WAC.DE","SNH.DE","37C.DE","2FI.DE","8GV.DE","NNN1.DE","UNIN.DE","PHIA.DE","OBS.DE","OPC.DE","POC.DE","SBNC.DE","RYS1.DE","OHB.DE","OSP2.DE","PPA.DE","UPAB.DE","PC6A.DE","WOP.DE","R66.DE","PXLX.DE","TCG.DE","PWO.DE","PV3A.DE","PUM.DE","TPE.DE","RHM.DE","RTC.DE","SAG.DE","SHF.DE","SDF1.DE","SD1.DE","MANC.DE","SFO.DE","SFTU.DE","SII.DE","SOW.DE","0TS.DE","99SC.DE","VODJ.DE","SR9A.DE","ST5.DE","SYK.DE","SUR.DE","SVJ.DE","SYZ.DE","VWSA.DE","TGT.DE","T3W1.DE","17T.DE","TLI.DE","TWR.DE","UNH.DE","UZU.DE","UUU.DE","V1RA.DE","VFP.DE","3V64.DE","5WP.DE","B1C.DE","BASA.DE","BMM.DE","C2Z.DE","E4U.DE","M11.DE","5FB.DE","INNA.DE","HOT.DE","2PP.DE","0RY.DE","R9G2.DE"]

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
