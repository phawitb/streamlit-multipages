import streamlit as st
import pygsheets
import extra_streamlit_components as stx
import requests
import pandas as pd
import io
import pygsheets
import math
import datetime
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

gc = pygsheets.authorize(service_account_file='led-sheet-47e8afe294c8.json')
spreadsheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/16dO1zkakREjZxbjB6XFGijHFjjOUDYNpjwoeuUW5gP8/edit?usp=sharing')
worksheet = spreadsheet.sheet1

if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'
try:
    st.set_page_config(layout="wide",initial_sidebar_state=st.session_state.sidebar_state)
except:
    pass

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
    
        worksheet.update_value(f'A{last_row+1}', user_id)
        worksheet.update_value(f'B{last_row+1}', province)
        worksheet.update_value(f'C{last_row+1}', sta)
        worksheet.update_value(f'D{last_row+1}', link)

def delete_allfavorate(user_id,province,sta):
    df = worksheet.get_as_df()
    
    condition1 = df['user_id'] == user_id
    condition2 = df['province'] == province

    df_f = df[condition1 & condition2]
    index = list(df_f.index)

    for i in index:
        print('data exist')
        worksheet.update_value(f'A{i+2}', user_id)
        worksheet.update_value(f'B{i+2}', province)
        worksheet.update_value(f'C{i+2}', sta)

def create_list(df,n_total,p):
 
    for index, row in df.iterrows():
        COL = st.columns(3)

        with COL[0]:
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

            if st.button(f"Delete Favorate",key=f"{p}{index}"):
                st.write('delete favorate complete')
                update_sheet(person_id,p,row['link'],0)
     
        with COL[1]:
            st.image(row['img0'],use_column_width='auto')

        with COL[2]:
            try:
                st.image(row['img1'],use_column_width='auto')
            except:
                pass

def get_data(province):
    # province = 'nonthaburi'
    url = f'https://raw.githubusercontent.com/phawitb/crawler-led3-window/main/df_{province}.csv'
    response = requests.get(url)
    df = pd.read_csv(io.StringIO(response.text))
    return df


cookie_manager = stx.CookieManager()
person_id = cookie_manager.get(cookie='person_id')

st.markdown(f'### {person_id}')

#init pygsheets
gc = pygsheets.authorize(service_account_file='led-sheet-47e8afe294c8.json')
spreadsheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/16dO1zkakREjZxbjB6XFGijHFjjOUDYNpjwoeuUW5gP8/edit?usp=sharing')
worksheet = spreadsheet.sheet1

df_favorate = worksheet.get_as_df()

condition1 = df_favorate['user_id'] == person_id
condition2 = df_favorate['sta'] == 1
df_filter = df_favorate[condition1 & condition2]

tabs_list = list(df_filter['province'].unique())

if tabs_list:
    data = []
    for k in tabs_list:
        data.append(stx.TabBarItemData(id=k, title=k, description=""))
    chosen_idM = stx.tab_bar(data = data,default=tabs_list[0])

    if st.button('Delete All Favorate'):
        delete_allfavorate(person_id,chosen_idM,0)

    for index,p in enumerate(tabs_list):
        if chosen_idM == p:
            df_favorate_province = df_filter[df_filter['province']==p]
            df_province = get_data(p)
           
            df2 = df_province[df_province['link'].isin(list(df_favorate_province['link']))]
            df2['lastSta_date'] = df2['lastSta_date'].astype(int)
            df2['lastSta_date'] = df2['lastSta_date'].astype(str)
            tabs_list2 = list(df2['lastSta_date'].unique())
            tabs_list2.sort()
      
            if tabs_list2:
                data = []
                for k in tabs_list2:
                    try:
                        k = str(int(float(k)))
                        input_date = datetime.datetime.strptime(k, "%Y%m%d")
                        title = input_date.strftime("%d-%m-%Y")
                    except:
                        title = k
                    data.append(stx.TabBarItemData(id=k, title=title, description=""))
                chosen_idM2 = stx.tab_bar(data = data,default=tabs_list2[0])

                for index,p in enumerate(tabs_list2):
                    if chosen_idM2 == p:
                        df3 = df2[df2['lastSta_date']==p]
                        df3['bid_time'] = df3['bid_time'].astype(int)
                        df3['bid_time'] = df3['bid_time'].astype(str)
                        tabs_list3 = list(df3['bid_time'].unique())
                        if tabs_list3:
                            data = []
                            for k in tabs_list3:
                                data.append(stx.TabBarItemData(id=k, title=f'นัด{k}', description=""))
                            chosen_idM3 = stx.tab_bar(data = data,default=tabs_list3[0])

                            for index,p in enumerate(tabs_list3):
                                 if chosen_idM3 == p:
                                    df4 = df3[df3['bid_time']==p]
                                
                                    df = df4.reset_index()
                                    
                                    n_page = df.shape[0]//10 + 1
                                    T = [str(i) for i in range(1, n_page+1)]
                                    data = []
                                    for k in T:
                                        data.append(stx.TabBarItemData(id=k, title=k, description=""))
                                    chosen_idMM = stx.tab_bar(data = data,default=T[0])
            
                                    for i in range(n_page):
                                        if chosen_idMM == T[i]:
                                            filtered_df = df.iloc[i*10:i*10+10]
                                            create_list(filtered_df,df.shape[0],p)

else:
    st.markdown('#### No favorate property')
