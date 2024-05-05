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
    available_tickers = ["TRAN.BA","APBR.BA","CSCO.BA","COME.BA","BHIP.BA","RIGO.BA","LEDE.BA","GCLA.BA","APBRA.BA","ABX.BA","MOLI.BA","TGNO4.BA","PSUR.BA","KOFM.BA","HD.BA","FERR.BA","FNMA.BA","FRAN.BA","SAMI.BA","SEMI.BA","JMIN.BA","PATY.BA","KO.BA","KMB.BA","TS.BA","YPCZO.BA","NEM.BA","OYP19.BA","NKE.BA","BRIO6.BA","BRIO.BA","DIY0.BA","AY24.BA","AS17.BA","AGRO.BA","DICE.BA","OVO3P.BA","AO20.BA","AO17.BA","AF17.BA","OAEY1.BA","OVOP.BA","CTIO.BA","OIRY7.BA","TVPP.BA","CO17.BA","PMD18.BA","SNP.BA","QCOM.BA","QCC8O.BA","VALE.BA","TGLT.BA","T.BA","YPCNO.BA","UTX.BA","ERAR.BA","WMT.BA","DISN.BA","WFC.BA","XOM.BA","YPCPO.BA","BDED.BA","GJ17.BA","BPLD.BA","XNC4O.BA","XNC6O.BA","XNC5O.BA","XNC3O.BA","XNC2O.BA","PBJ21.BA","TSC10.BA","AUY.BA","YPFD.BA","YHOO.BA","IRSA.BA","DOME.BA","CRES.BA","YZC.BA","YCA5O.BA","YCA2O.BA","PATA.BA","YCA7O.BA","YCABO.BA","YCA4O.BA","YCA8O.BA","ESTR.BA","YPCUC.BA","YPCUO.BA","OIRX6.BA","YPCRO.BA","OIRX7.BA","YCA6O.BA","OYPF0.BA","YCAAO.BA","GARO.BA","AAPL.BA","AA17D.BA","AA17C.BA","AA.BA","AA17Z.BA","AA17.BA","AA17X.BA","ABT.BA","MBT.BA","BP.BA","AD16X.BA","AD16D.BA","AEN.BA","AF17D.BA","CS.BA","NVS.BA","SIEGY.BA","INAG.BA","VALO.BA","INTR.BA","BD2C9.BA","AIG.BA","BBO16.BA","AJ17X.BA","AJ17.BA","GOOGL.BA","MO.BA","AL16X.BA","ALUA.BA","AL16.BA","AXP.BA","AM20.BA","AMGN.BA","AM18X.BA","AM17.BA","AMX9.BA","BA-C.BA","AM20D.BA","AM17X.BA","AMX8.BA","AM18.BA","AMX9X.BA","DYCA.BA","AN18X.BA","AN18.BA","AN18D.BA","AO16D.BA","AO20D.BA","AO20C.BA","AO20X.BA","AO17X.BA","AO16X.BA","APSA.BA","PETR.BA","INTC.BA","IBM.BA","CARC.BA","CAPU.BA","C.BA","BPAT.BA","TRVV.BA","PEP.BA","POLL.BA","PG.BA","PESA.BA","PAMP.BA","MORI.BA","MMM.BA","MIRG.BA","HSBC.BA","GG.BA","GFI.BA","FIPL.BA","DGCU2.BA","CVX.BA","COLO.BA","BNG.BA","BMA.BA","BBRY.BA","CEPU.BA","CAT.BA","FMX.BA","TSM.BA","CX.BA","TSCH9.BA","BDC18.BA","AY16.BA","MRK.BA","FCX.BA","TI.BA","GRIM.BA","MVIA.BA","NDG21.BA","DD.BA","BUN16.BA","AVP.BA","EBAY.BA","PHG.BA","DICY.BA","MCD.BA","PUM21.BA","JPM.BA","NOKA.BA","INVJ.BA","OCR14.BA","OGZD.BA","CELU.BA","ORCL.BA","SNE.BA","GNCEO.BA","PAA0.BA","EDN.BA","TXN.BA","BMA-5.BA","EMC.BA","CECO2.BA","MOLI5.BA","FORM3.BA","CHL.BA","RNG21.BA","MPC7O.BA","BA.BA","FMCC.BA","MDC4O.BA","PARP.BA","MELI.BA","PTR.BA","TUCS1.BA","ERG16.BA","DEO.BA","BHP.BA","BBD.BA","PR15.BA","NGG.BA","VZ.BA","LONG.BA","PARY.BA","TECO2.BA","NF18.BA","BCS.BA","BNN16.BA","H04Y6.BA","PUO19.BA","MON.BA","TVPA.BA","ERD16.BA","TVPY.BA","BADER.BA","LMT.BA","PR13.BA","CL.BA","OEST.BA","BDC19.BA","GBAN.BA","BOLT.BA","INDU.BA","HMY.BA","OCK2P.BA","NORT6.BA","PFE.BA","BBV.BA","HPQ.BA","AUSO.BA","PARA.BA","BSBR.BA","SLB.BA","VOD.BA","PMO18.BA","REGE.BA","ERJ17.BA","DIA0.BA","AD16.BA","RDS.BA","TXR.BA","DICP.BA","IBN.BA","HMC.BA","BD6C6.BA","BC2N6.BA","BMY.BA","CUAP.BA","E.BA","METR.BA","JNJ.BA","BNN17.BA","UN.BA","GGAL.BA","TM.BA","BAO17.BA","MSFT.BA","TOT.BA","SBUX.BA","ROSE.BA","MTU.BA","GE.BA","CGPA2.BA","BDC20.BA","PAP0.BA","GSK.BA","DIP0.BA","TGSU2.BA","ESME.BA","GN10Q.BA","DICA.BA","ORAN.BA","AZN.BA","SAP.BA","CADO.BA","CAPX.BA","AS17X.BA","AS16X.BA","AY24X.BA","AY24C.BA","AY24D.BA","STD.BA","BARY1.BA","BCG16.BA","BCN16.BA","BD2C0.BA","BD4C6.BA","BDEDD.BA","BD7C6.BA","BARX1.BA","BDC16.BA","BD2C6.BA","BFCGO.BA","BFCHO.BA","BFCBO.BA","BHCDO.BA","BHCXO.BA","TSC1O.BA","BNL17.BA","BNM17.BA","BNJ16.BA","BPLE.BA","BPMD.BA","BP21D.BA","BPLDD.BA","BP18.BA","BP28.BA","BP21.BA","BR00P.BA","IRCP.BA","BWS6V.BA","BY08C.BA","CEDI.BA","CG27C.BA","CG26B.BA","CG27B.BA","CG26C.BA","CLCEO.BA","CL4OD.BA","CLC4O.BA","CN15Q.BA","CN16Q.BA","CPC6O.BA","CPC2O.BA","CPC4O.BA","CSBNO.BA","CS9JO.BA","CSBMO.BA","CS8HO.BA","CUAPX.BA","CZ12B.BA","DICYC.BA","DICAX.BA","DICAC.BA","DIA0D.BA","DICAD.BA","DIE0.BA","DICPX.BA","DICYD.BA","ER2D6.BA","REP.BA","TEF.BA","GJ17C.BA","GJ17D.BA","GL08Q.BA","GLW.BA","GL08C.BA","LB2A6.BA","LCY16.BA","LDC3O.BA","LEY16.BA","LG72O.BA","MBCOO.BA","MDC6O.BA","ML09B.BA","ML10B.BA","MTALO.BA","MTAUO.BA","NF18X.BA","NF18C.BA","NJC3O.BA","NLC2V.BA","NO20.BA","NRH2.BA","NS00A.BA","NVC3O.BA","OAOY2.BA","OCEY1.BA","ODNY9.BA","OGBY1.BA","ONY13.BA","OPNY1.BA","OROY5.BA","OROY4.BA","PAC.BA","PARAC.BA","PARAX.BA","PAA0D.BA","PARE.BA","PAY0.BA","PARAD.BA","PBM24.BA","PNC7O.BA","PNC8O.BA","PNC4O.BA","PR15X.BA","RAC2O.BA","RCC8O.BA","RICLO.BA","RICGO.BA","RIK4O.BA","RICMO.BA","RIK2O.BA","RIK2P.BA","RIH2P.BA","RIH1O.BA","RICFO.BA","RIK1O.BA","RIJ2P.BA","RIK3O.BA","RIH2O.BA","RICOO.BA","RIJ1O.BA","RICNO.BA","RNG22.BA","SCCO.BA","SD13B.BA","SNS1O.BA","SSC5V.BA","SV3GO.BA","TSC11.BA","TSC12.BA","TSCH7.BA","TSCH8.BA","TUBB1.BA","TVPYD.BA","TVY0.BA","TVPPX.BA","TVPYX.BA","TVPE.BA","VC05A.BA","VC03B.BA","BAE17.BA","COLOX.BA","PARPX.BA","PRO9.BA","SARH.BA","TRCNO.BA"]

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
