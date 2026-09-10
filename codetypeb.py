
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
          if len(parts) >= 3:
            rows.append(parts)
    elif isinstance(item, str):
      parts = item.split(",")
      if len(parts) >= 3:
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
                    #Historical data 
#====================================================== ===================
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
#==================================================================================================
                                          # master button
#===================================================================================================
url = 'https://api.mstock.trade'
response = requests.get(f"{url}/openapi/typea/getoptionchainmaster/2", headers=headers3)
expiry = response.json()
st.write(response.status_code)
expiry_ids = expiry['data']['dctExp']                       # dictionary of key:value
list_epoch = list(expiry_ids.values())                       #list of epoch
epoch_len =len(list_epoch)
with st.expander (" serial no.7 is 1st-Sep-2026 expiry"):
  st.write(list_epoch)

master_chain = pd.DataFrame(expiry)

expiry_ID = list(expiry['data']['dctExp'].keys())
expiry_epoch = list(expiry['data']['dctExp'].values())
merged_ID={"expiry_ID":expiry_ID, "expiry_epoch":expiry_epoch}

IDdf = pd.DataFrame(merged_ID)

future = expiry['data']['FUTIDX']
future_ID = parse_option_data1(future)

#------------------------below calculation is only for getting Nifty symbol token to get Intraday data of individual strikes---------------------

expiry_epoch = st.selectbox("Select Expiry", options = list_epoch, index=7, key='outexp')
response1 = requests.get(f"{url}/openapi/typea/GetOptionChain/2/{expiry_epoch}/26000", headers=headers3)
#st.write("status", response1.status_code)
result101 = response1.json()
expiry101 = result101["data"]["contractModel"]["exp"]
contract = result101["data"]["contractModel"]
st.write(expiry101)
st.write(contract)

st.write(list_epoch[0])
month_exp=[]
for i in list_epoch:
  exp = requests.get(f"{url}/openapi/typea/GetOptionChain/2/{i}/26000", headers=headers3)
  if exp.status_code==200 & exp['data']!='NULL':  
    result101 = exp.json()
    st.write(result101)
  else:
    st.write("Not Found")

st.write("Expiry Details", month_exp)











#--------------------------------------------------------get spot price-----------------------------

spot = requests.get(f'{url}/openapi/typea/instruments/intraday/1/26000/minute', headers=headers3)
st.write("Spot", spot.status_code)
spot1 = spot.text
spot2 = json.loads(spot1)
Time = spot2['data']['candles'][0][0]
Nifty_Close = round(spot2['data']['candles'][0][3])
Nifty_round = round(spot2['data']['candles'][0][3], -2)
Nifty_round_lower = round(spot2['data']['candles'][0][3], -2)- 800
Nifty_round_upper = round(spot2['data']['candles'][0][3], -2) + 800

st.write("Spot Nifty Intraday", Time, Nifty_Close, Nifty_round)

#---------------------------dataframe call /put data---------------------------------------------------------------------------- 

strike1_d =st.number_input("select first strike", value= Nifty_round_lower, key='strike1_d')
strike2_d =st.number_input("select second strike", value= Nifty_round_upper, key='strike2_d')
call_data_d = result101["data"]["call"]
put_data_d = result101["data"]["put"]
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
st.dataframe(option_chain_d, column_order=['CE.token','CE.OI','CE.volume','CE.strike', 'PE.volume','PE.OI', 'PE.token', 'CE.expiry'])

#ce_token = calldf_d['CE.token']
#pe_token = putdf_d['PE.token']

ce_token = calldf_refined_d['CE.token']
pe_token = putdf_refined_d['PE.token']


#------------------------------------------------getting intraday data------------------------------------------

token=st.number_input("F&O token No.", value=74068, key='f&o') 
response9 = requests.get(f'{url}/openapi/typea/instruments/intraday/2/{token}/minute', headers=headers3)
st.write("Intra", response9.status_code)
data12 = response9.text
data12 = json.loads(data12)
result01=data12["data"]["candles"]
result_df01 = pd.DataFrame(result01, columns =['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

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
CE_details = get_option_ind(ce_token, "CE")
PE_details = get_option_ind(pe_token, "PE")

st.write(PE_details)
st.write(CE_details)
