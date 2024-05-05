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
    available_tickers = ["ATF.MU","WEO.MU","RDDA.MU","MOR.MU","ADV.MU","YOC.MU","XA6.MU","VFF.MU","V6C.MU","V3V.MU","UUU.MU","UMS.MU","TTO.MU","SZU.MU","SPB.MU","SOW.MU","SKB.MU","SGL.MU","SFX.MU","SED.MU","RHM.MU","QSC.MU","PAD.MU","OLG.MU","OA4.MU","NWD.MU","NTG.MU","NN6.MU","NHB.MU","N1M.MU","MXH.MU","MAK.MU","LO24.MU","LEI.MU","KUN1.MU","KUL.MU","KPH.MU","KKD.MU","KD8.MU","JOX.MU","IS8.MU","HAW.MU","GDX.MU","GBF.MU","FRA.MU","FPE.MU","EUK3.MU","ESK.MU","EBK.MU","7B7.MU","FNM.MU","XMF.MU","FDO.MU","CAJ.MU","WOO.MU","UFG.MU","ZWC1.MU","HRH.MU","2H2.MU","XCY.MU","XCI.MU","WKH.MU","V1Y.MU","TTDA.MU","TIM.MU","SHX.MU","S9Q.MU","RHI.MU","YOK.MU","XSC.MU","TOY.MU","SON1.MU","SKI.MU","SHD.MU","SH0.MU","QC9.MU","PYV.MU","OCU.MU","OCJ.MU","OBA.MU","NVP2.MU","NVAY.MU","NKO.MU","NISA.MU","NGI.MU","NF2.MU","MFZ.MU","LOO.MU","LCY.MU","LCJ.MU","KIK.MU","KHE.MU","JUS1.MU","JNP.MU","JM2.MU","JHY.MU","IQ3.MU","HDM.MU","FUJ1.MU","EAR.MU","DWH.MU","CMC.MU","ASI1.MU","7SS.MU","2JT.MU","1SK.MU","PP1.MU","NOF.MU","RL2.MU","ZOF.MU","5JP.MU","0MJA.MU","HZ4.MU","TCW.MU","EZ7A.MU","TSQ.MU","BMZ.MU","1J4.MU","MZA.MU","TAX.MU","JAK1.MU","TMI.MU","JM4A.MU","AJI.MU","SUMA.MU","MIE1.MU","SBW.MU","ASAA.MU","BKY.MU","S7E.MU","JAT.MU","DW1.MU","WFG1.MU","NFU.MU","NKN.MU","D4S.MU","FJE.MU","1RH.MU","MFU.MU","MZ8.MU","FJT.MU","PIO.MU","MH6.MU","EJR.MU","NPS.MU","WI2.MU","SFT.MU","IOC.MU","JUVE.MU","ON4.MU","EO7.MU","SWD.MU","YEC.MU","JOE.MU","JAV.MU","JAF.MU","YPH.MU","JUN3.MU","RDN.MU","JCN.MU","7NX.MU","81A.MU","VAN.MU","UMZ.MU","JIM.MU","JAW.MU","S6M.MU","NSK.MU","NEX.MU","NSC.MU","013A.MU","DNO.MU","SMM.MU","8GC.MU","0WP.MU","TKD.MU","QHH.MU","TECA.MU","ISU.MU","TDK.MU","UBE.MU","HIZ.MU","KWI.MU","CNN1.MU","CTZ.MU","59M.MU","PM6.MU","JOHB.MU","CNJ.MU","TQC.MU","PW5.MU","PGJ.MU","LCLA.MU","KYM1.MU","KT9.MU","KIO.MU","KG0A.MU","KC4.MU","K8A.MU","HOO.MU","HOA.MU","HHI.MU","CHH.MU","BGR.MU","7KT.MU","5YG.MU","1LP.MU","1HD.MU","KSC.MU","KTB1.MU","FFO1.MU","KOP.MU","TPK2.MU","HGNC.MU","34T1.MU","XPG.MU","SWC.MU","SUL1.MU","NYVT.MU","NYT.MU","NXWB.MU","NWL.MU","NVP6.MU","NGR.MU","W8V.MU","UU4.MU","OZH.MU","OMUB.MU","OCBA.MU","O3S.MU","ICA.MU","HT2.MU","7GG.MU","OC5.MU","UOF.MU","OU5.MU","SP4A.MU","KVO.MU","OHR.MU","OWW1.MU","AKY.MU","OFK.MU","WON1.MU","OSP2.MU","FAC.MU","OWX.MU","FTE.MU","ONL.MU","GQQ.MU","OA9.MU","XS4.MU","E1V.MU","QLG.MU","QIW.MU","QE1.MU","QLT.MU","NYVH.MU","QNT1.MU","QDI.MU","QU5A.MU","TYI.MU","QKS.MU","QIN.MU","V0M.MU","QNMA.MU","QHI.MU","QFSP.MU","QY6.MU","QS5.MU","QS8.MU","QG1A.MU","QSV.MU","QSN.MU","CU7.MU","QAN.MU","QIA.MU","HPR.MU","QL2.MU","QRL.MU","QJQ.MU","0QP.MU","QM0.MU","LB3A.MU","QCI.MU","2QO.MU","QR2.MU","QS2A.MU","QPMC.MU","QSU.MU","QSI.MU","Q86.MU","QCE.MU","Q9H1.MU","Q6IA.MU","QCTA.MU","RNT.MU","7BF.MU","0GT1.MU","YM1.MU","XYXR.MU","W02.MU","VQKA.MU","ZCH.MU","TZL1.MU","TCM1.MU","LKI.MU","GJ3.MU","CUM.MU","CTP2.MU","ZYA.MU","ZCHA.MU","ZAS.MU","X0M.MU","WHT.MU","WC3.MU","VX1.MU","TW6.MU","VFP.MU","VA7A.MU","UUM.MU","UUEC.MU","TUP.MU","TUL1.MU","TEY.MU","SWG.MU","SONA.MU","SGNV.MU","S9P2.MU","S46.MU","RUD.MU","RTN1.MU","RGN.MU","R42.MU","PXLX.MU","PV3A.MU","PUP.MU","PTM.MU","PP9.MU","PMGN.MU","PLO.MU","PJX.MU","PEW.MU","PE1.MU","PAX.MU","MTT.MU","NH0.MU","MS7.MU","MOB.MU","ME5A.MU","MDF.MU","M0SA.MU","LTT.MU","LTD.MU","LFA.MU","IWY1.MU","HYU.MU","HWHG.MU","HTR.MU","HS2.MU","HP5A.MU","HI9.MU","HAZ.MU","HAR.MU","GS7A.MU","GRM.MU","GOV.MU","GGRA.MU","FNZ.MU","FDU.MU","F2P.MU","ETH.MU","ESDA.MU","EI0.MU","ECJ.MU","DYH.MU","DUBA.MU","CYP.MU","CXF.MU","CX5N.MU","CUW.MU","CTV.MU","CTMA.MU","CTD.MU","CSN.MU","CG3.MU","CE7.MU","CAO.MU","BVJ.MU","BREC.MU","BOX.MU","BAC.MU","B2X.MU","AXP.MU","AX1.MU","ATN.MU","APC.MU","AOL1.MU","VEM.MU","BBP2.MU","VLON.MU","VOS.MU","VWS.MU","8SV.MU","VCX.MU","VI6.MU","VSA.MU","V7N.MU","18V.MU","WTB3.MU","VNX.MU","VTZ.MU","35V.MU","I93.MU","VEH.MU","VI9.MU","BZF1.MU","EAJD.MU","EIN3.MU","VW9.MU","VOL1.MU","SQU.MU","SV5.MU","VON.MU","W2R.MU","VOX.MU","STO3.MU","AYJ.MU","VHC.MU","7NB.MU","VWK.MU","VT9.MU","VS6.MU","VBK.MU","KUN2.MU","ATQP.MU","VLE.MU","VNA.MU","UIJ.MU","VLM.MU","V33.MU","VODJ.MU","YAB2.MU","VOR1.MU","VW1.MU","VHO.MU","WL5P.MU","RTHA.MU","AHE.MU","WEP.MU","EJZN.MU","KWZ2.MU","CTE.MU","KBWA.MU","W7L.MU","FDK.MU","WELA.MU","WIN.MU","WHX.MU","WFS.MU","WG3.MU","ILT.MU","WMT.MU","WAN.MU","WP7.MU","WDL.MU","N2R.MU","M6FE.MU","WWR.MU","W9Z.MU","WMC1.MU","DWNI.MU","WMB.MU","4GNB.MU","SWS.MU","TG9.MU","PYA.MU","UWS.MU","3DW.MU","WHL.MU","08W1.MU","WFF.MU","WAF.MU","WSE.MU","T3A.MU","NWT.MU","WI3.MU","4RW.MU","WDC.MU","WCMK.MU","T3W1.MU","W8A.MU","B4O1.MU","0WPA.MU","MWB.MU","WF5A.MU","WMC.MU","WIP.MU","MTA.MU","P13.MU","S1V.MU","WTT.MU","WUP.MU","RDO.MU","XUN.MU","XGH.MU","XIC.MU","LXSN.MU","XOU.MU","PJP.MU","XL9A.MU","4GK.MU","XM8.MU","XNP.MU","NRN.MU","XAE2.MU","XWM.MU","EXU.MU","CXGH.MU","XPH.MU","RYSB.MU","E5F.MU","XD4.MU","XGJ.MU","XT3B.MU","33X1.MU","3XRA.MU","XTL.MU","XYD.MU","DO51.MU","XMY.MU","XTA.MU","O1BC.MU","X9T.MU","XTP.MU","VSL.MU","XEN.MU","XER.MU","X9X.MU","XEUA.MU","XE9.MU","XIS.MU","MXD.MU","XONA.MU","X2S.MU","XIX.MU","E7RA.MU","XEK.MU","RUT.MU","13X.MU","XEP.MU","X6S.MU","X0VN.MU","1XM.MU","XHN1.MU","XCN.MU","XC01.MU","XBLA.MU","XKK.MU","XYUA.MU","XCA.MU","XCQ.MU","XXT.MU","XSA.MU","Y0E.MU","AY3.MU","YM9A.MU","YTAA.MU","RNY.MU","C7Y.MU","YP9.MU","YB4N.MU","YC8.MU","Y06.MU","YXS.MU","YU4.MU","A60.MU","YCP.MU","Y9L.MU","Y8I.MU","YDX.MU","YIN.MU","CMUA.MU","0YYA.MU","YHO.MU","YTS.MU","M6O.MU","YZC.MU","WPP.MU","YZA.MU","YAK.MU","YIT.MU","CYD.MU","LRH1.MU","2SO.MU","YSM.MU","YT2A.MU","YUE1.MU","JMI.MU","LIA.MU","YDAB.MU","YE5.MU","D1LN.MU","TGR.MU","RY4C.MU","YAG.MU","YG12.MU","YB2P.MU","YIZH.MU","TYC1.MU","YB3.MU","YGD.MU","AIB1.MU","IU2.MU","G9Y.MU","YG4.MU","YOJ.MU","YI2A.MU","YZCA.MU","YTT.MU","YK3.MU","KY5.MU","YTV.MU","YAAA.MU","YMA.MU","YSN.MU","SRS.MU","RPHA.MU","HAM1.MU","5TP.MU","ZWS.MU","M9R.MU","0ZG.MU","ZDC.MU","G4Z.MU","ZEG.MU","ZSB.MU","ZSK.MU","ZCT1.MU","ZP8.MU","ZSV.MU","59A.MU","ZGV1.MU","BOW.MU","BRL1.MU","1ZY.MU","DUB1.MU","AFA.MU","ZEGA.MU","ZNH.MU","ISC1.MU","ZMR1.MU","ZAV.MU","FZM.MU","ZAL.MU","ZMG1.MU","FSRA.MU","0SG.MU","WEK.MU","D3H.MU","ZPFK.MU","LCQ.MU","ZYT.MU","ZB31.MU","ZO1.MU","AU6.MU","ZHJ.MU","T9Z.MU","ZY3.MU","0CZ.MU","ZEF.MU","ZVL.MU","EB9.MU","RE7.MU","BTKC.MU","ZOE.MU","ZIM.MU","ZNHH.MU","W1I.MU","ZEP1.MU","AFX.MU","IU8.MU","AOD1.MU","ZAR.MU","6ZY.MU","CMY.MU","ZIL2.MU","UG8K.MU","0ZD.MU","ZGY.MU","ZFIN.MU","EDGA.MU","SKC2.MU","ZJS1.MU","LL6.MU","PUZ.MU","FJZ.MU","IZ8A.MU","EUZ.MU","NQL1.MU","ZM7.MU","ZVF.MU","IPHB.MU","ZH5.MU","AAZ.MU","AAQ.MU","AAY.MU","AAB.MU","AAGN.MU","AAH.MU","AAD.MU","ARL.MU","AA9.MU","AA2.MU","ABP.MU","ABG.MU","AB1.MU","AUC.MU","AYO.MU","AML.MU","ABL.MU","AB3A.MU","ABEA.MU","ABA.MU","ABEC.MU","4AB.MU","AB7.MU","ABHA.MU","AIO.MU","ABS2.MU","ABJ.MU","ABW.MU","AB2.MU","AFT.MU","ABK.MU","NJM.MU","115.MU","ABR.MU","AIY.MU","ACV.MU","ACE1.MU","VGA.MU","OCI1.MU","IER1.MU","CSA.MU","33A.MU","AC5G.MU","E7S.MU","FRTB.MU","DCA.MU","OT3.MU","8AT.MU","PW9.MU","AC8.MU","ACBB.MU","ACR.MU","ADA.MU","AJ3.MU","ACOG.MU","TA3G.MU","ACWN.MU","ACT.MU","ACJ.MU","NXI.MU","AC3A.MU","APM.MU","AKB2.MU","GAZ.MU","ALVA.MU","1LUA.MU","PJXA.MU","A64.MU","MV9L.MU","MKN1.MU","SNW2.MU","5DQ2.MU","GW2A.MU","B1C.MU","FOMA.MU","VCLC.MU","08IA.MU","VYO.MU","NNIC.MU","OAO.MU","06E.MU","50CA.MU","TR3.MU","AHLA.MU","GP3N.MU","DNQA.MU","1VPA.MU","HUP.MU","ADP.MU","MGJ.MU","LUK.MU","CID.MU","NER.MU","CLF.MU","H6Q.MU","AVFA.MU","EMY.MU","PTC.MU","MRO.MU","FL3.MU","T5Z.MU","ERCA.MU","SIEB.MU","LFL.MU","IOY.MU","AD9S.MU","AHS.MU","EZHA.MU","NSY.MU","3BBB.MU","AMD.MU","8AHB.MU","0SGA.MU","TLV.MU","CIA.MU","S9H.MU","N1N.MU","BSU.MU","2WBA.MU","CHUA.MU","LGA.MU","NGLD.MU","A71.MU","R6C1.MU","BVXB.MU","FSY.MU","PKX.MU","CTYA.MU","TOTA.MU","0TUA.MU","PTI.MU","NOTA.MU","BTQA.MU","RTL.MU","AVH.MU","SP2.MU","1MOA.MU","NOAA.MU","MV9A.MU","NTZ.MU","VOW4.MU","AKOB.MU","ADM.MU","SBNC.MU","78IB.MU","GSM.MU","TSP.MU","2CDA.MU","AD5.MU","2BZA.MU","0JUA.MU","BHP.MU","ADD.MU","RIOA.MU","AD2.MU","MKY.MU","0C9A.MU","VX8A.MU","ADT.MU","A7R.MU","ADG.MU","TEV.MU","SGN.MU","TW1.MU","ADF.MU","AEDA.MU","IWQ.MU","FZKA.MU","ADB.MU","LD41.MU","EDG.MU","RGRA.MU","EPN.MU","SAO.MU","OMXA.MU","VSJ.MU","SAPA.MU","M8U2.MU","AISF.MU","GRC.MU","HAM.MU","LUX.MU","R2RA.MU","TNE2.MU","TATB.MU","AMNA.MU","HX1A.MU","NEH.MU","SCF.MU","AEC1.MU","AE9.MU","MTX.MU","CIOC.MU","BE1.MU","3A1.MU","AEND.MU","GCY.MU","AEP.MU","AED.MU","2AE.MU","AP1.MU","G9N1.MU","HE8.MU","AEU.MU","AVK1.MU","AES.MU","G7A.MU","A44.MU","AEX.MU","AFF.MU","SQY1.MU","H73.MU","AFG.MU","1AF.MU","AFL.MU","CUBB.MU","AF5.MU","AFS.MU","AFZ.MU","AFR.MU","G1V.MU","AJXA.MU","A28.MU","AFO1.MU","A5Y.MU","AGS.MU","AGD.MU","SVQ.MU","AGE.MU","C2J1.MU","AY5.MU","DBAN.MU","AGR.MU","N0GA.MU","AGR3.MU","ALG.MU","AGU.MU","IHA.MU","H9W.MU","AGJ.MU","MSGL.MU","RZU.MU","HIW.MU","AGX.MU","AG8.MU","CQT.MU","4OQ.MU","ASX.MU","4G3A.MU","WIB.MU","CHA.MU","FO4N.MU","LUM.MU","SHT.MU","EK7.MU","AGV.MU","AHV.MU","AHC.MU","CTY.MU","AIW.MU","OYC.MU","INR.MU","7A2.MU","NYVQ.MU","AI3A.MU","AP3.MU","AINN.MU","TX3.MU","JAL.MU","THAF.MU","AITA.MU","SWN.MU","RTA.MU","SIA1.MU","AIL.MU","NVPE.MU","MJS.MU","A1G.MU","AIXA.MU","AIV.MU","AIR.MU","NWC.MU","AJ4.MU","AJW.MU","AKQ.MU","AK3.MU","AKU.MU","FKM.MU","AK2.MU","AKJ.MU","AK7A.MU","T2Z.MU","EAD.MU","AKTA.MU","AK7.MU","AK1.MU","CSV.MU","6AT.MU","ALV.MU","LID.MU","AOCA.MU","A1OS.MU","ANO.MU","PHM7.MU","9AS.MU","GMZ.MU","VTM.MU","9ME.MU","CGE.MU","LVN.MU","7X81.MU","A9D.MU","AOMD.MU","TQL.MU","ALD.MU","J6W.MU","T921.MU","A6Y.MU","APL.MU","8AK.MU","4FU.MU","ATD.MU","1AG.MU","ALE.MU","A2O.MU","ALS.MU","AOC.MU","A4Y.MU","ALB.MU","BJJA.MU","ATC.MU","DUL.MU","A2V1.MU","AOX.MU","BMT.MU","B3O.MU","A4S.MU","AMG.MU","AMT.MU","SZ7.MU","AMS1.MU","111N.MU","AS4.MU","AMP.MU","3A0.MU","AXZA.MU","MFNC.MU","A0T.MU","A8B.MU","9AC.MU","NGLB.MU","APR.MU","PA2.MU","1YA.MU","PSRA.MU","AMY.MU","0CI.MU","54M.MU","AXNA.MU","AM3D.MU","9AE.MU","PKA.MU","NCB.MU","AM8.MU","MV9.MU","HCQ.MU","NAPN.MU","1AU.MU","72A.MU","CCL.MU","N6H.MU","AMK.MU","0UA.MU","RQ4.MU","AQ4.MU","2VA1.MU","AOS.MU","AMZ.MU","FG1.MU","FKP.MU","124.MU","PZX.MU","ANL.MU","AZ2.MU","A58.MU","B1Z.MU","ANCA.MU","AS7.MU","SCL.MU","GNV.MU","GPI1.MU","HGR.MU","OFX.MU","GJ2A.MU","ITK.MU","ANB.MU","AOD.MU","HU7.MU","AQE.MU","ITKA.MU","BZY.MU","FKR.MU","HUD.MU","BSFA.MU","LHOG.MU","L41.MU","R00N.MU","NVAH.MU","W9X.MU","AOR.MU","AO9.MU","A8N.MU","OIA.MU","BP1.MU","AON.MU","AOF.MU","AOP.MU","APA.MU","APDA.MU","A9KN.MU","APO.MU","7AA.MU","AP2.MU","DP4B.MU","APS.MU","NYVA.MU","AQK.MU","AQL.MU","3HA.MU","RN3.MU","V1S.MU","0WC.MU","HDP1.MU","MAC1.MU","ARR1.MU","HIJ2.MU","ARW.MU","A6T.MU","AYH.MU","4GJ.MU","ARRC.MU","6AX.MU","ARRB.MU","ERT.MU","REB.MU","I9DN.MU","ARX.MU","SAZ.MU","ARM.MU","A8U.MU","AR4.MU","D2EN.MU","ARQ.MU","A9RB.MU","TEO.MU","ASME.MU","A5A.MU","4OJ.MU","DHU.MU","JT9.MU","SHJ.MU","IUA.MU","ASJA.MU","IAA3.MU","HEH.MU","0LC.MU","SHN.MU","A8M1.MU","BZG2.MU","JAN.MU","BOA.MU","TPY1.MU","S3Z.MU","R1E.MU","MHT.MU","NVA5.MU","ASG.MU","SFB1.MU","AVS.MU","DIC.MU","BHQ.MU","A1U.MU","AUS.MU","TA1.MU","IMO.MU","AU9.MU","ATO.MU","AXI.MU","LEN.MU","T1L.MU","COR.MU","1FC.MU","O2C.MU","SLL.MU","OEWA.MU","BWO.MU","RAD.MU","RAW.MU","OBK.MU","MYM.MU","OMV.MU","PKL.MU","PFI.MU","H6O.MU","D7I.MU","FAA.MU","WSV2.MU","O3P.MU","BFC.MU","BZ6.MU","EBO.MU","P4N.MU","VAS.MU","AW2.MU","FLW.MU","ROI.MU","EVN.MU","WOF.MU","14A.MU","36M1.MU","SAC.MU","SANT.MU","DOQ.MU","CMBT.MU","SOBA.MU","MKL.MU","T7V.MU","P4Q.MU","LLC.MU","HJI.MU","0S5.MU","5CW.MU","GCL.MU","21P.MU","G7P.MU","TL4.MU","T4W.MU","TQT.MU","KN6.MU","LVT.MU","D7A.MU","AUB.MU","LYI.MU","02G.MU","OM6.MU","NC0E.MU","OXR.MU","2NC.MU","PMQ.MU","BGD.MU","3CAA.MU","MQG.MU","HJ1.MU","NYG1.MU","WV8.MU","GV6.MU","AVD.MU","VNI.MU","HSD.MU","GU8.MU","W2U1.MU","AVT.MU","3AY.MU","AVP.MU","CUCA.MU","AX8.MU","AWM.MU","AWR.MU","9AX.MU","HGQN.MU","AXA.MU","SPR.MU","3AS.MU","AYUF.MU","AYCN.MU","AZ5.MU","HDB.MU","P8AA.MU","A6Z.MU","PO0.MU","LLD.MU","KONN.MU","COM.MU","BKKF.MU","BSL.MU","BABB.MU","BI7.MU","BPI.MU","FZC.MU","T2L.MU","BBB.MU","BSD2.MU","BKG.MU","B8A.MU","PK5.MU","PTQ.MU","BBY.MU","BG1A.MU","BYRA.MU","BHM.MU","FBI.MU","BM1.MU","WB1.MU","TMLF.MU","BWB.MU","BAR.MU","BTL.MU","6BF.MU","BBZA.MU","BB2.MU","BBK.MU","BBDB.MU","9BM.MU","BOY.MU","BBI.MU","BFP.MU","BBH.MU","BBN.MU","BCLN.MU","BCO.MU","BCP.MU","BC8.MU","BCSA.MU","BCY.MU","BCE1.MU","BDSB.MU","BDE2.MU","BDT.MU","BDZ.MU","MOS.MU","EAI.MU","M3L.MU","T6W.MU","BMU.MU","DN1.MU","SJZN.MU","OU6.MU","BEZ.MU","T4I.MU","CGC.MU","GBQ.MU","3RB.MU","BEM.MU","BJEB.MU","LK7A.MU","CIB.MU","MA1.MU","DHZ.MU","BX7.MU","G9U.MU","USE.MU","EF9.MU","BRYN.MU","E4S.MU","BSIB.MU","J9B.MU","ECK.MU","DVU.MU","BW7.MU","13B.MU","NBG6.MU","BFV.MU","9BC.MU","BGOA.MU","BGB.MU","BGPA.MU","BIG1.MU","BGW.MU","BGO.MU","BGT.MU","HUL.MU","BHU.MU","BH5.MU","B9B.MU","BIL.MU","BHP1.MU","EYW.MU","BIO.MU","TFHD.MU","8NE1.MU","BIF.MU","TMS1.MU","IDP.MU","BO1.MU","SBS.MU","BIJ.MU","CEPR.MU","ONY.MU","KYX.MU","2LB.MU","BM8.MU","HBI.MU","BIR.MU","F8S.MU","PQX1.MU","4FM.MU","NB3.MU","BIO3.MU","GBY.MU","OKF.MU","EZB.MU","BIY.MU","BIU2.MU","MR4.MU","B6E.MU","NB1N.MU","PBNA.MU","PDL.MU","TRBA.MU","4GM.MU","B8F.MU","ETG.MU","WS7A.MU","SSN.MU","HBP.MU","BJF.MU","BJI.MU","CWW.MU","BKN.MU","C4C.MU","D7C.MU","BOZA.MU","BKE1.MU","HSB.MU","RYS1.MU","C6T.MU","SID.MU","NBC.MU","NVPI.MU","NVPB.MU","BK9.MU","TDB.MU","BKP2.MU","NAL.MU","C0V.MU","BZZ.MU","GHFH.MU","SIPF.MU","BK6B.MU","UOB.MU","PYT.MU","RY2.MU","BLON.MU","18B.MU","6BH.MU","BLQA.MU","3EV.MU","B7E.MU","04B.MU","H1Q.MU","D1Y.MU","SWF.MU","RI1.MU","TK4.MU","HLH.MU","ESHB.MU","EM3A.MU","BMM.MU","CGR.MU","FPC.MU","S9A.MU","WCQ1.MU","EM7A.MU","IIN.MU","P5C.MU","NE6.MU","BOI5.MU","CBA.MU","BMI.MU","PAA.MU","GHK.MU","SHUA.MU","HVP.MU","PNY.MU","N3Y.MU","CTJ1.MU","DJR2.MU","3RR.MU","TNHA.MU","BMW.MU","PYW.MU","KT3.MU","0M3.MU","MG3B.MU","7TR.MU","GIO.MU","GLV.MU","MPY.MU","OYD.MU","VTCB.MU","CEY2.MU","ORG.MU","MTK.MU","LBJ.MU","VTX.MU","HK51.MU","1NC.MU","SMA.MU","KEH.MU","GDC.MU","KYW.MU","LIUB.MU","FOU1.MU","BZX.MU","PJJ1.MU","SO7.MU","EBZ.MU","BU3.MU","CL1A.MU","TPV.MU","NBI.MU","CFNB.MU","FPO.MU","CTH.MU","C8G1.MU","MVL.MU","C3Q1.MU","PVEN.MU","WNZ7.MU","BNR.MU","BNN.MU","BNE.MU","BN9.MU","BNP.MU","9BR1.MU","HQK.MU","BOU1.MU","BON.MU","BSY.MU","BOP.MU","3BX.MU","VIB3.MU","BO9.MU","UXX.MU","1B9.MU","DB1.MU","BOR.MU","JBX.MU","BOF.MU","T21.MU","B8D.MU","BWJ.MU","BYG.MU","BO5.MU","BSX.MU","64B.MU","BVB.MU","GSH.MU","BOSS.MU","MSRB.MU","LUA.MU","BPE5.MU","BPD.MU","BPFG.MU","P9O.MU","NXZ.MU","BRR1.MU","BRW.MU","B6S.MU","BRX.MU","BRW1.MU","8BU.MU","SLB.MU","ITB.MU","BSN.MU","BSB.MU","BSP.MU","BSA.MU","BST.MU","NYM.MU","BTQ.MU","BTF.MU","4BV.MU","B7B.MU","MBU.MU","BUR.MU","3FH.MU","TUB.MU","B5H.MU","BUOB.MU","UCM1.MU","WBAG.MU","BUHA.MU","M6YA.MU","BUY.MU","B1W1.MU","BZ7A.MU","BV3.MU","BVF.MU","BWI.MU","BXR.MU","BYW6.MU","4BY.MU","BY6.MU","BYW.MU","BY91.MU","TZ1.MU","TYK.MU","TIA.MU","RFS.MU","RC8.MU","PCD1.MU","PC8.MU","P01.MU","N3MN.MU","M8R.MU","M1W.MU","L8G.MU","L48N.MU","IKL.MU","CRC.MU","CGM.MU","C8Q.MU","62M.MU","3FO.MU","CCDG.MU","POC.MU","ENMN.MU","HXCK.MU","LME.MU","GQN2.MU","GF6.MU","CDZ.MU","GSR.MU","0IX.MU","CSC.MU","GV8A.MU","HRJ1.MU","IUQ.MU","3XO.MU","GWN.MU","6LMN.MU","CMZ.MU","9SC1.MU","TRL.MU","T3F2.MU","DFK.MU","CVY.MU","9EW.MU","C5S.MU","CB1A.MU","CBK.MU","C5S1.MU","CB5.MU","48I.MU","CBT.MU","RF6.MU","CBGB.MU","CCB.MU","CCC3.MU","CC6.MU","CCG.MU","CDE.MU","1GE.MU","CDM1.MU","CDS.MU","CAI.MU","S5C1.MU","RQQ1.MU","CENB.MU","CR8.MU","SCA.MU","HOU.MU","GEH.MU","CWC.MU","CYT.MU","THRN.MU","CLS1.MU","CEXB.MU","CE1.MU","CEXA.MU","LSRN.MU","CEK.MU","CEV.MU","CTNK.MU","CE2.MU","TIE.MU","CFJ.MU","CTW.MU","CRE.MU","CEW3.MU","CEZ.MU","C44.MU","C3OA.MU","JAP.MU","TIC.MU","9CX.MU","PFQ.MU","CEA.MU","NVAQ.MU","TCE1.MU","DG3.MU","UNI3.MU","T3K.MU","1C0.MU","CSH.MU","CKNA.MU","CFX.MU","C4F.MU","CGZ.MU","CG5.MU","CGP.MU","CGN.MU","CGOB.MU","94C.MU","CGD.MU","LO3.MU","DIN.MU","GIN.MU","CKZA.MU","SR2.MU","6ML.MU","RITN.MU","45S.MU","TAMN.MU","CRLN.MU","CNO.MU","CS1.MU","KAX2.MU","CTM.MU","UEO.MU","M1H.MU","SR9.MU","SU1N.MU","CHR.MU","MNSN.MU","HLG.MU","RIHN.MU","C6G.MU","S3F.MU","C9F.MU","PHBN.MU","7CH.MU","EZQ.MU","MH4N.MU","CH2.MU","PEL1.MU","VTLN.MU","9C6.MU","ED4.MU","SN2.MU","2CU.MU","PGH1.MU","0CP1.MU","CHQ1.MU","E5C.MU","TOJ.MU","CNS.MU","EMC1.MU","PLG.MU","RHO5.MU","HIFH.MU","CHL.MU","SWJ.MU","ROH.MU","KCC.MU","HPD.MU","CO9.MU","CYY.MU","CVV.MU","MONV.MU","LIH.MU","NYVC.MU","C4S1.MU","GLR.MU","CIE1.MU","LTH.MU","B5SK.MU","KCY.MU","CRU.MU","CIJ.MU","44C.MU","RY5.MU","CPF.MU","B7O.MU","TRVC.MU","CI3.MU","JBL.MU","CTX.MU","MJG1.MU","CIS.MU","CIT.MU","CIV1.MU","CI4A.MU","PUWA.MU","CI9.MU","NKX.MU","CJ3A.MU","CJ6.MU","CJ9.MU","CJ8.MU","FXG.MU","1CK.MU","2CK.MU","C3T.MU","CLP.MU","C6O.MU","HK2C.MU","WIQ.MU","CLP1.MU","FBC.MU","CS3.MU","D9Z.MU","CU1.MU","P72.MU","C7S.MU","CLH.MU","SCG.MU","KCP.MU","CLRN.MU","CLV.MU","CVA.MU","CXX.MU","UR9.MU","CMAB.MU","UKV.MU","CM9.MU","MX4A.MU","CSG.MU","CMW.MU","CMR.MU","CMID.MU","TSI.MU","NC2B.MU","ICK.MU","6MT.MU","PIR.MU","GRV.MU","DWC.MU","1NS.MU","2LR.MU","D4D.MU","PC6.MU","R4P.MU","5CM.MU","DT7.MU","6WX.MU","C2L.MU","NNJ.MU","WI4.MU","1PC.MU","G2M.MU","TVL.MU","HUP1.MU","4FF.MU","WEZ.MU","2E5.MU","EXF1.MU","0CYA.MU","SHZH.MU","SGJH.MU","G5HA.MU","HR1.MU","SIY.MU","FTP.MU","5HF.MU","GKE.MU","HIUC.MU","EZ5.MU","62C.MU","PJC.MU","D7N.MU","75C.MU","PXI.MU","CPU2.MU","SZ1.MU","CPW.MU","CPI.MU","CPM.MU","CPA.MU","CPP.MU","CPOF.MU","CR51.MU","CTL.MU","CR6.MU","CUT.MU","PK0.MU","TE4A.MU","PK3.MU","CRG.MU","C7N.MU","CRIH.MU","OLD.MU","LUC.MU","CX1.MU","PC1A.MU","CRN3.MU","CR2.MU","CRP.MU","CRA1.MU","8CW.MU","CSJ.MU","CSQ.MU","CSX.MU","CVG.MU","CXR.MU","CS9.MU","TBK.MU","CSUA.MU","CSR.MU","CSF.MU","CTI.MU","EVD.MU","CTO.MU","CTP1.MU","C7T.MU","CT1.MU","CTAA.MU","CUEH.MU","CNY.MU","LBR.MU","CUS.MU","CUR.MU","CUP.MU","CV3.MU","CV6.MU","CVLB.MU","CVL.MU","CVS.MU","CWLR.MU","CYC.MU","KK3A.MU","CY1K.MU","C9S.MU","C04.MU","CY9A.MU","E36.MU","CYJ.MU","CY2.MU","UPL.MU","CZ61.MU","TEE.MU","DAI.MU","DSY1.MU","DAP.MU","RVS1.MU","49D.MU","DCIK.MU","DAR.MU","1DT.MU","DAM.MU","DSE.MU","HX9.MU","D7P.MU","6AH.MU","DDB.MU","D6H.MU","DTPA.MU","DPM.MU","DMO.MU","IA4.MU","DDN.MU","DSR.MU","9VD.MU","4DS.MU","DSN.MU","DLR.MU","TDT.MU","SO3.MU","PSX.MU","8OLN.MU","D2U.MU","DBQA.MU","DBK.MU","DB5.MU","DEVL.MU","DC7.MU","DCO.MU","DC6.MU","DCH1.MU","DC4.MU","DCR.MU","DCS.MU","DC6B.MU","DDQ.MU","D8HA.MU","TGT.MU","EQS.MU","NDA.MU","98DA.MU","GME.MU","JTH.MU","MRK.MU","HNR1.MU","N7G.MU","UP7.MU","ECX.MU","RIB.MU","PGN.MU","MED.MU","SY1.MU","LHA.MU","HHFA.MU","VES.MU","NOEJ.MU","DLSF.MU","HEI.MU","MDB.MU","CON.MU","TIN.MU","WL6.MU","DGR.MU","PDA.MU","SLT.MU","SKYD.MU","FLA.MU","FEV.MU","IFX.MU","DRE2.MU","ISR.MU","LXS.MU","RHK.MU","D2F.MU","DFJ.MU","DF3.MU","DFXN.MU","DGY.MU","HPP.MU","GM3.MU","DLD.MU","DL7A.MU","EOT.MU","KDM.MU","N7D1.MU","WDP.MU","DO1.MU","PPK.MU","DIO.MU","PD4.MU","EDIA.MU","MPG.MU","DSG.MU","D8X.MU","DIE.MU","DYBP.MU","SD6.MU","GUI.MU","UVD.MU","DIP.MU","FQI.MU","DLG.MU","SPE1.MU","NOVC.MU","GNN.MU","DS81.MU","T2V1.MU","LDB.MU","TDN1.MU","NZM2.MU","5NN.MU","DS5.MU","3P7.MU","D2V.MU","DLL.MU","DL8.MU","GIL.MU","DNQ.MU","NK1A.MU","EZV.MU","5GN.MU","A9L.MU","PMOX.MU","DOD.MU","0DA.MU","ADZ.MU","DOV.MU","DT3.MU","MCN.MU","KABN.MU","7DG.MU","FUO.MU","DR8A.MU","DP3.MU","DPWN.MU","DP5.MU","DPU.MU","DPW.MU","DPK.MU","DRM.MU","DRW3.MU","3MJ.MU","HDD.MU","HNL.MU","OD3.MU","1DD.MU","DRI.MU","DRW8.MU","DST.MU","DTE.MU","O2D.MU","EFF.MU","DTEA.MU","9BE.MU","DTV.MU","DUR.MU","D2J.MU","DUT.MU","DUE.MU","R6C.MU","D2MN.MU","E6R.MU","R6C3.MU","TXC2.MU","2DB.MU","DUP.MU","DVK.MU","DVC1.MU","RYE.MU","DWD.MU","4DX.MU","D3S.MU","DY6.MU","ND3.MU","D5I.MU","DY8.MU","DY2.MU","SD5.MU","DZE.MU","O5P.MU","F6H.MU","PJFB.MU","EH01.MU","J00.MU","P4XA.MU","E9P1.MU","3EC.MU","EAC.MU","ERL1.MU","KODN.MU","EJT1.MU","EAM.MU","NYVD.MU","RAE.MU","FEN.MU","EWZ.MU","EBA.MU","E4C.MU","FOMC.MU","EN61.MU","ECGF.MU","GRJ.MU","2BN.MU","0BD.MU","8EM.MU","EDL.MU","E2F.MU","MDD.MU","2IG.MU","EDC.MU","SQE.MU","EIX.MU","EDW.MU","EGZ.MU","EDP.MU","3UE.MU","ROT.MU","T5N.MU","A1T.MU","EEF.MU","O9G.MU","E2S.MU","EFX.MU","EFI.MU","EFS3.MU","EFS.MU","EFGD.MU","N4Q1.MU","O03.MU","EGT.MU","EG4.MU","EGQ.MU","EH8.MU","EIA.MU","G82.MU","EII.MU","EJD.MU","EJ7.MU","EKA.MU","EKT.MU","EKF.MU","EKQ.MU","EKE.MU","EKS.MU","R8V.MU","NVAW.MU","ELG.MU","E2M.MU","ELAA.MU","NEN.MU","LPK.MU","EP6.MU","ELB.MU","E6B.MU","ELVA.MU","FKA.MU","USR.MU","KCE1.MU","MITA.MU","WCI.MU","EMR.MU","FJG.MU","21E.MU","ELD.MU","LLY.MU","ELO.MU","HLL.MU","TKY.MU","TPO.MU","NVPA.MU","NVAE.MU","NUC.MU","GEC.MU","ELX.MU","SND.MU","L3X.MU","SKS.MU","E8X.MU","SMO.MU","FNE.MU","ELP.MU","GE7C.MU","RDF1.MU","7EL.MU","EMH1.MU","EMQ.MU","FV6.MU","GT81.MU","EMP.MU","ICS1.MU","TBD.MU","TUIJ.MU","ER2N.MU","ENA.MU","1FE.MU","ENI.MU","NUS.MU","SEQ.MU","SM3.MU","FP3.MU","GZ5.MU","HKE.MU","G1MN.MU","20R.MU","79V.MU","EPR.MU","SW5.MU","EO5.MU","EOAN.MU","EPD.MU","SE7.MU","MT4.MU","EQN2.MU","EQR.MU","HPBK.MU","EQ6.MU","NUQA.MU","LSE.MU","ERV1.MU","ER9.MU","ER7.MU","ERCB.MU","GAN.MU","ES4.MU","GTQ1.MU","POPD.MU","G9K.MU","MEL.MU","REP.MU","EV1.MU","HSC1.MU","RWW.MU","KBU.MU","VHM.MU","MES.MU","48CA.MU","HUA.MU","BAKA.MU","ESF.MU","EU4.MU","VIS.MU","IBE3.MU","TNE5.MU","OZTA.MU","IR1.MU","MEQA.MU","IBE1.MU","ADL.MU","EST.MU","FCC.MU","EXP.MU","IXD1.MU","FV01.MU","ESL.MU","HZJ.MU","ETRA.MU","ENXB.MU","EUQ.MU","DEQ.MU","E3B.MU","EUE.MU","TNU3.MU","6E9.MU","E2G.MU","EUCA.MU","E5T.MU","E7CD.MU","OCW.MU","EUX.MU","2EV.MU","EVK.MU","EVT.MU","WE7.MU","EV4.MU","EV9.MU","EVZ.MU","EVI.MU","EW1.MU","S8W1.MU","3PY1.MU","EX9.MU","F7E.MU","NVAL.MU","HEE.MU","J2B.MU","EXK.MU","PNW1.MU","E4X1.MU","TYM.MU","MCF.MU","IC2.MU","1L4.MU","PTTG.MU","4QW.MU","2EX.MU","NX9.MU","EXM.MU","4XS.MU","SOU.MU","PEO.MU","R4Y.MU","E3X1.MU","EXB.MU","SEG1.MU","L6Y.MU","EZH1.MU","EZ1.MU","EZF.MU","FVI.MU","FCD.MU","FAM1.MU","FBLM.MU","FVK.MU","T6O.MU","FAU.MU","2B6.MU","FFX.MU","1FA.MU","FB2A.MU","HQP.MU","NFA.MU","FAS.MU","FAI.MU","FXH.MU","FT7.MU","FUC.MU","FR7.MU","SES.MU","FDN.MU","FDX.MU","FDM.MU","FE2.MU","2FE.MU","FEU.MU","FEK.MU","FRU.MU","FEX.MU","FEY1.MU","FEW.MU","FE7.MU","FFV.MU","FFH.MU","FFP.MU","UVS.MU","NLC.MU","FHL.MU","FHS.MU","RATV.MU","4FY.MU","GFIN.MU","1F9.MU","F4B.MU","FIV.MU","F9E.MU","FMNB.MU","FISN.MU","SYU1.MU","FW3.MU","N9G.MU","LT5.MU","FJI.MU","FKJ1.MU","FKGC.MU","FKC.MU","9NF.MU","FL4.MU","IFF.MU","FLE.MU","FXI.MU","FLU.MU","FWV.MU","8FT.MU","FMC1.MU","FMEA.MU","FMV.MU","FMH.MU","FMQ.MU","FME.MU","MFZA.MU","FNI.MU","FNTN.MU","12F.MU","TFA.MU","FOJ1.MU","WFM.MU","FZA.MU","FSL.MU","FXB.MU","F2T.MU","F5D.MU","FRS.MU","FOH.MU","1CT.MU","FOO.MU","TF7A.MU","FOB.MU","FOT.MU","FVJ.MU","FTQ.MU","HO7.MU","F4S.MU","L1OA.MU","LUY1.MU","FPE3.MU","FPH.MU","FPP.MU","FPT.MU","FPMB.MU","THP.MU","SEJ1.MU","PEU.MU","1T9.MU","C4X.MU","RCF.MU","IL2.MU","TOTB.MU","7SO.MU","NQ9.MU","LRC.MU","T7H1.MU","SJ7.MU","PPX.MU","S1A.MU","I7G.MU","LOR.MU","7PO.MU","HMI.MU","P2W.MU","E7V.MU","4SP.MU","NGP.MU","UBL.MU","KPR.MU","FRK.MU","GRB.MU","7FP.MU","6NU.MU","GI6A.MU","VVD.MU","GZF.MU","MCH.MU","IPZ.MU","1VD.MU","PER.MU","LAG.MU","WIS.MU","FS8.MU","FSX.MU","FSE.MU","FTI.MU","FUE1.MU","VO51.MU","IT2A.MU","FWG.MU","FWC.MU","FWQ.MU","FZH.MU","FZ9.MU","LGN.MU","HCG.MU","P5HH.MU","0UK.MU","GH8.MU","GS2C.MU","60N.MU","GEY.MU","GSG.MU","GWK3.MU","GAD.MU","NUB.MU","PGB1.MU","UMA.MU","GAP.MU","LK9.MU","GGG.MU","9TG.MU","GRZ.MU","SK8C.MU","SCT.MU","IJ7.MU","MN3.MU","RIO1.MU","S4VC.MU","IVKA.MU","LJ2.MU","IV4.MU","PHZ.MU","HDK.MU","RTO1.MU","MTR.MU","INW1.MU","P6K.MU","GS7.MU","1LG.MU","TCO.MU","PI2.MU","PES.MU","RDEB.MU","IJ8.MU","JPR1.MU","TQW.MU","OXU.MU","LFD.MU","GCC.MU","3GY.MU","6T1.MU","SYR.MU","L9S.MU","5M71.MU","IRYA.MU","RLYG.MU","SSUN.MU","RLI.MU","OJS1.MU","GDUA.MU","RTS2.MU","KO71.MU","R6L1.MU","17LA.MU","N9E1.MU","PIQ2.MU","RL9A.MU","RTSD.MU","H0H1.MU","TPA.MU","SSU.MU","MF7G.MU","3Y5A.MU","VLX1.MU","92G.MU","8GM.MU","MYD.MU","GRU.MU","GE2.MU","MCG.MU","GXI.MU","GTN.MU","GGK.MU","5IM.MU","RIG2.MU","4NX.MU","I3X.MU","GSC1.MU","G1A.MU","LHG1.MU","GGC.MU","GWI1.MU","GHH.MU","SGE.MU","B7A.MU","GEI.MU","LDV.MU","7A7.MU","4VL.MU","SGT.MU","MUK.MU","0GI.MU","G4S.MU","GON.MU","GTX.MU","GPT.MU","GFT.MU","GF8.MU","GFK.MU","GGD.MU","GGS.MU","GG81.MU","GG3.MU","GGZ.MU","GHG.MU","GH3.MU","PIG.MU","GIB.MU","C8V.MU","GI0A.MU","GI2.MU","GSA.MU","GIS.MU","2GI.MU","GKS.MU","OTC.MU","GLJ.MU","JXC1.MU","29M.MU","3GOK.MU","JO3.MU","GBT.MU","G5DN.MU","NI9.MU","RXC.MU","GLW.MU","P9G.MU","S3Y.MU","4GE.MU","GMM.MU","IGG.MU","L3D.MU","5G5.MU","3RV.MU","KIN2.MU","T66.MU","38D.MU","32N.MU","21M.MU","P2O.MU","MJT.MU","1A5.MU","G0G.MU","GTR.MU","1GW.MU","MI5.MU","55G.MU","PGW.MU","SO1.MU","OVXA.MU","D4R.MU","RV0.MU","MY4.MU","ORY.MU","JE4.MU","HGM.MU","C8U.MU","GS5.MU","SRM.MU","MRG.MU","LI9.MU","G6P.MU","5TN.MU","VN3A.MU","G5M.MU","68B.MU","MF9A.MU","GOS.MU","D8M.MU","3V4.MU","GOB.MU","G4D.MU","RG3.MU","GO5.MU","2G3.MU","SBTA.MU","WGF1.MU","GPG.MU","GTU.MU","GTT.MU","GUG.MU","G2U.MU","TTU.MU","KUG1.MU","GRCH.MU","GVM.MU","6GI.MU","GWW.MU","GW4N.MU","GXD.MU","HAB.MU","HLAG.MU","NVAX.MU","RAQJ.MU","PND.MU","HNN.MU","CO0.MU","HII.MU","SVHG.MU","WPA.MU","HFF.MU","HHX.MU","0HC1.MU","TQ42.MU","HN9.MU","NWX.MU","H9Y.MU","HLV.MU","HMC.MU","HAS.MU","HNC.MU","H2R.MU","BRH.MU","HAL.MU","0BN.MU","HAY.MU","HH2.MU","HAA1.MU","6HW.MU","HAV.MU","HBC1.MU","HBM.MU","HBH.MU","HBC2.MU","5H5A.MU","HCW.MU","HC5.MU","HCU.MU","HCH.MU","HCL.MU","2BH.MU","SNH.MU","HDI.MU","HDJ0.MU","SIH.MU","HE9.MU","7MH.MU","NYVE.MU","HNK1.MU","TG2R.MU","HEZ.MU","RTMK.MU","4H5.MU","0I2.MU","HLPN.MU","LPO.MU","THC1.MU","HXGB.MU","HETA.MU","P7O.MU","KHNZ.MU","USJ.MU","HMSB.MU","HLD.MU","MHR.MU","MTP.MU","SSM1.MU","IPO.MU","HSY.MU","MIH.MU","HPC.MU","HEN.MU","OTE.MU","HLE.MU","HEN3.MU","HGJ.MU","HG1.MU","HHN.MU","HMO.MU","HLW.MU","23H.MU","IHM.MU","HI11.MU","HIA1.MU","HIK.MU","HIN.MU","HKN.MU","0HG.MU","MHL.MU","N8Z1.MU","3H3.MU","HQS.MU","MRI.MU","39J.MU","TIB1.MU","MX7A.MU","4SK.MU","L5R.MU","SNO.MU","3SD.MU","SGI.MU","LIP.MU","SWI.MU","SHK.MU","SHG.MU","IO5A.MU","LIQ.MU","TH3B.MU","HP81.MU","HKT.MU","WHA.MU","IB5A.MU","TBCN.MU","MRU2.MU","TLW.MU","CHK.MU","LHL.MU","OS1.MU","3SY.MU","TXW.MU","IL3.MU","PFH.MU","IOV.MU","3SI.MU","NVAM.MU","TTI.MU","UT5A.MU","LTJ.MU","HLBN.MU","KPI1.MU","0OG.MU","C9IB.MU","MJ8.MU","0KE.MU","TJC.MU","P2H.MU","VBHK.MU","1JP.MU","I8D.MU","M3C.MU","ONJ3.MU","SW7N.MU","MYRK.MU","RRU.MU","M04.MU","SGP1.MU","RHO.MU","KOA.MU","USI.MU","TYU2.MU","HLS.MU","3BG.MU","46C1.MU","HL8.MU","04M.MU","UGD2.MU","4OR.MU","N9B.MU","SLW.MU","O5H.MU","KPJ.MU","NNND.MU","TGE1.MU","NP9.MU","SWTF.MU","NSE.MU","HMT.MU","HNIB.MU","HNM.MU","O4B.MU","MWI.MU","2HP.MU","7HP.MU","HRT.MU","HRB.MU","HRU.MU","HR3.MU","HRPK.MU","HSZ.MU","HTU.MU","HTD.MU","HT4.MU","PPL.MU","H09.MU","MOGA.MU","HUM.MU","OTP.MU","6HB.MU","HUKI.MU","MGYB.MU","096.MU","RMV1.MU","HU3.MU","HVE.MU","HWSA.MU","HX5A.MU","1HTA.MU","HYF.MU","NOH1.MU","HYQ.MU","HYI.MU","IAL.MU","IBM.MU","ICY.MU","I7O.MU","3IC.MU","TBA.MU","P5TA.MU","LK4B.MU","OB8.MU","SMS2.MU","LPL2.MU","8JN1.MU","IDO1.MU","MLQ2.MU","ISM.MU","IKP.MU","LU6A.MU","I41.MU","LFU2.MU","IDT.MU","TCID.MU","PQ9.MU","R4U.MU","D7V.MU","5IL.MU","OAIA.MU","TIH1.MU","OB9.MU","5AA.MU","RU6.MU","PS9A.MU","IDC2.MU","T9Q.MU","OHH.MU","IUD.MU","KM6.MU","UTG.MU","UTY.MU","IDZ.MU","IDJ.MU","MEF.MU","LFV.MU","UH1.MU","WB7.MU","ITP.MU","07K.MU","3IB.MU","IES.MU","2IS.MU","IEI.MU","SZX1.MU","2M6.MU","IE2A.MU","PNT.MU","IL0A.MU","PQ4.MU","IFA.MU","IGQ5.MU","IH9.MU","IHCB.MU","IHJ.MU","II8.MU","IIJ.MU","IKF.MU","MT2.MU","ORB.MU","WZM.MU","SRY.MU","AU1.MU","OT5.MU","SCY.MU","ILU.MU","IPJ1.MU","LBN.MU","IR3B.MU","TLG.MU","IM3.MU","ISX.MU","IMP.MU","IMU.MU","SY5N.MU","LEG.MU","IMX.MU","P1Z.MU","IMN.MU","IY4.MU","TEG.MU","IMTA.MU","SOP.MU","PQL.MU","IMV.MU","IMG.MU","ISI.MU","IO4.MU","1IP.MU","IP4.MU","IPG.MU","IRH.MU","TZ8.MU","IRM.MU","TPIG.MU","NVPF.MU","2CI.MU","I8R.MU","ISH2.MU","PAQ3.MU","IS7.MU","SNM.MU","P4I.MU","ME9.MU","4HW.MU","ITTA.MU","SPE.MU","7PI.MU","MDS.MU","S5U5.MU","PIL3.MU","S7A.MU","LUXA.MU","SOAN.MU","M6Z.MU","AUL.MU","STNA.MU","PIE1.MU","ITN.MU","NYVF.MU","ITU.MU","TXE.MU","PRP.MU","UEI.MU","PGA2.MU","TI5.MU","MOV.MU","MGG.MU","ENL.MU","TOB.MU","ITA.MU","MOK.MU","TIQ1.MU","0OV1.MU","MPI3.MU","ITH.MU","REJ.MU","TQI.MU","I7N.MU","IU9.MU","P1I.MU","B8ZB.MU","1F8.MU","IUI1.MU","IVX.MU","IVU.MU","MIS.MU","IYAA.MU","IVY.MU","IVSB.MU","IWA.MU","IXJ.MU","IXX.MU","IXY.MU","JZTB.MU","JASN.MU","JB1.MU","JCP.MU","JEN.MU","JEM.MU","R6L.MU","JHJ.MU","JSN.MU","JIX.MU","JJO.MU","JNJ.MU","JY8.MU","S3X.MU","RZC.MU","MMO.MU","CAC1.MU","NOX.MU","I8U.MU","SKX.MU","NEC1.MU","MTS1.MU","KAJ.MU","MUR1.MU","NGK.MU","TBT.MU","RIC1.MU","KUO1.MU","SZ8.MU","SRP.MU","NR7.MU","MEA.MU","TOS.MU","MU2.MU","MMK.MU","MBI.MU","TD4.MU","NCZ.MU","KYR.MU","MARA.MU","TUO.MU","TSE1.MU","OIT.MU","MAT1.MU","SPH1.MU","OKN.MU","SB3.MU","NIU.MU","SEH.MU","RYU.MU","NTO.MU","KBK.MU","KAO.MU","KEE.MU","RAK.MU","MTW.MU","KKA.MU","OLY1.MU","4HN.MU","TOM.MU","DEN.MU","NX8.MU","NIT.MU","TKK1.MU","KIR.MU","TZ6.MU","SJ8.MU","KST.MU","MSI.MU","ROM.MU","SOK.MU","KOM1.MU","MHO.MU","7SN.MU","J2S.MU","3RU.MU","JUD.MU","UOM.MU","KQ1.MU","KHZ1.MU","31Z.MU","NVAR.MU","TFBF.MU","0KB1.MU","LIZ.MU","KKBB.MU","KA8.MU","KBC.MU","KB7.MU","KBIA.MU","KBH.MU","KB2.MU","KCO.MU","KCN.MU","3K2.MU","KDIC.MU","KEP1.MU","KEK.MU","7AZ1.MU","KEY.MU","KM1N.MU","KEL.MU","ROF.MU","KFI1.MU","KGX.MU","KGHA.MU","KHP.MU","NVA7.MU","2KD.MU","N9VA.MU","KIJ.MU","KIFF.MU","KLN.MU","KMY.MU","9KX.MU","NVA6.MU","KR5.MU","SUA2.MU","KLA.MU","2KX.MU","WOSB.MU","KMLK.MU","KMB.MU","KNIA.MU","KUB1.MU","KOG.MU","KOC.MU","KPN.MU","VPK5.MU","NVA8.MU","KRN.MU","KRT.MU","K1R.MU","K1W.MU","KSB3.MU","KSB.MU","SDF.MU","KTF.MU","KTC.MU","LKM.MU","KUN4.MU","KU1.MU","KUD.MU","KU2.MU","W2N.MU","KWS.MU","29X.MU","RLF.MU","3FV.MU","29P.MU","8MG.MU","RZF.MU","0WH.MU","MKN.MU","N9J.MU","0XC.MU","LNLB.MU","VH1.MU","6BK.MU","COA1.MU","8WY.MU","85C.MU","PXQ.MU","CH8.MU","83B.MU","P7K.MU","599A.MU","S7N1.MU","UM9.MU","G31.MU","LAH1.MU","09B.MU","LUS.MU","LBH1.MU","LAB.MU","OLJ.MU","LED.MU","6LA.MU","8GL.MU","RV6.MU","LAR.MU","PRL.MU","LLI.MU","LR81.MU","ULC.MU","NYVB.MU","LA5.MU","PRZ.MU","OL5.MU","ULD.MU","LCR.MU","LBA.MU","LCO.MU","LCX.MU","TLA.MU","LXK.MU","8LC.MU","LEC.MU","LRT.MU","LX31.MU","LNSX.MU","LMP.MU","LNN.MU","OSR.MU","LVCN.MU","LEO.MU","LFY.MU","LFP.MU","LGLG.MU","LHW.MU","6LH.MU","LLV.MU","98D.MU","LMI.MU","LMX.MU","LM02.MU","LOM.MU","TGH.MU","L3I.MU","G17.MU","LWE.MU","LOJ.MU","MLL.MU","9LG.MU","LTEC.MU","LO6A.MU","3PX.MU","LPZB.MU","LPT.MU","LQZ.MU","LQZ1.MU","LR21.MU","LS4C.MU","LSX.MU","LSPP.MU","COC.MU","1SO.MU","RRTL.MU","3W9K.MU","TR5.MU","0OE.MU","SEN.MU","E1S.MU","TW11.MU","BMSA.MU","UGY.MU","UGZ.MU","MOH.MU","LWB.MU","LY1.MU","TLY.MU","SHH1.MU","MAN.MU","PIT.MU","MM2.MU","MSN.MU","MT3.MU","M4I.MU","MT1.MU","MAOA.MU","TWL.MU","MAQ.MU","MZX.MU","MPN.MU","M5Z.MU","R7X1.MU","4MG.MU","NF9.MU","MXW.MU","MUM.MU","MBQ.MU","MBB.MU","MB9.MU","BRU.MU","MBK.MU","MVB1.MU","MDO.MU","RJ8.MU","MCP.MU","US8A.MU","MCX.MU","MCY.MU","MCK.MU","MDN.MU","MDG1.MU","6MK.MU","3CQ.MU","MGP.MU","VNM.MU","MVR.MU","4FZ.MU","42S.MU","PUS.MU","MWZ.MU","MZN.MU","M3V.MU","M3R.MU","I4T1.MU","6MD.MU","SPM.MU","15M1.MU","MGC.MU","MGA.MU","MGN.MU","TCD.MU","MHSG.MU","MHH.MU","MHI.MU","3TK.MU","ORS.MU","NMM.MU","SMHN.MU","MVIN.MU","M8B.MU","MIN.MU","18E.MU","NMA.MU","D7Q1.MU","7C6.MU","RV2.MU","NJF.MU","PB3.MU","5LM1.MU","PGM.MU","PZM.MU","2J1A.MU","MKT.MU","MLP.MU","MLU.MU","MMT.MU","MMX.MU","MMM.MU","PXU.MU","9PM.MU","MNM.MU","WC7.MU","3HG.MU","23M.MU","02M.MU","KYC.MU","MWK.MU","MTLA.MU","9MO.MU","COQ.MU","MOJB.MU","TMW.MU","0ME.MU","MRS.MU","TL0.MU","MOO.MU","2NS.MU","MO7A.MU","MPCK.MU","MPW.MU","MPV.MU","MQ8.MU","4I1.MU","MSF.MU","MSQ.MU","MSPA.MU","MSAG.MU","MTO.MU","7SU.MU","MTE.MU","MT7.MU","MTN1.MU","MUQ.MU","MUB.MU","NGU.MU","MUV2.MU","M4N.MU","MUF.MU","MVX.MU","MVV1.MU","4FO.MU","MXR.MU","OSOB.MU","MXI.MU","4FN.MU","4FV.MU","TLV1.MU","4GP.MU","MX5.MU","6MY.MU","8NSK.MU","NNS.MU","NO8.MU","TB5.MU","NAI.MU","N7E.MU","NAQ.MU","N2F.MU","NNGE.MU","NNM.MU","NAGE.MU","N9M.MU","PNK.MU","NI1.MU","NBH.MU","NBQ.MU","NB6.MU","NC0.MU","NC2A.MU","NC5A.MU","NCL.MU","NC0B.MU","NCYD.MU","NCR1.MU","NDB.MU","NDX1.MU","PNG.MU","WAC.MU","NR4.MU","4NS.MU","2NR.MU","NU41.MU","NEM.MU","NS9B.MU","NTA.MU","NESR.MU","NG9.MU","NXS.MU","NGJ.MU","SPN.MU","NV81.MU","NEF.MU","NETK.MU","N7V.MU","NQI.MU","OE6.MU","NW5.MU","NXU.MU","NOL.MU","NWU1.MU","NFC.MU","NFS.MU","NFPH.MU","NHM.MU","NL9.MU","BR3.MU","NLE.MU","NKE.MU","NLV.MU","TPL.MU","2NN.MU","PHI1.MU","RSH.MU","9ST.MU","SGM.MU","WER.MU","INN.MU","0PQ.MU","OEM.MU","NLM.MU","TNTC.MU","2FI.MU","NMV.MU","NNF1.MU","NRD.MU","N1O.MU","R3Q.MU","NOT.MU","N7MG.MU","R80.MU","OS3.MU","NVAD.MU","NOA3.MU","D9M.MU","TMR.MU","NVV.MU","O49.MU","N2X.MU","TEQ.MU","NOR.MU","NVQ.MU","NTH.MU","NRA.MU","NSU.MU","NTQ3.MU","37S.MU","SC2.MU","23N.MU","NU2.MU","NUO.MU","NVA4.MU","NYVP.MU","NVA3.MU","NVA1.MU","NYVK.MU","NVAV.MU","NVD.MU","NYVL.MU","NVAC.MU","NYVS.MU","TUU.MU","NVAK.MU","NYVG.MU","NVAN.MU","NVP5.MU","NVP4.MU","NYVU.MU","NYVJ.MU","NVK.MU","NVJN.MU","NVAB.MU","NVP7.MU","NVAA.MU","NX1B.MU","OS7.MU","OBD.MU","OBH.MU","OBS.MU","RQQ.MU","OPC.MU","OCN.MU","ODP.MU","49F.MU","VVV1.MU","OEZ.MU","VVV3.MU","UWV.MU","OHP.MU","OHE.MU","O7P1.MU","OHB.MU","USS.MU","OI2.MU","TVTA.MU","B9I1.MU","OJU1.MU","OLN.MU","ORJ.MU","OPE.MU","3O8.MU","2JC.MU","C5N.MU","P4O.MU","AU7A.MU","OTX.MU","OPO.MU","OR6.MU","PNO.MU","TPA1.MU","ORC.MU","ORO.MU","6OT.MU","ORL.MU","OS2.MU","7OT.MU","OUTA.MU","5VO.MU","M6Q.MU","OVW.MU","OVER.MU","OXGP.MU","UIS.MU","UPAB.MU","LIL3.MU","PSU.MU","PD2.MU","PA8.MU","17PA.MU","UNP.MU","PCX.MU","PAM.MU","PB4.MU","PQE.MU","3P51.MU","2G1.MU","6PM.MU","P6X.MU","INP.MU","G3U.MU","7PW.MU","WHE.MU","2PP.MU","PBB.MU","PEN.MU","PB9.MU","PCS.MU","PC6A.MU","PCG.MU","PCC.MU","PCE1.MU","PD9.MU","56P.MU","SHI.MU","PKN.MU","14R.MU","PT8.MU","PEP.MU","P6T.MU","5PF.MU","WOPA.MU","PE51.MU","TEHN.MU","CHU.MU","2MP1.MU","0P8.MU","P2F.MU","PFV.MU","M0P.MU","PFE.MU","PGV.MU","PG4.MU","PGP.MU","6PG.MU","PH7.MU","PHX.MU","P8H1.MU","SNC3.MU","PTCA.MU","SVB.MU","R66.MU","RGO.MU","I3F.MU","2TK.MU","9IP.MU","UUD.MU","FRHN.MU","PY2.MU","PS4.MU","GBMB.MU","PM7A.MU","PQ2.MU","9EP.MU","SPJ.MU","TEL1.MU","S90.MU","I4P.MU","I5P.MU","PIP.MU","UDW.MU","PXL.MU","PKY1.MU","PKW.MU","PNC1.MU","7PZ.MU","G3V.MU","PLEK.MU","F7U.MU","PMC.MU","PMTA.MU","PNU.MU","PNE3.MU","PNP.MU","PU8.MU","POJN.MU","SGR.MU","PLUN.MU","PY9.MU","58I.MU","G8O2.MU","RI4.MU","PO9.MU","PPA.MU","PAH3.MU","PPQ.MU","PQ6.MU","SQI.MU","PRU.MU","RK8.MU","PXR.MU","7PS.MU","TR1.MU","PRRB.MU","PZ9.MU","N5C.MU","PSM.MU","PSQ.MU","PSE.MU","PSAN.MU","RN4.MU","PTOF.MU","SCS.MU","PTNA.MU","S4LA.MU","P91.MU","PU7.MU","PUM.MU","PU4.MU","PUG.MU","PUD.MU","PUR.MU","P5X.MU","TPE.MU","PVH.MU","PWO.MU","RRZ.MU","RA6.MU","RAX.MU","RMB.MU","RRA.MU","RGR1.MU","RDS.MU","RR5.MU","RNKA.MU","RAG.MU","46BB.MU","RBE1.MU","RB0.MU","RC0.MU","RCO.MU","RCIB.MU","RF9.MU","RG2A.MU","EN2.MU","RH8.MU","RUC.MU","R7G.MU","RSTA.MU","RJN.MU","RJR1.MU","RKET.MU","RKQ.MU","WP4.MU","VO7.MU","RLG.MU","RMC.MU","RME.MU","RN7.MU","1T5.MU","RNL.MU","RSI.MU","RSO.MU","R5IA.MU","RWL.MU","RWC.MU","6BC.MU","M17.MU","8RR.MU","2M1G.MU","3R9.MU","RYC.MU","RPL.MU","2IV.MU","RSL2.MU","RTC.MU","ST2.MU","C3B.MU","RWE.MU","RWE3.MU","RX5.MU","2YS.MU","RY6.MU","STS1.MU","SAX.MU","SB7.MU","TDZ2.MU","8S8.MU","SZG.MU","S2Z.MU","SBOA.MU","SBJ.MU","SHA.MU","SCUN.MU","S4A.MU","TN8.MU","SDRC.MU","SCC.MU","SFU1.MU","SL1.MU","G24.MU","SHF.MU","SWA.MU","M5S.MU","59S.MU","SDV.MU","TLS.MU","SI2.MU","TU0.MU","SS8.MU","SVKB.MU","S7MB.MU","SUR.MU","F3C.MU","SFO.MU","SFM1.MU","021.MU","SFD1.MU","THK1.MU","SIT4.MU","M3T.MU","SG2.MU","SJX.MU","H2W1.MU","SGK1.MU","PLF.MU","C6D1.MU","V6JN.MU","SUVN.MU","SR6.MU","SW1.MU","9SH.MU","SHWK.MU","UK2.MU","SIX3.MU","SIE.MU","1SZ.MU","SIZ.MU","SII.MU","SIX2.MU","SIS.MU","SNG.MU","SI3.MU","SZZ.MU","TQJ.MU","7KXN.MU","S9Y.MU","SJR.MU","SJL.MU","SK1A.MU","SM1.MU","06O1.MU","S92.MU","SM2.MU","SMPA.MU","8S9.MU","SNW.MU","COZ.MU","2ED.MU","SOT.MU","SYT.MU","SQM1.MU","0VS.MU","SWVK.MU","0SC.MU","L5A.MU","F3A.MU","S7Y.MU","SO4.MU","32Z.MU","SAG.MU","SOO1.MU","SEZ.MU","WIOA.MU","SPW.MU","7SI.MU","SQ3.MU","SRT3.MU","SRX1.MU","SRX.MU","SRB.MU","SSK.MU","USX1.MU","ST5.MU","STD.MU","SYK.MU","T3V1.MU","S82.MU","V4JA.MU","S1N.MU","SU3.MU","WFR.MU","LIE.MU","14S.MU","3S9.MU","SUU.MU","SUY1.MU","SVJ.MU","SVC.MU","UHR.MU","SYV.MU","LIO1.MU","VTY.MU","SYZ.MU","SYI.MU","SYM.MU","SYY.MU","SY9.MU","VF2.MU","SYP.MU","TXF1.MU","5TE.MU","TLM.MU","TAFG.MU","TTK.MU","THL.MU","TCS.MU","TKE.MU","T4L.MU","TTFB.MU","7T0.MU","TLX.MU","TM0.MU","TSFA.MU","TAEN.MU","TCA.MU","TCG.MU","TC1.MU","TH51.MU","TX5.MU","VZAA.MU","04IA.MU","TOC.MU","17T.MU","TIF.MU","TII.MU","TTEB.MU","TJX.MU","TKA.MU","TLK.MU","TLI.MU","TMJ.MU","TNR.MU","28T.MU","TPN.MU","1TU.MU","TU9.MU","TXM1.MU","T2G.MU","TSTA.MU","TSS.MU","TZO.MU","TTR1.MU","TT1.MU","TTC.MU","1TB.MU","TUUF.MU","TUR.MU","TUI1.MU","VTV.MU","TXG.MU","TXT.MU","UAL1.MU","C1U.MU","UBK.MU","UB5.MU","0UB.MU","UEN.MU","UCA1.MU","UNC.MU","UCD1.MU","UF0.MU","UD5.MU","UEC.MU","UXO.MU","UE3.MU","UGR.MU","UHY1.MU","US1.MU","34U.MU","UR3.MU","U1B.MU","0UV.MU","UTH.MU","UNVB.MU","W3U.MU","UNH.MU","UTDI.MU","UNS1.MU","USY1.MU","UQM.MU","U9E.MU","U6Z.MU","2FU.MU","M6J.MU","U9V.MU","U9M1.MU","U9T.MU","D6J.MU","8GP.MU","T6A.MU","32C.MU","UTC1.MU","VAW.MU","VAC.MU","VBL.MU","VCH.MU","VRS.MU","VR9.MU","VEN.MU","FR4N.MU","VEO.MU","VIH.MU","VTQ.MU","VHY.MU","VIA.MU","VS51.MU","3V64.MU","VIU.MU","V4L.MU","VVU.MU","VOL3.MU","VOW3.MU","V0Y.MU","VOW.MU","VODI.MU","VSC.MU","BMW3.MU","MAN3.MU","WAZ.MU","WCH.MU","WSU.MU","WTB.MU","1WF.MU","WBC.MU","WCL.MU","WDI.MU","WD5.MU","WF3.MU","WHC.MU","WEG1.MU","WGB.MU","WW6.MU","WHF4.MU","WHR.MU","WM1.MU","CH1A.MU","07W.MU","WM8.MU","W7D.MU","WTH.MU","1TW.MU","WYR.MU","ADI1.MU","ADS.MU","9FSA.MU","4CIA.MU","CHWD.MU","49BA.MU","AUD.MU","8RA.MU","LIV.MU","BA3.MU","BAF.MU","B6JA.MU","SEBA.MU","R2F.MU","BAS.MU","B5A.MU","9BX.MU","BAYN.MU","BEI.MU","BME.MU","CHY1.MU","3IW.MU","BRM.MU","COK.MU","11L1.MU","3CC.MU","8CT.MU","CAN.MU","C5Y.MU","U7N1.MU","2BC.MU","CAP.MU","CAR.MU","C57.MU","1CA1.MU","CAT1.MU","CHV.MU","M4B.MU","C53.MU","CNP.MU","COY.MU","C1O.MU","COI.MU","D7H.MU","308.MU","CO3A.MU","1COV.MU","DEX.MU","DEZ.MU","1P2.MU","0M4.MU","EN3.MU","E2N.MU","E0P.MU","2TR.MU","44T.MU","B4U.MU","ENQ.MU","ENUR.MU","ENUA.MU","E65A.MU","W2L.MU","FIE.MU","PLL.MU","5FB.MU","FRE.MU","GRA.MU","9GR.MU","GRR.MU","G3C.MU","41G1.MU","GRF.MU","4M4.MU","TEN.MU","1GU.MU","HOT.MU","INH.MU","B6IH.MU","4HB.MU","HO2.MU","HOX.MU","2IB.MU","INL.MU","I3R.MU","03M.MU","6IS.MU","1L3.MU","LIN.MU","LTC.MU","M6G.MU","U1P.MU","M0R.MU","MA6.MU","68M.MU","MEO.MU","M8Y.MU","M14.MU","S2M.MU","P1J1.MU","30M.MU","PAE.MU","PAR.MU","PRA.MU","PRG.MU","A3N1.MU","T4VI.MU","8XC.MU","R9H.MU","01X.MU","19S.MU","2S8.MU","SAYN.MU","77S.MU","SAP.MU","SEE.MU","6LD.MU","S7U.MU","SEO.MU","0RS.MU","SOH.MU","SPT6.MU","N4D.MU","2S7.MU","9LMA.MU","STP.MU","STE.MU","TEKB.MU","4LL.MU","3T4.MU","THYG.MU","THS.MU","TRS.MU","PA9.MU","TWR.MU","B8W.MU","E2E.MU","1GX.MU","HO1.MU","1E8.MU","G5N.MU"]

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
