import streamlit as st
st.set_page_config(layout="wide",initial_sidebar_state='expanded')
import folium
from streamlit_folium import folium_static
import pandas as pd
import requests
import io
from streamlit_folium import st_folium
from datetime import datetime
from folium import plugins
import base64
import extra_streamlit_components as stx
import json
import math
import pygsheets
from streamlit_js_eval import streamlit_js_eval

hide_st_style = """
            <style>
            .block-container {
                padding-top: 0rem;
                padding-bottom: 0rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

def all_province():
    url = f'https://raw.githubusercontent.com/phawitb/crawler-led3-window/main/currentstage.csv'
    response = requests.get(url)
    df = pd.read_csv(io.StringIO(response.text))
    return list(df['province'].unique())

def check_favorate(user_id,link):
    condition1 = st.session_state["fav_df"]['user_id'] == user_id
    condition2 = st.session_state["fav_df"]['link'] == link
    condition3 = st.session_state["fav_df"]['sta'] == 1
    df_f = st.session_state["fav_df"][condition1 & condition2 & condition3]

    if df_f.shape[0] != 0:
        return True
    else:
        return False
    
def update_sheet(user_id,province,link,sta):
    df = worksheet.get_as_df()
    condition1 = df['user_id'] == user_id
    condition2 = df['province'] == province
    condition3 = df['link'] == link
    df_f = df[condition1 & condition2 & condition3]
    index = list(df_f.index)

    if index:
        print('data exist')
        worksheet.update_value(f'A{index[0]+2}', user_id)
        worksheet.update_value(f'B{index[0]+2}', province)
        worksheet.update_value(f'C{index[0]+2}', sta)
        worksheet.update_value(f'D{index[0]+2}', link)
        
    else:
        print('data not exist')
        cells = worksheet.get_all_values(include_tailing_empty_rows=None, include_tailing_empty=False, returnas='matrix')
        last_row = len(cells)

        cells = worksheet.get_all_values(include_tailing_empty_rows=None, include_tailing_empty=False, returnas='matrix')
        last_row = len(cells)
        # print(last_row)
        worksheet.update_value(f'A{last_row+1}', user_id)
        worksheet.update_value(f'B{last_row+1}', province)
        worksheet.update_value(f'C{last_row+1}', sta)
        worksheet.update_value(f'D{last_row+1}', link)

def strprice2int(s):
    if 'k' in s or 'M' in s:
        if s[-1] == 'k':
            x = 1000
        if s[-1] == 'M':
            x = 1000000
        return int(s[:-1])*x
    else:
        return int(s)

def filter_equal(df,col,L):
    df2 = df[df[col]==L[0]]
    for a in L[1:]:
        df2 = df2._append(df[df[col]==a])
    return df2

def filter_range(df,col,mi,mx):
    df['max_price'].fillna(0, inplace = True)
    df2 = df[df[col]>=mi]

    if mx != 500000000:
        df2 = df2[df2[col]<=mx]
    return df2

def filter_df(df,selected_province,selected_aumpher,selected_min,selected_max,selected_date,types,size_min, size_max):
    print('selectttt',selected_province,selected_aumpher,selected_min, selected_max,selected_date,types,size_min, size_max)

    df['tarangwa'] = df['size0']+df['size1']*100+df['size2']*400

    if size_min != 'max':
        size_min = int(size_min)
    else:
        size_min = 10000
    if size_max != 'max':
        size_max = int(size_max)
    else:
        size_max = 100000
    df = filter_range(df,'tarangwa',size_min,size_max)


    T = []
    for t in types.keys():
        if types[t]:
            T.append(t)
    #filter df
    if not selected_aumpher:
        selected_aumpher = list(df['aumper'].unique())
    selected_date = selected_date.replace('/','')
    dfs = filter_equal(df,'aumper',selected_aumpher)
    dfs = filter_range(dfs,'max_price',strprice2int(selected_min),strprice2int(selected_max))
    dfs = filter_equal(dfs,'type',T)
    if selected_date != 'All Date':
        matchDate = []
        for index, row in dfs.iterrows():
            print(selected_date,type(selected_date))
            print(row['bid_dates'],type(row['bid_dates']))
            if str(row['bid_dates']) != 'nan' and selected_date in eval(row['bid_dates']):
                matchDate.append(True)
            else:
                matchDate.append(False)
        dfs['matchDate'] = matchDate
    else:
        dfs['matchDate'] = True
    dfs = dfs[dfs['matchDate'] == True]
    return dfs

def get_data(province):
    # province = 'nonthaburi'
    url = f'https://raw.githubusercontent.com/phawitb/crawler-led3-window/main/df_{province}.csv'
    response = requests.get(url)
    df = pd.read_csv(io.StringIO(response.text))
    return df

def create_map(df):
    initial_location = [df['lat'].mean(),df['lon'].mean()]  
    map = folium.Map(location=initial_location, zoom_start=12)

    L = list(df['type'].unique())
    
    Layers = []
    for l in L:
        la = folium.FeatureGroup(name=l)
        map.add_child(la)

        Layers.append(la)

    no_gps = []
    for index, row in df.iterrows():

        try:
            color = COLORS[row['type']]
            fill_color = COLORS[row['type']]
        except:
            color = 'black'
            fill_color = 'white'

        if row['size0'] < 30 and row['size1'] == 0 and row['size2'] == 0 and row['type']=='ที่ดินพร้อมสิ่งปลูกสร้าง':
            color = 'orange'
            fill_color = 'orange'

        if str(row['lastSta_detail']) in ['ขายได้','ถอนการยึด']:
            fill_opacity = 0.3
            fill_color = 'black'

        else:
            fill_opacity = 0.8
            
        if str(row['lon']) != 'nan':
            A = ''
            if row['size2'] != 0:
                A += f"{row['size2']} ไร่ "
            if row['size1'] != 0 or row['size2']>0:
                A += f"{row['size1']} งาน "
            if row['size0'] != 0 or row['size2']>0 or row['size1']>0:
                A += f"{row['size0']} ตร.ว."

            htm = ""

            if row['lat']:
                decimal_coordinates = (row['lat'], row['lon'])
                formatted_coordinates = format_coordinates(*decimal_coordinates)
                map_url = f"https://www.google.com/maps/place/{formatted_coordinates}/@{row['lat']},{row['lon']},17z"
            
            try:
                htm += f"<h2>{row['type']}</h2>"
            except:
                pass
            try:
                htm += f"<h5><a href={map_url} target='_blank'>{row['tumbon']},{row['aumper']},{row['province']}</a></h5>"
            except:
                pass
            try:
                htm += f"<h5>{A}</h5>"
            except:
                pass
            try:
                htm += f"<h5>นัด{int(row['bid_time'])} : {datetime.strptime(str(int(row['lastSta_date'])), '%Y%m%d').strftime('%d/%m/%Y')} {row['lastSta_detail']}</h5>"
            except:
                pass
            try:
                htm += f"<h5>{row['status']}</h5>"
            except:
                pass
            try:
                htm += f"<h4><a href='{row['link']}' target='_blank'>{'{:,}'.format(int(row['max_price']))}</a></h4>"
            except:
                pass
            try:
                htm += f"<img src='{row['img0']}' alt='Trulli' style='max-width:100%;max-height:100%'>"
            except:
                pass

            row['user_id'] = st.session_state["current_id"]
            row['province_eng'] = st.session_state["selected_province"]

            encoded_text = base64.b64encode(json.dumps(dict(row)).encode('utf-8'))
            # htm += f"<h4><a href=http://localhost:8503/-/?name={encoded_text} target='_blank'>⭐</a></h4>"
            htm += f"<h4><a href=https://app-multipages-ctqwmtnfofmdyowhaoayqb.streamlit.app/api/?name={encoded_text} target='_blank'>⭐</a></h4>"

            popup=folium.Popup(htm, max_width=400)

            if check_favorate(st.session_state["current_id"],row['link']):
                marker = folium.Circle(popup=popup,location=[float(row['lat']), float(row['lon'])], radius=200,weight=2, fill=True, color=color,fill_color='yellow',fill_opacity=1)
            else:
                marker = folium.Circle(popup=popup,location=[float(row['lat']), float(row['lon'])], radius=100,weight=1, fill=True, color=color,fill_color=fill_color,fill_opacity=fill_opacity)
  
            i = L.index(row['type'])
            marker.add_to(Layers[i])
        
        else:
            no_gps.append(row['link'])


    plugins.Fullscreen(                                                         
        position = "topleft",                                   
        title = "Open full-screen map",                       
        title_cancel = "Close full-screen map",                      
        force_separate_button = True,                                         
    ).add_to(map) 

    satellite_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    folium.TileLayer(tiles=satellite_tiles, attr="Esri World Imagery", name="Satellite").add_to(map)
    # folium.TileLayer(tiles='Stamen Terrain',name="Satellite2").add_to(map)
    folium.LayerControl(position='topleft').add_to(map)

    return map,no_gps

def decimal_to_dms(decimal_degrees):
    degrees = int(decimal_degrees)
    decimal_minutes = (decimal_degrees - degrees) * 60
    minutes = int(decimal_minutes)
    seconds = (decimal_minutes - minutes) * 60

    return degrees, minutes, seconds

def format_coordinates(latitude, longitude):
    latitude_dms = decimal_to_dms(latitude)
    longitude_dms = decimal_to_dms(longitude)
    
    latitude_str = f"{latitude_dms[0]}°{latitude_dms[1]}'{latitude_dms[2]:.1f}\"N"
    longitude_str = f"{longitude_dms[0]}°{longitude_dms[1]}'{longitude_dms[2]:.1f}\"E"

    return latitude_str + '+' + longitude_str

def create_list(df,n_total):
    for index, row in df.iterrows():
        COL = st.columns(3)
        with COL[0]:
            if check_favorate(st.session_state["current_id"],row['link']):
                type = 'primary'
            else:
                type = 'secondary'
            st.subheader(f":green[{index+1}/{n_total}[{row['sell_order']}]{row['type']}]")

            if not math.isnan(row['lat']):
                decimal_coordinates = (row['lat'], row['lon'])
                print('decimal_coordinates',decimal_coordinates)
                formatted_coordinates = format_coordinates(*decimal_coordinates)
                url = f"https://www.google.com/maps/place/{formatted_coordinates}/@{row['lat']},{row['lon']},17z"
                st.markdown(f"*[{row['tumbon']},{row['aumper']},{row['province']}]({url})*")
            else:
                st.markdown(f"*{row['tumbon']},{row['aumper']},{row['province']}*")

            area = ''
            a = ['ตร.ว.','งาน','ไร่']
            for i in range(2, -1, -1):
                if isinstance(row[f'size{i}'], int) or isinstance(row[f'size{i}'], float):
                    if row[f'size{i}'] != 0:
                        area += f"{row[f'size{i}']} {a[i]} "
            area = area[:-1]
            st.markdown(f"**:triangular_ruler: {area}**")
            st.markdown(f"วางเงิน {row['pay_down']:,.0f} บาท")
            
            try:
                date_object = datetime.strptime(str(int(row['lastSta_date'])), "%Y%m%d")
                formatted_date = date_object.strftime("%d/%m/%y")
            except:
                formatted_date = row['lastSta_date']
            try:
                st.markdown(f":orange[นัด {int(row['bid_time'])} {formatted_date} {row['lastSta_detail']}]")
            except:
                st.markdown(f":orange[นัด -]")

            st.markdown(f":red[{row['status']}]")
            st.subheader(f"[:moneybag: :blue[{row['max_price']:,.0f}]]({row['link']})")

            if st.button(f"⭐",key=index,type=type):
                st.write(':red[Add favorate complete]')
                update_sheet(st.session_state["current_id"],st.session_state["selected_province"],row['link'],1)
                
        with COL[1]:
            try:
                st.image(row['img0'],use_column_width='auto')
            except:
                pass

        with COL[2]:
            try:
                st.image(row['img1'],use_column_width='auto')
            except:
                pass

#------------------------------------------------------------------------------------------

screen_width = streamlit_js_eval(js_expressions='screen.width', key = 'SCR')

gc = pygsheets.authorize(service_account_file='led-sheet-47e8afe294c8.json')
spreadsheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/16dO1zkakREjZxbjB6XFGijHFjjOUDYNpjwoeuUW5gP8/edit?usp=sharing')
worksheet = spreadsheet.sheet1

if "screen_width" not in st.session_state:
    st.session_state["screen_width"] = screen_width
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'
if 'button_type' not in st.session_state:
    st.session_state.button_type = {}
if "current_id" not in st.session_state:
    st.session_state["current_id"] = None
if "selected_province" not in st.session_state:
    st.session_state["selected_province"] = None
if "fav_df" not in st.session_state:
    fav_df = df = worksheet.get_as_df()
    st.session_state["fav_df"] = fav_df
if "all_province" not in st.session_state:
    st.session_state["all_province"] = all_province()


cookie_manager = stx.CookieManager()
person_id = cookie_manager.get(cookie='person_id')
st.session_state["current_id"] = person_id

COLORS = {
    'ที่ดินพร้อมสิ่งปลูกสร้าง' : 'red',
    'ที่ดินว่างเปล่า' : 'green',
    'ห้องชุด' : 'blue',
    'หุ้น' : 'gray',
    'สิ่งปลูกสร้าง' : 'black'
}
                
if st.session_state["current_id"]:

    st.sidebar.header("Find")
    # selected_province = st.sidebar.selectbox('Province',['Select Province','nonthaburi', 'nakhonpathom','samutsakorn','songkhla','chonburi'])
    selected_province = st.sidebar.selectbox('Province',['Select Province'] + st.session_state["all_province"])
    if selected_province != 'Select Province':
        st.session_state["selected_province"] = selected_province

        df = get_data(selected_province)
        cookie_manager.set('province', selected_province, expires_at=datetime(year=2025, month=2, day=2))
        selected_aumpher = st.sidebar.multiselect('Aumpher',list(df['aumper'].unique()))
        selected_min, selected_max = st.sidebar.select_slider('Price',options=['0','100k','500k','1M','3M','5M','10M','500M'],value=('0', '500M'))

        #find all dates
        all_date = []
        for i in list(df['bid_dates'].unique()):
            if str(i) != 'nan':
                all_date = all_date+eval(i)
        all_date = set(all_date)
        all_date = ['All Date'] + [datetime.strptime(x, '%Y%m%d').strftime('%Y/%m/%d') for x in all_date]
        selected_date = st.sidebar.selectbox('Date',all_date)

        types = {}
        for l in list(df['type'].unique()):
            types[l] = st.sidebar.checkbox(l,value=True)

        size_min, size_max = st.sidebar.select_slider('Size(ตร.ว.)',options=['0','20','30','40','50','100','200','400','max'],value=('0', 'max'))
        print('size_min, size_max',size_min, size_max)

        dfs = filter_df(df,selected_province,selected_aumpher,selected_min,selected_max,selected_date,types,size_min, size_max)
        dfs = dfs.reset_index(drop=True)
        st.session_state["df"] = dfs

        #================================================
        df = st.session_state["df"]
        df['lastSta_date'].fillna("-", inplace=True)

        data = []
        # for k in ['🏠 Sell-order','min↑','max↓','🌎 Map']:
        for k in ['🌎 Map','🏠 Sell-order','min↑','max↓']:
            data.append(stx.TabBarItemData(id=k, title=k, description=""))
        chosen_id00 = stx.tab_bar(data = data,default='🏠 Sell-order')

        if chosen_id00 == 'min↑':
            df = df.sort_values(by='max_price')
            df = df.reset_index()
        elif chosen_id00 == 'max↓':
            df = df.sort_values(by='max_price',ascending=False)
            df = df.reset_index()

        if chosen_id00 in ['🏠 Sell-order','min↑','max↓']:
            data = []
            title = ['All','ประเภท','อำเภอ','วางเงิน','วันที่']
            for i,k in enumerate(['All','type','aumper','pay_down','lastSta_date']):
                data.append(stx.TabBarItemData(id=k, title=title[i], description=""))
            chosen_id0 = stx.tab_bar(data = data,default='All')

            df['max_price'] = df['max_price'].fillna(0)

            if chosen_id0 == 'All':
                n_page = df.shape[0]//10 + 1
                data2 = []
                for i in range(1,n_page+1):
                    data2.append(stx.TabBarItemData(id=i, title=i, description=""))

                chosen_id2 = stx.tab_bar(data = data2, default=1)
                df = df.reset_index()
                filtered_df2 = df.iloc[(int(chosen_id2)-1)*10:(int(chosen_id2)-1)*10+10]

                create_list(filtered_df2,df.shape[0])

            else:
                data = []
                K = []
                list_a = list(df[chosen_id0].unique())
                try:
                    list_a.sort()
                except:
                    pass

                if chosen_id0 == 'lastSta_date':
                    title = []
                    for t in list_a:
                        if t != '-':
                            date_obj = datetime.strptime(str(int(t)), "%Y%m%d")
                            formatted_date = date_obj.strftime("%d/%m/%Y")
                            title.append(formatted_date)
                        else:
                            title.append(t)

                    print('list_a',list_a)
                    for i,k in enumerate(list_a):
                        try:
                            k = '{:,}'.format(int(k))
                        except:
                            pass
                        data.append(stx.TabBarItemData(id=k, title=title[i], description=""))
                        K.append(k)
                    print(K)
                    chosen_id = stx.tab_bar(data = data,default=K[0])
                    placeholder = st.container()

                    data = []
                    K = []
                    bid_times = list(df[df[chosen_id0]==float(chosen_id.replace(",", ""))]['bid_time'].unique())
                    bid_times.sort()
                    for i,k in enumerate(bid_times):
                        try:
                            data.append(stx.TabBarItemData(id=k, title=f'นัด {int(k)}', description=""))
                        except:
                            data.append(stx.TabBarItemData(id=k, title=f'นัด {k}', description=""))
                        K.append(k)
                    print(K)
                    chosen_idb = stx.tab_bar(data = data,default=K[0])
                    placeholderb = st.container()

                    condition1 = df[chosen_id0]==float(chosen_id.replace(",", ""))
                    condition2 = df['bid_time']==float(chosen_idb)
                    
                    df_filter = df[condition1 & condition2]
                    df_filter = df_filter.reset_index()

                    n_page = df_filter.shape[0]//10 + 1
                    data2 = []
                    for i in range(1,n_page+1):
                        data2.append(stx.TabBarItemData(id=i, title=i, description=""))

                    chosen_id2 = stx.tab_bar(data = data2, default=1)
                    placeholder2 = placeholder.container()

                    filtered_df2 = df_filter.iloc[(int(chosen_id2)-1)*10:(int(chosen_id2)-1)*10+10]

                    create_list(filtered_df2,df_filter.shape[0])

                else:
                    title = list_a
                    
                    for i,k in enumerate(list_a):
                        try:
                            k = '{:,}'.format(int(k))
                        except:
                            pass
                
                        data.append(stx.TabBarItemData(id=k, title=title[i], description=""))
                        K.append(k)
                        
                    print(K)
                    chosen_id = stx.tab_bar(data = data,default=K[0])
                    placeholder = st.container()

                    try:
                        df_filter = df[df[chosen_id0]==float(chosen_id.replace(",", ""))]
                    except:
                        df_filter = df[df[chosen_id0]==chosen_id]

                    df_filter = df_filter.reset_index()

                    n_page = df_filter.shape[0]//10 + 1
                    data2 = []
                    for i in range(1,n_page+1):
                        # data.append(stx.TabBarItemData(id=i, title="✍️ To Do", description="Tasks to take care of"))
                        data2.append(stx.TabBarItemData(id=i, title=i, description=""))

                    chosen_id2 = stx.tab_bar(data = data2, default=1)
                    placeholder2 = placeholder.container()

                    filtered_df2 = df_filter.iloc[(int(chosen_id2)-1)*10:(int(chosen_id2)-1)*10+10]
                    # st.write(filtered_df2)
                    create_list(filtered_df2,df_filter.shape[0])

        else:

            data = []
            for k in ['Map','No GPS']:
                data.append(stx.TabBarItemData(id=k, title=k, description=""))
            chosen_idM = stx.tab_bar(data = data,default='Map')

            map,no_gps = create_map(st.session_state["df"])
            if chosen_idM == 'Map':
                map.get_root().html.add_child(folium.Element('<style>#map-container { height: 100vh !important; width: 100% !important; }</style>'))
                m = folium_static(map,height=1000, width=st.session_state["screen_width"])

            if chosen_idM == 'No GPS':
                df = st.session_state["df"]
                no_gps_df = df[df['link'].isin(no_gps)]
                no_gps_df = no_gps_df.reset_index()
                n_page = no_gps_df.shape[0]//10 + 1
                data2 = []
                for i in range(1,n_page+1):
                    data2.append(stx.TabBarItemData(id=i, title=i, description=""))

                chosen_id2 = stx.tab_bar(data = data2, default=1)
                filtered_df2 = no_gps_df.iloc[(int(chosen_id2)-1)*10:(int(chosen_id2)-1)*10+10]

                create_list(filtered_df2,no_gps_df.shape[0])



else:
    st.markdown('### please login!')
            
