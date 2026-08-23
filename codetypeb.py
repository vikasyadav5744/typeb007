
import http.client
import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timezone, date

my_ip = requests.get("https://api.ipify.org", timeout=10).text
st.write("Current public IP:", my_ip)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="m.Stock NIFTY Option Chain",
    layout="wide"
)

st.title("Mirae Asset m.Stock - NIFTY Option Chain- Type B")
# ============================================================
# LOGIN
# ============================================================
conn = http.client.HTTPSConnection('api.mstock.trade')
st.sidebar.header("Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input(
    "Password",
    type="password"
)

if st.sidebar.button("Generate OTP", key='key2', help='note jwt & refresh token'):

    if not username:
        st.error("Enter Username")
    elif not password:
        st.error("Enter Password.")
    else:
    
        headers = {
            'X-Mirae-Version': '1',
            'Content-Type': 'application/json',
        }

        json_data = {
            'clientcode': username,
            'password': password,
            'totp': '',
            'state': '',
        }

        try:
            conn.request('POST',
            '/openapi/typeb/connect/login',
            json.dumps(json_data),
            headers=headers)
            response = conn.getresponse()
            st.write("Login HTTP Status:", response.status)
            st.write("HTTPS reason:", response.reason)

            try:
                st.json(response.json())
            except:
                st.write(response.read().decode("utf-8"))

            if response.ok:
                st.success("OTP sent to your registered mobile.")

        except Exception as e:
            st.error(f"Login error: {e}")


# ============================================================
# GENERATE Session with OTP
# ============================================================

api_key = st.sidebar.text_input(
    "m.Stock  API Key",
    type="password", key='key1')

refreshToken = st.sidebar.text_input(
    "refreshToken",
    type="password", 
    key= 'key3')

otp = st.sidebar.text_input(
    "Enter OTP",
    type="password", key= 'key4')

if st.sidebar.button("Generate Session", key='key5', help="requires freshtoken and otp"):

    if not api_key:
        st.error("Enter API Key.")
    elif not refreshToken:
        st.error("Enter refreshToken.")
    elif not otp:
        st.error("Enter OTP.")
    else:
        headers1 = {
        'X-Mirae-Version': '1',
        'X-PrivateKey': api_key,
        'Content-Type': 'application/json',
        }
        json_data1 = {
        'refreshToken': refreshToken,
        'otp': otp
        }
        try:
            conn.request('POST',
            '/openapi/typeb/session/token',
            json.dumps(json_data1), headers1)
            response1 = conn.getresponse()

            st.write("Session HTTP Status:", response1.status)
            st.write("HTTPS reason:", response1.reason)
            result1 = response1.json()
            st.json(result1)
        except Exception as e:
            st.write("Error:", e)
        else:
            st.write("nice job")
            st.write("Session generated successfully")

# ============================================================
#jwtTOKEN
# ============================================================
# Optional manual access token
jwtToken = st.sidebar.text_input("jwtToken Token", key='key6', type="password")
#==========================================================

# ============================================================
# OPTION CHAIN MASTER
# ============================================================

if st.sidebar.button("ChainMaster", key='key7', help="jwt &api_ke"):
    if not api_key:
        st.error("Enter API Key.")
    elif not jwtToken:
        st.error("Enter jwtToken.")
        try:
            headers4 = {
            'X-Mirae-Version': '1',
            'Authorization': jwtToken,
            'X-PrivateKey': api_key,
            'Content-Type': 'application/json',
            }
            conn.request(
            "GET",
            "/openapi/typeb/getoptionchainmaster/2",
            headers=headers4
            )
            response2 = conn.getresponse()
            st.write("HTTP Status:", response2.status)
            st.write("Reason:", response2.reason)
            result2 = response2.read().decode("utf-8")
            st.write("API Response:")
            st.write(result2)
        except Exception as e:
            st.write("Error:", e)
        finally:
            conn.close()
    


    


    
