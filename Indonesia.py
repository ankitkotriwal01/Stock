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
    available_tickers = ["AALI.JK","ANTM.JK","ASII.JK","AKRA.JK","BBCA.JK","APIC.JK","ADMF.JK","ADHI.JK","ADES.JK","INPC.JK","APLN.JK","ADRO.JK","PTBA.JK","BNII.JK","BNGA.JK","BBRI.JK","MAYA.JK","BNLI.JK","SDRA.JK","BBNI.JK","BMRI.JK","BFIN.JK","PNBN.JK","BKSW.JK","BCAP.JK","BJBR.JK","NISP.JK","BSDE.JK","BRMS.JK","BKSL.JK","BDMN.JK","BABP.JK","MEGA.JK","DSFI.JK","ELTY.JK","ABDA.JK","SMDM.JK","PDES.JK","LPPF.JK","MEDC.JK","ERAA.JK","MTDL.JK","ENRG.JK","KLBF.JK","PNLF.JK","CFIN.JK","KBLV.JK","FORU.JK","KAEF.JK","AISA.JK","GIAA.JK","KREN.JK","BMTR.JK","SULI.JK","PGAS.JK","SILO.JK","MYRX.JK","HERO.JK","AHAP.JK","ACES.JK","YPAS.JK","SMCB.JK","JSMR.JK","JPRS.JK","JKON.JK","JPFA.JK","PSAB.JK","PJAA.JK","JSPT.JK","JKSW.JK","JECC.JK","BJTM.JK","ASJT.JK","1562405.JK","DAJK.JK","JRPT.JK","ANJT.JK","JTPE.JK","KIJA.JK","BIKA.JK","KARW.JK","WIKA.JK","WSKT.JK","KINO.JK","INKP.JK","KPIG.JK","WTON.JK","TKIM.JK","PKPK.JK","MCOR.JK","LPKR.JK","KOIN.JK","KOBX.JK","KICI.JK","KBLI.JK","IKBI.JK","DGIK.JK","BRAM.JK","AKKU.JK","ICBP.JK","ITMG.JK","MTFN.JK","MERK.JK","INDF.JK","TIRT.JK","SMMA.JK","MYOH.JK","BCIC.JK","MLPL.JK","MLIA.JK","MDLN.JK","ROTI.JK","PTSN.JK","NIPS.JK","CPGT.JK","UNIT.JK","NIKL.JK","BSWD.JK","ISSP.JK","DKFT.JK","UNVR.JK","PTPP.JK","PANS.JK","PNIN.JK","INCO.JK","INTP.JK","TINS.JK","ISAT.JK","IMPC.JK","BIPI.JK","WEHA.JK","TBIG.JK","SMGR.JK","TURI.JK","SRIL.JK","RAJA.JK","GGRM.JK","BUMI.JK","ASRI.JK","ARII.JK","AGRO.JK","SQMI.JK","TLKM.JK","INDS.JK","CNTX.JK","BIRD.JK","SSMS.JK","PRAS.JK","UNTR.JK","UNIC.JK","TAXI.JK","RUIS.JK","MIDI.JK","BUKK.JK","MSKY.JK","BVIC.JK","VRNA.JK","FASW.JK","LION.JK","WOMF.JK","JAWA.JK","EXCL.JK","YULE.JK","BBYB.JK","ZBRA.JK","ABBA.JK","ABMM.JK","SRSN.JK","ACST.JK","MAPI.JK","ADMG.JK","MBAP.JK","ASSA.JK","POOL.JK","CSAP.JK","HEXA.JK","CASS.JK","SMRA.JK","SGRO.JK","AGRS.JK","MAGP.JK","SMAR.JK","FISH.JK","SOBI.JK","IIKP.JK","PALM.JK","AIMS.JK","AKPI.JK","AKSI.JK","ALMI.JK","TRUB.JK","TALF.JK","AMRT.JK","ALTO.JK","ALKA.JK","IKAI.JK","ALDO.JK","INAI.JK","KKGI.JK","AMFG.JK","AMIN.JK","AMAG.JK","DART.JK","ATIC.JK","SRAJ.JK","PSDN.JK","ITMA.JK","OKAS.JK","APOL.JK","APEX.JK","MYTX.JK","APII.JK","APLI.JK","ARNA.JK","BNBA.JK","ARTI.JK","ARGO.JK","MASA.JK","ARTO.JK","SCBD.JK","ARTA.JK","BAPA.JK","BIMA.JK","ASBI.JK","ASRM.JK","VIVA.JK","AUTO.JK","3800551.JK","ASMI.JK","KIAS.JK","ASDM.JK","ASGR.JK","POLY.JK","TRIM.JK","TPIA.JK","ATPK.JK","TIRA.JK","BATA.JK","TOBA.JK","TBLA.JK","SMBR.JK","BTPN.JK","BTEL.JK","BSSR.JK","BRPT.JK","BPII.JK","BNBR.JK","BBTN.JK","BBNP.JK","BALI.JK","BBKP.JK","1838362.JK","BBHI.JK","BPFI.JK","BBRM.JK","BYAN.JK","BBLD.JK","BBMD.JK","BCIP.JK","BEKS.JK","BRAU.JK","MBTO.JK","BTON.JK","BLTA.JK","BRNA.JK","RMBA.JK","BHIT.JK","HDFA.JK","BIPP.JK","BMSR.JK","BISI.JK","BINA.JK","RBMS.JK","MLBI.JK","BKDP.JK","BLTZ.JK","BOLT.JK","RANC.JK","BORN.JK","PBRX.JK","BSIM.JK","BTEK.JK","BUDI.JK","SKBM.JK","BUVA.JK","BULL.JK","BAYU.JK","GTBO.JK","BWPT.JK","MDIA.JK","CANI.JK","CENT.JK","CMPP.JK","CEKA.JK","CPRO.JK","CNTB.JK","FPNI.JK","CPIN.JK","LPCK.JK","SCMA.JK","MNCN.JK","GMCW.JK","CTRP.JK","NRCA.JK","CITA.JK","CTRA.JK","CTRS.JK","ECII.JK","CTBN.JK","2699991.JK","CTTH.JK","CINT.JK","CMNP.JK","CKRA.JK","CLPI.JK","CNKO.JK","DVLA.JK","DEWA.JK","DEFI.JK","SIDO.JK","DLTA.JK","COWL.JK","DSNG.JK","DILD.JK","DSSA.JK","DNAR.JK","GDST.JK","ERTX.JK","DMAS.JK","DNET.JK","SCPI.JK","DOID.JK","DPNS.JK","DPUM.JK","DUTI.JK","NELY.JK","DYAN.JK","SMMT.JK","LRNA.JK","EKAD.JK","BAEK.JK","ELSA.JK","VOKS.JK","EMTK.JK","EMDE.JK","TMAS.JK","HRUM.JK","SUGI.JK","1726328.JK","INDY.JK","EPMT.JK","GSMF.JK","ESTI.JK","ESSA.JK","BEST.JK","ETWA.JK","LCGP.JK","GREN.JK","FAST.JK","PYFA.JK","MAIN.JK","TIFA.JK","TRUS.JK","TFCO.JK","FMII.JK","GAMA.JK","GJTL.JK","GPRA.JK","GDYR.JK","LPGI.JK","GEMS.JK","GEMA.JK","PEGE.JK","RICY.JK","GLOB.JK","GMTD.JK","MDKA.JK","GZCO.JK","GOLL.JK","PTSP.JK","GOLD.JK","GWSA.JK","MYRXP.JK","HMSP.JK","HADE.JK","HDTX.JK","HITS.JK","IATA.JK","IBST.JK","IBFN.JK","ICON.JK","TSPC.JK","TRST.JK","TOTO.JK","TMPO.JK","TMPI.JK","TELE.JK","TCID.JK","STTP.JK","STAR.JK","SQBB.JK","SOCI.JK","SIAP.JK","RELI.JK","PUDP.JK","PTRO.JK","PSKT.JK","PADI.JK","MYOR.JK","MTLA.JK","MPPA.JK","MITI.JK","MFIN.JK","MBSS.JK","MAMIP.JK","LSIP.JK","LPIN.JK","LEAD.JK","INVS.JK","INTA.JK","INRU.JK","INAF.JK","IMAS.JK","MTSM.JK","META.JK","ITTG.JK","SDPC.JK","KOPI.JK","INDR.JK","KBLM.JK","INTD.JK","PANR.JK","TKGA.JK","MFMI.JK","INCI.JK","OCAP.JK","SQBI.JK","HOTL.JK","SMSM.JK","MIRA.JK","SCCO.JK","TPMA.JK","MTRA.JK","SKYB.JK","WINS.JK","INDX.JK","SMRU.JK","MLPT.JK","PTIS.JK","TOTL.JK","KRAS.JK","SONA.JK","PNBS.JK","IGAR.JK","TGKA.JK","MMLP.JK","MREI.JK","SIPD.JK","OMRE.JK","NOBU.JK","SAFE.JK","KRAH.JK","MPMX.JK","RALS.JK","MARI.JK","IMJS.JK","RDTX.JK","SDMU.JK","PLAS.JK","RODA.JK","SSIA.JK","VINS.JK","SHID.JK","LINK.JK","LTLS.JK","MIKA.JK","LPPS.JK","TRIL.JK","LPLI.JK","PPRO.JK","RIMO.JK","MRAT.JK","TARA.JK","WICO.JK","SMDR.JK","WIIM.JK","HOME.JK","UNSP.JK","LAPD.JK","MKPI.JK","KDSI.JK","ULTJ.JK","LMPI.JK","SAME.JK","TBMS.JK","SIMP.JK","TRIS.JK","FREN.JK","MKNT.JK","LAMI.JK","MICE.JK","INPP.JK","PGLI.JK","TRIO.JK","BAJA.JK","SIMA.JK","SUPR.JK","JIHD.JK","PICO.JK","KONI.JK","PWON.JK","RIGS.JK","TOWR.JK","KBRI.JK","PLIN.JK","LMSH.JK","SRTG.JK","TRAM.JK","BMAS.JK","VICO.JK","UNTX.JK","IDPR.JK","MDRN.JK","MGNA.JK","IPOL.JK","SSTM.JK","NIRO.JK","WAPO.JK","SPMA.JK","LMAS.JK","NAGA.JK","MAMI.JK","PNSE.JK","SKLT.JK","BACA.JK","2035956.JK","26155128.JK","3816479.JK"]

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
