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
    available_tickers = ["DLEKG.TA","ESLT.TA","EZCH.TA","EVGN.TA","ELTR.TA","AVNR-L.TA","FRUT.TA","JOEL.TA","JBKT.TA","JBNK.TA","KMDA.TA","KTOV.TA","KRUR.TA","KNFM.TA","KETR.TA","TEVA.TA","SCIX.TA","ICL.TA","BLRX.TA","UNON.TA","MZTF.TA","MZOR.TA","NFTA.TA","SPNS.TA","NVMI.TA","NTO.TA","NISA.TA","NFEX-L.TA","ORL.TA","ORAD.TA","GIVO-L.TA","QNCO.TA","QLTU.TA","RMLI.TA","PLX.TA","MNKD.TA","LPSN.TA","DRCN.TA","VISN.TA","VILR.TA","VTNA.TA","WTS.TA","WIZP.TA","XENA.TA","XTLB.TA","KRYT.TA","YBOX.TA","SEFA.TA","SRFT.TA","ZNKL.TA","ZRAH-L.TA","ZMH.TA","ZUR.TA","ABTR.TA","ABIL.TA","ALD.TA","ADO.TA","ADN.TA","ADGR.TA","AFIL.TA","AFRE.TA","AFPR.TA","AFHL.TA","APIO.TA","AFID.TA","BRMG.TA","ELAL.TA","MAXM.TA","BSI.TA","ALBA.TA","ALVR.TA","ALGS.TA","ALMD.TA","ALLT.TA","ALRPR.TA","ALHE.TA","ALMO.TA","AMRK.TA","AMOT.TA","AMAN.TA","AMS.TA","AMNS.TA","AMNS-R5.TA","ANLT.TA","KARE.TA","NSEL.TA","MGDL.TA","ANGL.TA","ENRS.TA","AOC.TA","APLY.TA","APOS.TA","ARYT.TA","ARNA.TA","ARKO.TA","ARPT.TA","ARD.TA","ARAN.TA","ARAD.TA","ARGM.TA","ARZM.TA","ASPR.TA","SVAS.TA","ASHO.TA","ASGR.TA","ASHG.TA","ASRR.TA","ASDR.TA","AURA.TA","AVGL.TA","AVER.TA","AVLN.TA","AVRT-M.TA","AVIA.TA","AVIV.TA","AYAL-L.TA","AZRG.TA","AZRM.TA","BRAN.TA","BBYL.TA","LUMI.TA","BCOM.TA","BCNV.TA","BEZQ.TA","BNTM-L.TA","BGI.TA","RDHL.TA","CBI.TA","BIRM-L.TA","NAVB.TA","BVXV.TA","BIOV.TA","BTX.TA","THXBY.TA","GLTN.TA","BIG.TA","VAXL-M.TA","DNA.TA","BNIN.TA","BICL.TA","BONS.TA","CANF.TA","BOLT.TA","HDST.TA","BLSR.TA","PROB-L.TA","BMDX.TA","BOTI-L.TA","BRIL.TA","BRIN.TA","DUNI.TA","BSP.TA","BSEN.TA","IBLD.TA","BUY2.TA","SHOM.TA","CDEV.TA","BYAR.TA","BYSD.TA","ISCN.TA","CRNT.TA","CLSN.TA","CEL.TA","PLAZ.TA","CFX.TA","CGEN.TA","CHAM.TA","CNMA-L.TA","CISY.TA","OR.TA","CLIS.TA","CLPT.TA","CMER.TA","CMDR.TA","CPHO-M.TA","CPTP.TA","CRMT.TA","CRSO.TA","CTPL5-L.TA","CTPL1.TA","MDPR.TA","CYRN.TA","DANH.TA","DANE.TA","DCI.TA","DEDR.TA","DISI.TA","DSCT.TA","DIFI.TA","DIMRI.TA","NNDM.TA","DLEN.TA","DLMT.TA","DLEA.TA","DORI.TA","DPRM.TA","DRAL.TA","DRSL.TA","HGG.TA","DXIL.TA","ECJM.TA","ECP.TA","EDRL.TA","EMTC.TA","ELRN.TA","EMITF.TA","ELLO.TA","ELDAV.TA","SUNY.TA","ELCO.TA","ELCRE.TA","ELSPC.TA","EMCO.TA","EMDV.TA","MGIC.TA","MDIN-L.TA","GLVR.TA","EQTL.TA","ROTS.TA","POLY-L.TA","ETVW.TA","RATI-L.TA","EXPO.TA","EXEN.TA","EXCE.TA","FNTS.TA","FBRT.TA","FIBI.TA","PLTF.TA","FNFR.TA","FOX.TA","FORTY.TA","FRST.TA","FRDN.TA","FTIN.TA","FVT.TA","GAON.TA","SOG.TA","GZT.TA","GAMT-L.TA","GEFEN.TA","GFC.TA","PRGO.TA","GIBC.TA","GILT.TA","GLPL.TA","GLEX.TA","GMUL.TA","GNGR.TA","GODM.TA","IGLD.TA","GOLF.TA","GOHO.TA","GOLD.TA","SCOP.TA","GSFI.TA","HAHO-L.TA","HAML.TA","POLI.TA","HAMAT.TA","HAP.TA","MSAH.TA","HARL.TA","HMAM.TA","OPK.TA","HLAN.TA","TTAM.TA","HLDS-L.TA","HNMR.TA","LBTL.TA","HRON.TA","IBI.TA","ICCM.TA","IDIN.TA","IDBD.TA","IE.TA","IES.TA","PTNR.TA","PLST.TA","ITMR.TA","TSEM.TA","TLSY.TA","TFRE.TA","TDRN.TA","SPEN.TA","SKBN.TA","RPAC.TA","RLCO.TA","RIT1.TA","RHTCH.TA","PZOL.TA","PLRM.TA","MTRX.TA","MSLA.TA","MMHD.TA","MLSR.TA","MEDI.TA","LEVA.TA","INTP.TA","INSL.TA","ININ.TA","IMCO.TA","ILCO.TA","PRSK.TA","TALD.TA","MISH.TA","LDER.TA","ORON.TA","LODZ.TA","MTMY.TA","PEN.TA","INFR.TA","MNIN.TA","PAYT.TA","PRTL.TA","MCRNL.TA","SRAC.TA","REKA.TA","SPCH.TA","MRPR.TA","RABN.TA","MDVI.TA","SFLG-L.TA","PERI.TA","STCM.TA","NICE.TA","NEZU.TA","ISTA.TA","SNEL.TA","CAST.TA","SLGN.TA","INCR.TA","ISRS.TA","ISRO.TA","NCT.TA","TIGBUR.TA","MLTM.TA","TAYA.TA","TATT.TA","MAYN-M.TA","MDTR.TA","JTI.TA","ORBI.TA","NZHT.TA","ISOP-L.TA","ONE.TA","TEDE.TA","KMNK.TA","BRAM.TA","KLNT.TA","MRHL.TA","TEFN.TA","KRIS.TA","INRM.TA","CHR.TA","RSEL.TA","SDS.TA","PLSN.TA","NXTM.TA","NXGN.TA","CAMT.TA","TUZA.TA","SALG.TA","UNIT.TA","NETZ.TA","PPIL.TA","ORTC.TA","PIU.TA","MNRV.TA","RIMO.TA","OHH.TA","SOHO.TA","PLRC.TA","LEVI.TA","KLIN-M.TA","WLFD.TA","LPHL-L.TA","SLARL.TA","MDGS.TA","STRS.TA","TZMI.TA","NAWI.TA","SODA.TA","SHAN.TA","ENLT.TA","TFVC.TA","MGOR.TA","OBAS.TA","LAHAV.TA","AUDC.TA","SMT.TA","PTBL.TA","ITYF.TA","PHOE.TA","TREN.TA","ULTR.TA","LVPR.TA","SHNP.TA","VCTR.TA","SCC.TA","USER-M.TA","OPCT.TA","SAE.TA","ORTM.TA","KDST.TA","KLIL.TA","NAMN.TA","SPNTC.TA","TDGN.TA","SNTG.TA","NTML.TA","MABR.TA","MCTC.TA","PLIND.TA","ENRG.TA","INTR.TA","MEDN-L.TA","SNFL.TA","MMAN.TA","WTPI-M.TA","PNTR.TA","OPAL.TA","LUDN.TA","ISRA-L.TA","TOPS.TA","LAPD.TA","TNPV.TA","SANO1.TA","TMDA.TA","SILC.TA","SMNIN.TA","LDRC.TA","ORIN.TA","ITRN.TA","KAFR.TA","NERZ.TA","MTDS.TA","GRNG-L.TA","MTCO.TA","ILX.TA","MBMX.TA","PTCH.TA","ILDC.TA","MSHR.TA","BRND.TA","TFRLF.TA","PCBT.TA","LHIS.TA","ENDY.TA","MDCL.TA","TUBE.TA","TIVA-L.TA","LEOF.TA","DELT.TA","OSEM.TA","MYDS.TA","WSMK.TA","MTRN.TA","NTGR.TA","NRH.TA","RMN.TA","HOD.TA","RAVD.TA","RVL.TA","PRTC.TA","KRNV.TA","KEN.TA","MYSZ.TA","MYL.TA","NSTR.TA","ORA.TA","PHMD.TA","PSTI.TA","SKLN.TA","SMTO.TA"]

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
