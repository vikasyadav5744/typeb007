
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

st.title("Mirae Asset m.Stock - NIFTY Option Chain")

# ============================================================
# API SETTINGS
# ============================================================

# IMPORTANT:
# Do NOT hard-code your real API key in this file.
# Enter it through Streamlit sidebar or secrets.
api_key = st.sidebar.text_input(
    "m.Stock  API Key",
    type="password"
)

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

        conn = http.client.HTTPSConnection('api.mstock.trade')

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
            json.dumps(json_data),timeout=15,
            headers=headers)
            response = conn.getresponse()
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
otp = st.sidebar.text_input(
    "Enter OTP",
    type="password"
)

if st.sidebar.button("Generate Access Token"):

    if not api_key or not otp:
        st.error("Enter API Key and OTP.")
    else:

        session_url = f"{BASE_URL}/openapi/typea/session/token"

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
        except exceptions as e:
            st.write("Error:", e)
        else:
            st.write("nice job")
            st.write("Access token generated successfully")

# ============================================================
# ACCESS TOKEN
# ============================================================

# Optional manual access token

access_token = st.sidebar.text_input("Access Token (optional)",type="password")

# ============================================================
# COMMON HEADERS
# ============================================================

headers1 = {
    "X-Mirae-Version": "1",
    "Authorization": f"token {api_key}:{access_token}"
}

# ============================================================
# OPTION CHAIN MASTER
# ============================================================
chainmaster =st.sidebar.button("ChainMaster", key='key1')
if chainmaster:
    try:
        conn = http.client.HTTPSConnection("api.mstock.trade", timeout=10)
        headers4 = {
        "X-Mirae-Version": "1",
        "Authorization": f"token {api_key}:{access_token}"
        }
        conn.request(
        "GET",
        "/openapi/typea/getoptionchainmaster/2",
        headers=headers4
        )
        response = conn.getresponse()
        st.write("HTTP Status:", response.status)
        st.write("Reason:", response.reason)
        result = response.read().decode("utf-8")
        st.write("API Response:")
        st.write(result)
    
    except Exception as e:
        st.write("Error:", e)
    finally:
        conn.close()
    


    


    
