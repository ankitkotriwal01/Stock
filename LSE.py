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
    available_tickers = ["QED.L","ADN.L","AV.L","AHT.L","AZN.L","AGL.L","PETS.L","LAS.L","BPTY.L","AXS.L","AMA.L","ALO.L","AAL.L","SMA.L","RMP.L","MGAM.L","KBC.L","FSJ.L","CAMB.L","BBA.L","BATS.L","BABS.L","AVV.L","AVR.L","ASH.L","AML.L","AHCG.L","SLED.L","ABF.L","ABC.L","BARC.L","LLOY.L","RBS.L","LRE.L","BRBY.L","BP.L","BOE.L","BLND.L","BA.L","BKG.L","MAB.L","GKP.L","BVS.L","BVIC.L","BOK.L","BG.L","BAB.L","RAME.L","PEBI.L","BT-A.L","BRW.L","BRSN.L","BMY.L","BLNX.L","BGO.L","BGEO.L","BDEV.L","OCN.L","MAIL.L","HSX.L","GFM.L","RDSA.L","RDSB.L","DEB.L","DCG.L","LWDB.L","DOM.L","DCC.L","JDW.L","DTY.L","DRX.L","DRS.L","DLAR.L","TUI.L","SMDS.L","RMG.L","DVO.L","DPP.L","DNLM.L","DKL.L","DJAN.L","DDDD.L","BFA.L","SPD.L","PDL.L","HPAC.L","GEMD.L","GED.L","EDP.L","DRV.L","DREF.L","DPH.L","DPA.L","DGB.L","DFIB.L","DEMG.L","DCD.L","DC.L","C4XD.L","B8F.L","WLG.L","STEL.L","SEPL.L","SDVZ.L","PRG.L","NBDX.L","NBDD.L","MLD.L","MCON.L","KMK.L","HZD.L","GDL.L","FDI.L","FDEV.L","EKF.L","EXPN.L","NEPI.L","ECM.L","KWE.L","JE.L","ETI.L","CNE.L","RKH.L","NEX.L","LSE.L","INFI.L","FEV.L","EVR.L","ESUR.L","EDIN.L","EBQ.L","IAE.L","GEC.L","EZJ.L","EXI.L","ETO.L","ELTA.L","ELM.L","UVEL.L","ULE.L","TRIN.L","TOM.L","TEM.L","PCGE.L","OPHR.L","MYT.L","MTL.L","LGO.L","JEL.L","IAG.L","GWI.L","GSS.L","ESG.L","ERGO.L","EPWN.L","EME.L","EHP.L","EDR.L","EAS.L","BVA.L","BKY.L","AEY.L","AEN.L","ZHEH.L","XEL.L","WOS.L","PFG.L","IPF.L","FGP.L","FRES.L","FGT.L","FCPT.L","PFL.L","JUP.L","FPM.L","COD.L","TTA.L","ORCH.L","NFC.L","MCRO.L","JD.L","IOG.L","HFG.L","GLIF.L","FXPO.L","FOXT.L","FOUR.L","FMPG.L","FLYB.L","FFY.L","FDSA.L","FBT.L","FAN.L","CARD.L","VOF.L","TPF.L","TIR.L","TT.L","NG.L","GLEN.L","VOD.L","SRP.L","HSBA.L","STAN.L","GSK.L","SVI.L","CPG.L","TIG.L","CCL.L","SIA.L","RR.L","OML.L","IMG.L","III.L","IAP.L","CNA.L","WEIR.L","TCG.L","SAB.L","RNK.L","RIO.L","REX.L","PFC.L","LMI.L","LGEN.L","ISAT.L","GOG.L","CRST.L","COB.L","WTB.L","WG.L","VCT.L","ULVR.L","TLW.L","SNR.L","SHB.L","SDY.L","SDR.L","QRT.L","NANO.L","MRW.L","MGGT.L","JMAT.L","THT.L","ITV.L","HOME.L","GNS.L","GNC.L","CLLN.L","WTAN.L","WMH.L","VM.L","UKOG.L","TRS.L","TEP.L","TATE.L","SLI.L","SGE.L","SBRY.L","RTO.L","RTN.L","RSA.L","RRS.L","PSON.L","PNN.L","PLND.L","NOG.L","LVD.L","LRM.L","KIE.L","KGF.L","KAZ.L","JLT.L","IMI.L","IGG.L","HSTN.L","HOC.L","GWP.L","GKN.L","GFRD.L","CWK.L","CLDN.L","WEB.L","VLS.L","VER.L","UANC.L","TSCO.L","TRY.L","TPK.L","TCM.L","SXS.L","SSPG.L","SMP.L","SL.L","SKP.L","SAGA.L","ROL.L","REL.L","RE.L","PZC.L","PUB.L","PRV.L","PML.L","PDG.L","PAY.L","PAG.L","PA.L","OXIG.L","OVG.L","OCDO.L","MTW.L","MTPH.L","MRC.L","MONY.L","MJW.L","MERC.L","MCGN.L","MARS.L","LSL.L","KLR.L","JRG.L","INV.L","INF.L","INCH.L","ICP.L","ICGC.L","HVN.L","HMSO.L","HL.L","HGM.L","HEAD.L","HAS.L","GRI.L","GLE.L","GFS.L","SYR.L","CWC.L","SPRT.L","COMS.L","CGI.L","CBG.L","BYG.L","BWY.L","BQE.L","BILB.L","BHMG.L","BET.L","QPP.L","PRZ.L","WRES.L","WKP.L","WHI.L","VTC.L","VNET.L","VLK.L","VELA.L","TW.L","TRX.L","TRK.L","TON.L","TLPR.L","TIGT.L","TIDE.L","THRG.L","TED.L","TALK.L","SYNT.L","SVT.L","SVE.L","SVCA.L","SUH.L","STJ.L","STHR.L","STB.L","STAF.L","SRB.L","SPO.L","SPI.L","SOLG.L","SNT.L","SN.L","SML.L","SMJ.L","SKY.L","SIV.L","SHRE.L","SHI.L","SGRO.L","SEPU.L","SDRC.L","SDL.L","RTC.L","RSW.L","RPS.L","RPC.L","ROR.L","RNWH.L","RMMC.L","RMM.L","RGP.L","REDT.L","RAT.L","QTX.L","QQ.L","QP.L","PTCM.L","PSN.L","PRU.L","POS.L","PMG.L","PHNX.L","PGH.L","PCT.L","OSB.L","OMG.L","OBT.L","HTY.L","NXT.L","NWT.L","NVT.L","NSCI.L","NRR.L","NEW.L","NCC.L","NBB.L","NASA.L","NAS.L","MYI.L","MWG.L","MUBL.L","MSYS.L","MSMN.L","MRO.L","MPI.L","MOGP.L","MNDI.L","MLC.L","MKT.L","MKS.L","MIG3.L","MCKS.L","LSR.L","LRD.L","LND.L","RYA.L","HON.L","NHY.L","IHG.L","HTG.L","HSV.L","HSS.L","HSP.L","HLMA.L","HGG.L","HFD.L","HCP.L","HAYD.L","GPRT.L","GHH.L","CCH.L","ARM.L","ALY.L","WWH.L","VENN.L","THL.L","TXH.L","TEF.L","SHFT.L","SPHR.L","RHM.L","SHP.L","WPP.L","3IN.L","POLY.L","JPM.L","RICO.L","RGU.L","MIRL.L","MBO.L","JPR.L","JKX.L","CREI.L","CHOO.L","BOOM.L","BEZ.L","AO.L","17GK.L","UBM.L","TYT.L","SWJ.L","STAR.L","SIG.L","SCHO.L","SARS.L","ROSN.L","RCI.L","PGIL.L","NGR.L","MNOD.L","MCLS.L","LTHM.L","LKOH.L","KNM.L","KMGA.L","JQW.L","JRS.L","JRIC.L","JPG.L","JPE.L","JOG.L","JNY.L","JLP.L","JLIF.L","JIM.L","JIL.L","JGC.L","JFJ.L","JDSB.L","JDG.L","JAM.L","HWDN.L","GTS.L","GRL.L","GLS.L","GENL.L","FXI.L","CSFG.L","CRPR.L","CIRC.L","CIR.L","CEY.L","BREE.L","BMTO.L","BMT.L","AKRN.L","ACE.L","36GK.L","33KE.L","0QO6.L","0H65.L","MYSL.L","LEF.L","CMCL.L","JCH.L","JHD.L","JPS.L","AFG.L","0EXP.L","UJO.L","JMF.L","LXB.L","JMIS.L","MMK.L","BGFD.L","JII.L","GAZ.L","JIGC.L","0EX6.L","IDHC.L","0Q45.L","BD32.L","SSA.L","SJG.L","CIU.L","DX.L","SCN.L","ACT.L","FJV.L","37QB.L","TPFZ.L","JDT.L","JETG.L","JLG.L","JARB.L","SNN.L","JLEN.L","0MU8.L","0LRI.L","OGZD.L","HFEL.L","FJVS.L","JPRL.L","0MK2.L","MASA.L","VTBR.L","BZM.L","TREE.L","JGCI.L","KIBO.L","KMR.L","KGP.L","KENV.L","KEFI.L","KCOM.L","IKK.L","AGK.L","WKOF.L","TMZ.L","TILS.L","TET.L","SKG.L","PLP.L","PAX.L","PEL.L","NETD.L","MVI.L","LEAF.L","KUBC.L","KSK.L","KOOV.L","KOD.L","KNOS.L","KLN.L","KBT.L","KBE.L","KAKU.L","KHTC.L","GNK.L","GEL.L","FRR.L","FRX.L","FLK.L","FCRM.L","EYE.L","CNG.L","CLST.L","CHOC.L","0Q3Y.L","0GTO.L","0NPP.L","0NMU.L","0M14.L","0F08.L","PSPI.L","WRL.L","URU.L","PLAZ.L","GRPH.L","BWNG.L","YNGN.L","ULS.L","NYO.L","NUM.L","NTQ.L","NTN.L","NTG.L","NTBC.L","NSI.L","NRI.L","NPT.L","NOVA.L","NMD.L","NLMK.L","NLG.L","NIPT.L","NICL.L","NHL.L","SBER.L","OCL.L","ICTA.L","CGT.L","CDI.L","AVA.L","ASL.L","UKRO.L","UAV.L","TPOU.L","TMPL.L","SOLO.L","SMT.L","SLET.L","SAUD.L","SDP.L","SCP.L","SCIN.L","SCAM.L","RSB.L","RCP.L","PGR.L","POWR.L","PNL.L","PMO.L","PLI.L","PIN.L","PHST.L","PHI.L","PEQ.L","OSG.L","OXH.L","ORCP.L","OPPP.L","OCT.L","OAP3.L","NCA.L","MOIL.L","MNL.L","MDO.L","MCP.L","LTI.L","IVI.L","IPU.L","IE1F.L","ICTB.L","HRI.L","FTD.L","FOGL.L","FOG.L","FMPI.L","FCS.L","FAS.L","EPG.L","ELA.L","DP3D.L","DP3C.L","DNE.L","DNDL.L","DIG.L","CRWN.L","COP.L","CLIG.L","CHAR.L","CAZA.L","BVT.L","BUT.L","BSV.L","BRSC.L","BRLA.L","BNS.L","BNKR.L","BGS.L","BDV.L","BAF.L","ATST.L","ATI.L","ANW.L","AAS.L","AAM.L","AAEV.L","90ID.L","59PQ.L","0QHX.L","0GC9.L","TYK4.L","VIN.L","0F29.L","OXT.L","OEX.L","AADV.L","ION1.L","0O9Q.L","NTV.L","HHI.L","BRIG.L","0K9W.L","DP3H.L","GLAF.L","0R42.L","ONEV.L","SST.L","0JLQ.L","0NV5.L","AOFC.L","RPCN.L","HAN.L","0NR7.L","0KG0.L","0CX9.L","BTEM.L","HGL.L","FSV.L","OTMT.L","MIG2.L","TE20.L","CZA.L","EDGG.L","0R8V.L","0FFY.L","IVPB.L","EOG.L","MIX.L","0APM.L","0NES.L","PTEC.L","RDI.L","CRH.L","ZMNO.L","PFLM.L","UCP.L","QXT.L","QFI.L","CROS.L","QIL.L","55BC.L","MAB1.L","QIF.L","ENTU.L","PU11.L","PEMB.L","GAMA.L","0H1Z.L","0O6Z.L","ALD.L","FQM.L","0FRE.L","0NYK.L","AERO.L","0CHZ.L","QRM.L","SQS.L","RRL.L","INDV.L","CAL.L","AMED.L","ZOX.L","XTR.L","URA.L","SPSM.L","SWEF.L","STGR.L","SRT.L","SRES.L","SGZ.L","RUG.L","RGI.L","SZCD.L","TYRU.L","VZC.L","80GM.L","VSN.L","UU.L","UTV.L","UTL.L","UTG.L","UKM.L","UKCM.L","UCG.L","TYR.L","SRIA.L","SPSY.L","SOM.L","PPIX.L","MHM.L","LLD1.L","GFTU.L","GEEC.L","ENDV.L","DUPD.L","BXP.L","BC94.L","ALF.L","CCC.L","ATMA.L","ZEG.L","WAFM.L","VTU.L","VSVS.L","VRP.L","VP.L","VLE.L","VIS.L","VIP.L","VGAS.L","VEC.L","VCP.L","VAL.L","SEQI.L","PREM.L","MIL.L","LIV.L","IEVH.L","FTSV.L","DP3E.L","DO1D.L","D4OA.L","BME.L","AUTO.L","AMC.L","AGR.L","AGQ.L","AGP.L","AAA.L","0OPA.L","KAY.L","0NM8.L","ECEL.L","VLX.L","PPEA.L","0KDD.L","PCGB.L","0NQM.L","0FJQ.L","0GYM.L","0N2Z.L","DO1B.L","YKBD.L","DP2C.L","0IIF.L","VNI.L","MMH.L","DVWA.L","NCCL.L","DP3A.L","TPV1.L","NWIG.L","D4SO.L","CLC.L","FLX.L","TECH.L","0NMK.L","VAST.L","0QFP.L","OTC.L","OCV4.L","IEVD.L","VRS.L","PUM9.L","0MKX.L","0G67.L","PMH.L","BRWM.L","ATK.L","WHE.L","WTI.L","WSG.L","WSBN.L","WRN.L","WORK.L","WLFE.L","WINK.L","WIN.L","WIL.L","TLA.L","SPX.L","SMWH.L","SLE.L","SHAW.L","PRW.L","MWE.L","GAW.L","ELE.L","AMFW.L","AFS.L","AEWU.L","0NR4.L","0MKZ.L","0EEZ.L","BWRA.L","PPB.L","0G6J.L","WSL.L","0N0B.L","GWMO.L","NWR.L","0O8X.L","0OBQ.L","0O0U.L","CBP.L","WGP.L","D4LC.L","RDL.L","WTG.L","PXOG.L","0HZD.L","PEWZ.L","PUR.L","WYN.L","0O0V.L","EHG.L","XPP.L","XCH.L","XAR.L","LBB.L","GTLY.L","FIVE.L","87UC.L","40SI.L","APGN.L","TAL.L","0OR4.L","XLM.L","40JP.L","0ELC.L","UKML.L","89VS.L","44RS.L","LLPG.L","XPL.L","XSG.L","IHC.L","0R3P.L","AVCT.L","YOU.L","YNGA.L","TLY.L","SOPH.L","RRR.L","RGM.L","PTV.L","PRTC.L","PRSM.L","PHP.L","PFP.L","EQN.L","CTP.L","CSP.L","BNR.L","FCIF.L","CRC.L","0QG5.L","YMTD.L","0FR0.L","USG.L","YOLO.L","GLOO.L","STX.L","0O7D.L","ASCL.L","ERET.L","IBST.L","SEN.L","0R51.L","ONZ.L","0N73.L","ACP.L","GHG.L","RRE.L","DFX.L","CGP.L","YMT1.L","OTB.L","DUKE.L","HONY.L","YUJ.L","DVT.L","0K96.L","MCS.L","HUNT.L","SCH.L","SEQC.L","DLG.L","0O6D.L","NXR.L","LIVN.L","YU.L","CLCD.L","PEZ.L","CCJI.L","365.L","HSTG.L","FISH.L","HW.L","SILF.L","0M3P.L","SERE.L","0HAC.L","0HAA.L","98KI.L","PROJ.L","RGL.L","FAL.L","JMO.L","FAIC.L","HSW.L","PURP.L","CER.L","0GKA.L","LVRT.L","GHS.L","CHGN.L","SCT.L","WPG.L","NCYF.L","SQNC.L","MTRO.L","MTV.L","DTC.L","CGNR.L","BWO.L","0RB9.L","0QQD.L","0QP2.L","BRFC.L","INLZ.L","CICZ.L","ECWZ.L","0MNP.L","ZZZ.L","SALV.L","SHOE.L","0R8I.L","0NR6.L","0M2V.L","0NNC.L","0QXN.L","AIFZ.L","UTLC.L","0DVR.L","AST.L","REAT.L","0QQ8.L","MHN.L","0MYY.L","ZIOC.L","ZOL.L","DP2K.L","ZAM.L","ELTZ.L","0MJH.L","87FZ.L","0OII.L","0NZU.L","SIPP.L","ZCC.L","GYM.L","0DHC.L","SAC.L","0NZY.L","ZYT.L","JZCZ.L","ZENB.L","ZTF.L","ZBO.L","0NO3.L","0QJQ.L","ZOO.L","WATR.L","CHZN.L","AA.L","AAU.L","0MG0.L","0GUV.L","0OKS.L","AAIF.L","AAAP.L","AAVC.L","0NX1.L","AAI.L","AA4.L","0N5A.L","AAZ.L","AATG.L","ABT.L","0IZM.L","0GRP.L","0GXG.L","0HBP.L","0R87.L","0GT1.L","0R80.L","0H9P.L","0NX2.L","0R6W.L","0R3W.L","0GO4.L","0QDX.L","0QJA.L","0QCV.L","0R82.L","0GW3.L","0P49.L","0MI6.L","AJIT.L","0NNR.L","0HR3.L","0RBI.L","0HEZ.L","DAB.L","0QRA.L","0QXM.L","0GWL.L","0Q8G.L","0I5O.L","0N31.L","0R53.L","0R7S.L","0QIG.L","0O93.L","AGIT.L","0R84.L","0N7D.L","0HDL.L","0GWB.L","0R8O.L","0NL3.L","0OA9.L","0MR5.L","0GRX.L","0GNX.L","0MHZ.L","0RD7.L","0R7R.L","0R8W.L","0H14.L","AUKT.L","0GO5.L","0R8T.L","ABZA.L","0GTM.L","0RCY.L","0M8Y.L","0NWX.L","0H0G.L","0QEN.L","0NWD.L","0H0F.L","0N7X.L","0NC6.L","0Q77.L","ABDP.L","0QUU.L","0GXJ.L","0MDT.L","0R86.L","0R6R.L","0HBY.L","0QFH.L","0GP7.L","0GWC.L","ASCH.L","0NC5.L","0HTP.L","0MTD.L","0H30.L","0NWW.L","0KII.L","0R4P.L","0R8U.L","0RDM.L","0MI1.L","0H34.L","0MWH.L","0KIZ.L","0QUT.L","0R81.L","ABTU.L","0RB7.L","0GTN.L","0Q78.L","0RBW.L","0HNK.L","APEF.L","0R9X.L","0QE6.L","0NUK.L","0L9Q.L","0P4X.L","0NCQ.L","0GX4.L","0GTR.L","0O5H.L","0GYX.L","0OPJ.L","ALAI.L","0MHT.L","ABD.L","0GZV.L","0R8R.L","0H38.L","0HDK.L","0GTW.L","0H0L.L","0GT3.L","0NB9.L","0GNM.L","0R4G.L","ABBY.L","0MQG.L","0HW6.L","0NDX.L","0GWV.L","0GRZ.L","0H6T.L","0MR4.L","0QD0.L","0OFO.L","0IAH.L","0MW2.L","0GWG.L","0IKJ.L","0QSD.L","0QIA.L","0OFP.L","0JNL.L","0R77.L","0JAA.L","0GN0.L","0IHM.L","0RCO.L","0MHW.L","0MI5.L","0R7Q.L","0QV0.L","0O1W.L","0KBQ.L","0H0U.L","0R5W.L","0R7X.L","0H2Z.L","0H2O.L","0QI7.L","0JYZ.L","0N5E.L","0JDU.L","0R8Q.L","0GTU.L","0HBT.L","0GQE.L","0HC0.L","0H19.L","0GUX.L","0OAE.L","0QUB.L","0MI3.L","0R7O.L","0MWK.L","0QVR.L","0NNF.L","0NUI.L","0HDJ.L","0GSU.L","0GW0.L","ACA.L","PACC.L","AIF.L","ACL.L","ACID.L","22406.L","0H59.L","0QMD.L","GACA.L","ACO.L","ACHL.L","CHAL.L","GACB.L","0MHD.L","ACHP.L","0QRT.L","0H4K.L","0N2Q.L","0HV2.L","0QMN.L","0E80.L","0OIQ.L","ACC.L","AEG.L","ACSO.L","0P4C.L","ACD.L","BVC.L","ADT.L","ADM.L","AVO.L","AMS.L","AFN.L","ADSS.L","ADGO.L","0NOL.L","ADAM.L","0N5H.L","0OLD.L","0RA1.L","0QNM.L","ADL.L","0LO9.L","ADA.L","BA29.L","AEX.L","AEC.L","SPRP.L","0DKX.L","AEO.L","0FC9.L","0R3R.L","0GY8.L","0OHY.L","0R4Y.L","AEP.L","0Q0Y.L","AFPO.L","CMB.L","AFRB.L","AFC.L","3DR.L","AFRI.L","0OG4.L","AFRK.L","AOF.L","AFMF.L","PAF.L","AFHP.L","CAF.L","SAPO.L","AFID.L","0QWD.L","SBLM.L","0QVL.L","0QIQ.L","PMEA.L","CZB.L","AGY.L","AGRO.L","AGM.L","0QMG.L","0QKD.L","0O1R.L","0JK4.L","0H3T.L","0FRW.L","0HAI.L","0EUH.L","0NIQ.L","0P0C.L","0KED.L","0RB8.L","TUIN.L","0IZC.L","0Q8Q.L","0MG2.L","0OM4.L","0QGG.L","0O0J.L","0MPH.L","0G77.L","0FDT.L","0P5F.L","0NJO.L","0Q4C.L","0P6O.L","0E4K.L","0LQ4.L","62UL.L","0NBT.L","0G7B.L","0JVS.L","0EYI.L","0GOX.L","0HA0.L","0H3Q.L","0G6T.L","0QJV.L","0O2G.L","0JYO.L","0R3T.L","0OPB.L","0R6U.L","0NJB.L","0K5E.L","0QC9.L","0QN1.L","0DXG.L","0GNN.L","0R97.L","AGOL.L","0QOQ.L","0QOA.L","TUIJ.L","0MT8.L","0MKE.L","0R5G.L","0QTP.L","REA.L","0K7F.L","0P6S.L","0QP5.L","0Q9C.L","0R3N.L","0FQR.L","0Q99.L","0R50.L","0NBI.L","0RBK.L","0QFU.L","0GDR.L","0EPW.L","0DK9.L","0QOG.L","0QM5.L","0NKH.L","0NDP.L","0M2T.L","0MJZ.L","0I3Z.L","0N70.L","0MIP.L","0RC9.L","0N6Z.L","0QON.L","0MFU.L","0MUF.L","0R7E.L","0MJ1.L","0RAR.L","0QPJ.L","0NYZ.L","0QJS.L","0J9O.L","0R88.L","0QOK.L","0QQ2.L","0EX7.L","0QKA.L","0N7O.L","0RCG.L","0O05.L","0DPM.L","0GJN.L","0QJX.L","0NIF.L","0NXR.L","0FRJ.L","0QPP.L","0Q3C.L","0M98.L","0IYN.L","0E4J.L","0NFG.L","0O1C.L","0H7I.L","0NR1.L","0IRF.L","0P6N.L","0QDS.L","0MJK.L","0DQ7.L","0QQY.L","0EEI.L","0R8P.L","0EWR.L","0NJK.L","0ENN.L","0MFY.L","0O27.L","0QAL.L","0QMT.L","0MCG.L","0OP0.L","0QQ7.L","0QWC.L","0QP1.L","0H9X.L","0OC2.L","0QP4.L","0HI7.L","0K77.L","0EEE.L","0MMD.L","0QJC.L","0DLW.L","AGOU.L","0QN3.L","0R9K.L","0QGJ.L","0KUY.L","0MG5.L","0QO7.L","0IZ8.L","AGTA.L","0QK5.L","0QOL.L","0QM4.L","0QQR.L","0NTM.L","0NXX.L","0DYD.L","0MJ5.L","0MZX.L","0H7D.L","0MMJ.L","0QO3.L","0QNA.L","0DUI.L","0Q8F.L","0AH7.L","0L9J.L","0NI1.L","0DLF.L","0FGL.L","0QOP.L","0QUC.L","0QO8.L","0NF3.L","0QMW.L","0QA8.L","0R3M.L","0N6M.L","0MPT.L","0GE4.L","AIA.L","0NTI.L","0QKI.L","AMPH.L","0GC8.L","0QLR.L","0QMA.L","0QMV.L","0RBM.L","0MV2.L","0FJC.L","0QPY.L","0QO1.L","0NKL.L","0G15.L","0QK3.L","0QMO.L","0QUW.L","0J04.L","0QNE.L","0EW1.L","0QNG.L","0NDV.L","0QQ6.L","0OQX.L","0NZ7.L","0P3F.L","0NIR.L","0MJ9.L","0MPM.L","0QFR.L","0GJK.L","0GVE.L","0QW9.L","AIEA.L","NCA2.L","HHV.L","0FGH.L","0NP9.L","OSEC.L","0NWF.L","0LN7.L","AIR.L","HHVT.L","WIZZ.L","OOA.L","0KVV.L","AJG.L","0LUU.L","0NS1.L","0E6Y.L","0LZF.L","0O0N.L","0MHU.L","0H3X.L","0OFR.L","0FMN.L","0MG1.L","0NJS.L","0H4A.L","0G29.L","0IPT.L","0NCV.L","0OK7.L","0KFE.L","0QBM.L","0OIU.L","0E64.L","0QX7.L","0H6X.L","0MCK.L","0GRG.L","0QXP.L","0LS5.L","0GB7.L","0P2A.L","0LQG.L","0FMO.L","0LVL.L","0OLG.L","0P6M.L","0DVE.L","0N2X.L","AKR.L","0DRH.L","0LND.L","BPKD.L","0MJR.L","0Q2N.L","0J9C.L","0QI0.L","0H13.L","0LWM.L","0O8D.L","0MJX.L","0NMI.L","0FPQ.L","0F58.L","0MPJ.L","0LQ1.L","0NBO.L","0JOE.L","0MKH.L","0O5C.L","0BQD.L","0GWS.L","0H7B.L","0MCJ.L","0QA0.L","0NQH.L","ALM.L","BABU.L","APH.L","ANR.L","AN.L","ALT.L","0RAN.L","0RAL.L","AXM.L","0Q2F.L","0O1S.L","78QZ.L","0NZV.L","0O9B.L","ALU.L","LEAL.L","ATS.L","ALLG.L","ALPH.L","ARGP.L","0J2R.L","HAST.L","0RCS.L","0MGN.L","0K7K.L","0M6S.L","0LBS.L","ALBA.L","ATT.L","APAX.L","0DJI.L","0OIR.L","ATSS.L","ALBH.L","0N5Z.L","0IWK.L","PACL.L","0HA8.L","0N7N.L","0DJV.L","AMP.L","AMER.L","AMBR.L","0K7Y.L","0N61.L","CRS.L","AT2.L","0RDX.L","BAC.L","0P2W.L","NAIT.L","0R4L.L","AMO.L","BRNA.L","0OGQ.L","0O7J.L","AMR.L","0DLI.L","0RAE.L","ANTO.L","SCL.L","EAH.L","ANP.L","ANH.L","ANCR.L","0O1Z.L","DMGT.L","0NP8.L","0IGF.L","PGOO.L","0O33.L","HNL.L","0P6Z.L","OGDC.L","PEW.L","0NX0.L","0HVA.L","04HK.L","APF.L","CMIP.L","0QSH.L","MIG6.L","HSM.L","0NEX.L","RIV.L","0MFW.L","0O6E.L","0QAI.L","0QTI.L","UAI.L","ANA.L","0K9N.L","0HB1.L","0Q1G.L","0CSD.L","37OC.L","ASY.L","0NK9.L","0IPY.L","RKMD.L","NUOG.L","AYM.L","0OMV.L","BKIR.L","0G2X.L","0DP0.L","AOMD.L","AOR.L","APC.L","0R2V.L","APT.L","0QTZ.L","0GZK.L","0NNU.L","APR.L","0OLF.L","AQP.L","0I8C.L","ARW.L","ARL.L","ARGO.L","ARBB.L","AVP.L","0OI0.L","0IB0.L","ARC.L","0KAV.L","ARG.L","ARDN.L","ARS.L","ARO.L","0NSF.L","ARTA.L","0N6B.L","ASTO.L","ASHM.L","LIO.L","ASC.L","ASCD.L","0JI9.L","0K78.L","0Q92.L","0N08.L","0JII.L","0MTP.L","0NX3.L","NSA.L","0MV4.L","0KEH.L","0DME.L","0OJC.L","0QB8.L","0FIN.L","0MHR.L","0IUQ.L","ATR.L","0QB7.L","SQN.L","0FI5.L","IAT.L","0MHP.L","0J8S.L","0FS8.L","IPX.L","0JEZ.L","0OHL.L","0OA7.L","0Q8M.L","0R4H.L","0HW0.L","0E4Q.L","0GW8.L","0R4V.L","0P0T.L","0M2Z.L","0DNW.L","0QWK.L","0Q2S.L","0DIJ.L","0P3N.L","0R3I.L","0GF6.L","0OAW.L","0OMB.L","0EHF.L","0MSG.L","0R9I.L","0IMT.L","ASBE.L","0NO0.L","0KB6.L","0FHP.L","PAC.L","0FWY.L","PHU.L","0JWO.L","0MSJ.L","0R6B.L","0QWV.L","0DMQ.L","0FF9.L","0OCD.L","0K82.L","0RD6.L","CAML.L","0MHM.L","0G8C.L","0IKH.L","KMCA.L","0O84.L","0RAI.L","EAT.L","0EOF.L","0GM2.L","0KV7.L","ASPL.L","0JXF.L","0MD9.L","0M5J.L","ASA.L","0MHS.L","0E9S.L","0P2J.L","0IM3.L","0R3Y.L","ATQT.L","0OKR.L","0DNH.L","0MJT.L","0MIQ.L","0MKP.L","ATAD.L","ATY.L","0M8O.L","0I2R.L","ATYM.L","0IY1.L","ATC.L","SEE.L","MNC.L","IFL.L","FCR.L","BSE.L","88E.L","AUK.L","AUG.L","0JHU.L","0DZC.L","0LD1.L","FTE.L","AVN.L","AVM.L","AVGR.L","0QTX.L","AVG.L","GMAA.L","AVS.L","AV-A.L","0IAX.L","AV-B.L","0N6K.L","AVON.L","AVAP.L","0Q2K.L","0QVY.L","0NV2.L","AXB.L","0HAR.L","0P5L.L","AXBA.L","AXI.L","0MHJ.L","0N9I.L","0LBM.L","BCN.L","BAG.L","TSB.L","TIBD.L","LLPD.L","HLCL.L","BNK.L","BLEY.L","BKM.L","BBY.L","BODD.L","0QL3.L","0O5V.L","BAUD.L","TGBD.L","SBID.L","UBLS.L","BAV.L","0LBN.L","0LNQ.L","TBCB.L","GRTB.L","BAR.L","0DOS.L","BBYB.L","BBOX.L","BB39.L","BB90.L","SFI.L","IBEX.L","BCRE.L","BCB.L","BCGR.L","BCA.L","BC88.L","BC32.L","BDI.L","BD15.L","BD45.L","BD70.L","BD82.L","BLV.L","RB.L","BMK.L","BEM.L","BEG.L","0O9C.L","0NEM.L","0R72.L","0Q9M.L","0NHV.L","0QI2.L","0FQN.L","0G99.L","0EYG.L","0EKR.L","0KK7.L","0O8G.L","0KDK.L","0DQK.L","0MFT.L","0N9Z.L","0KCP.L","0J0M.L","0DPU.L","0JXZ.L","0MEL.L","0IN2.L","BOTB.L","0ON7.L","0NTU.L","0FSO.L","NTBR.L","0FSN.L","0K6S.L","0NZT.L","0OF3.L","BQ30.L","0HNZ.L","BHRD.L","0K9A.L","0MU2.L","0N2C.L","0R55.L","0FA0.L","0NZR.L","0FBS.L","BZT.L","0OQJ.L","0O2T.L","0QGK.L","0QF5.L","0IWV.L","BEE.L","0NSI.L","0G8L.L","BVM.L","TCS.L","GLTD.L","0NDA.L","SNGR.L","BGLF.L","BLT.L","BHMU.L","RSE.L","BHY.L","BHME.L","TRIG.L","GMR.L","BHGU.L","BHGG.L","BIOM.L","BILN.L","0O0E.L","BISI.L","RXB.L","0JG5.L","BVXP.L","0MGP.L","IBT.L","0OBK.L","BILL.L","BIOG.L","0J2W.L","0DUK.L","0NK7.L","MTFB.L","0N6Y.L","SBS.L","OXB.L","0NRG.L","LNTA.L","BJU.L","BKMA.L","37NY.L","0QOS.L","BKIC.L","BSET.L","BLVN.L","BLUR.L","BRCI.L","BLBD.L","TBGR.L","BRGE.L","BRD.L","BLP.L","BLU.L","BRGS.L","BSIF.L","0QSW.L","BQAD.L","BPFU.L","DGS.L","CTI.L","CAPD.L","CAT.L","UTLE.L","RQIH.L","UEMS.L","0QIX.L","SLP.L","0K9V.L","CATC.L","HKLD.L","JAR.L","BMN.L","0K8L.L","0Q2T.L","RLD.L","0HYK.L","0NV9.L","0REH.L","SRO.L","BMD.L","MDOB.L","UEM.L","BOL.L","PURE.L","BMS.L","BMR.L","BNZL.L","BNC.L","0QUI.L","ELSA.L","0HB5.L","BOR.L","LWB.L","BOY.L","BON.L","BOIL.L","0N75.L","BOD.L","0MMZ.L","0R6E.L","0LO8.L","BOX.L","0ELN.L","0HAN.L","0O7A.L","BOO.L","0IXZ.L","0DTF.L","BP-A.L","BP-B.L","BPI.L","SIS.L","BPC.L","BPM.L","0DPG.L","CCDS.L","NBS.L","KWS.L","IMT.L","BRK.L","HVT.L","BWSA.L","BRY.L","BRAM.L","0OLJ.L","44GL.L","MOSB.L","MBH.L","BSD.L","BSC.L","BTG.L","BUR.L","0LRV.L","0NVR.L","0MH1.L","0NVQ.L","0QVD.L","EFID.L","FP.L","LKOB.L","RSTI.L","LKOD.L","HYDR.L","BYOT.L","CHE.L","CIHL.L","GAL.L","CDFF.L","CAU.L","CAR.L","CAPC.L","CAD.L","SPPC.L","SGR.L","POLR.L","PLA.L","MGHC.L","ECAP.L","COG.L","CMX.L","CAY.L","CARR.L","CAM.L","CAKE.L","EDG.L","0MGH.L","CSI.L","CFYN.L","FCI.L","MCT.L","AUE.L","MXCP.L","TPS.L","CMBN.L","CBQS.L","CBUY.L","CBKD.L","CCP.L","CCT.L","CCR.L","CCPG.L","CCPA.L","CCAP.L","CCPE.L","CCPC.L","CNIC.L","OPM.L","CDOG.L","CLL.L","TCSC.L","FETD.L","CEPS.L","C21.L","0R9C.L","0HY2.L","CWR.L","CRND.L","GOAL.L","0N8F.L","CNKS.L","0K02.L","LKCS.L","CEIR.L","0N7Q.L","0DYQ.L","0QFK.L","0QV5.L","0FJJ.L","0GRK.L","TRCN.L","0NZF.L","STCM.L","CEIA.L","0NQZ.L","CLTV.L","TOWN.L","CFHL.L","CF.L","CFX.L","CFHS.L","CGS.L","CGLO.L","CGH.L","CGVD.L","CGW.L","0O2V.L","CTG.L","CHRT.L","CTR.L","CSN.L","CHH.L","CHG.L","CHA.L","CNSD.L","0QR4.L","0QOR.L","0LS7.L","CHT.L","58GZ.L","0QKM.L","0NPL.L","CIC.L","CINE.L","CTY.L","0HJC.L","RSAB.L","CICG.L","0E2N.L","CIFU.L","ECV.L","CITY.L","CIN.L","CYN.L","BA69.L","CTYA.L","CKN.L","GRIT.L","CLNR.L","CLI.L","CLG.L","IXI.L","HANA.L","CLIN.L","CLP.L","CTO.L","CLCC.L","CLON.L","CLSU.L","CTAG.L","GCLA.L","CMS.L","CMH.L","CML.L","CMCX.L","CNC.L","CNR.L","CNN.L","CNS.L","CNMI.L","CNEL.L","0QGU.L","CPP.L","CPI.L","NTEA.L","RE-B.L","CPX.L","CPS.L","CPR.L","CRV.L","CRL.L","CRDA.L","CSSG.L","CRX.L","CRW.L","0K93.L","CRAW.L","CRU.L","50GP.L","0E1S.L","0I1W.L","PVCS.L","CRE.L","0NF8.L","CRN.L","49GP.L","0DZJ.L","WCW.L","CRON.L","0HBF.L","CSRT.L","CSG.L","CTH.L","0QIM.L","0Q7S.L","MNP.L","CVSG.L","CVR.L","CWD.L","CYBG.L","0KJ1.L","0MNQ.L","SPDI.L","CYAN.L","0J5Y.L","UEN.L","CYS.L","DTG.L","DRTY.L","DATA.L","DAN.L","DAIP.L","0HB4.L","0HDP.L","0E3C.L","0N4I.L","RDT.L","DAL.L","0E1N.L","0KFX.L","0NVC.L","DALR.L","DNL.L","NBDG.L","0QAJ.L","LBOW.L","DCP.L","DCI.L","DDV1.L","DDD.L","DLN.L","0FH7.L","0MSD.L","0H00.L","0HBA.L","0QFT.L","0O14.L","0MYZ.L","0NW8.L","DFS.L","0RB3.L","DGE.L","DGED.L","0QEO.L","DPLM.L","DIA.L","DIVI.L","SDV.L","DIS.L","KDR.L","0HY6.L","0NWR.L","0GZX.L","0R7P.L","HDIV.L","ODX.L","0QWA.L","0N8R.L","GMD.L","DSG.L","SDI.L","DIGS.L","0QWI.L","PRO.L","0OLN.L","0NWJ.L","DJI.L","0QCQ.L","0R78.L","0QJ4.L","0JH4.L","0NPJ.L","0G33.L","0MGE.L","0R5Z.L","0Q4U.L","0R6Z.L","0QIU.L","0MGB.L","0MRM.L","0QBO.L","0QRS.L","0RB2.L","0ND5.L","0QEK.L","0QFA.L","0MGD.L","0K9P.L","0O77.L","0NEZ.L","0M4M.L","0MGC.L","0MOP.L","0AI4.L","0O76.L","0MR6.L","0DPB.L","0M0A.L","0JN9.L","0NQC.L","0O3W.L","0OJA.L","DNA3.L","DNA2.L","DNA.L","DOTD.L","DO1O.L","D4OO.L","D4SA.L","DODS.L","DP2G.L","DP2D.L","0F2Q.L","0FYM.L","DO1C.L","DO1A.L","DP2F.L","0E63.L","DP2E.L","D467.L","DP3J.L","DP2A.L","DP3F.L","DQE.L","GDG.L","DRIP.L","DRG.L","EFM.L","FEVR.L","0F7F.L","0LN9.L","0FN4.L","DVW.L","DWHA.L","DWHT.L","MERL.L","TME.L","REM.L","EZH.L","EEP.L","EPO.L","EBIV.L","LME.L","FEC.L","0NYH.L","OEC1.L","ECWO.L","ECR.L","0QS1.L","ECK.L","ELLA.L","EDGI.L","EDGD.L","EDL.L","EDGH.L","66XD.L","EDGF.L","0HBO.L","EDGC.L","WEY.L","EDEN.L","0MUM.L","0ML1.L","0OF7.L","EPIC.L","EDV.L","0QS9.L","EDGE.L","EWI.L","EFGD.L","EGS.L","32QX.L","TEEG.L","EGMD.L","EGI.L","EIH.L","0E5V.L","0NPT.L","EKT.L","TTG.L","ELCO.L","0QVP.L","0NWV.L","51FL.L","TECD.L","0EA2.L","LGLD.L","0NVD.L","ELX.L","0K9T.L","0RA8.L","0I8Y.L","JPEC.L","MEL.L","39IB.L","JPEI.L","SMSD.L","0K97.L","TRE.L","FEET.L","EMG.L","EMAN.L","EMIS.L","EMM.L","ESP.L","SVM.L","EMH.L","EMR.L","SOU.L","SEY.L","PHE.L","INSE.L","IGAS.L","HAWK.L","GOOD.L","ESR.L","ENQ.L","ETQ.L","0OJX.L","IE1D.L","0N9S.L","HR1O.L","IE1G.L","INSP.L","HR1A.L","0NRE.L","REAC.L","ESO.L","EPIA.L","FPEO.L","SLES.L","FAST.L","SEP.L","IVPU.L","IVPG.L","SEC.L","PAL.L","JPEL.L","PEY.L","ERM.L","0O87.L","0MHC.L","0MGV.L","0RCP.L","SBD.L","GPOR.L","ESNT.L","0RC6.L","0NQG.L","0N9V.L","0RE4.L","0MKW.L","0OFU.L","RLE.L","0R7W.L","0ILK.L","0OMG.L","ESCH.L","TDE.L","0R9G.L","0M0Q.L","0QVM.L","0EM7.L","MTVW.L","0ILL.L","FCRE.L","0QRL.L","0MKT.L","0NQ2.L","0OMK.L","0QF4.L","0HA9.L","0MKO.L","0R99.L","0RDV.L","SRE.L","MOLD.L","HWG.L","0H7O.L","0KD1.L","0N9G.L","0Q8P.L","0R9F.L","ET.L","0P2N.L","0MKG.L","0RDU.L","0G9W.L","0NV7.L","0EDZ.L","SGRE.L","0O4L.L","0EBQ.L","0QDL.L","0K9H.L","0NRN.L","0NFS.L","HID.L","0QEU.L","0H4N.L","0OHG.L","0HIT.L","0NPV.L","ETX.L","ETLN.L","0HV8.L","0OFM.L","62UM.L","0N4Y.L","EUSP.L","EUA.L","0HZC.L","0QE2.L","0QVJ.L","EUT.L","HNE.L","0RA4.L","JESC.L","0NW7.L","MTE.L","0JNI.L","0LTM.L","TRG.L","0P72.L","TORO.L","HVE.L","HEFT.L","EWG.L","0OBR.L","JEO.L","0MV5.L","0LNI.L","JETI.L","EVG.L","EVO.L","0IX0.L","0QQJ.L","MPE.L","FTVP.L","KMG.L","S68.L","PPE.L","EXO.L","0EEV.L","FFX.L","FJET.L","0MGR.L","FFWD.L","FARN.L","FAIR.L","0MFG.L","FAM.L","FRP.L","0NXV.L","FKL.L","FBDU.L","FBH.L","FCCN.L","FCS.NZ","FDM.L","FDL.L","FDP.L","FDBK.L","FENR.L","FEN.L","0RDT.L","0P52.L","0R4W.L","FEES.L","PUMX.L","TEA.L","PCF.L","LFI.L","FKE.L","0KI5.L","FIF.L","0EGH.L","0QFC.L","0M2O.L","0O46.L","FITB.L","0JX9.L","SKFS.L","0MET.L","GLIZ.L","MFX.L","0ONG.L","0G91.L","PCFS.L","NSF.L","0EG8.L","0KC3.L","TFG.L","0KBX.L","NBLS.L","FLO.L","0R96.L","FLOW.L","NBLU.L","0EHB.L","RGD.L","FRM.L","PFD.L","FSFL.L","FRCL.L","FTVI.L","FTF.L","FTSC.L","0J6V.L","FTN.L","FOX.L","FTV.L","0P4F.L","0OFC.L","0MQ2.L","0MKM.L","TUNE.L","0HAH.L","0FI1.L","VLG.L","FPO.L","TERN.L","0Q6Q.L","0MGU.L","0IUJ.L","0FPB.L","0F3T.L","0R8M.L","0G1T.L","0KB3.L","0RC1.L","0IN3.L","0NDS.L","0NKO.L","0IEB.L","0IW5.L","0QVK.L","0EVI.L","0MV8.L","0OPS.L","0MGJ.L","0OPY.L","0MH6.L","0K4O.L","0NPH.L","0NEL.L","0NZM.L","0J3F.L","0IXT.L","0MGL.L","0EKE.L","0NWK.L","0MGS.L","0NR2.L","0IQU.L","0P5I.L","0OFQ.L","0NY8.L","0F8T.L","0NQF.L","0NQ5.L","0OCQ.L","0OO9.L","0NY3.L","0K8N.L","0NTX.L","0HB2.L","0NW1.L","0NQT.L","0RCC.L","0NM7.L","0F8V.L","0O9Y.L","FSTA.L","FTC.L","FUM.L","0LNT.L","MPO.L","54GW.L","PTF.L","0B4R.L","IGC.L","FUL.L","FUTR.L","GRIO.L","TCF.L","OIG.L","WTR.L","MXF.L","SOI.L","OTM.L","53GW.L","0LCR.L","HYF.L","PJF.L","VND.L","VEND.L","KLBT.L","0NOF.L","INDI.L","GAME.L","GAID.L","NTOG.L","0EMK.L","GVP.L","HDY.L","81JK.L","0QT5.L","STR.L","0B67.L","GAH.L","VOG.L","SCGL.L","GLR.L","LOGP.L","LAD.L","ITRK.L","IPO.L","INTQ.L","IME.L","GRG.L","GNI.L","TYM.L","TSTL.L","TSG.L","TRIC.L","TRI.L","TPT.L","TNI.L","TFW.L","TCN.L","TAN.L","TAIH.L","SXX.L","SVS.L","SVR.L","SUS.L","SUN.L","SULA.L","STY.L","STI.L","STCK.L","SRSP.L","SPT.L","SPH.L","SPE.L","SNTY.L","SNG.L","SND.L","SMS.L","SMIN.L","SGI.L","SGC.L","SFR.L","SEA.L","SAVP.L","SAT.L","SAL.L","RPT.L","RPO.L","RHL.L","RENE.L","RCN.L","RBN.L","PYC.L","PTY.L","PTD.L","PRS.L","PRM.L","PRES.L","PPS.L","POG.L","PNS.L","PMR.L","PLE.L","PIM.L","PHTM.L","PHO.L","PFLB.L","PEN.L","PAYS.L","PANR.L","MUR.L","MUL.L","MTO.L","MTC.L","MSLH.L","MSG.L","MOS.L","MONI.L","MLIN.L","MKLW.L","MGNS.L","MER.L","MDZ.L","MCO.L","MBT.L","MAI.L","MACF.L","LTG.L","LSC.L","LPA.L","LOOK.L","LOK.L","LMP.L","LGT.L","LEG.L","LDSG.L","LDP.L","LAND.L","LAKE.L","ITQ.L","ITE.L","IOM.L","INVP.L","INTU.L","INPP.L","INL.L","IMTK.L","IMO.L","IGR.L","IGP.L","IGE.L","HZM.L","HYNS.L","HUM.L","HRG.L","HMLH.L","HILS.L","HCFT.L","GPX.L","GHE.L","GGP.L","GDWN.L","GDP.L","GCL.L","E2V.L","76ID.L","67GX.L","TRCS.L","SOG.L","IDH.L","RCDO.L","NTA.L","HYG.L","MCB.L","85GU.L","SPA.L","OXF.L","MAGP.L","NAK.L","GTC.L","LLPE.L","PCA2.L","TRAF.L","IGV.L","SAG.L","WGB.L","SLN.L","MXO.L","KIT.L","7DIG.L","0RBC.L","SAN.L","PINN.L","TPVA.L","PTO.L","GEM.L","MIG1.L","OXS.L","LLPC.L","NBI.L","GCM.L","KRS.L","GFIN.L","SSTY.L","SSE.L","RXP.L","ROSE.L","HYD.L","PAA.L","HUW.L","STVG.L","TCT.L","PXS.L","TRC.L","STE.L","ISG.L","TE18.L","PROG.L","SHG.L","MTU.L","PGY.L","HYR.L","LAM.L","SCPA.L","PEG.L","68HN.L","IVO.L","MIN.L","TRP.L","TE23.L","TEK.L","TR00.L","OCV3.L","HAT.L","RMV.L","92IP.L","MRCH.L","CHL.L","MMP.L","SERV.L","REDX.L","LID.L","HR2O.L","TE19.L","UTW.L","INVR.L","RWS.L","MIG.L","IBSA.L","PNA.L","MGHP.L","NEP.L","TE24.L","PGD.L","79GL.L","UNG.L","PIRI.L","MYIB.L","MGHI.L","IPP.L","IDOX.L","JPB.L","SAMS.L","MPM.L","HYUP.L","HLPD.L","14NY.L","TAT.L","46GM.L","19PS.L","WTKD.L","50XD.L","0KHH.L","0EKA.L","0QT6.L","0OGA.L","0DQZ.L","0RBN.L","0OPE.L","0NIJ.L","0IE9.L","0J6Y.L","G4M.L","WIND.L","SMTG.L","0HAZ.L","MGHU.L","GFIR.L","0JWU.L","0O2W.L","SPL.L","PPH.L","JZCP.L","TPOG.L","IBPO.L","IGCS.L","VTA.L","TFIF.L","NESF.L","SMIF.L","0QXZ.L","RUSP.L","SIGB.L","KGLD.L","HBRN.L","GHT.L","TTR.L","GINV.L","888.L","NKTN.L","GIPO.L","0QPS.L","SWAP.L","GKO.L","GLPR.L","38KH.L","GLB.L","GBP.L","GBGR.L","PCFT.L","MIGO.L","PCGH.L","HSD.L","TGBL.L","MWGT.L","GWIK.L","P2P.L","GLTR.L","SIGT.L","0QV3.L","GMS.L","TGL.L","GOLD.L","GSR.L","NORD.L","NMG.L","ORE.L","0OHC.L","SFE.L","GPE.L","STM.L","TPVC.L","GUS.L","0ELV.L","GUSC.L","GVC.L","HDD.L","HHPD.L","HALO.L","JHDA.L","HHPG.L","HR2A.L","HAYT.L","HALS.L","HAIK.L","0M9A.L","0MGT.L","HSBK.L","HAL.L","HMI.L","HCL.L","HCM.L","HDT.L","0FIZ.L","HOT.L","0P5H.L","0R3U.L","0O26.L","THRL.L","UDG.L","0K9U.L","0M6I.L","PHC.L","0HAU.L","NMC.L","OTES.L","HSL.L","0EO8.L","HVTB.L","0NBD.L","HER.L","HVTA.L","0NVV.L","OPTI.L","HINT.L","0FIW.L","HGT.L","HWC.L","HMSF.L","PHDC.L","HNR.L","HIK.L","LED.L","0ISM.L","TNCI.L","HMSG.L","HNT.L","IL0A.L","HRN.L","HUR.L","0NUG.L","HUN.L","0M69.L","JLH.L","HVO.L","HYUD.L","MANX.L","HYUO.L","HYDG.L","0LWU.L","IBM.L","ICGT.L","IDEA.L","0QAG.L","PCI.L","TOT.L","INM.L","CON.L","PVR.L","MIO.L","NSH.L","GRN.L","PAP.L","IEVF.L","IEH.L","IFP.L","ORM.L","IEVG.L","0QT8.L","IE1H.L","IEM.L","PTR.L","PET.L","OGN.L","KYGA.L","0NBX.L","IGSS.L","IHUK.L","IHTD.L","IIT.L","IIP.L","RC2.L","IKA.L","PLUS.L","SIM.L","TRIT.L","MTMY.L","TAP.L","0MGY.L","BAGR.L","MATD.L","0QY1.L","NCON.L","IPEL.L","0QVU.L","TCA.L","IMB.L","IMPT.L","3LEG.L","OPG.L","IMM.L","TAU.L","OPP.L","0BJP.L","0NPX.L","IONA.L","IONB.L","IOF.L","FIPP.L","IPSA.L","OMIP.L","0KA3.L","IPE.L","IQE.L","42CL.L","IRAO.L","IRR.L","IRV.L","IRON.L","IRG.L","0MUN.L","0ESX.L","RIIC.L","ISL.L","RIII.L","0QRG.L","ITM.L","0MU6.L","0LLP.L","0R8Y.L","0NIG.L","0GA3.L","0NQP.L","0O2D.L","0NJP.L","0RD2.L","0NV1.L","0NWY.L","0H6I.L","0QEP.L","0EWD.L","0NV4.L","0NUX.L","0OLX.L","0J03.L","0NFP.L","0DHJ.L","0HBC.L","0R5R.L","0O2B.L","0G9J.L","0QEJ.L","0NQB.L","0Q6M.L","0Q54.L","0KBS.L","0FNI.L","0N7I.L","0FM1.L","0R40.L","0IE3.L","0NE2.L","0N54.L","0O98.L","0NHY.L","0QII.L","0R9H.L","0E40.L","0QHK.L","PNX.L","0BKH.L","0NE1.L","0QVF.L","0G0W.L","0ND7.L","0FP9.L","0R8S.L","0RC2.L","0EW0.L","0MHA.L","0NSS.L","0MVJ.L","0E5M.L","0N6O.L","0NV0.L","0NJ5.L","0QE8.L","0R7M.L","0R4T.L","0QWN.L","0K69.L","0ONR.L","0NLD.L","0RDO.L","0N4P.L","0BKR.L","IVPM.L","JPSS.L","JWNG.L","JDS.L","0MGO.L","0EXG.L","WAND.L","UBMN.L","MAYA.L","TMT.L","MEDI.L","0N0K.L","MACC.L","PSDL.L","JIGI.L","JIGU.L","JSI.L","JUSC.L","JMC.L","JMI.L","KCEL.L","MGNT.L","NVTK.L","MNZS.L","JSG.L","SGGD.L","NCSP.L","MFON.L","WJG.L","URKA.L","0Q0J.L","MAW.L","JPI.L","KKB.L","SSAA.L","RM.L","JUS.L","0QS4.L","0EYB.L","96OX.L","0KVR.L","KCR.L","0BNT.L","KEM.L","0MGG.L","70HF.L","0Q9Y.L","0IIH.L","0G68.L","0G5B.L","0QV7.L","LWRF.L","0F4I.L","0N77.L","0O8F.L","0LNG.L","0II2.L","KTCD.L","133971.L","0F1N.L","UEP.L","VCBC.L","TPL.L","LEK.L","VNL.L","VNIL.L","0Q82.L","0QKY.L","LTOD.L","LTHP.L","SO4.L","0O4B.L","LSLI.L","LCG.L","0QKB.L","PSL.L","LNTR.L","RLH.L","0MW7.L","0IVJ.L","LGCD.L","TTST.L","RIGD.L","PHRM.L","MAVD.L","61HE.L","U14.L","LSIC.L","SUBX.L","NPSN.L","LKOE.L","LKOS.L","LLD7.L","LLD8.L","0MK9.L","LLD2.L","LLD5.L","LLD6.L","SIR.L","TAVI.L","LWI.L","0QNO.L","0QK6.L","LOTS.L","LSRG.L","54UD.L","0MNC.L","0OEY.L","0OGK.L","0QUL.L","0O4N.L","RM2.L","0HXB.L","INFT.L","0M6P.L","REDD.L","MMC.L","MAJE.L","MHID.L","MTEC.L","0DU3.L","MCC.L","MDC.L","MDMG.L","0FC3.L","72HN.L","OSU.L","0KCU.L","MGR.L","MHPC.L","71HT.L","0QTR.L","PDZ.L","MIG4.L","MPAY.L","OMI.L","MMX.L","MNKS.L","0M8V.L","0FB0.L","0MQT.L","MORT.L","SIT.L","MRL.L","MRS.L","MSI.L","MTH.L","MTR.L","MUT.L","37HR.L","MWY.L","MXCT.L","0R5P.L","MYX.L","NBR.L","0RCR.L","0QKG.L","NAH.L","0QAV.L","0IHK.L","NAR.L","NWBD.L","0KBT.L","0R8Z.L","NBNK.L","NCT.L","STAC.L","STAB.L","NET.L","WOR.L","NII.L","NTLG.L","0GX2.L","0K11.L","RMA.L","AUCT.L","0P47.L","0QGH.L","0QVV.L","0NXM.L","0NO1.L","0NLS.L","0LNJ.L","0NW2.L","0RCL.L","0QHL.L","0NX9.L","0NIS.L","0OAB.L","0QUM.L","0NMR.L","0QXR.L","0NXN.L","0QSG.L","0EPM.L","0QCO.L","0INB.L","0P1G.L","0LNN.L","0MKS.L","0KAR.L","0R6J.L","0DM6.L","NLMA.L","0DQH.L","0O8V.L","0G45.L","0MEC.L","0J1N.L","0IVM.L","NVA.L","NOP.L","0Q57.L","0P38.L","0G40.L","NRRP.L","0J1Z.L","0HAF.L","0QSQ.L","VICO.L","0FM2.L","0MTK.L","0GAF.L","NWF.L","69SI.L","OTV2.L","SBIA.L","38LF.L","STS.L","91ID.L","40XT.L","70SK.L","PHOR.L","10NC.L","70ZF.L","OKEY.L","0FHC.L","ONL.L","UTN.L","0QVQ.L","OPRA.L","0LX1.L","TPOP.L","TE21.L","WPC.L","TE13.L","SHRS.L","VNC.L","PUMA.L","SCF.L","SDU.L","PUM8.L","TE10.L","VEN2.L","TPO.L","0OQV.L","PVN.L","0M2N.L","MAV4.L","VEN.L","VENC.L","0Q18.L","MIG5.L","OTT.L","TE22.L","TE25.L","TES4.L","SLS.L","TP5B.L","OTPD.L","0MGI.L","0FJ8.L","OUT.L","COPL.L","U11.L","OXP.L","0DP4.L","0MFI.L","0HAG.L","0OA1.L","0FNZ.L","0CXC.L","0EIE.L","0KCK.L","0M1M.L","SVST.L","TMKS.L","PINR.L","PKG.L","PCTN.L","PESD.L","PER.L","0NQ9.L","PEMV.L","0HAT.L","TPRD.L","SNP.L","PRP.L","PFLA.L","PFZ.L","0MN3.L","0FQ8.L","PHD.L","WPHO.L","PHSC.L","PIDD.L","PIK.L","0RCT.L","PIP.L","0OQ0.L","PIL.L","PWS.L","0KO8.L","SDM.L","37ZM.L","TCSA.L","SYM.L","0GB6.L","SCLP.L","RIC.L","COST.L","SLNG.L","PTH.L","SMDR.L","ENRT.L","PMP.L","0MC5.L","TPCL.L","0KLO.L","POL.L","0RA2.L","PLMO.L","PPG.L","PPC.L","PPIR.L","0QG9.L","0ML0.L","PTSG.L","0IEF.L","TLI.L","0IZ2.L","PURI.L","0NQE.L","0FQI.L","PVG.L","RSS.L","0CIJ.L","RUS.L","RBD.L","RBG.L","RDW.L","SCS.L","RGS.L","RIFA.L","RIFS.L","0QMU.L","RSTR.L","RNO.L","RWA.L","0O1V.L","SNG1.L","RTI.L","RST.L","AURR.L","RUR.L","0MUI.L","SRX.L","0O6A.L","0NW4.L","0IIO.L","0IT3.L","SSY.L","SCE.L","LIFE.L","SREI.L","0RDS.L","SRG.L","0KJB.L","SGP.L","0QMI.L","SGM.L","U96.L","S63.L","0MPL.L","S59.L","SKS.L","SNCL.L","SIXH.L","SIHL.L","SKMD.L","SNAK.L","SNX.L","S32.L","0NJQ.L","SPSC.L","SQZ.L","WSE.L","TE02.L","STOB.L","37ZL.L","STG.L","TE01.L","58HA.L","STL.L","0OHK.L","SUMM.L","SUEL.L","SPGH.L","0QQ9.L","0NRV.L","SWP.L","0QL6.L","SWL.L","WTS.L","0HDQ.L","0QSA.L","TNG.L","TND.L","TAST.L","TCY.L","TRT.L","UKT.L","THAL.L","TJI.L","TLOU.L","TMMG.L","TMK.L","TPG.L","TSTR.L","0D53.L","TUNG.L","TYMN.L","0NVL.L","UBI.L","UTLD.L","UKW.L","MINC.L","UKR.L","MINI.L","SANB.L","USY.L","93MQ.L","0NLK.L","0HH1.L","UPL.L","0QIW.L","0OB3.L","0QP8.L","VED.L","SER.L","MYSQ.L","WALG.L","WPCT.L","VNH.L","VMT.L","WTM.L","WTE.L","0DQP.L","WINE.L","86IP.L","0QVI.L","WSP.L","WYG.L","AUM.L","AUR.L","0MI0.L","BRH.L","78GL.L","0O0F.L","MAC.L","RED.L","CNCT.L","COA.L","0P46.L","0J3X.L","COS.L","0NZ1.L","0K8W.L","0E7S.L","0MPP.L","0LD0.L","R4E.L","0OG6.L","MAFL.L","0QL7.L","FRI.L","FRUT.L","GBG.L","GRA.L","0KAZ.L","INB.L","IND.L","0OQQ.L","INFA.L","0KA0.L","0QAU.L","INS.L","LTTD.L","MARL.L","MED.L","0QAH.L","MES.L","0F89.L","THR.L","MIRA.L","MYXR.L","SAR.L","SAA.L","REC.L","47IE.L","SAFE.L","TRD.L","SAV.L","TRAK.L","0FOS.L","PRND.L","PROX.L","REH.L","REVO.L","0KBZ.L","0FVZ.L","SAF.L","0IU8.L","0O59.L","0Q4J.L","0QAX.L","SEV.L","SOLI.L","0QLN.L","0J6X.L","TRB.L","TRV.L"]

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
