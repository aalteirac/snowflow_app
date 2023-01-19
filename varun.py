import streamlit as st
from utils.snowflake_connector import get_connector, query_snowflake, query_snowflake_no_cache
from streamlit_option_menu import option_menu
from global_ui import setUI
from typing import List
import pandas as pd
import requests
import streamlit.components.v1 as components
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import altair as alt
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode


api_user=st.secrets["api_login"]['user']
api_token=st.secrets["api_login"]['password']
api_start_url=st.secrets["api_login"]['url_start']
session = requests.Session()
session.auth = (api_user, api_token)

#@st.experimental_memo(suppress_st_warning=True)
def wordcloud():
        #df_db = query_snowflake("select obj.value:objectName::string TableName, count(*) uses from snowflake.account_usage.access_history, table(flatten(direct_objects_accessed)) obj where obj.value:objectDomain = 'Table' group by 1 order by uses DESC;;")
        df_db = query_snowflake("select obj.value:objectName::string TableName from snowflake.account_usage.access_history, table(flatten(direct_objects_accessed)) obj where obj.value:objectDomain = 'Table';")
        new= df_db['TABLENAME'].str.split(".", n = 2, expand = True)
        cloud_string= new[2].to_list()
        #print(cloud_string)
        #cloud_string=','.join(cloud_string)
        cloud_strings=', '.join(["%s" % w for w in cloud_string])
        #cloud_string=cloud_string.replace("]","")
        # Create some sample text
        text = cloud_strings
        #print(text)

        # Create and generate a word cloud image:
        wordcloud = WordCloud(background_color = "white").generate(text)

        # Display the generated image:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()
        st.pyplot(plt)

def varun_page():
    with st.expander("Search Objects:",expanded=True):
        df_db = query_snowflake("SHOW DATABASES LIMIT 10;")
        # database, schema, tables = st.columns(3)
        database_list = []
        table_comments = []
        search_list = []
        # for index, row in df_db.iterrows():
        #         database_list.append(row['name'])
        # df_sch = query_snowflake("SHOW SCHEMAS;")
        # for index, row in df_sch.iterrows():
        #             database_list.append(row['name'])
        df_sch_table = query_snowflake("SHOW TABLES;")
        for index, row in df_sch_table.iterrows():
                    database_list.append(row['database_name']+"."+row['schema_name']+"."+row['name'])
                    
        
        #print("----------snowdf----------------")
        #print(database_list)
        #print("--------------------------")

        # Store the initial value of widgets in session state
        if "visibility" not in st.session_state:
            st.session_state.visibility = "visible"
            st.session_state.disabled = False

       
        text_input = st.text_input(
            "Search datasets 👇",
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
        )

        if text_input:
            text_input=text_input.upper()
            matched_indexes = []
            i = 0
            length = len(database_list)

            while i < length:
                if text_input in database_list[i]:
                    #matched_indexes.append(i)
                    search_list.append(database_list[i])
                i += 1

            #print(f'{text_input} is present in list at indexes {matched_indexes}')
            #for i in matched_indexes:
            #    search_list.append(database_list[i])
            
            i = 0
            selected_options_approval = []
            selected_options_use = []
            length = len(search_list)
            while i < length:
                curr_table_name=search_list[i]
                indx = database_list.index(curr_table_name)
                print("index  :",indx)
                print(df_sch_table.iloc[indx])
                table_comments.append(df_sch_table.iloc[indx,5])
                print(table_comments)

                if 'CUSTOMER' in search_list[i]:
                    selected_options_approval.append('🚓')
                    print(search_list[i])
                    query="select count(1) from snowvation.workflow.workflow_status where w_object= '"+search_list[i]+"';"
                    print(query)
                    df_sch = query_snowflake_no_cache(query)
                    selected_options_use.append(df_sch['COUNT(1)'].tolist()[0])
                else:
                    selected_options_approval.append('🚀')
                    query="select count(1) from snowvation.workflow.workflow_status where w_object= '"+search_list[i]+"';"
                    df_sch = query_snowflake_no_cache(query)
                    selected_options_use.append(df_sch['COUNT(1)'].tolist()[0])
                i += 1


            table_df = pd.DataFrame(
                {'Table Name': search_list,
                'Table Description': table_comments,
                'Need Approval': selected_options_approval,
                'Access in Last 24 hours': selected_options_use
                })

            st.subheader("Request access for below Objects")
            #for objects in selected_options:
            #        st.write("{0}".format(objects))

            gb = GridOptionsBuilder.from_dataframe(table_df, min_column_width=30)
            gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
            gb.configure_side_bar()
            gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
            gb.configure_column('Table Name', headerCheckboxSelection = True)

            gridOptions = gb.build()
            gridOptions['rowHeight']=35
            gridOptions['suppressCellSelection']=True

            custom_css = {
                    ".ag-ltr .ag-cell": {
                        "border-right-width": "0px"
                    },
                    ".ag-header":{
                        "margin-bottom": "12px"
                    },
                    ".ag-row": {
                        "max-height":"30px",
                        "font-size": "14px !important",
                        "border-radius": "10px",
                        "padding-top": "0px",
                        "border":"var(--ag-borders-row) var(--ag-row-border-color)"
                    },
                    ".ag-body-horizontal-scroll-viewport":{
                        "display":"none"
                    },
                    ".ag-header-row": {
                        "font-size": "18px !important",
                        "border-radius": "10px",
                        "border":"var(--ag-borders-row) var(--ag-row-border-color)",
                        "background-color":"transparent"
                    },
                     ".ag-theme-streamlit":{
                        "--ag-row-hover-color":"rgb(75,220,255,10%)",
                        "--ag-alpine-active-color":"rgb(75,220,255)",
                        "--ag-selected-row-background-color":"rgb(75,220,255,10%)",
                        "--ag-input-focus-border-color":"rgb(75,220,255,10%)",
                        "--ag-border-color":"none",
                        "--ag-grid-size": "5px",
                        "--ag-list-item-height": "30px"
                    }
                }
            grid_response= AgGrid(
                table_df,
                gridOptions=gridOptions,
                allow_unsafe_jscode=True,
                data_return_mode='AS_INPUT', 
                update_mode='MODEL_CHANGED', 
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=False,
                height=350, 
                width='100%',
                custom_css=custom_css,
                reload_data=False
            )

            request_submit = st.button("Request Resource")
            m = st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #0d6efd;
                color:#FFFFFF;
            }
            div.stButton > button:onclick {
            background-color: #0d6efd;
            color:#FFFFFF;
            }
            </style>""", unsafe_allow_html=True)
            selected = grid_response['selected_rows']
            if selected:
                selected_rows = pd.DataFrame(selected)
                #print(selected_rows)
                selected_rows_table=selected_rows['Table Name'].tolist()
                #print(selected_rows_table)


            if request_submit:
                        for tables in selected_rows_table:
                            values = tables.split('.')
                            #print(values)
                            #print(values[0],"   ",values[1],"   ",values[2])
                            json_data = {
                                "DatabaseName": values[0],
                                "SchemaName": values[1],
                                "TableName": values[2],
                                "User": st.session_state['curuser']
                            }
                            response = session.post(api_start_url, json=json_data)
                        if response:
                            st.success('Request Submitted to the ADMIN, watch out for the approval email.',
                                    icon="✅")
                        else:
                            st.error('Error {0} in Submission, Please try again later'.format(response), icon="🚨")
                                

    with st.expander("Select Objects:",expanded=False):
    
        df_db = query_snowflake("SHOW DATABASES LIMIT 10;")
        # database, schema, tables = st.columns(3)
        database_list = []
        schema_list = []
        tables_list = []
        table_comments = []
        col1, col2 = st.columns(2)
        with col1:
            for index, row in df_db.iterrows():
                database_list.append(row['name'])
            database = st.radio(
                "Select the database that you are interested 👉",
                key="database",
                options=database_list,
                index=2
            )
            with col2:
                df_sch = query_snowflake("SHOW SCHEMAS IN DATABASE {0};".format(database))
                for index, row in df_sch.iterrows():
                    schema_list.append(row['name'])
                schema = st.radio(
                    "Select the schema ",
                    key="schema",
                    options=schema_list,
                    index=1
                )

        df_sch = query_snowflake("SHOW TABLES IN {0}.{1};".format(database, schema))
        
        for index, row in df_sch.iterrows():
            tables_list.append(row['database_name']+"."+row['schema_name']+"."+row['name'])
            table_comments.append(row['comment'])

        # tables = st.radio(
        #    "Select the table",
        #    key="tables",
        #    options=tables_list,
        # )
        search_list = tables_list
        # print(tables_list)
        i = 0
        selected_options_approval = []
        selected_options_use = []
        length = len(search_list)
        st.subheader("Request access for below Objects")
        while i < length:

            if 'CUSTOMER' in search_list[i]:
                selected_options_approval.append('🚓')
                print(search_list[i])
                query="select count(1) from snowvation.workflow.workflow_status where w_object= '"+search_list[i]+"';"
                print(query)
                df_sch = query_snowflake(query)
                selected_options_use.append(df_sch['COUNT(1)'].tolist()[0])
            else:
                selected_options_approval.append('🚀')
                query="select count(1) from snowvation.workflow.workflow_status where w_object= '"+search_list[i]+"';"
                df_sch = query_snowflake(query)
                selected_options_use.append(df_sch['COUNT(1)'].tolist()[0])
            i += 1


        table_df = pd.DataFrame(
            {'Table Name': search_list,
            'Table Description': table_comments,
            'Need Approval': selected_options_approval,
            'Access in Last 24 hours': selected_options_use
            })

       

        #for objects in selected_options:
        #        st.write("{0}".format(objects))

        gb = GridOptionsBuilder.from_dataframe(table_df)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_column('Table Name', headerCheckboxSelection = True)
        gb.configure_side_bar()
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")


        gridOptions = gb.build()
        gridOptions['rowHeight']=35
        gridOptions['suppressCellSelection']=True

        custom_css = {
                ".ag-ltr .ag-cell": {
                    "border-right-width": "0px"
                },
                ".ag-header":{
                    "margin-bottom": "12px"
                },
                ".ag-row": {
                    "max-height":"30px",
                    "font-size": "14px !important",
                    "border-radius": "10px",
                    "padding-top": "0px",
                    "border":"var(--ag-borders-row) var(--ag-row-border-color)"
                },
                ".ag-body-horizontal-scroll-viewport":{
                    "display":"none"
                },
                ".ag-header-row": {
                    "font-size": "18px !important",
                    "border-radius": "10px",
                    "border":"var(--ag-borders-row) var(--ag-row-border-color)",
                    "background-color":"transparent"
                },
                ".ag-theme-streamlit":{
                    "--ag-row-hover-color":"rgb(75,220,255,10%)",
                    "--ag-alpine-active-color":"rgb(75,220,255)",
                    "--ag-selected-row-background-color":"rgb(75,220,255,10%)",
                    "--ag-input-focus-border-color":"rgb(75,220,255,10%)",
                    "--ag-border-color":"none",
                    "--ag-grid-size": "5px",
                    "--ag-list-item-height": "30px"
                }
            }
        grid_response= AgGrid(
            table_df,
            gridOptions=gridOptions,
            allow_unsafe_jscode=True,
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED', 
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=False,
            height=350, 
            width='100%',
            custom_css=custom_css,
            reload_data=False
        )
            

        request_submit = st.button("Request Access")
        m = st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #0d6efd;
            color:#FFFFFF;
        }
        div.stButton > button:onclick {
        background-color: #0d6efd;
        color:#FFFFFF;
        }
        </style>""", unsafe_allow_html=True)

        selected = grid_response['selected_rows']
        st.text(selected)
        if selected:
            selected_rows = pd.DataFrame(selected)
            #print(selected_rows)
            selected_rows_table=selected_rows['Table Name'].tolist()
            #print(selected_rows_table)


        if request_submit:
                    for tables in selected_rows_table:
                        values = tables.split('.')
                        #print(values)
                        #print(values[0],"   ",values[1],"   ",values[2])
                        json_data = {
                            "DatabaseName": values[0],
                            "SchemaName": values[1],
                            "TableName": values[2],
                            "User": st.session_state['curuser']
                        }
                        response = session.post(api_start_url, json=json_data)
                    if response:
                        st.success('Request Submitted to the ADMIN, watch out for the approval email.',
                                icon="✅")
                    else:
                        st.error('Error {0} in Submission, Please try again later'.format(response), icon="🚨")

    col1, col2 = st.columns(2)
    with col1:
        wordcloud()
    
    with col2:
        df_db = query_snowflake("select obj.value:objectName::string TableName, count(*) uses from snowflake.account_usage.access_history, table(flatten(direct_objects_accessed)) obj where obj.value:objectDomain = 'Table' group by 1 order by uses DESC;")
        #st.bar_chart(df_db,x="TABLENAME",y="USES",use_container_width=True)
        new= df_db['TABLENAME'].str.split(".", n = 2, expand = True)
        df_db['TABLENAME']= new[2]
        #st.write(df_db)
        c = alt.Chart(df_db).mark_bar().encode(
            x=alt.X('TABLENAME', sort=None),
            y='USES',
            color = 'TABLENAME'
        )
        st.altair_chart(c, use_container_width=True)



