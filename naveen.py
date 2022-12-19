from utils.snowflake_connector import query_snowflake
import streamlit as st
import requests
import configparser

api_user=st.secrets["api_login"]['user']
api_token=st.secrets["api_login"]['password']
api_start_url=st.secrets["api_login"]['url_start']
session = requests.Session()
session.auth = (api_user, api_token)


def naveen_page():
    df_db = query_snowflake("SHOW DATABASES LIMIT 10;")
    # database, schema, tables = st.columns(3)
    database_list = []
    schema_list = []
    tables_list = []
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        for index, row in df_db.iterrows():
            database_list.append(row['name'])
        database = st.radio(
            "Select the database that you are interested 👉",
            key="database",
            options=database_list,
        )
        with col2:
            df_sch = query_snowflake("SHOW SCHEMAS IN DATABASE {0} LIMIT 10;".format(database))
            for index, row in df_sch.iterrows():
                schema_list.append(row['name'])
            schema = st.radio(
                "Select the schema ",
                key="schema",
                options=schema_list,
            )
            with col3:
                df_sch = query_snowflake("SHOW TABLES IN {0}.{1} LIMIT 10;".format(database, schema))
                for index, row in df_sch.iterrows():
                    tables_list.append(row['name'])
                # tables = st.radio(
                #    "Select the table",
                #    key="tables",
                #    options=tables_list,
                # )
                containercol4 = st.container()
                all = st.checkbox("Select all")

                if all:
                    selected_options = containercol4.multiselect("Select one or more tables:",
                                                                 tables_list, tables_list)
                else:
                    selected_options = containercol4.multiselect("Select one or more tables:",
                                                                 tables_list)
                with col4:
                    st.write("Objects Selected for Access")
                    for objects in selected_options:
                        st.write("{0}.{1}.{2}".format(database, schema, objects))
                    request_submit = st.button("Submit")

                    if request_submit:
                        for tables in selected_options:
                            json_data = {
                                "DatabaseName": database,
                                "SchemaName": schema,
                                "TableName": tables,
                                "User": "TestUser"
                            }
                            response = session.post(api_start_url, json=json_data)
                        if response:
                            st.success('Request Submitted to the ADMIN, watch out for the approval email.',
                                       icon="✅")
                        else:
                            st.error('Error {0} in Submission, Please try again later'.format(response), icon="🚨")
