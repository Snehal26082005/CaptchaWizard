import streamlit as st
import cv2
from streamlit_pdf_viewer import pdf_viewer
from tinydb import TinyDB, Query
import time

db = TinyDB('users.json')

THRESHOLD = 0.5

# captcha
if 'captcha' not in st.session_state:
    st.session_state['captcha'] = False
if 'loggedin' not in st.session_state:
    st.session_state['loggedin'] = False

def captcha(framelimit=100):
    nframes = 0
    nfaces = 0
    cam = cv2.VideoCapture(0)
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face = None 

    while nframes < framelimit:
        nframes = nframes + 1
        
        _ret, frame = cam.read()
        
        frame = cv2.flip(frame,1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            nfaces = nfaces + 1
            x, y, w, h = faces[0]
            face = frame[x:x+w, y:y+h]

    cam.release()
    cv2.destroyAllWindows()


    print(f'{nframes=} {nfaces=}')
    
    return (nfaces / nframes) > THRESHOLD

@st.dialog("Sign Up")
def signup():
    st.header("Sign Up")
    uname = st.text_input("*Enter Username:*", placeholder='Username', key='signupu')
    password = st.text_input("*Enter Password:*", type='password', placeholder='Password', key='signupp')

    if st.button('Sign Up', type='primary', icon='🐼'):
        db.insert({'uname': uname, 'password': password})
        st.rerun()

# login
def login():
    _, col, _ = st.columns(3)
    uname = col.text_input("*Enter Username:*", placeholder='Username')
    password = col.text_input("*Enter Password:*", type='password', placeholder='Password')

    if col.button('Login', 
        type="primary", 
        disabled=not st.session_state['captcha'],
        icon="👤",
        use_container_width=True):
        result = db.search(Query().uname == uname)
        if not result:
            st.toast("please signup, user does not exist", icon="🙅‍♂️")

        if not result[0]['password'] == password:
            st.toast("invalid password", icon="❌")
        st.session_state['loggedin'] = True

    if col.button('Sign Up', type='primary', icon='🐼', use_container_width=True):
        signup()

    with st.spinner("Verifying For Human..."):    
        if not st.session_state['captcha'] and captcha():
            st.session_state['captcha'] = True
        
    if st.session_state['captcha']:
        st.success("Human Detected!!!")
    else:
        err, rerun = st.columns([7, 3])
        err.error('Human Not Detected')

        if rerun.button("rerun", icon="♾️"):
            st.rerun()

if __name__ == "__main__":
    st.set_page_config(
        page_title="CaptchaWizard",
        page_icon="✅"
    )

    st.header("CaptchaWizard: Non-Interactive CAPTCHA demo")       

    if not st.session_state['loggedin']:
        login()
    else:
        pdf_viewer(input="./CaptchaWizard_researchPaper.pdf", width=700)
