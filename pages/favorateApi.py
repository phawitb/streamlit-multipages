# http://localhost:8504/Favorate/?name=joe
import streamlit as st
import base64
import json
import pygsheets

st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#init pygsheets
gc = pygsheets.authorize(service_account_file='led-sheet-47e8afe294c8.json')
spreadsheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/16dO1zkakREjZxbjB6XFGijHFjjOUDYNpjwoeuUW5gP8/edit?usp=sharing')
worksheet = spreadsheet.sheet1

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

try:
    url = st.experimental_get_query_params()
    if 'name' in url:
        name = url['name'][0]
    else:
        name = None
    if name:
        name = name[2:-1]
        decoded_bytes = base64.b64decode(name)
        decoded_string = decoded_bytes.decode('utf-8')
        data = json.loads(decoded_string)

        update_sheet(data['user_id'],data['province_eng'],data['link'],1)
        st.title('Complete add to favorate')

except Exception as e:
    st.title('Error! can not add favorate',e)
