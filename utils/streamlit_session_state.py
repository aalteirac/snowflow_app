# Import libraries.
import streamlit as st



# Set the session state so users don't need to keep entering things when navigating between pages.
def set_session_state():
    if 'st_org_name' not in st.session_state:
        st.session_state['st_org_name'] = ''
    else:
        st.session_state['st_org_name'] = st.session_state['st_org_name']

    if 'st_org_id' not in st.session_state:
        st.session_state['st_org_id'] = ''
    else:
        st.session_state['st_org_id'] = st.session_state['st_org_id']

    if 'st_deployment' not in st.session_state:
        st.session_state['st_deployment'] = ''
    else:
        st.session_state['st_deployment'] = st.session_state['st_deployment']

    if 'st_account_id' not in st.session_state:
        st.session_state['st_account_id'] = ''
    else:
        st.session_state['st_account_id'] = st.session_state['st_account_id']

    if 'st_account_locator' not in st.session_state:
        st.session_state['st_account_locator'] = ''
    else:
        st.session_state['st_account_locator'] = st.session_state['st_account_locator']

    if 'st_account_name' not in st.session_state:
        st.session_state['st_account_name'] = ''
    else:
        st.session_state['st_account_name'] = st.session_state['st_account_name']

    if 'st_sfdc_account_name' not in st.session_state:
        st.session_state['st_sfdc_account_name'] = ''
    else:
        st.session_state['st_sfdc_account_name'] = st.session_state['st_sfdc_account_name']

    if 'st_warehouse_name' not in st.session_state:
        st.session_state.st_warehouse_name = ''
    else:
        st.session_state['st_warehouse_name'] = st.session_state['st_warehouse_name']



# Set the session state so users don't need to keep entering things when navigating between pages.
def debug_details():
    # Show the current session state...
    with st.expander("Debug"):
        st.write('Session State:')
        st.write(st.session_state)