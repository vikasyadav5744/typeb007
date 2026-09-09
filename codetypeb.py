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


