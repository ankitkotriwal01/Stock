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
    available_tickers = ["510010.SS","510680.SS","510420.SS","502000.SS","502001.SS","512210.SS","512230.SS","522971.SS","522975.SS","501002.SS","502016.SS","523985.SS","522985.SS","523971.SS","523975.SS","511880.SS","522665.SS","523664.SS","522664.SS","510430.SS","523665.SS","511930.SS","510581.SS","502032.SS","502031.SS","510880.SS","510170.SS","510560.SS","519002.SS","511980.SS","512500.SS","502018.SS","511010.SS","510660.SS","510650.SS","502017.SS","510630.SS","518800.SS","510610.SS","513100.SS","511210.SS","510050.SS","510410.SS","510020.SS","500058.SS","513500.SS","519889.SS","510330.SS","510620.SS","510090.SS","512990.SS","519888.SS","510230.SS","519801.SS","519800.SS","519119.SS","511900.SS","511960.SS","603919.SS","512010.SS","510510.SS","510520.SS","518880.SS","511860.SS","510710.SS","512600.SS","512220.SS","511220.SS","513600.SS","505888.SS","513660.SS","502002.SS","603066.SS","501000.SS","502010.SS","502058.SS","502053.SS","502005.SS","502008.SS","502042.SS","502011.SS","502022.SS","502020.SS","502012.SS","502054.SS","502056.SS","502021.SS","603520.SS","502057.SS","601155.SS","501001.SS","502007.SS","502041.SS","502003.SS","502023.SS","502055.SS","510580.SS","502024.SS","502040.SS","502025.SS","502026.SS","502028.SS","502004.SS","502027.SS","603027.SS","511820.SS","502006.SS","512510.SS","502038.SS","502036.SS","510360.SS","502037.SS","510290.SS","601988.SS","601398.SS","600640.SS","600635.SS","600027.SS","900932.SS","601998.SS","601808.SS","601006.SS","600809.SS","600618.SS","600519.SS","600426.SS","600180.SS","600104.SS","600079.SS","600036.SS","600029.SS","600015.SS","900930.SS","900922.SS","900918.SS","900915.SS","900907.SS","603838.SS","603729.SS","603398.SS","603366.SS","603318.SS","603268.SS","603188.SS","603168.SS","603108.SS","603003.SS","601996.SS","601939.SS","601818.SS","601801.SS","601799.SS","601788.SS","601766.SS","601717.SS","601677.SS","601628.SS","601618.SS","601600.SS","601588.SS","601558.SS","601555.SS","601258.SS","601169.SS","601166.SS","601118.SS","601111.SS","601100.SS","601098.SS","601088.SS","601028.SS","601018.SS","601012.SS","600999.SS","600993.SS","600990.SS","600988.SS","600983.SS","600967.SS","600965.SS","600959.SS","600893.SS","600892.SS","600890.SS","600889.SS","600875.SS","600858.SS","600857.SS","600841.SS","600826.SS","600825.SS","600824.SS","600822.SS","600819.SS","600812.SS","600805.SS","600797.SS","600792.SS","600790.SS","600789.SS","600770.SS","600765.SS","600756.SS","600750.SS","600744.SS","600742.SS","600741.SS","600738.SS","600737.SS","600736.SS","600719.SS","600706.SS","600703.SS","600695.SS","600694.SS","600684.SS","600681.SS","600680.SS","600677.SS","600671.SS","600662.SS","600649.SS","600641.SS","600633.SS","600629.SS","600626.SS","600605.SS","600600.SS","600592.SS","600588.SS","600583.SS","600572.SS","600570.SS","600549.SS","600545.SS","600535.SS","600521.SS","600503.SS","600498.SS","600462.SS","600452.SS","600444.SS","600438.SS","600422.SS","600418.SS","600415.SS","600400.SS","600395.SS","600377.SS","600358.SS","600356.SS","600351.SS","600350.SS","600345.SS","600337.SS","600335.SS","600320.SS","600309.SS","600308.SS","600305.SS","600302.SS","600295.SS","600292.SS","600291.SS","600283.SS","600282.SS","600271.SS","600267.SS","600255.SS","600247.SS","600241.SS","600240.SS","600233.SS","600216.SS","600213.SS","600207.SS","600197.SS","600196.SS","600190.SS","600177.SS","600172.SS","600171.SS","600168.SS","600167.SS","600166.SS","600152.SS","600148.SS","600136.SS","600135.SS","600132.SS","600131.SS","600127.SS","600123.SS","600111.SS","600088.SS","600086.SS","600066.SS","600056.SS","600055.SS","600054.SS","600053.SS","600038.SS","600031.SS","600021.SS","600020.SS","600018.SS","600017.SS","600016.SS","600011.SS","600010.SS","600008.SS","600456.SS","600105.SS","600491.SS","600608.SS","600145.SS","601700.SS","603788.SS","603555.SS","603311.SS","600191.SS","600317.SS","600887.SS","600069.SS","600536.SS","600532.SS","510190.SS","600978.SS","600775.SS","603696.SS","603300.SS","600710.SS","600262.SS","601616.SS","600393.SS","600303.SS","600718.SS","600962.SS","600776.SS","900935.SS","900934.SS","600281.SS","601899.SS","603019.SS","600696.SS","900940.SS","600060.SS","600185.SS","601311.SS","600319.SS","601001.SS","600328.SS","601633.SS","600509.SS","511890.SS","600516.SS","601789.SS","603166.SS","600520.SS","600232.SS","600760.SS","600539.SS","600091.SS","600149.SS","600581.SS","600361.SS","600883.SS","600785.SS","600163.SS","510310.SS","603799.SS","601000.SS","603993.SS","900924.SS","510260.SS","600513.SS","600873.SS","600073.SS","601519.SS","600222.SS","600975.SS","510070.SS","600795.SS","600259.SS","600439.SS","600886.SS","600468.SS","603000.SS","600421.SS","601991.SS","600657.SS","600575.SS","512340.SS","603778.SS","600239.SS","600475.SS","603611.SS","601918.SS","600781.SS","600331.SS","600745.SS","603088.SS","600771.SS","603077.SS","601179.SS","600811.SS","603023.SS","600506.SS","600231.SS","600157.SS","601208.SS","600109.SS","600888.SS","600576.SS","603589.SS","600052.SS","600850.SS","600463.SS","600330.SS","600782.SS","600981.SS","600604.SS","600654.SS","601800.SS","603399.SS","600150.SS","600837.SS","600122.SS","601798.SS","600348.SS","600485.SS","600774.SS","601069.SS","600815.SS","600287.SS","600836.SS","600481.SS","600602.SS","600405.SS","600764.SS","600100.SS","600843.SS","600712.SS","600969.SS","601669.SS","600894.SS","600298.SS","600290.SS","601901.SS","600512.SS","600862.SS","600594.SS","600005.SS","600329.SS","603698.SS","600556.SS","600369.SS","600193.SS","601225.SS","600355.SS","900912.SS","603806.SS","600814.SS","600367.SS","603002.SS","600299.SS","600787.SS","603866.SS","603118.SS","600229.SS","600026.SS","600676.SS","600313.SS","510210.SS","600000.SS","600648.SS","600141.SS","600372.SS","600540.SS","600218.SS","900939.SS","600169.SS","600566.SS","603686.SS","600332.SS","600423.SS","600279.SS","601339.SS","600155.SS","600634.SS","600392.SS","601007.SS","900906.SS","600360.SS","601288.SS","600769.SS","600386.SS","600023.SS","600189.SS","600987.SS","600076.SS","601515.SS","900936.SS","601636.SS","603989.SS","601218.SS","600449.SS","600371.SS","601016.SS","600261.SS","600867.SS","601890.SS","600336.SS","600061.SS","600095.SS","900947.SS","600083.SS","600757.SS","510450.SS","600114.SS","600628.SS","600107.SS","600467.SS","519011.SS","600984.SS","600856.SS","600170.SS","600508.SS","600478.SS","600525.SS","600715.SS","600869.SS","603026.SS","600614.SS","600729.SS","600288.SS","600307.SS","900933.SS","603223.SS","600265.SS","603338.SS","600823.SS","600217.SS","900937.SS","600072.SS","600067.SS","600783.SS","601898.SS","600368.SS","600383.SS","600096.SS","601038.SS","601003.SS","600817.SS","600085.SS","600479.SS","600187.SS","603688.SS","600636.SS","600997.SS","600206.SS","600526.SS","600704.SS","600973.SS","601186.SS","600399.SS","603969.SS","600674.SS","600917.SS","603703.SS","600697.SS","600702.SS","600470.SS","600138.SS","601226.SS","600518.SS","600493.SS","603997.SS","600063.SS","600685.SS","603616.SS","601965.SS","510030.SS","600103.SS","600112.SS","601929.SS","600835.SS","600252.SS","600584.SS","600724.SS","600420.SS","511990.SS","600080.SS","600133.SS","600740.SS","600064.SS","600496.SS","601107.SS","600833.SS","600486.SS","600713.SS","600108.SS","900938.SS","900901.SS","600620.SS","600179.SS","600050.SS","600601.SS","600613.SS","600058.SS","601872.SS","600980.SS","600807.SS","600791.SS","600363.SS","512110.SS","600234.SS","603936.SS","603009.SS","600653.SS","601106.SS","600068.SS","600380.SS","600256.SS","600767.SS","600796.SS","601928.SS","600728.SS","600459.SS","600780.SS","603128.SS","600831.SS","600698.SS","601388.SS","600396.SS","600558.SS","600359.SS","600711.SS","603306.SS","600280.SS","600226.SS","600223.SS","601009.SS","600257.SS","600650.SS","600571.SS","603606.SS","900956.SS","600249.SS","601158.SS","600059.SS","600803.SS","600480.SS","600156.SS","600603.SS","603608.SS","600884.SS","600768.SS","603618.SS","900905.SS","900914.SS","600118.SS","603818.SS","603996.SS","600810.SS","600158.SS","601699.SS","600425.SS","600779.SS","600182.SS","600501.SS","601211.SS","600435.SS","601058.SS","600895.SS","600688.SS","600982.SS","600579.SS","600868.SS","600870.SS","600515.SS","600569.SS","600186.SS","601010.SS","600161.SS","600235.SS","600089.SS","600408.SS","600647.SS","600137.SS","600203.SS","600866.SS","600221.SS","600098.SS","601233.SS","600074.SS","600730.SS","603766.SS","601368.SS","603315.SS","603669.SS","600855.SS","600375.SS","601689.SS","600714.SS","600865.SS","600178.SS","600617.SS","600699.SS","600285.SS","600854.SS","601168.SS","600961.SS","600844.SS","600587.SS","601880.SS","603167.SS","600727.SS","600821.SS","600845.SS","513030.SS","603309.SS","600859.SS","603299.SS","600746.SS","600139.SS","600793.SS","600009.SS","600165.SS","603636.SS","600106.SS","600489.SS","603123.SS","900903.SS","603158.SS","500056.SS","600759.SS","603979.SS","601099.SS","511810.SS","900952.SS","601222.SS","600326.SS","600820.SS","600555.SS","900909.SS","600755.SS","603169.SS","601377.SS","600543.SS","600502.SS","600215.SS","600033.SS","601390.SS","600387.SS","600487.SS","603328.SS","600366.SS","600458.SS","600538.SS","600316.SS","600201.SS","600872.SS","600362.SS","601002.SS","603222.SS","600802.SS","600258.SS","600176.SS","600352.SS","603601.SS","600547.SS","600838.SS","600839.SS","600339.SS","900908.SS","600721.SS","603789.SS","601599.SS","600272.SS","600490.SS","600693.SS","600373.SS","600642.SS","600834.SS","510900.SS","600028.SS","900927.SS","603020.SS","600708.SS","600656.SS","603828.SS","600398.SS","600097.SS","603085.SS","600461.SS","600117.SS","600557.SS","600099.SS","600093.SS","900957.SS","600119.SS","603021.SS","601919.SS","603355.SS","600624.SS","500038.SS","600726.SS","600300.SS","600243.SS","603999.SS","900948.SS","600808.SS","600658.SS","600661.SS","600876.SS","600497.SS","600970.SS","600476.SS","900943.SS","601518.SS","603126.SS","600126.SS","601318.SS","600891.SS","600208.SS","600198.SS","600665.SS","510180.SS","600219.SS","510120.SS","600897.SS","512330.SS","603227.SS","511800.SS","600683.SS","600998.SS","600228.SS","601888.SS","603699.SS","601985.SS","600585.SS","600315.SS","600666.SS","600115.SS","601231.SS","601313.SS","600577.SS","600237.SS","600596.SS","600871.SS","603005.SS","600037.SS","600754.SS","600312.SS","600758.SS","600778.SS","600090.SS","600153.SS","600804.SS","600527.SS","600829.SS","600250.SS","603598.SS","601989.SS","603117.SS","600523.SS","600269.SS","603566.SS","600725.SS","603567.SS","600612.SS","600353.SS","601008.SS","600448.SS","603100.SS","900945.SS","600578.SS","600346.SS","600121.SS","600630.SS","603889.SS","600739.SS","600110.SS","601566.SS","603006.SS","600690.SS","600323.SS","600220.SS","600622.SS","600652.SS","600284.SS","600406.SS","600589.SS","600537.SS","600378.SS","600370.SS","600860.SS","601999.SS","600976.SS","601668.SS","600610.SS","600184.SS","600212.SS","600550.SS","600275.SS","512120.SS","600209.SS","600322.SS","600563.SS","603012.SS","601908.SS","600668.SS","600565.SS","601101.SS","900921.SS","600645.SS","600686.SS","601727.SS","600293.SS","600428.SS","600403.SS","600900.SS","600160.SS","603939.SS","603116.SS","510500.SS","603898.SS","600500.SS","601113.SS","900928.SS","600195.SS","600070.SS","600877.SS","600507.SS","600505.SS","601969.SS","600230.SS","600268.SS","600716.SS","600113.SS","600846.SS","600340.SS","600733.SS","600236.SS","600551.SS","900923.SS","601126.SS","600183.SS","600531.SS","600717.SS","600419.SS","600619.SS","601877.SS","900913.SS","600673.SS","600801.SS","600338.SS","600847.SS","600992.SS","603377.SS","600687.SS","600675.SS","600120.SS","600663.SS","600477.SS","601015.SS","600853.SS","600590.SS","600747.SS","510130.SS","600573.SS","600321.SS","900925.SS","510160.SS","900917.SS","603008.SS","600580.SS","600818.SS","603883.SS","600735.SS","600567.SS","600794.SS","900955.SS","600199.SS","600548.SS","603901.SS","603099.SS","600682.SS","600246.SS","600488.SS","601369.SS","510060.SS","512640.SS","512070.SS","512610.SS","523972.SS","523976.SS","523973.SS","522973.SS","523977.SS","522972.SS","522976.SS","519973.SS","522977.SS","519972.SS","510440.SS","522677.SS","523677.SS","512511.SS","510280.SS","510110.SS","502015.SS","519300.SS","502013.SS","502050.SS","511830.SS","502014.SS","502049.SS","512310.SS","510150.SS","502048.SS","512300.SS","510220.SS","510300.SS","510270.SS","522566.SS","522567.SS","512221.SS","600410.SS","600297.SS","900953.SS","600568.SS","603558.SS","601333.SS","600966.SS","600731.SS","600460.SS","600310.SS","600071.SS","600116.SS","601199.SS","600482.SS","600995.SS","600751.SS","603018.SS","603568.SS","600707.SS","600734.SS","603600.SS","600318.SS","600401.SS","600958.SS","603025.SS","600062.SS","600159.SS","601718.SS","603368.SS","600311.SS","601567.SS","600082.SS","603011.SS","603010.SS","600057.SS","603918.SS","600078.SS","900926.SS","600101.SS","600896.SS","600388.SS","601336.SS","600455.SS","600864.SS","600597.SS","601139.SS","603609.SS","601866.SS","600466.SS","600679.SS","600763.SS","600851.SS","603718.SS","601021.SS","603519.SS","600130.SS","601857.SS","600260.SS","600720.SS","601678.SS","600986.SS","600637.SS","601216.SS","900902.SS","600798.SS","600379.SS","600643.SS","600397.SS","600882.SS","600692.SS","600593.SS","600691.SS","603808.SS","603017.SS","600985.SS","600863.SS","600651.SS","600129.SS","600528.SS","600325.SS","603456.SS","600469.SS","600777.SS","600599.SS","600753.SS","600830.SS","600606.SS","600012.SS","600749.SS","600960.SS","603199.SS","600094.SS","600748.SS","600151.SS","600861.SS","600227.SS","600615.SS","900910.SS","600562.SS","600251.SS","600598.SS","600879.SS","600816.SS","600007.SS","600623.SS","600827.SS","600382.SS","900950.SS","603308.SS","600365.SS","600238.SS","600616.SS","600343.SS","603998.SS","600242.SS","603800.SS","600880.SS","600723.SS","600077.SS","600499.SS","600173.SS","600530.SS","601579.SS","600128.SS","600266.SS","600289.SS","600761.SS","601968.SS","603508.SS","600391.SS","600655.SS","603001.SS","900946.SS","600609.SS","600638.SS","600390.SS","601116.SS","600644.SS","601608.SS","600611.SS","600881.SS","600678.SS","600971.SS","600162.SS","601137.SS","600146.SS","601900.SS","600175.SS","603899.SS","600660.SS","600389.SS","600200.SS","601601.SS","600766.SS","600433.SS","601005.SS","600722.SS","603968.SS","600192.SS","600806.SS","600446.SS","601886.SS","600006.SS","600561.SS","603599.SS","601328.SS","600019.SS","600664.SS","900904.SS","601992.SS","601688.SS","600125.SS","600595.SS","600075.SS","601607.SS","600143.SS","601011.SS","600248.SS","600560.SS","600689.SS","603333.SS","600848.SS","600202.SS","600277.SS","600225.SS","900929.SS","600004.SS","900919.SS","600327.SS","900951.SS","601117.SS","603678.SS","601777.SS","600510.SS","603885.SS","600276.SS","600979.SS","600621.SS","600582.SS","600432.SS","600436.SS","600273.SS"]

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
