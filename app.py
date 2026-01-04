import streamlit as st
from risk_calculator import show_risk_calculator
from trade_plan_dtt import show_trade_plan

st.set_page_config(
    page_title="Crypto Trading Suite",
    layout="wide" 
)
st.sidebar.title("Navigation") 
 
section = st.sidebar.radio(
    "Go to",
    ["Risk Calculator", "DTT Trade Plan"] 
 )
if section == "Risk Calculator":
    show_risk_calculator()
else: 
    show_trade_plan()