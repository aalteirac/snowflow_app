import streamlit as st
import pandas as pd
from snowflake.connector import connect
from snowflake.connector.connection import SnowflakeConnection


# Share the connector across all users connected to the app
@st.experimental_singleton()
def get_connector() -> SnowflakeConnection:
    """Create a connector using credentials filled in Streamlit secrets"""
    connector = connect(
        **st.secrets["snowflake"],  # <-- Only need user and account there
        client_session_keep_alive=True,
    )
    return connector


@st.experimental_memo()
def query_snowflake(query: str, ) -> pd.DataFrame:
    # Connect to Snowflake, we display a little list of Warehouses in the sidebar so we need to connect now!
    snowflake_connector = get_connector()

    return pd.read_sql(
        query,
        snowflake_connector,
    )

def query_snowflake_no_cache(query: str, ) -> pd.DataFrame:
    # Connect to Snowflake, we display a little list of Warehouses in the sidebar so we need to connect now!
    snowflake_connector = get_connector()

    return pd.read_sql(
        query,
        snowflake_connector,
    )    
