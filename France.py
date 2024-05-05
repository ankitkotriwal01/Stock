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
    available_tickers = ["ALU.PA","AI.PA","AIR.PA","CS.PA","ALO.PA","AC.PA","AF.PA","ALEHT.PA","SIPH.PA","OSI.PA","MT.PA","CAFO.PA","RMS.PA","MLMAB.PA","CDA.PA","ATO.PA","ATA.PA","ALT.PA","ALOCT.PA","ALMDG.PA","ALAST.PA","ADP.PA","ZC.PA","XIL.PA","BNP.PA","BN.PA","BAIN.PA","EN.PA","ML.PA","DSY.PA","DP.PA","EDF.PA","SMTPC.PA","MLFER.PA","EDL.PA","TAM.PA","MLMAI.PA","FDR.PA","DVT.PA","DPT.PA","DGM.PA","DBV.PA","CBSM.PA","BSD.PA","ODET.PA","MLTRA.PA","MLTED.PA","MLSHD.PA","MLNV.PA","MLLEM.PA","MLHK.PA","MLEAU.PA","MLDAM.PA","MLCMB.PA","MLCFM.PA","MALA.PA","HDP.PA","GUYD.PA","FDL.PA","SEV.PA","ERF.PA","EO.PA","EI.PA","CBE.PA","SU.PA","ERSC.PA","ENGI.PA","ELIOR.PA","ECP.PA","VIE.PA","UBI.PA","SESL.PA","RF.PA","GPE.PA","FGR.PA","ES.PA","ERYP.PA","EOS.PA","EKI.PA","EDEN.PA","ALSAS.PA","ALGEM.PA","ALESK.PA","MLCVG.PA","PUB.PA","OR.PA","SAN.PA","SAFT.PA","SAF.PA","GLE.PA","CRTO.PA","VIV.PA","SOI.PA","VRAP.PA","UL.PA","TKTT.PA","TCH.PA","SOP.PA","QUA.PA","MC.PA","MAU.PA","ILD.PA","HO.PA","FR.PA","FP.PA","CAF.PA","VK.PA","VIRP.PA","VAC.PA","UG.PA","THEP.PA","TES.PA","SX.PA","SW.PA","STAL.PA","SGO.PA","RXL.PA","RI.PA","RCO.PA","PARRO.PA","ORA.PA","NEO.PA","MLSML.PA","MGIC.PA","KER.PA","ITXT.PA","ICAD.PA","HIM.PA","HBW.PA","HAV.PA","GDS.PA","FLY.PA","FLE.PA","FII.PA","COX.PA","CAP.PA","CA.PA","BVI.PA","BB.PA","VRNL.PA","TRI.PA","TOUP.PA","TER.PA","TEC.PA","SY.PA","SWP.PA","STF.PA","SOA.PA","SEC.PA","SBT.PA","RNO.PA","QTE.PA","PIX.PA","PIG.PA","OPN.PA","NK.PA","NANO.PA","MON.PA","MMT.PA","MLSTR.PA","MLSIM.PA","MLRAM.PA","MLNOV.PA","MLHBB.PA","MLCNT.PA","MLCET.PA","MFG.PA","MF.PA","MERY.PA","MED.PA","MAGIS.PA","LBON.PA","LACR.PA","KN.PA","JBOG.PA","ITE.PA","IPS.PA","IPN.PA","IPH.PA","IMPL.PA","IML.PA","HONV.PA","GTT.PA","GFT.PA","GFI.PA","GFC.PA","GEA.PA","GBT.PA","FREY.PA","FPN.PA","FPG.PA","FNTS.PA","FNAC.PA","FFP.PA","FEM.PA","FBEL.PA","FAYE.PA","CIV.PA","CGM.PA","CGG.PA","CCA.PA","BOL.PA","BELI.PA","AREVA.PA","ALUMS.PA","ALTUT.PA","ALTRA.PA","ALTER.PA","ALQGC.PA","ALORO.PA","ALINN.PA","ALHVS.PA","ALGEN.PA","ALCLS.PA","ALCLA.PA","ALBUD.PA","ALALO.PA","ALADO.PA","AKA.PA","ACA.PA","ABIO.PA","ZIF.PA","VLAP.PA","VET.PA","VCT.PA","UFF.PA","UDIS.PA","TNG.PA","MLFIH.PA","HSB.PA","MSTY.PA","GJAJ.PA","DEC.PA","MLEST.PA","JCQ.PA","MLJAN.PA","MLKRI.PA","MLKIM.PA","KOF.PA","KEY.PA","ALKEY.PA","LAX.PA","PM.PA","MLSEQ.PA","MLSMP.PA","STM.PA","CSTM.PA","NXI.PA","NUM.PA","NRO.PA","NEX.PA","OXI.PA","ORP.PA","ORAP.PA","ONXEO.PA","OLG.PA","MLOPT.PA","MLONE.PA","ALONC.PA","ALODI.PA","ALOCA.PA","OSE.PA","AGTA.PA","SQI.PA","RX.PA","CATR.PA","MRK.PA","IFF.PA","HXL.PA","FORDP.PA","ALUCR.PA","RIN.PA","MLVER.PA","MLGEQ.PA","LTE.PA","GV.PA","DGNV.PA","DG.PA","CRAV.PA","ALVXM.PA","ALVMG.PA","ALVEL.PA","ALVDM.PA","ALVDI.PA","MLVAL.PA","MLVES.PA","VIAD.PA","MLANT.PA","MCNV.PA","MLPHW.PA","MBWS.PA","ALWEB.PA","IGE.PA","XPO.PA","GND.PA","MLDYH.PA","MLZAM.PA","STAGR.PA","ZCNV.PA","MLDUR.PA","CV.PA","ABCA.PA","ABBV.PA","AB.PA","MLABC.PA","ABVX.PA","MLACP.PA","CIB.PA","ACAN.PA","ALACI.PA","ALACR.PA","MLACT.PA","MLLEO.PA","ACNV.PA","ATI.PA","ALP.PA","ALADM.PA","ADVI.PA","ALPAT.PA","ADV.PA","ADOC.PA","ALADA.PA","ADI.PA","FGA.PA","MLNOT.PA","BOAF.PA","AFO.PA","MLAFT.PA","FOAF.PA","CRLO.PA","CRBP2.PA","CNF.PA","CAT31.PA","ALAGR.PA","CMO.PA","AGCR.PA","MLBRO.PA","MLMLT.PA","CRSU.PA","CRLA.PA","MLAAH.PA","MLIFE.PA","MLAGI.PA","ALFBA.PA","AKE.PA","MLAKD.PA","AKENV.PA","ALCOI.PA","ALATP.PA","LTA.PA","CRAP.PA","ATE.PA","ALUCI.PA","ALTHE.PA","ALTEV.PA","ALSPO.PA","ALSIM.PA","ALSDL.PA","ALS30.PA","ALRGR.PA","ALNEV.PA","ALNBT.PA","ALLOG.PA","ALIOX.PA","ALIMO.PA","ALICR.PA","ALHIT.PA","ALHEO.PA","ALGOW.PA","ALGLD.PA","ALGEP.PA","ALFRE.PA","ALFPC.PA","ALEUP.PA","ALENT.PA","ALDEI.PA","ALCYB.PA","ALCOR.PA","ALCJ.PA","ALCAR.PA","ALAUP.PA","ALANT.PA","AREIT.PA","ALTRO.PA","ALNXT.PA","ALHPC.PA","ALMER.PA","ALSGD.PA","ALECR.PA","ALPHX.PA","ALREW.PA","ALINT.PA","ALTTI.PA","ALMGI.PA","ALEZV.PA","ALIDS.PA","ALMTH.PA","ALMED.PA","ALHOL.PA","ALI2S.PA","ALIMR.PA","ALREA.PA","ALPHY.PA","ALRIC.PA","ALPJT.PA","ALBFR.PA","ALMNG.PA","ALODS.PA","ALINS.PA","ALDBT.PA","ALBLD.PA","ALSFT.PA","ALBRS.PA","ALKDY.PA","ALIVA.PA","ALDBL.PA","ALBRI.PA","ALBI.PA","ALMDT.PA","ALMOU.PA","ALBIO.PA","ALAQU.PA","ALFST.PA","ALOBR.PA","ALTVO.PA","ALDEL.PA","ALDAR.PA","ALDR.PA","ALTXC.PA","ALCRB.PA","ALCOG.PA","ALHER.PA","ALUT.PA","ALSOA.PA","ALLIX.PA","ALSER.PA","ALWED.PA","ALMIL.PA","ALDMO.PA","ALMAK.PA","ALHYG.PA","ALSPW.PA","ALDLS.PA","ALLEX.PA","ALBLU.PA","ALGBE.PA","ALLMG.PA","ALMAS.PA","ALMET.PA","ALENR.PA","ALVIV.PA","ALDOL.PA","ALLP.PA","ALGIL.PA","ALCRM.PA","ALOSP.PA","ALMLB.PA","ALHIO.PA","ALISC.PA","ALANV.PA","ALPCI.PA","ALSEN.PA","ALSTW.PA","ALMIC.PA","ALCES.PA","ALCOF.PA","ALA2M.PA","ALBDM.PA","ALSOL.PA","ALBPS.PA","ALGEV.PA","ALTA.PA","ALVER.PA","ALPDX.PA","ALMDW.PA","ALDRV.PA","ALPGG.PA","ALNSE.PA","ALNOV.PA","ALTRI.PA","ALESA.PA","ALFIL.PA","ALPLA.PA","ALGCM.PA","ALROC.PA","ALTUR.PA","ALDIE.PA","ALVIA.PA","ALPOU.PA","ALWEC.PA","ALM.PA","ALLHB.PA","ALDV.PA","ALEO2.PA","ALPRI.PA","ALGAU.PA","ALSIP.PA","ALFOC.PA","ALEMV.PA","ALTLX.PA","ALEUA.PA","ALGIS.PA","ALPRO.PA","AMUN.PA","AMEBA.PA","AM.PA","AMPLI.PA","MLARD.PA","AML.PA","ROSA.PA","PSAT.PA","PROL.PA","PAOR.PA","PERR.PA","MLIMP.PA","MLHOP.PA","MLGRC.PA","GUI.PA","FIPP.PA","ETL.PA","EDI.PA","CO.PA","BLUE.PA","BLEE.PA","MPI.PA","ANF.PA","MND.PA","NSGP.PA","MLCEC.PA","MLPSH.PA","MLOLM.PA","MLAMA.PA","MLSIC.PA","ORPNV.PA","MLETA.PA","MLHYD.PA","TNFN.PA","INFE.PA","AUGR.PA","RAL.PA","MLFXO.PA","FALG.PA","LLY.PA","SLB.PA","STNT.PA","MLMTD.PA","MLFRC.PA","MLCMI.PA","NRX.PA","MLFMM.PA","MLTDS.PA","MLCFD.PA","SFCA.PA","SII.PA","APR.PA","MLAAT.PA","MLGAI.PA","ARTE.PA","ARG.PA","MLART.PA","MLARO.PA","JXR.PA","MLAMY.PA","ARTO.PA","PRC.PA","MLNMA.PA","ASY.PA","ASK.PA","MLVOP.PA","MLAEM.PA","CNP.PA","ASP.PA","ML350.PA","FATL.PA","ATEME.PA","ATONV.PA","AURE.PA","AUB.PA","AURS.PA","AVT.PA","AVQ.PA","AWOX.PA","AXW.PA","CSNV.PA","MLAZL.PA","BLC.PA","BCRA.PA","BCAM.PA","MLGES.PA","BEN.PA","MLMFI.PA","MLIOC.PA","DEXB.PA","MLV4S.PA","BERR.PA","MTU.PA","DIM.PA","BIM.PA","BIG.PA","MLCLI.PA","MLTBM.PA","BND.PA","BNS.PA","GBB.PA","BOI.PA","MLBOK.PA","CARP.PA","BON.PA","ENNV.PA","BOLNV.PA","MLLB.PA","MRB.PA","BUR.PA","BVINV.PA","BUI.PA","MLHMC.PA","CBDG.PA","CAS.PA","CAPLI.PA","CBOT.PA","CBR.PA","CCN.PA","CCE.PA","CC.PA","CDI.PA","CLNV.PA","CGR.PA","CEREN.PA","CEN.PA","MLROU.PA","CGD.PA","CFAO.PA","CFI.PA","TVRB.PA","MLTRC.PA","LHN.PA","CHSR.PA","MLFIR.PA","CHAU.PA","MLCSP.PA","MLOVE.PA","CIEM.PA","MLMAT.PA","MLTHA.PA","MLCIO.PA","FORE.PA","MLPIV.PA","VIL.PA","LTAN.PA","MLCJS.PA","CNV.PA","MLFCI.PA","MLCRO.PA","CRINV.PA","CRI.PA","CRBT.PA","CROS.PA","MLCTA.PA","CTRG.PA","MLSIL.PA","DAN.PA","IMDA.PA","MLDHZ.PA","DLT.PA","DSYNV.PA","DRTY.PA","DBT.PA","DBG.PA","COM.PA","MLMGL.PA","MLSDR.PA","MLMED.PA","DLTA.PA","ULDV.PA","FDPA.PA","MLEDR.PA","DGE.PA","DIREN.PA","MLDIG.PA","MLDDP.PA","MLBRI.PA","DIG.PA","DNX.PA","DOMS.PA","DPAM.PA","DUC.PA","DUPP.PA","MLEDS.PA","PVL.PA","FCMC.PA","MLDYN.PA","MLDYX.PA","MLEAS.PA","EEM.PA","ECASA.PA","EC.PA","MLECO.PA","MLEDU.PA","EDENV.PA","EFI.PA","GID.PA","EINV.PA","EIFF.PA","ELIS.PA","ELEC.PA","ELE.PA","GNE.PA","SUNV.PA","EPS.PA","TONN.PA","ELINV.PA","EMG.PA","SCHP.PA","MLEES.PA","MCPHY.PA","ENX.PA","EOSI.PA","MLEMG.PA","EONV.PA","EXPL.PA","ERA.PA","ERFNV.PA","ESI.PA","MLEBX.PA","MLHIN.PA","PAT.PA","MLCAC.PA","MLERO.PA","MLERI.PA","EURS.PA","EUCAR.PA","GET.PA","MLMCE.PA","MLITG.PA","EUR.PA","MLEVE.PA","GLO.PA","METEX.PA","EXE.PA","EXAC.PA","MLHYE.PA","MLMEX.PA","LEY.PA","FAUV.PA","MLFAC.PA","MFC.PA","MALT.PA","FED.PA","FINM.PA","NOKIA.PA","14488435.PA","ORIA.PA","FIM.PA","FLO.PA","FMU.PA","LEBL.PA","INEA.PA","MLCFI.PA","SPEL.PA","LFVE.PA","MLVIN.PA","FPNV.PA","THER.PA","TFF.PA","SOG.PA","SOFR.PA","SO.PA","SCDU.PA","SFT.PA","SFBS.PA","SDG.PA","SCR.PA","SAMS.PA","SABE.PA","RIB.PA","RCF.PA","PSB.PA","MUN.PA","MRM.PA","MMB.PA","MLVST.PA","MLTRO.PA","MLSTM.PA","MLPPI.PA","MLPOL.PA","MLPFX.PA","MLNLF.PA","MLMON.PA","MLLEA.PA","MLIML.PA","MLIDS.PA","MLGEO.PA","MLCOR.PA","LSS.PA","LR.PA","LPE.PA","LOCAL.PA","LD.PA","LAF.PA","ITS.PA","ITP.PA","INSD.PA","INN.PA","ING.PA","IDIP.PA","HF.PA","GTCL.PA","GOE.PA","GLENV.PA","GECP.PA","GDMS.PA","GAM.PA","FTRN.PA","COUR.PA","COH.PA","MLLOI.PA","MLIFC.PA","MLCOU.PA","MLUSG.PA","COFA.PA","MLRIV.PA","GENX.PA","MLFTI.PA","MLLED.PA","INF.PA","LAN.PA","MLSAT.PA","RIA.PA","SK.PA","MLSRP.PA","MLQUD.PA","OREGE.PA","MLUNT.PA","MLARI.PA","MLAUD.PA","MLGAL.PA","UNBL.PA","NRG.PA","SPIE.PA","MLCMG.PA","MKEA.PA","TXCL.PA","LNA.PA","PHA.PA","GNFT.PA","MLPLC.PA","MLCOL.PA","GBTNV.PA","SESNV.PA","VLTSA.PA","ROTH.PA","005408.PA","RUI.PA","MEMS.PA","GRVO.PA","MLPVG.PA","MLMII.PA","MLPAC.PA","MLCHP.PA","KORI.PA","TVLY.PA","RBT.PA","MLMUL.PA","MLGRD.PA","MLSBT.PA","MLNEO.PA","MRNNV.PA","POXEL.PA","PCA.PA","FREDS.PA","MLGLO.PA","RXLNV.PA","PREC.PA","MLTEK.PA","POM.PA","DEVR.PA","TFINV.PA","IDL.PA","CATG.PA","MLJSA.PA","LAT.PA","VDLO.PA","PAR.PA","PGP.PA","MLIDP.PA","MLGEL.PA","GTO.PA","GIRO.PA","MLGCR.PA","MLUMH.PA","HCO.PA","HERIG.PA","HIPAY.PA","MLHTT.PA","MLION.PA","MLTMT.PA","MLMHO.PA","IAM.PA","MLIPP.PA","SSI.PA","MLIPY.PA","MLSNT.PA","VIT.PA","ITL.PA","DECNV.PA","KAZI.PA","KERNV.PA","LI.PA","LCO.PA","LDL.PA","LNC.PA","MLLCS.PA","LOUP.PA","MLLSK.PA","SESG.PA","ORC.PA","MCLC.PA","MLSKN.PA","MLNEI.PA","MLWEY.PA","MLUMG.PA","MLHOT.PA","MLORC.PA","MLSEC.PA","MLMOV.PA","MLCHE.PA","MLNES.PA","MLTEA.PA","MLHCF.PA","MLBAT.PA","MLMAD.PA","MLCSV.PA","MLVIS.PA","MLSOL.PA","MLPHO.PA","MLMUT.PA","MLWTT.PA","MLONL.PA","MLDEX.PA","MLOSA.PA","MLTRS.PA","MLFDV.PA","MLPPF.PA","MLMNR.PA","MLPRI.PA","MLSUM.PA","MLPRO.PA","MLCLP.PA","MLDTB.PA","MLAAE.PA","MLATV.PA","MLSOC.PA","MLPGO.PA","MLUNI.PA","MONC.PA","MONT.PA","MRN.PA","GREV.PA","NXTV.PA","NERG.PA","NTG.PA","SACI.PA","SAFOR.PA","PARP.PA","RUSAL.PA","RUIDS.PA","RLL.PA","ROD.PA","RUINV.PA","VALE3.PA","SDT.PA","SFPI.PA","SGONV.PA","SRP.PA","TAYN.PA","TFI.PA","TIPI.PA","TOU.PA","VLA.PA","VETO.PA","VIA.PA","WLN.PA","RE.PA","SPI.PA","HOP.PA","INFY.PA","4848650.PA","LIN.PA","MAN.PA","SANNV.PA","SAVE.PA","SEFER.PA","SELER.PA","SEQ.PA"]

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
