import streamlit as st
import pandas as pd
import altair as alt
import graphviz
from utils.snowflake_connector import query_snowflake
import hydralit_components as hc


def get_page():
    countReq={'icon': 'fa fa-hashtag','icon_color':'darkgrey'}
    comp = {'icon': 'fa fa-check','icon_color':'#29b6e9'}
    rej = {'icon': 'fa fa-skull-crossbones','icon_color':'coral'}
    tm={'icon': 'fa fa-hourglass','icon_color':'darkseagreen'}
    col0, col1, col2, col3= st.columns(4)
    icoSize="30vw"
    with col0:
        tot_query = "select count(*) as total from snowvation.workflow.workflow_status wrkflw; "
        df_db = query_snowflake(tot_query)
        hc.info_card(key="2",title=str(df_db['TOTAL'][0]), title_text_size="12vw",content="Total Request Count",icon_size=icoSize,theme_override=countReq)
    with col1:
        tot_query = "select count(*) as total from snowvation.workflow.workflow_status wrkflw where w_status = 'Completed' or w_status = 'Approved'; "
        df_db = query_snowflake(tot_query)
        hc.info_card(key="3",title=str(df_db['TOTAL'][0]),title_text_size="12vw",content="Completed Count",icon_size=icoSize,theme_override=comp)   
    with col2:
        tot_query = "select count(*) as total from snowvation.workflow.workflow_status wrkflw where w_status = 'Rejected'; "
        df_db = query_snowflake(tot_query)
        hc.info_card(key="4",title=str(df_db['TOTAL'][0]),title_text_size="12vw",content="Rejected Count",icon_size=icoSize,theme_override=rej)      
    with col3:
        avg_query = "select avg( timediff('minute', wrkflw.w_created, case when wrkflw.w_lastmodified is null then " \
                "wrkflw.w_created else wrkflw.w_lastmodified end)) as Average_Request_Time from " \
                "snowvation.workflow.workflow_status wrkflw where w_status = 'Completed' and W_ID not like '12%'; "
        df_db = query_snowflake(avg_query)
        hc.info_card(key="5",title=str(round(df_db['AVERAGE_REQUEST_TIME'][0],2))+'sec',title_text_size="12vw",content="Average Time",icon_size=icoSize,theme_override=tm)

    st.write("")

    fig_col1, fig_col2 = st.columns(2)
    with fig_col1:
        sql_query = "SELECT COUNT(CASE WHEN wrkflw.w_status = 'Completed' THEN 1 ELSE NULL END) as completed_count, " \
                    "'completed_count' as name, to_date(wrkflw.w_created) as date FROM " \
                    "snowvation.workflow.workflow_status wrkflw " \
                    "group by to_date(wrkflw.w_created) union SELECT COUNT(CASE WHEN wrkflw.w_status != 'Completed' " \
                    "THEN " \
                    "1 ELSE NULL END) as in_progress_count, 'in_progress_count', to_date(wrkflw.w_created) as date " \
                    "FROM " \
                    "snowvation.workflow.workflow_status wrkflw group by to_date(wrkflw.w_created) ; "
        df_db = query_snowflake(sql_query)
        df_db = pd.read_csv('dummydata.csv')
        chart = alt.Chart(df_db).mark_line().encode(
            x=alt.X("DATE:O", timeUnit="monthdate", title="Date"),
            y=alt.Y('COMPLETED_COUNT:Q'),
            color=alt.Color("NAME:N")
        ).properties(title="Request per day")
        st.altair_chart(chart, use_container_width=True)

    with fig_col2:
        objects_list = []
        search_list = []
        df_sch_table = query_snowflake("SHOW ROLES;")
        for index, row in df_sch_table.iterrows():
            objects_list.append(row['name'])
        df_sch_table = query_snowflake("SHOW USERS;")
        for index, row in df_sch_table.iterrows():
            objects_list.append(row['login_name'])
        df_sch_table = query_snowflake("SHOW TABLES;")
        for index, row in df_sch_table.iterrows():
            objects_list.append(row['database_name'] + "." + row['schema_name'] + "." + row['name'])
        # Store the initial value of widgets in session state
        if "visibility" not in st.session_state:
            st.session_state.visibility = "visible"
            st.session_state.disabled = False
        text_input = st.text_input(
            "Search roles/objects/users to find their access👇",
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
        )
        if text_input:
            text_input = text_input.upper()
            matched_indexes = []
            i = 0
            length = len(objects_list)

            while i < length:
                if text_input in objects_list[i]:
                    matched_indexes.append(i)
                i += 1

            # print(f'{text_input} is present in list at indexes {matched_indexes}')
            for i in matched_indexes:
                search_list.append(objects_list[i])

            option = st.selectbox(
                "How would you like to be contacted?",
                search_list,
                label_visibility=st.session_state.visibility,
                disabled=st.session_state.disabled,
            )

            graph = graphviz.Digraph()
            graph.attr(rankdir="LR", size="0,8")
            graph.attr("node", shape="doublecircle")
            graph_query = "select grantee_name, privilege, granted_on as object_type, case when table_schema is not null " \
                          "and name != table_schema and name != table_catalog then concat_ws('.',table_catalog," \
                          "table_schema,name) when table_schema is null and name = table_catalog then table_catalog when " \
                          "table_schema is not null and name = table_schema then concat_ws('.',table_catalog," \
                          "table_schema) end as object_name from snowflake.account_usage.grants_to_roles where deleted_on " \
                          "is null and table_catalog is not null and granted_on != 'PROCEDURE' order by privilege; "
            df_db = query_snowflake(graph_query)
            # st.write(df_db)
            for index, row in df_db.iterrows():
                if row['GRANTEE_NAME'] == option or row['OBJECT_NAME'] == option or row['PRIVILEGE'] == option:
                    graph.edge(row['GRANTEE_NAME'], row['OBJECT_NAME'], label=row['PRIVILEGE'])
            st.graphviz_chart(graph, use_container_width=True)
    with st.container():
        st.write("")