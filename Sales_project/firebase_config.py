import streamlit as st
import pyrebase

# Secure Firebase Configuration using Streamlit Secrets
# The actual keys are stored in .streamlit/secrets.toml (locally) 
# and in the Streamlit Cloud dashboard (on deployment)
firebaseConfig = st.secrets["firebase"]

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
