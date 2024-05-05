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
    available_tickers = ["E5H.SI","AU8U.SI","A23.SI","J7X.SI","5IB.SI","B32.SI","N21.SI","B2F.SI","BN4.SI","K29.SI","J37.SI","MU7.SI","J36.SI","F10.SI","D05.SI","D03.SI","D79.SI","D11.SI","CZ4.SI","AJBU.SI","5CH.SI","T16.SI","MT1.SI","LG8.SI","LG6.SI","K2M.SI","S63.SI","S59.SI","P40U.SI","EB5.SI","5GB.SI","G07.SI","5OU.SI","5ME.SI","5DN.SI","U04.SI","T8JU.SI","R07.SI","LS9.SI","ER0.SI","E13.SI","C2PU.SI","B61.SI","AW9U.SI","A78.SI","5KU.SI","ND8U.SI","J69U.SI","F34.SI","K2N.SI","F99.SI","F01.SI","G13.SI","MC7.SI","K6S.SI","OV8.SI","MR8.SI","MC0.SI","H07.SI","SK7.SI","RF1U.SI","RC5.SI","NS8U.SI","N2H.SI","MS7.SI","H64.SI","BCV.SI","B58.SI","AK3.SI","5VJ.SI","5FX.SI","Y03.SI","V69.SI","U10.SI","T03.SI","S7P.SI","S41.SI","S21.SI","J03.SI","J10.SI","J91U.SI","UD2.SI","N33.SI","K1Q.SI","J2T.SI","J17.SI","E9L.SI","C8R.SI","C07.SI","5FA.SI","5PF.SI","42R.SI","BEX.SI","J18.SI","JA9.SI","BEW.SI","IH1.SI","JC6.SI","CW4.SI","J0M.SI","5WR.SI","K71U.SI","K3OD.SI","K22.SI","Y34.SI","MV4.SI","KT9.SI","KJ9.SI","K3SD.SI","K3PD.SI","K3HD.SI","K14.SI","G41.SI","G11.SI","F1E.SI","EB7.SI","E90.SI","C86.SI","BLT.SI","BDN.SI","ADN.SI","5TT.SI","5MZ.SI","5MC.SI","5DL.SI","554.SI","504.SI","SK3.SI","KF8.SI","K3KD.SI","U96.SI","NF1.SI","PA3.SI","M26.SI","Z78.SI","5DM.SI","Y08.SI","R01.SI","S51.SI","ME8U.SI","M44U.SI","M11.SI","N03.SI","G0I.SI","O39.SI","O32.SI","O08.SI","5CF.SI","TS0U.SI","O9E.SI","O5RU.SI","O2I.SI","G4F.SI","EH5.SI","5PL.SI","5FI.SI","41X.SI","O9B.SI","508.SI","P13.SI","T13.SI","Q01.SI","QF6.SI","Q5T.SI","Q0X.SI","5I0.SI","QS0.SI","QR9.SI","QL2.SI","QK9.SI","QC7.SI","BCW.SI","Q7W.SI","QL3.SI","QS9.SI","Q1P.SI","Q0F.SI","Q0W.SI","W81.SI","T82U.SI","S6NU.SI","RW0U.SI","S46.SI","S19.SI","U11.SI","C52.SI","U14.SI","T39.SI","C76.SI","C38U.SI","T19.SI","T08.SI","S68.SI","W05.SI","T43.SI","T41.SI","T14.SI","558.SI","U9E.SI","U19.SI","U06.SI","I17.SI","H78.SI","G1O.SI","E16.SI","BGO.SI","V03.SI","535.SI","PH0.SI","BN2.SI","569.SI","545.SI","HD9.SI","BIP.SI","40N.SI","BJD.SI","K01.SI","M35.SI","E3B.SI","B49.SI","5RJ.SI","C50.SI","N0Z.SI","5F7.SI","J0P.SI","T06.SI","MN5.SI","M9F.SI","I04.SI","BRE.SI","X06.SI","K6Y.SI","J0O.SI","BQC.SI","KT2.SI","KV5.SI","IH4.SI","HD6.SI","KJ6.SI","LG7.SI","KV8.SI","J0R.SI","J0N.SI","CX5.SI","J0Q.SI","KJ7.SI","IH0.SI","KT3.SI","KT4.SI","BQF.SI","LG9.SI","KF6.SI","Z25.SI","Y92.SI","F13.SI","BS6.SI","AFC.SI","E02.SI","BJV.SI","BCD.SI","AWS.SI","Y35.SI","E6A.SI","G10.SI","AXB.SI","K3GD.SI","5BS.SI","BKX.SI","BPF.SI","Y06.SI","Z59.SI","AXC.SI","SO7.SI","5KK.SI","Y45.SI","Z77.SI","Z74.SI","Z01.SI","D5N.SI","5SR.SI","40W.SI","5KT.SI","I9T.SI","K3TD.SI","5EG.SI","AAJ.SI","5GZ.SI","A35.SI","533.SI","L5I.SI","541.SI","ADQU.SI","ACW.SI","ACV.SI","G1K.SI","AYW.SI","AYV.SI","A59.SI","P60.SI","A75.SI","A31.SI","AD8.SI","PU6D.SI","K3JD.SI","K3QD.SI","5IA.SI","BLZ.SI","K3CD.SI","N6DD.SI","ADJ.SI","K3UD.SI","ADP.SI","AXH.SI","5EF.SI","K3MD.SI","K3RD.SI","N6ED.SI","AWX.SI","AWG.SI","AWQ.SI","AWY.SI","P8Z.SI","5JS.SI","BNE.SI","F9M.SI","NC2.SI","AGS.SI","C6L.SI","C6U.SI","AI1.SI","A0P.SI","AIY.SI","AJ2.SI","A13.SI","5TS.SI","S91.SI","40F.SI","A34.SI","M1P.SI","H1O.SI","G3B.SI","AOF.SI","MF5.SI","A52.SI","AUE.SI","G5X.SI","KI3.SI","P11.SI","AO9.SI","F18.SI","AP4.SI","5RA.SI","5AU.SI","P5P.SI","D1R.SI","5NK.SI","BLGR.SI","B03.SI","A04.SI","H22.SI","CY6U.SI","A55.SI","A30.SI","585.SI","43D.SI","A68U.SI","BQI.SI","S7OU.SI","5EW.SI","RE2.SI","I98.SI","BEC.SI","5CR.SI","BAZ.SI","41C.SI","5WE.SI","A17U.SI","42S.SI","M62.SI","5WV.SI","5UE.SI","LF1.SI","N6M.SI","MT7.SI","O9P.SI","GH3.SI","505.SI","575.SI","5AM.SI","5UL.SI","5ET.SI","ATL.SI","ATN.SI","5GJ.SI","T42.SI","KV6.SI","CT1.SI","G92.SI","BKY.SI","AVZ.SI","AVW.SI","AVV.SI","AVY.SI","AVM.SI","AVX.SI","A05.SI","AWF.SI","AWN.SI","AWI.SI","AWE.SI","AWK.SI","AWV.SI","AWZ.SI","AWO.SI","AWP.SI","AWC.SI","AWM.SI","5CP.SI","AXJ.SI","AXL.SI","AXYU.SI","AXZ.SI","AXA.SI","42U.SI","AXV.SI","AYN.SI","AYC.SI","AYM.SI","AYO.SI","AYD.SI","AYE.SI","AYB.SI","AYL.SI","AYF.SI","AYG.SI","AZA.SI","AZX.SI","AZI.SI","AZG.SI","AZB.SI","AZS.SI","AZY.SI","AZR.SI","AZW.SI","AZZ.SI","BBW.SI","AZT.SI","568.SI","G50.SI","G08.SI","BAI.SI","BBQ.SI","BBP.SI","KJ5.SI","BCY.SI","BCX.SI","BCZ.SI","BDG.SI","BDX.SI","BDR.SI","BDY.SI","BDV.SI","BDF.SI","BDA.SI","BDU.SI","H13.SI","BEH.SI","SGF16-C.SI","AD7.SI","B66.SI","L09.SI","BEI.SI","BEZ.SI","BESU.SI","BEV.SI","5ER.SI","BFU.SI","BFI.SI","BFK.SI","BFT.SI","BGK.SI","NC9.SI","BHQ.SI","BHK.SI","BHP.SI","BQN.SI","BHO.SI","BHU.SI","BHD.SI","BMGU.SI","L46.SI","B20.SI","587.SI","42C.SI","BIX.SI","42H.SI","BJE.SI","BJK.SI","BJZ.SI","BJL.SI","BJW.SI","BKA.SI","BKW.SI","BKK.SI","O15.SI","BKB.SI","BKZ.SI","BKV.SI","BLYR.SI","BLR.SI","BLH.SI","BLU.SI","BLA.SI","BLS.SI","UQ7.SI","BLW.SI","BLL.SI","41H.SI","MQ4.SI","FQ8.SI","C71.SI","B73.SI","B16.SI","N4E.SI","C37.SI","BMT.SI","O2F.SI","5GD.SI","D01.SI","5DW.SI","M41.SI","DK2.SI","L28.SI","T18.SI","C56.SI","T15.SI","BMH.SI","S3N.SI","B0I.SI","M04.SI","BR9.SI","546.SI","P36.SI","FP1.SI","BMA.SI","F12.SI","L34.SI","D38.SI","F11.SI","L22.SI","B10.SI","F9D.SI","B28.SI","BOL.SI","BOU.SI","BQP.SI","BQSR.SI","BQM.SI","BQD.SI","BQO.SI","5DA.SI","B69.SI","BRIR.SI","K75.SI","BRD.SI","SV3U.SI","C61U.SI","5EC.SI","C31.SI","CC3.SI","J85.SI","P15.SI","TQ5.SI","OU8.SI","5EB.SI","573.SI","D50.SI","C05.SI","528.SI","S24.SI","A7S.SI","HD8.SI","I54.SI","C33.SI","RS1.SI","K3ED.SI","5CJ.SI","D4N.SI","5TW.SI","42E.SI","C29.SI","5OX.SI","GU5.SI","C09.SI","P9D.SI","C70.SI","A7RU.SI","5HJ.SI","C22.SI","C03.SI","42F.SI","5GC.SI","539.SI","A0W.SI","544.SI","C06.SI","5TI.SI","C14.SI","CZ3.SI","P12.SI","D04.SI","5CB.SI","HE0.SI","O9C.SI","N2F.SI","HD7.SI","KV4.SI","KF7.SI","N2E.SI","O9D.SI","SH8.SI","IH2.SI","K6K.SI","KV7.SI","LF2.SI","IH3.SI","O9A.SI","KF5.SI","GJ8.SI","D07.SI","I21.SI","DM0.SI","DU4.SI","5SO.SI","D6U.SI","NO4.SI","N0L.SI","O10.SI","5TJ.SI","5HV.SI","5CT.SI","NR7.SI","RQ1.SI","5HG.SI","586.SI","EE6.SI","EG0.SI","42Z.SI","500.SI","581.SI","F03.SI","42O.SI","5DE.SI","H1N.SI","UQ4.SI","S44.SI","RE4.SI","R14.SI","MF6.SI","A02.SI","594.SI","L23.SI","TI6.SI","5MQ.SI","532.SI","FO8.SI","ES3.SI","40S.SI","G54.SI","5RC.SI","H1Q.SI","JC5.SI","G1M.SI","A9A.SI","G1N.SI","JC7.SI","P58.SI","H1P.SI","A9B.SI","E27.SI","5G1.SI","E23.SI","5FL.SI","F22.SI","5WJ.SI","S23.SI","K03.SI","P34.SI","F25U.SI","H30.SI","5OI.SI","T4B.SI","P74.SI","FQ7.SI","E28.SI","P2Q.SI","D2U.SI","RF7.SI","5CQ.SI","5IG.SI","O02.SI","41T.SI","5VP.SI","GG7.SI","GG0.SI","B7K.SI","543.SI","595.SI","P9J.SI","UD3.SI","O87.SI","L38.SI","K6J.SI","41B.SI","UD1U.SI","5PC.SI","5TP.SI","G20.SI","T77.SI","MR7.SI","H18.SI","G18.SI","43A.SI","J16.SI","41F.SI","F17.SI","H02.SI","5VS.SI","C92.SI","P47.SI","5DP.SI","41A.SI","KF4.SI","5NG.SI","5OR.SI","5PD.SI","526.SI","510.SI","5PO.SI","5JK.SI","H17.SI","S07.SI","H27.SI","588.SI","K3FD.SI","I07.SI","H20.SI","B1N.SI","H15.SI","P7VU.SI","H73.SI","H16.SI","H19.SI","600.SI","5I4.SI","5TN.SI","I49.SI","5WA.SI","42T.SI","U77.SI","42N.SI","571.SI","I11.SI","I15.SI","5WF.SI","I19.SI","40T.SI","IW5.SI","IX2.SI","5I3.SI","BAC.SI","JK8.SI","S2D.SI","5OS.SI","K11.SI","42G.SI","5ML.SI","5G2.SI","5I1.SI","5BK.SI","5VC.SI","K3ID.SI","5OC.SI","578.SI","40I.SI","B0Z.SI","G86.SI","A26.SI","S9B.SI","5HH.SI","5EL.SI","593.SI","B26.SI","D8DU.SI","41O.SI","L10.SI","S05.SI","5TR.SI","5MD.SI","LJ3.SI","5VI.SI","540.SI","O6Z.SI","5IE.SI","K2LU.SI","5LY.SI","L19.SI","P2P.SI","D5IU.SI","B1ZU.SI","N2IU.SI","M15.SI","5QR.SI","5UF.SI","5RF.SI","5MS.SI","5DS.SI","5NF.SI","5BM.SI","5EN.SI","5DD.SI","40U.SI","M05.SI","N5YD.SI","F86.SI","42D.SI","5IF.SI","N01.SI","N08.SI","5QY.SI","5UJ.SI","N32.SI","5GF.SI","547.SI","N02.SI","5HC.SI","579.SI","584.SI","557.SI","C13.SI","U6C.SI","ON7.SI","O23.SI","BER.SI","5UX.SI","P52.SI","596.SI","T8V.SI","P19.SI","K3DD.SI","C9Q.SI","P31.SI","T12.SI","5AE.SI","P01.SI","5BI.SI","F3EU.SI","5WD.SI","L6T.SI","E8Z.SI","H12.SI","A50.SI","E6R.SI","580.SI","M1GU.SI","S61.SI","M30.SI","S69.SI","S85.SI","S08.SI","5CN.SI","591.SI","564.SI","T55.SI","T35.SI","T09.SI","M14.SI","L17.SI","I03.SI","F3V.SI","D3W.SI","5WH.SI","5KI.SI","5GI.SI","566.SI","S71.SI","I5H.SI","F83.SI","U13.SI","L02.SI","P8A.SI","567.SI","L20.SI","5TG.SI","C41.SI","5UZ.SI","U09.SI","5F4.SI","40D.SI","5UN.SI","S49.SI","561.SI","583.SI","T6I.SI","T24.SI","C10.SI","5NV.SI","5OQ.SI","C2J.SI","5H0.SI","T8B.SI","B9S.SI","U05.SI","5DO.SI","S53.SI","40R.SI","5UO.SI","570.SI","5PI.SI","CH8.SI","5G9.SI","5QT.SI","M01.SI","M03.SI","V01.SI","40V.SI","S56.SI","5UA.SI","5HT.SI","UV1.SI","40E.SI","574.SI","5FW.SI","5OF.SI","5FR.SI","I85.SI","42L.SI","40B.SI","E94.SI","BAJ.SI","K2P.SI","43B.SI","5G3.SI","T4E.SI","S29.SI","BAA.SI","5AI.SI","SK6U.SI","5IC.SI","5UV.SI","M1Z.SI","F31.SI","S58.SI","502.SI","L03.SI","C04.SI","5FQ.SI","5LE.SI","S35.SI","5MM.SI","S10.SI","5RE.SI","5DX.SI","I06.SI","5OT.SI","5AB.SI","S20.SI","S45U.SI","5SY.SI","5EV.SI","A6F.SI","5WG.SI","B08.SI","S27.SI","N6FD.SI","UR9.SI","C0Z.SI","BRJR.SI"]

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
