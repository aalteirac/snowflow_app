import streamlit as st
import pandas as pd 
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from utils.snowflake_connector import query_snowflake_no_cache, get_connector
from streamlit_elements import elements, mui, html




def tony_page():
    queryuser=f'''SELECT *
        FROM SNOWVATION.WORKFLOW.WORKFLOW_STATUS w1
        WHERE w1.username='{st.session_state.get('curuser')}' and w_lastmodified = (SELECT MAX(W_LASTMODIFIED) FROM SNOWVATION.WORKFLOW.WORKFLOW_STATUS w2 WHERE w1.w_id = w2.w_id)
        ORDER BY w_lastmodified DESC;
        '''
    query=f'''
        SELECT *
        FROM SNOWVATION.WORKFLOW.WORKFLOW_STATUS w1
        WHERE w_lastmodified = (SELECT MAX(W_LASTMODIFIED) FROM SNOWVATION.WORKFLOW.WORKFLOW_STATUS w2 WHERE w1.w_id = w2.w_id)
        ORDER BY w_lastmodified DESC;
        '''
    try:
        if st.session_state.get('authentication_status')=='USER':
            query=queryuser
            print("HEY "+ st.session_state.get('authentication_status'))
        df_db = query_snowflake_no_cache(query)
    except:
        get_connector.clear()
        if st.session_state.get('authentication_status')=='USER':
            query=queryuser
        df_db = query_snowflake_no_cache(query)
    return prepTable(df_db)

def clickrefresh():
    st.session_state['filter']=False

def getRefreshButton():
    mt = elements(key='td')
    with mt:
        mui.Button(mui.icon.Autorenew,"REFRESH",onClick=clickrefresh)

def clickFilter():
    st.session_state['filter']=True

def getFilterButton():
    if st.session_state.get('filter') is None:
        st.session_state['filter']=False
    mt = elements(key='tf')
    with mt:
        mui.Button(mui.icon.FilterAlt,"REQUIRING ACTION",onClick=clickFilter)             

def prepTable(data):
    data.drop(['W_COMPLETED','W_LASTMODIFIED'], axis=1,inplace=True)
    gb = GridOptionsBuilder.from_dataframe(data)
    # gb.configure_pagination(paginationAutoPageSize=True)
    st.session_state['gb']=gb
    col1,col2,col3,c4,c5,c6=st.columns([1,2,2,2,2,2],gap='small')
    with col2:
        getFilterButton()
        if  st.session_state['filter']==True:
            gb.configure_grid_options(quickFilterText="Email")
    with col1:
        getRefreshButton()     
            
    gb.configure_column("W_JOINURL", hide=True)
    gb.configure_column("W_ID", hide=True)
    gb.configure_column("EMAIL", hide=True)
    gb.configure_column("USERNAME",headerName="USER NAME",cellRenderer= getIconRender())
    gb.configure_column("W_OBJECT",headerName="REQUEST OBJECT")
    gb.configure_column("W_CREATED",headerName="CREATION DATE")
    gb.configure_column("W_STATUS",headerName="STATUS")
    gridOptions = gb.build()
    gridOptions['rowHeight']=90
    gridOptions['suppressCellSelection']=True
    js = JsCode("""
        function(e) {
            let api = e.api;
            let rowIndex = e.rowIndex;
            let col = e.column.colId;

            let rowNode = api.getDisplayedRowAtIndex(rowIndex);
            console.log("CHANGED ",rowNode);
        };
        """)
    
    gb.configure_grid_options(onCellValueChanged=js) 
    if st.session_state['authentication_status']=='ADMIN':
        gridOptions['columnDefs'].append({
            "field": "ACTIONS",
            "header": "ACTIONS",
            "cellRenderer": getApprovalButtonRender(),
            "cellRendererParams": {
                "color": "red",
                "background_color": "black",
            },
        })
    custom_css = {
        ".ag-root-wrapper":{
             "border-bottom": "2px",
            " border-bottom-color": "#b9b5b5",
             "border-bottom-style": "double"
        },
        ".ag-ltr .ag-cell": {
            "border-right-width": "0px"
        },
         ".ag-header":{
            "margin-bottom": "12px"
        },
        ".ag-row": {
            "max-height":"80px",
            "font-size": "18px !important",
            "border-radius": "10px",
            "padding-top": "20px",
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
            "--ag-border-color":"none",
            "--ag-row-hover-color":"rgb(75 220 255 / 10%)",
            "--ag-grid-size": "5px",
            "--ag-list-item-height": "30px"
        }
    }
    
    grid_response= AgGrid(
        data,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        height=594, 
        width='100%',
        custom_css=custom_css,
        reload_data=False
    )
    data = grid_response['data']
    selected = grid_response['selected_rows'] 
    # st.write(grid_response['data'])
    # df = pd.DataFrame(selected)
    # st.write(df)
   # data = grid_response['data']


def getApprovalButtonRender():    
    rd = JsCode('''
        class BtnCellRenderer {
            init(params) {
                this.params = params;
                this.eGui = document.createElement('div');
                this.eGui.style.display='flex';
                this.eGui.style.justifyContent='space-around';
                var isEdit=this.params.data.W_STATUS=="Email to approver";
                var colorb='lightgrey';
                if(isEdit==true){
                    colorb="transparent";
                }
                this.eGui.innerHTML = `
                <style>
                .btn-primary.lightgrey{
                    opacity:0.3!important;
                }
                .btn-primary.${colorb} {
                    opacity:0.8;
                    line-height: 0.8em;
                    margin: 1px;
                    font-size: 14px;
                    width: 35px;
                    height: 30px;
                    padding: 5px;
                    background:${colorb};
                    color: #fff;
                    outline: none;
                    border-radius: 4px;
                    transition: 0.5s;
                    border-color: grey;
                    border-width: 1px;
                }
                .btn-primary:focus,.btn-primary:active {
                    box-shadow: none!important; 
                    background-color: transparent!important;
                    background: transparent;
                }
                .btn-primary:hover {
                    background: transparent;
                    opacity:1;
                    transition: 0.5s;
                }
                .btn-primary.lightgrey:hover {
                    background: lightgrey!important;
                    opacity:0.3;
                    transition: 0.5s;
                }
                </style>
                <div style="width:50px;margin-right: auto;">
                    <span style="width:50px">
                        <button ${colorb!="transparent"?"disabled":""} title="Approve" id='click-button' 
                            class='btn-primary ${colorb}' 
                            style=''><img style="width: 20px;margin-top: -2px" src="https://alteirac.com/ico/check.png"></i></button>
                    </span>
                    <span style="width:50px">
                    <button ${colorb!="transparent"?"disabled":""} title="Reject" id='reject' 
                        class='btn-primary br ${colorb}' 
                        style=''><img style="width: 20px;margin-top: -2px" src="https://alteirac.com/ico/cross.png"></i></button>
                    </span>
                </div>
                `;
                if (colorb=="transparent"){
                    this.eButton = this.eGui.querySelector('#click-button');
                    this.btnClickedHandler = this.btnClickedHandler.bind(this);
                    this.eButton.addEventListener('click', this.btnClickedHandler);
                    
                    this.eButtonReject = this.eGui.querySelector('#reject');
                    this.btnClickedHandlerReject = this.btnClickedHandlerReject.bind(this);
                    this.eButtonReject.addEventListener('click', this.btnClickedHandlerReject);
                }

            }

            getGui() {
                return this.eGui;
            }

            refresh() {
                return true;
            }

            destroy() {
                if (this.eButton) {
                    this.eGui.removeEventListener('click', this.btnClickedHandler);
                }
            }
    
            btnClickedHandler(event) {
                var r=this.params.data.W_JOINURL.split("join=");
                if(r.length>1){
                    r=r[1];
                    var xmlHttp = new XMLHttpRequest();
                    xmlHttp.open( "GET", 'https://flow.boomi.com/api/run/1/state/'+r, false ); 
                    xmlHttp.setRequestHeader("manywhotenant", "4c999db7-45a8-4864-9532-cf693189c17c");
                    xmlHttp.send( null );
                    var all=JSON.parse(xmlHttp.responseText);
                    var cmp=all.currentMapElementId;
                    var sttoken=all.stateToken;

                    var xhr = new XMLHttpRequest();
                    xhr.open("POST", 'https://flow.boomi.com/api/run/1/state/'+r, false);
                    xhr.setRequestHeader("manywhotenant", "4c999db7-45a8-4864-9532-cf693189c17c");
                    xhr.setRequestHeader('Content-Type', 'application/json');
                    xhr.send(JSON.stringify({
                        "invokeType": "NAVIGATE",
                        "currentMapElementId": cmp,
                        "stateId": r,
                        "selectedMapElementId": "a31010e6-611d-0763-e59b-07321fb05891", 
                        "stateToken": sttoken,
                        "mapElementInvokeRequest": {
                            "pageRequest": {},
                            "selectedOutcomeId": null
                            }

                    }));
                    this.refreshTable(new Date().getTime());
                }
            }

            btnClickedHandlerReject(event) {
            console.log("HEY " + this.params.data.W_JOINURL);
            var r=this.params.data.W_JOINURL.split("join=");
            if(r.length>1){
                r=r[1];
                var xmlHttp = new XMLHttpRequest();
                xmlHttp.open( "GET", 'https://flow.boomi.com/api/run/1/state/'+r, false ); 
                xmlHttp.setRequestHeader("manywhotenant", "4c999db7-45a8-4864-9532-cf693189c17c");
                xmlHttp.send( null );
                var all=JSON.parse(xmlHttp.responseText);
                var cmp=all.currentMapElementId;
                var sttoken=all.stateToken;

                var xhr = new XMLHttpRequest();
                xhr.open("POST", 'https://flow.boomi.com/api/run/1/state/'+r,false);
                xhr.setRequestHeader("manywhotenant", "4c999db7-45a8-4864-9532-cf693189c17c");
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify({
                    "invokeType": "NAVIGATE",
                    "currentMapElementId": cmp,
                    "stateId": r,
                    "selectedMapElementId": "65e28c07-7e5c-f293-4288-568ab64f4e37", 
                    "stateToken": sttoken,
                    "mapElementInvokeRequest": {
                        "pageRequest": {},
                        "selectedOutcomeId": null
                        }

                }));

                this.refreshTable(new Date().getTime());
            }
        }

            refreshTable(value) {
                this.params.setValue(value);
            }
        };
    ''')
    return rd


def getIconRender():
    rd = JsCode('''
    function(params) {return '<span><i class="material-icons"><img style="width: 30px;margin-top: 0px;margin-right: 8px;" src="https://alteirac.com/ico/man.png"></i>' + params.value + '</span>'}
    ''') 
    return rd   
 