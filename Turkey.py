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
    available_tickers = ["SELEC.IS","PSDTC.IS","GLBMD.IS","EREGL.IS","ANSA.IS","THYAO.IS","TSKB.IS","PRKAB.IS","KORDS.IS","KARTN.IS","ENKAI.IS","ASYAB.IS","ADEL.IS","VAKFN.IS","KRTEK.IS","MARTI.IS","SANKO.IS","PINSU.IS","TCHOL.IS","ATAGY.IS","OYLUM.IS","ODAS.IS","ISYAT.IS","FROTO.IS","ETYAT.IS","ALGYO.IS","AKSGY.IS","METUR.IS","OZGYO.IS","OLMIP.IS","YKGYO.IS","ISGSY.IS","TUPRS.IS","YAPRK.IS","HURGZ.IS","EGSER.IS","EGPRO.IS","EDIP.IS","CIMSA.IS","BRSAN.IS","AKCNS.IS","CEMTS.IS","KARSN.IS","TMSN.IS","MIPAZ.IS","PETUN.IS","TTRAK.IS","KILER.IS","GSRAY.IS","ANELT.IS","SANEL.IS","SAMAT.IS","INTEM.IS","ASELS.IS","ECILC.IS","FMIZP.IS","ERBOS.IS","ATPET.IS","TMPOL.IS","GOLTS.IS","IPEKE.IS","BRISA.IS","VANGD.IS","ESEMS.IS","SISE.IS","BURVA.IS","KERVT.IS","AKSUE.IS","TKNSA.IS","UNYEC.IS","NIBAS.IS","SKPLC.IS","VKING.IS","VAKKO.IS","EPLAS.IS","KRATL.IS","INDES.IS","CUSAN.IS","YKBNK.IS","ANELE.IS","KAPLM.IS","ARENA.IS","DEVA.IS","AFYON.IS","OYAYO.IS","EGCYO.IS","FONSY.IS","PAGYO.IS","YYAPI.IS","DGGYO.IS","GLRYH.IS","IHYAY.IS","GENYH.IS","ATSYH.IS","DZGYO.IS","ISMEN.IS","ISGYO.IS","YAYLA.IS","SRVGY.IS","YESIL.IS","EGYO.IS","GRNYO.IS","RAYSG.IS","HDFGS.IS","IDGYO.IS","AVGYO.IS","NUGYO.IS","FVORI.IS","VKFYO.IS","MERIT.IS","ECBYO.IS","YGYO.IS","UZERB.IS","ATLAS.IS","DOBUR.IS","YUNSA.IS","LINK.IS","GNPWR.IS","DENGE.IS","ISYHO.IS","VERTU.IS","ULAS.IS","MRGYO.IS","EGLYO.IS","AVTUR.IS","EUHOL.IS","BANVT.IS","EUKYO.IS","PRZMA.IS","DAGHL.IS","FNSYO.IS","MEMSA.IS","PEGYO.IS","EKGYO.IS","KLGYO.IS","OZKGY.IS","INFO.IS","HLGYO.IS","METAL.IS","RHEAG.IS","BJKAS.IS","EGCYH.IS","KRGYO.IS","VKGYO.IS","GDKGS.IS","EUYO.IS","METRO.IS","RYSAS.IS","LOGO.IS","YGGYO.IS","TRGYO.IS","ARTI.IS","BLCYT.IS","CMBTN.IS","DITAS.IS","KUYAS.IS","SEYKM.IS","GEDIK.IS","ALYAG.IS","BOYP.IS","YAZIC.IS","AKMGY.IS","ARFYO.IS","YONGA.IS","MMCAS.IS","KERVN.IS","YBTAS.IS","RYGYO.IS","AKPAZ.IS","OSTIM.IS","KPHOL.IS","GYHOL.IS","AVHOL.IS","TURGG.IS","TSPOR.IS","YATAS.IS","SNGYO.IS","SAYAS.IS","ETILR.IS","COSMO.IS","SAFGY.IS","GLYHO.IS","AKSEL.IS","AGYO.IS","BRYAT.IS","ECZYT.IS","TSGYO.IS","MZHLD.IS","GEDZA.IS","TEKTU.IS","KOZAA.IS","ZOREN.IS","ACSEL.IS","ANACM.IS","ADESE.IS","ADBGR.IS","SASA.IS","ADNAC.IS","AEFES.IS","AFMAS.IS","TARAF.IS","FENER.IS","AKENR.IS","AKBNK.IS","USAK.IS","USAS.IS","AKGUV.IS","AKSA.IS","AKSEN.IS","AKFGY.IS","ATEKS.IS","PKART.IS","AKGRT.IS","AKFEN.IS","DOCO.IS","ALCTL.IS","ALKA.IS","ALBRK.IS","FENIS.IS","IHEVA.IS","RTALB.IS","MAALT.IS","ALARK.IS","HALKB.IS","AYCES.IS","TUCLK.IS","ALCAR.IS","ALKIM.IS","KOZAL.IS","DURDO.IS","SEKUR.IS","BAKAB.IS","BNTAS.IS","EMNIS.IS","PGSUS.IS","ARTOG.IS","TEKST.IS","MCTAS.IS","AYES.IS","BEYAZ.IS","ASUZU.IS","OZBAL.IS","PLASP.IS","MEGAP.IS","BASCM.IS","ANSGR.IS","ANHYT.IS","MANGO.IS","IHMAD.IS","ORMA.IS","TKURU.IS","ADANA.IS","IZFAS.IS","ASCEL.IS","MEPET.IS","EKIZ.IS","BTCIM.IS","VAKBN.IS","FLAP.IS","ARCLK.IS","ARMDA.IS","ARSAN.IS","KATMR.IS","ARBUL.IS","IHGZT.IS","ASLAN.IS","KRONT.IS","IDAS.IS","CEMAS.IS","MENBA.IS","HITIT.IS","TOASO.IS","BAKAN.IS","DESPC.IS","ISATR.IS","AVISA.IS","AVOD.IS","AYGAZ.IS","DERIM.IS","AYEN.IS","GARAN.IS","ISBTR.IS","ISKUR.IS","BERDN.IS","VESBE.IS","BFREN.IS","KOMHL.IS","DGATE.IS","BIMAS.IS","BIZIM.IS","BRMEN.IS","BMEKS.IS","ULKER.IS","BISAS.IS","TBORG.IS","BRKO.IS","ICBCT.IS","DENIZ.IS","SKBNK.IS","KLNMA.IS","DYOBY.IS","CBSBO.IS","BOSSA.IS","BMELK.IS","MRSHL.IS","BOLUC.IS","DOGUB.IS","BOYNR.IS","GUBRF.IS","ISBIR.IS","BSOKE.IS","BUCIM.IS","BURCE.IS","PRTAS.IS","CCOLA.IS","CELHA.IS","CLKHO.IS","CLEBI.IS","CMENT.IS","CRFSA.IS","CRDFA.IS","ISCTR.IS","SODA.IS","DARDL.IS","DAGI.IS","ISDMR.IS","TUDDF.IS","GOZDE.IS","DGKLB.IS","DGZTE.IS","GSDHO.IS","TGSAS.IS","MRDIN.IS","GEDIZ.IS","DIRIT.IS","KRDMD.IS","KRDMA.IS","DMSAS.IS","KRDMB.IS","DOAS.IS","DOHOL.IS","MNDRS.IS","SODSN.IS","EGEEN.IS","EGGUB.IS","IEYHO.IS","EMKEL.IS","VESTL.IS","PRKME.IS","ORGE.IS","GEREL.IS","SONME.IS","ESCOM.IS","SARKY.IS","TCELL.IS","KAREL.IS","ULUSE.IS","ERSU.IS","OZRDN.IS","ERICO.IS","BAGFS.IS","GARFA.IS","LIDFA.IS","FFKRL.IS","ITTFH.IS","SEKFK.IS","SANFM.IS","GENTS.IS","ISFIN.IS","TACTR.IS","FRIGO.IS","TUKAS.IS","KNFRT.IS","IZTAR.IS","PENGD.IS","UYUM.IS","KIPA.IS","MERKO.IS","MRTGG.IS","KENT.IS","SELGD.IS","GOODY.IS","GOLDS.IS","GSDDE.IS","GUSGR.IS","HALKS.IS","HATEK.IS","TAVHL.IS","HZNDR.IS","ROYAL.IS","NUHCM.IS","HEKTS.IS","LKMNH.IS","POLHO.IS","PETKM.IS","IHLAS.IS","SNKRN.IS","UTPYA.IS","IZOCM.IS","IZMDC.IS","JANTS.IS","OTKAR.IS","TIRE.IS","LUKSK.IS","KRSAN.IS","TRKCM.IS","KCHOL.IS","SERVE.IS","KLMSN.IS","KRSTL.IS","KONYA.IS","TATGD.IS","KSTUR.IS","COMDO.IS","MAKTK.IS","KUTPO.IS","LATEK.IS","TTKOM.IS","OSMEN.IS","MGROS.IS","UNICO.IS","FINBN.IS","DENCM.IS","NETAS.IS","NTTUR.IS","NTHOL.IS","TRNSK.IS","PARSN.IS","SNPAM.IS","UMPAS.IS","PKENT.IS","TRCAS.IS","PNSUT.IS","PIMAS.IS","POLTK.IS","BRKSN.IS","RODRG.IS","VERUS.IS","SILVR.IS","SKTAS.IS","ULUUN.IS","BALAT.IS","DESA.IS","TKFEN.IS","SAHOL.IS"]

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
