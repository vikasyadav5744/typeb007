
import http.client
import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timezone, date

my_ip = requests.get("https://api.ipify.org", timeout=10).text
st.write("Current public IP:", my_ip)

#_--------++++----------------------

def parse_option_data(option_data):
  rows = []
  for item in option_data:
    # item may itself be a list
    if isinstance(item, list):
      for x in item:
        if isinstance(x, str):
          parts = x.split(",")
          if len(parts) == 4:
            rows.append(parts)
    elif isinstance(item, str):
      parts = item.split(",")
      if len(parts) == 4:
        rows.append(parts)
  return rows
#====================================================
def parse_option_data1(option_data):
  rows = []
  for item in option_data:
    # item may itself be a list
    if isinstance(item, list):
      for x in item:
        if isinstance(x, str):
          parts = x.split(",")
          if len(parts) == 6:
            rows.append(parts)
    elif isinstance(item, str):
      parts = item.split(",")
      if len(parts) == 6:
        rows.append(parts)
  return rows
# ============================================================
                                      # PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="m.Stock NIFTY Option Chain",
    layout="wide"
)

st.title("Mirae Asset m.Stock - NIFTY Option Chain")


#=============================================================
                      #Session State
#============================================================
def generate__access_token():
    token = "YOUR_GENERATED_ACCESS_TOKEN"
    st.session_state.access_token = token
    api = "YOUR_GENERATED_API_KEY"
    st.session_state.access_token = api

#def generate__api_key():
    #api = "YOUR_GENERATED_API_KEY"
   # st.session_state.access_token = api
# ============================================================
                                         # API SETTINGS
# ============================================================

api_key = st.sidebar.text_input(
        "m.Stock Type A API Key",
        type="password", key="api_key")
# ============================================================
                                         # ACCESS TOKEN
# ============================================================
access_token = st.sidebar.text_input("Access Token (optional)",type="password", key="access_token")

#=======================================================================

login_input =st.sidebar.checkbox("show login Inputs", key='key11')

if login_input==True:  
    BASE_URL = "https://api.mstock.trade"
# ============================================================
                                      # LOGIN
# ============================================================
    st.sidebar.header("Login")
    
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input(
        "Password",
        type="password"
    )
    
    if st.sidebar.button("Generate OTP"):
    
        if not username or not password:
            st.error("Enter Username and Password.")
        else:
    
            login_url = f"{BASE_URL}/openapi/typea/connect/login"
    
            headers = {
                "X-Mirae-Version": "1",
                "Content-Type": "application/x-www-form-urlencoded"
            }
    
            payload = {
                "username": username,
                "password": password
            }
    
            try:
    
                response = requests.post(
                    login_url,
                    headers=headers,
                    data=payload,
                    timeout=15
                )
    
                st.write("Login HTTP Status:", response.status_code)
    
                try:
                    st.json(response.json())
                except:
                    st.write(response.text)
                if response.ok:
                    st.success("OTP sent to your registered mobile.")
            except Exception as e:
                st.error(f"Login error: {e}")
# ============================================================
                     # GENERATE ACCESS TOKEN
# ============================================================
session_token  =st.sidebar.checkbox("Generate Access Token ", key='key10')

if session_token:
    otp = st.sidebar.text_input(
        "Enter OTP",
        type="password"
    )
    BASE_URL1 = "https://api.mstock.trade"
    if st.sidebar.button("Generate Access Token"): # on_click=generate_access_token):
    
        if not api_key or not otp:
            st.error("Enter API Key and OTP.")
        else:
    
            session_url = f"{BASE_URL1}/openapi/typea/session/token"
    
            headers = {
                "X-Mirae-Version": "1",
                "Content-Type": "application/x-www-form-urlencoded"
            }
    
            payload = {
                "api_key": api_key,
                "request_token": otp,
                "checksum": "L"
            }
    
            try:
    
                response = requests.post(
                    session_url,
                    headers=headers,
                    data=payload,
                    timeout=15
                )
    
                st.write("Session HTTP Status:", response.status_code)
                result = response.json()
                st.json(result)
                #st.session_state.api_key = api_key
           
            except exceptions as e:
                st.write("Error:", e)
            else:
                st.write("nice job")
                st.write("Access token generated successfully")
# ============================================================
# COMMON HEADERS


#  ---------------------------------------------------------- Getting NIFTY / Stock Chain details--------------------------------------------
                      #Intraday Data
#------------------------------------------------------------------------------
conn = http.client.HTTPSConnection('api.mstock.trade')
headers3 = {
          "X-Mirae-Version": "1",
          "Authorization": f"token {api_key}:{access_token}",
      }

Intraday_criteria =st.sidebar.checkbox("show Intraday Data", key='key20')

if Intraday_criteria==True:
  exchange = st.sidebar.selectbox("Choose Exchange", key="key101", options=[1,2,3,4], help="1-NSE, 2-NFO, 3-CDS, 4-BSE, 5-BFO")
  token = st.sidebar.number_input("Symbol No.", key="key102", value=26000)
  interval = st.sidebar.selectbox("Choose Interval", key="key103", options=['minute','5minute','10minute', '15minute', '30minute', '60minute', 'day'])
  conn.request(
      'GET',
      f'/openapi/typea/instruments/intraday/{exchange}/{token}/{interval}',
      headers=headers3
  )
  response6 = conn.getresponse()
  submit3 = st.sidebar.button("NIFTY / Stock Data", key="key109")
  if submit3:
      st.write("HTTP Status:", response6.status)
      response_text2 = response6.read().decode("utf-8")
      data2 = json.loads(response_text2)
      result202= data2["data"]["candles"]
      st.json(data2)
      result_df = pd.DataFrame(result202, columns =['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
      st.write(result_df)
# ============================================================
# OPTION CHAIN MASTER Expiry data
# ============================================================
conn1 = http.client.HTTPSConnection('api.mstock.trade')
epoch_list =[1475159400,1477578600,1479911400,1483021800,1490884200,1498746600,1472740200,1473345000,1473949800,1474554600,1514471400,1530196200,1561645800,1577284200,1593095400,1609425000,1624545000]
chaimaster_criteria =st.sidebar.checkbox("show Expiry Data", key='key12')
if chaimaster_criteria==True:
    chainmaster =st.sidebar.button("ChainMaster Expiry Data", key='chainmaster')
    if chainmaster:
        try:
            conn1.request(
            "GET",
            "/openapi/typea/getoptionchainmaster/2",
            headers=headers3
            )
            response = conn1.getresponse()
            st.write("HTTP Status:", response.status)
            st.write("Reason:", response.reason)
            result = response.read().decode("utf-8")
            result = json.loads(result)
            st.json(result)
            #st.write(result['data']['OPTIDX'][3])    
        except Exception as e:
            st.write("Error:", e)
        finally:
            conn.close()
#======================================================
                    #Historical data 
#====================================================== 
conn3 = http.client.HTTPSConnection('api.mstock.trade')
hist_criteria=st.sidebar.checkbox("Historical Data", key='hist_criteria')
if hist_criteria:
  exchange_str= st.sidebar.selectbox("Exchane", key='exchange', options=['NSE','NFO','BSE','BFO'], index=0)
  inst_token=int(st.sidebar.number_input("Instrument Token", key='instrument', value=74068))
  interval_hist= st.sidebar.selectbox("Choose Interval", key="interval_hist", options=['minute','5minute','10minute', '15minute', '30minute', '60minute', 'day'])
  fromdate = st.sidebar.date_input("Choose From Date", format="YYYY-MM-DD", key='fromdate')
  todate = st.sidebar.date_input("Choose To Date", format="YYYY-MM-DD", key='todate')
  
  if st.sidebar.button("Historical Data", key="historical_data"):
    conn3.request(
    'GET',
    f'/openapi/typea/instruments/historical/{exchange_str}/{inst_token}/{interval_hist}?from={fromdate}&to={todate}',
    headers=headers3)
    response_hist = conn3.getresponse()
    st.write("HTTP hist status:", response_hist.status)
    st.write("HTTP hist reason:", response_hist.reason)
    result4 = response_hist.read().decode("utf-8")
    data4= json.loads(result4)
    st.json(data4)
#======================================================
                    #scrip Master
#====================================================== 
conn4 = http.client.HTTPSConnection('api.mstock.trade')
script_criteria=st.sidebar.checkbox("Script Master Data", key='script_criteria')
if script_criteria:
  if st.sidebar.button("Script Mastert Data", key="scriptmaster_data"):
    conn4.request(
    'GET',
    f'/openapi/typea/instruments/scriptmaster',
    headers=headers3)
    response_script = conn4.getresponse()
    st.write("HTTP hist status:", response_script.status)
    st.write("HTTP hist reason:", response_script.reason)
    result5 = response_script.read().decode("utf-8")
    #st.write (result5)

#======================================================
                    # OHLC
#====================================================== 
ohlc_criteria=st.sidebar.checkbox("OHLC Data", key='ohlc_criteria')
if ohlc_criteria:
  exchange_str1 = st.sidebar.selectbox("Exchange", key='exchange1', options=['NSE','NFO','BSE','BFO'], index=0)
  symboleq = st.sidebar.text_input("Trading Symbol for Equity", key='sybmol', value='ACC-EQ', help='if using NFO:- NIFTY2681224350CE')
  if st.sidebar.button("OHLC Data", key="ohlc_data"):
    params = {
        'i':
            f'{exchange_str1}:{symboleq}'
    }
    st.write(params)
    response_ohlc = requests.get('https://api.mstock.trade/openapi/typea/instruments/quote/ohlc', params=params, headers=headers3)
    st.write("HTTP hist status:", response_ohlc.status_code)
    st.write("HTTP hist reason:", response_ohlc.reason)
    if response_ohlc == response_ohlc.json():
      st.json(response_ohlc)
    else:
      st.json(response_ohlc.text)
  # ============================================================
# OPTION CHAIN MASTER  CALL / PUT Data
# ============================================================

conn2 = http.client.HTTPSConnection('api.mstock.trade')
call_criteria=st.sidebar.checkbox("Contract Master Data", key='call_criteria')
if call_criteria:
  strike1=st.sidebar.number_input("select first strike", 21000, 28000, 23500, 50, key='strike1')
  strike2=st.sidebar.number_input("select second strike", 21000, 28000, 24500, 50, key='strike2')
  expiry= st.sidebar.selectbox("Epoch", key='expiry', options=epoch_list, index=6)
  token1=st.sidebar.number_input("select token", value=26000, key='token1')
  callmaster=st.sidebar.button("Get Contract Master CE/PE", key='callmaster')
  if callmaster:
    conn2.request(
    'GET',
    f'/openapi/typea/GetOptionChain/2/{expiry}/{token1}',
    headers=headers3)
    response101 = conn2.getresponse()
    st.write("HTTP reason:", response101.reason)
    st.write("HTTP status:", response101.status)
    result3 = response101.read().decode("utf-8")
    data3= json.loads(result3)
    with st.expander("See json response"):
      st.json(data3)
    expiry = data3["data"]["contractModel"]['exp']
    call_data= data3["data"]["call"]
    put_data= data3["data"]["put"]
    call_rows = parse_option_data(call_data)
    put_rows = parse_option_data(put_data)
    calldf = pd.DataFrame(call_rows, columns=['CE.token','CE.strike','CE.OI','CE.ChngOI']).fillna(0, inplace=True)
    calldf = calldf.astype('int64')
    calldf['CE.strike'] =calldf['CE.strike']/100
    calldf_refined = calldf[calldf['CE.strike'].between(strike1, strike2)]
    calldf_refined['CE.expiry'] = expiry
    putdf = pd.DataFrame(put_rows, columns=['PE.token','PE.strike','PE.OI','PE.ChngOI']).fillna(0, inplace=True)
    putdf = putdf.astype('int64')
    putdf['PE.strike'] = putdf['PE.strike']/100
    putdf_refined = putdf[putdf['PE.strike'].between(strike1, strike2)]
    putdf_refined['PE.expiry'] = expiry
    option_chain =pd.concat([calldf_refined,putdf_refined], axis=1, ignore_index=False)
    st.dataframe(option_chain, column_order=['CE.token','CE.OI','CE.ChngOI','CE.strike','PE.ChngOI','PE.OI','PE.token', 'CE.expiry'])
    st.write(calldf_refined)

    
    exp_list= []
    for item in epoch_list:
      response103=requests.get('https://api.mstock.trade'
      f'/openapi/typea/GetOptionChain/2/{item}/26000',
      headers=headers3)
      if response103== response103.json():
        exp1=response103["data"]["contractModel"]["exp"]
        exp_list.append(str(exp1))
        st.write("need to be printed", exp_list)
#==================================================================================================
                                          # master button
#===================================================================================================
url = 'https://api.mstock.trade'
response = requests.get(f"{url}/openapi/typea/getoptionchainmaster/2", headers=headers3)
expiry = response.json()
expiry_ids = expiry['data']['dctExp']                       # dictionary of key:value
list_epoch = list(expiry_ids.values())                       #list of epoch
epoch_len =len(list_epoch)
with st.expander (" serial no.7 is 1st-Sep-2026 expiry"):
  st.write(list_epoch)
#------------------------below calculation is only for getting Nifty symbol token to get Intraday data of individual strikes---------------------
expiry_epoch = st.selectbox("Select Expiry", options = list_epoch, index=7, key='outexp')
response1 = requests.get(f"{url}/openapi/typea/GetOptionChain/2/{expiry_epoch}/26000", headers=headers3)
st.write("status", response1.status_code)
result101 = response1.json()
expiry101 = result101["data"]["contractModel"]["exp"]
st.write(expiry101)
#---------------------------dataframe call /put data---------------------------------------------------------------------------- 
strike1_d=st.number_input("select first strike", 21000, 28000, 23500, 50, key='strike1_d')
strike2_d=st.number_input("select second strike", 21000, 28000, 24500, 50, key='strike2_d')
call_data_d= result101["data"]["call"]
put_data_d= result101["data"]["put"]
call_rows_d = parse_option_data(call_data_d)
put_rows_d = parse_option_data(put_data_d)
calldf_d = pd.DataFrame(call_rows_d, columns=['CE.token','CE.strike','CE.OI','CE.volume']).fillna(0, inplace=True)
calldf_d = calldf_d.astype('int64')
calldf_d['CE.strike'] =calldf_d['CE.strike']/100
calldf_d['CE.OI'] =calldf_d['CE.OI']/65
calldf_d['CE.volume'] =calldf_d['CE.volume']/65
calldf_refined_d = calldf_d[calldf_d['CE.strike'].between(strike1_d, strike2_d)]
calldf_refined_d['CE.expiry'] = expiry101
putdf_d = pd.DataFrame(put_rows_d, columns=['PE.token','PE.strike','PE.OI','PE.volume']).fillna(0, inplace=True)
putdf_d = putdf_d.astype('int64')
putdf_d['PE.strike'] = putdf_d['PE.strike']/100
putdf_d['PE.OI'] =putdf_d['PE.OI']/65
putdf_d['PE.volume'] =putdf_d['PE.volume']/65
putdf_refined_d = putdf_d[putdf_d['PE.strike'].between(strike1_d, strike2_d)]
putdf_refined_d['PE.expiry'] = expiry101
option_chain_d =pd.concat([calldf_refined_d,putdf_refined_d], axis=1, ignore_index=False)
st.dataframe(option_chain_d, column_order=['CE.token','CE.OI','CE.volume','CE.strike','PE.OI', 'PE.volume','PE.token', 'CE.expiry'])

ce_token = calldf_d['CE.token']
pe_token = putdf_d['PE.token']

#------------------------------------------------getting intraday data------------------------------------------
token=st.number_input("F&O token No.", value=74068, key='f&o') 
response9 = requests.get(f'{url}/openapi/typea/instruments/intraday/2/{token}/minute', headers=headers3)
st.write("Intra", response9.status_code)
data12 = response9.text
data12 = json.loads(data12)
result01=data12["data"]["candles"]
result_df01 = pd.DataFrame(result01, columns =['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
st.write('intraday:', result_df01)

st.write(ce_token)

def get_option_ind(token, para):

    option_data = []

    for tkn in token:

        response = requests.get(
            f'{url}/openapi/typea/instruments/intraday/2/{tkn}/minute',
            headers=headers3
        )

        data12 = response.json()

        # Check API response
        if data12.get("status") != "success":
            st.error(f"API Error for token {tkn}: {data12}")
            continue

        result01 = data12["data"]["candles"]

        if not result01:
            continue

        result_df01 = pd.DataFrame(
            result01,
            columns=[
                'Timestamp',
                'Open',
                'High',
                'Low',
                'Close',
                'Volume'
            ]
        )
      
        result_df01 ['token'] = tkn
        result_df01 ['type'] = para
      
        # Convert only numeric columns
        numeric_cols = [
            'Open',
            'High',
            'Low',
            'Close',
            'Volume'
        ]

        result_df01[numeric_cols] = result_df01[numeric_cols].apply(
            pd.to_numeric,
            errors='coerce'
        )

        option_data.append(result_df01)

    # Combine all option tokens
    if option_data:
        return pd.concat(
            option_data,
            axis=0,
            ignore_index=True
        )

    return pd.DataFrame(
        columns=[
            'Timestamp',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume',
            'token',
            'type'
        ]
    )
red = get_option_ind(ce_token, "CE")

st.dataframe(red)
