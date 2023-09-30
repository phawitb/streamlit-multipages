import streamlit as st


import extra_streamlit_components as stx
from hash import hash_password,verify_password,load_users,save_users,isEmail
import datetime
from sent_email import sent_otp
import random
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)




st.write("# Welcome to Streamlit! 👋")

# st.sidebar.success("Select a demo above.")

# st.markdown(
#     """
#     Streamlit is an open-source app framework built specifically for
#     Machine Learning and Data Science projects.
#     **👈 Select a demo from the sidebar** to see some examples
#     of what Streamlit can do!
#     ### Want to learn more?
#     - Check out [streamlit.io](https://streamlit.io)
#     - Jump into our [documentation](https://docs.streamlit.io)
#     - Ask a question in our [community
#         forums](https://discuss.streamlit.io)
#     ### See more complex demos
#     - Use a neural net to [analyze the Udacity Self-driving Car Image
#         Dataset](https://github.com/streamlit/demo-self-driving)
#     - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
# """
# )


screen_width = streamlit_js_eval(js_expressions='screen.width', key = 'SCR')

if "screen_width" not in st.session_state:
    st.session_state["screen_width"] = screen_width

try:    
    st.set_page_config(layout="wide",initial_sidebar_state=st.session_state.sidebar_state)
except:
    pass

cookie_manager = stx.CookieManager()
person_id = cookie_manager.get(cookie='person_id')

if not person_id:
    LIST_MENUS = ["📈 Login", "🗃 Register","Forgot Password"]
    tab1,tab2,tab3 = st.tabs(LIST_MENUS)
    
    #login
    users = load_users("users.json")
    login_username = tab1.text_input("Email :")
    login_password = tab1.text_input("Password :", type="password")

    if not isEmail(login_username):
        tab1.text("not email format")
    elif login_username not in users:
        tab1.text("email not register")

    if tab1.button('LOGIN'):
        if login_username in users:
            if verify_password(users[login_username], login_password):
                tab1.text("Login successful")
                cookie_manager.set('person_id', login_username, expires_at=datetime.datetime(year=2025, month=2, day=2))
            else:
                tab1.text("incorrect password")

    #register
    if "sentOTP" not in st.session_state:
        st.session_state["sentOTP"] = False
    if "randomotp" not in st.session_state:
        st.session_state["randomotp"] = None
    if "email" not in st.session_state:
        st.session_state["email"] = None
    if "password" not in st.session_state:
        st.session_state["password"] = None

    if not st.session_state["sentOTP"]:
        email = tab2.text_input("Email : ")
        pass1 = tab2.text_input("Password : ",type="password")
        pass2 = tab2.text_input("Re-Password : ",type="password")
        
        if not isEmail(email):
            tab2.text('not email format')
        elif email in load_users("users.json"):
            tab2.text('email already register')

        elif pass1 == pass2 and pass1:
            if tab2.button("sent otp"):
                tab2.text('sent otp...')

                otp_sented = str(random.randint(1000,9999))

                st.session_state["randomotp"] = otp_sented 
                if sent_otp(email,st.session_state["randomotp"]):
                    st.session_state["email"] = email
                    st.session_state["password"] = pass1
                    st.session_state["sentOTP"] = True
                    st.experimental_rerun()
                            
        else:
            tab2.text('password unmatch')

    else:
        otp = tab2.text_input("OTP :")
        if tab2.button("comfirm OTP"):
            if st.session_state["randomotp"] == otp:
               
                users = load_users("users.json")
                username = st.session_state["email"]
                password = st.session_state["password"]
                hashed_password = hash_password(password)
                users[username] = hashed_password

                save_users("users.json", users)

                tab2.write(f'Done register {username}')

            else:
                tab2.text('OTP unmatch')

    #forgot password
    if "randomotp" not in st.session_state:
        st.session_state["randomotp"] = False
    if "stage_fg" not in st.session_state:
        st.session_state["stage_fg"] = 0
    if "email" not in st.session_state:
        st.session_state["email"] = False

    if st.session_state["stage_fg"] == 0:
        email = tab3.text_input("E-mail :")
        if tab3.button('sent OTP'):
            
            if not isEmail(email):
                tab3.text('not email format')
            elif email not in load_users("users.json"):
                tab3.text('email not register!!')
            else:
                st.session_state["email"] = email
                tab3.text('sent otp...')
                otp_sented = str(random.randint(1000,9999))
                st.session_state["randomotp"] = otp_sented 
                if sent_otp(email,st.session_state["randomotp"]):
                    st.session_state["stage_fg"] = 1
                    st.experimental_rerun()
                else:
                    tab3.text('not sent otp')
                            
    elif st.session_state["stage_fg"] == 1:
        otp = tab3.text_input("OTP :")
        if tab3.button('comfire otp'):
            if otp == st.session_state["randomotp"]:
                st.session_state["stage_fg"] = 2
                st.experimental_rerun()
            else:
                tab3.text('incorrect otp')

    elif st.session_state["stage_fg"] == 2:
        newpassword = tab3.text_input("New password :",type="password")
        re_newpassword = tab3.text_input("Re-New password :", type="password")

        if tab3.button('confirm'):
            if newpassword == re_newpassword:
                tab3.text('complete!!')

                users = load_users("users.json")

                username = st.session_state["email"]
                password = newpassword
                hashed_password = hash_password(password)
                users[username] = hashed_password

                save_users("users.json", users)

            else:
                tab3.text('New password and Re-New password must same value')
    
else:
    st.sidebar.success(person_id)
    LIST_MENUS = ["📈 My Profile", "🗃 Change Password"]
    tab1,tab2 = st.tabs(LIST_MENUS)

    #login
    tab1.write(person_id)

    #logout
    if tab1.button('Logout'):
        try:
            cookie = 'person_id'
            cookie_manager.delete(cookie)
        except:
            pass

    #change password
    tab2.text(person_id)

    login_password = tab2.text_input("Old Password :",type="password")
    new_passsword = tab2.text_input("New Password :", type="password")
    renew_passsword = tab2.text_input("Re-New Password :", type="password")
    users = load_users("users.json")

    if login_password and verify_password(users[person_id], login_password):
        MATCH = False
        if new_passsword == renew_passsword and new_passsword:
            tab2.text("match!")
            MATCH = True
            
        else:
            tab2.text("New Password must same Re-New Password!!")
        if tab2.button('CONFIRM'):
            if MATCH:
                username = person_id
                password = new_passsword
                hashed_password = hash_password(password)
                users[username] = hashed_password

                save_users("users.json", users)

                tab2.text("Update password compleate!")

    else:
        tab2.text("old password incorrect")



