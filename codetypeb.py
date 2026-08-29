import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# ============================================================
# PAGE CONFIG
# ============================================================

my_ip = requests.get("https://api.ipify.org", timeout=10).text
st.write("Current public IP:", my_ip)


st.set_page_config(
    page_title="Mirae NIFTY Option Chain",
    layout="wide"
)

st.title("📊 Mirae Asset m.Stock - NIFTY Option Chain")


# ============================================================
# API INPUTS
# ============================================================

api_key = st.text_input(
    "Mirae API Key",
    type="password"
)

access_token = st.text_input(
    "Access Token",
    type="password"
)


# ============================================================
# SETTINGS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    interval = st.selectbox(
        "Candle Interval",
        [
            "minute",
            "3minute",
            "5minute",
            "10minute",
            "15minute",
            "30minute",
            "60minute"
        ]
    )

with col2:
    strikes_each_side = st.selectbox(
        "Strikes around ATM",
        [5, 10, 15, 20],
        index=1
    )

with col3:
    refresh = st.button(
        "🔄 Refresh Option Chain"
    )


# ============================================================
# HEADERS
# ============================================================

def get_headers():

    return {
        "X-Mirae-Version": "1",
        "Authorization": f"token {api_key}:{access_token}"
    }


# ============================================================
# GET OPTION CHAIN
# ============================================================

def get_option_chain():

    url = (
        "https://api.mstock.trade/openapi/typea/"
        "instruments/quote/optionchain"
    )

    params = {
        "i": "NSE:NIFTY"
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# PARSE CALL / PUT
# ============================================================

def parse_options(option_list, option_type):

    rows = []

    for item in option_list:

        try:

            values = item.split(",")

            if len(values) < 4:
                continue

            token = int(values[0])
            strike = int(values[1]) / 100
            oi = int(values[2])
            volume = int(values[3])

            rows.append({
                "token": token,
                "strike": strike,
                "OI": oi,
                "Volume": volume,
                "Type": option_type
            })

        except Exception:
            continue

    return pd.DataFrame(rows)


# ============================================================
# GET OHLC / CANDLES
# ============================================================

def get_latest_ohlc(token):

    # Current trading date
    today = datetime.now().strftime("%Y-%m-%d")

    from_time = f"{today} 09:15:00"
    to_time = f"{today} 15:30:00"

    url = (
        f"https://api.mstock.trade/openapi/typea/"
        f"instruments/historical/NFO/{token}/{interval}"
    )

    params = {
        "from": from_time,
        "to": to_time
    }

    try:

        response = requests.get(
            url,
            headers=get_headers(),
            params=params,
            timeout=15
        )

        response.raise_for_status()

        result = response.json()

        candles = result["data"]["candles"][""]

        if not candles:
            return {
                "Open": None,
                "High": None,
                "Low": None,
                "Close": None
            }

        latest = candles[-1]

        return {
            "Open": latest[1],
            "High": latest[2],
            "Low": latest[3],
            "Close": latest[4]
        }

    except Exception:

        return {
            "Open": None,
            "High": None,
            "Low": None,
            "Close": None
        }


# ============================================================
# MAIN
# ============================================================

if api_key and access_token:

    try:

        with st.spinner("Getting NIFTY option chain..."):

            result = get_option_chain()

        if result.get("status") != "success":

            st.error("Mirae API returned an error.")
            st.json(result)

        else:

            data = result["data"]

            # ----------------------------------------------
            # UNDERLYING
            # ----------------------------------------------

            spot_text = data.get("spot", "")

            spot = None

            try:
                spot = float(
                    spot_text.split(",")[1]
                )
            except Exception:
                pass


            # ----------------------------------------------
            # EXPIRY
            # ----------------------------------------------

            expiry = data["contractModel"]["exp"]


            # ----------------------------------------------
            # CALL
            # ----------------------------------------------

            call_df = parse_options(
                data.get("call", []),
                "CE"
            )


            # ----------------------------------------------
            # PUT
            # ----------------------------------------------

            put_df = parse_options(
                data.get("put", []),
                "PE"
            )


            # ----------------------------------------------
            # CHECK DATA
            # ----------------------------------------------

            if call_df.empty or put_df.empty:

                st.error(
                    "CE or PE data is empty."
                )

                st.json(result)

            else:

                # ------------------------------------------
                # FIND ATM
                # ------------------------------------------

                all_strikes = sorted(
                    set(call_df["strike"])
                    |
                    set(put_df["strike"])
                )

                if spot is not None:

                    atm = min(
                        all_strikes,
                        key=lambda x: abs(x - spot)
                    )

                else:

                    atm = all_strikes[
                        len(all_strikes) // 2
                    ]


                # ------------------------------------------
                # SELECT STRIKES
                # ------------------------------------------

                atm_index = all_strikes.index(atm)

                start = max(
                    0,
                    atm_index - strikes_each_side
                )

                end = min(
                    len(all_strikes),
                    atm_index + strikes_each_side + 1
                )

                selected_strikes = all_strikes[start:end]


                # ------------------------------------------
                # FILTER
                # ------------------------------------------

                call_df = call_df[
                    call_df["strike"].isin(
                        selected_strikes
                    )
                ].copy()

                put_df = put_df[
                    put_df["strike"].isin(
                        selected_strikes
                    )
                ].copy()


                # ==================================================
                # GET OHLC
                # ==================================================

                progress = st.progress(0)

                total = len(call_df) + len(put_df)

                counter = 0


                # CALL OHLC

                call_ohlc = []

                for token in call_df["token"]:

                    ohlc = get_latest_ohlc(token)

                    call_ohlc.append(ohlc)

                    counter += 1

                    progress.progress(
                        min(counter / total, 1.0)
                    )


                call_ohlc_df = pd.DataFrame(
                    call_ohlc,
                    index=call_df.index
                )

                call_df = pd.concat(
                    [call_df, call_ohlc_df],
                    axis=1
                )


                # PUT OHLC

                put_ohlc = []

                for token in put_df["token"]:

                    ohlc = get_latest_ohlc(token)

                    put_ohlc.append(ohlc)

                    counter += 1

                    progress.progress(
                        min(counter / total, 1.0)
                    )


                put_ohlc_df = pd.DataFrame(
                    put_ohlc,
                    index=put_df.index
                )

                put_df = pd.concat(
                    [put_df, put_ohlc_df],
                    axis=1
                )


                progress.empty()


                # ==================================================
                # RENAME
                # ==================================================

                call_df = call_df.rename(
                    columns={
                        "token": "CE_Token",
                        "OI": "CE_OI",
                        "Volume": "CE_Volume",
                        "Open": "CE_Open",
                        "High": "CE_High",
                        "Low": "CE_Low",
                        "Close": "CE_Close"
                    }
                )

                put_df = put_df.rename(
                    columns={
                        "token": "PE_Token",
                        "OI": "PE_OI",
                        "Volume": "PE_Volume",
                        "Open": "PE_Open",
                        "High": "PE_High",
                        "Low": "PE_Low",
                        "Close": "PE_Close"
                    }
                )


                # ==================================================
                # MERGE CE + PE
                # ==================================================

                final_df = pd.merge(
                    call_df.drop(
                        columns=["Type"]
                    ),
                    put_df.drop(
                        columns=["Type"]
                    ),
                    on="strike",
                    how="outer"
                )


                final_df = final_df.sort_values(
                    "strike"
                )


                # ==================================================
                # DISPLAY HEADER
                # ==================================================

                st.subheader("NIFTY")

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric(
                        "Spot",
                        f"{spot:,.2f}"
                        if spot is not None
                        else "N/A"
                    )

                with c2:
                    st.metric(
                        "ATM",
                        f"{atm:,.0f}"
                    )

                with c3:
                    st.metric(
                        "Expiry",
                        str(expiry)
                    )


                # ==================================================
                # FORMAT
                # ==================================================

                display_df = final_df.copy()

                numeric_columns = [
                    "CE_OI",
                    "CE_Volume",
                    "CE_Open",
                    "CE_High",
                    "CE_Low",
                    "CE_Close",
                    "PE_OI",
                    "PE_Volume",
                    "PE_Open",
                    "PE_High",
                    "PE_Low",
                    "PE_Close"
                ]

                for col in numeric_columns:

                    if col in display_df.columns:

                        display_df[col] = pd.to_numeric(
                            display_df[col],
                            errors="coerce"
                        )


                # ==================================================
                # FINAL DISPLAY ORDER
                # ==================================================

                display_df = display_df[
                    [
                        "CE_OI",
                        "CE_Volume",
                        "CE_Open",
                        "CE_High",
                        "CE_Low",
                        "CE_Close",
                        "strike",
                        "PE_Open",
                        "PE_High",
                        "PE_Low",
                        "PE_Close",
                        "PE_Volume",
                        "PE_OI"
                    ]
                ]


                display_df = display_df.rename(
                    columns={
                        "strike": "Strike"
                    }
                )


                # ==================================================
                # DISPLAY
                # ==================================================

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )


                # ==================================================
                # DOWNLOAD
                # ==================================================

                csv = display_df.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    "⬇️ Download CSV",
                    csv,
                    "nifty_option_chain.csv",
                    "text/csv"
                )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )

else:

    st.info(
        "Enter your Mirae API Key and Access Token."
    )
