import streamlit as st
import streamlit_login_page as lp

def logout():
   del st.session_state['authentication_status']
   st.experimental_rerun()

def logme():
    placeholder = st.empty()
    if st.session_state.get('authentication_status') is None:
      with placeholder:
         name=lp.streamlit_login_page()
      if name is not None:
         if name!="":
            if name.lower()=='alan':
               st.session_state['curuser']=name
               st.session_state['authentication_status']='USER'
            else:   
               st.session_state['curuser']=name
               st.session_state['authentication_status']='ADMIN'
            placeholder.empty()   
         else:
            st.stop()
      else:
         st.stop()    