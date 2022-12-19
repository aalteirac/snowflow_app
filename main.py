import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
from global_ui import setUI, setTransition
import streamlit.components.v1 as components

from utils.streamlit_session_state import set_session_state as set_session_state
import varun
import tony
import login
import analytics

im = Image.open("images/snowflow.png")
setUI()
login.logme()
role = st.session_state['authentication_status']

set_session_state()

setTransition()
page = option_menu("SnowFlow", ["Home", "Search", "Open Requests",'Exit'],
                   icons=['house', 'binoculars-fill', "list-task",'door-open'],
                   menu_icon="search", default_index=0, orientation="horizontal",
                   styles={
                       "container": {"max-width": "100%!important","--primary-color":"#29b6e9","--text-color":"#29b6e9"},
                       "nav-link": {"font-weight": "600"},
                       "menu-title" :{"font-weight": "600"}
                       # "container": {"padding": "0!important", "background-color": "#fafafa"}, "icon": {"color":
                       # "orange", "font-size": "25px"}, "nav-link": {"font-size": "25px", "text-align": "left",
                       # "margin":"0px", "--hover-color": "#eee"}, "nav-link-selected": {"background-color": "green"},
                   }
                   )

# page
hvar = """  <script>
                console.log("HEEEEEYY" + new Date().getTime())

                var my_awesome_script = window.parent.document.createElement('script');
                my_awesome_script.innerHTML=`document.addEventListener("DOMNodeInserted", function (event) {
                        console.log(event.relatedNode,event.relatedNode.className)
                        event.relatedNode.style.opacity="0";
                        setTimeout(()=>{event.relatedNode.style.opacity="1";},400)
                    }, false);`;
                window.parent.document.head.appendChild(my_awesome_script);

    
            </script> """

#components.html(hvar, height=0, width=0)
if page == 'Home':
    analytics.get_page()
if page == 'Search':
    varun.varun_page()
if page == 'Open Requests':
    tony.tony_page()
if page == 'Exit':
    login.logout()
