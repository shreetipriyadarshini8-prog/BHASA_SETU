# -*- coding: utf-8 -*-
"""
BHASA SETU — Elite Cinematic Rebuild
Phases: Splash → Language → Dashboard | Glassmorphism | I18N | Auto-TTS | Bidirectional
Preserves MediaPipe + LSTM inference intact.
"""
import streamlit as st
import json, os, asyncio, time, base64
from pathlib import Path
from collections import deque, Counter
import cv2, numpy as np, mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
import edge_tts
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av

st.set_page_config(page_title="BHASA SETU — Medical ISL Bridge", page_icon="🏥", layout="wide", initial_sidebar_state="collapsed")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "models" / "isl_model.keras"
LABEL_MAP_PATH = PROJECT_ROOT / "models" / "label_map.json"
HAND_MODEL_PATH = PROJECT_ROOT / "models" / "hand_landmarker.task"
RESULT_PATH = APP_DIR / "recognition_result.json"
AUDIO_DIR = APP_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

VOICE_MAP = {
    "English":"en-IN-NeerjaNeural","Hindi":"hi-IN-SwaraNeural","Bengali":"bn-IN-TanishaaNeural",
    "Gujarati":"gu-IN-DhwaniNeural","Tamil":"ta-IN-PallaviNeural","Telugu":"te-IN-ShrutiNeural",
    "Marathi":"mr-IN-AarohiNeural","Kannada":"kn-IN-SapnaNeural","Malayalam":"ml-IN-SobhanaNeural",
    "Punjabi":"pa-IN-GurpreetNeural","Urdu":"ur-IN-UzmaNeural","Odia":"or-IN-SubhasiniNeural"
}
# lang -> google font
FONT_MAP = {
    "English":"Inter","Hindi":"Noto Sans Devanagari","Bengali":"Noto Sans Bengali","Gujarati":"Noto Sans Gujarati",
    "Tamil":"Noto Sans Tamil","Telugu":"Noto Sans Telugu","Marathi":"Noto Sans Devanagari","Kannada":"Noto Sans Kannada",
    "Malayalam":"Noto Sans Malayalam","Punjabi":"Noto Sans Gurmukhi","Urdu":"Noto Nastaliq Urdu","Odia":"Noto Sans Oriya"
}
# deep-translator target codes
TRANS_CODE = {"English":"en","Hindi":"hi","Bengali":"bn","Gujarati":"gu","Tamil":"ta","Telugu":"te","Marathi":"mr","Kannada":"kn","Malayalam":"ml","Punjabi":"pa","Urdu":"ur","Odia":"or"}

# ============================================================
# I18N — system strings across languages
# ============================================================
I18N = {
 "English":{"welcome":"Welcome to BHASA SETU","subtitle":"Bridging Hands and Voices in Healthcare","continue":"Continue to Health Bridge →","select_lang":"Choose Your Language","select_sub":"All UI, recognition and speech will switch instantly","proceed":"Proceed to Consultation →","vision_title":"Patient Vision Stream","vision_sub":"Live ISL detection — hold ONE sign steady","live_sign":"Live Detected Sign","transcript":"Cumulative Translated Sentence","auto_speak":"Auto-speak","doctor_title":"Doctor's Console — Reverse Translation","doctor_sub":"Type in English/Hindi → auto-translates to patient's language","doctor_ph":"Type clinical advice, prescription…","speak_patient":"🔊 Speak to Patient","quick":"Quick Clinical Prompts","tips":"Tips","where_hurt":"Where does it hurt?","need_water":"Need Water","pain_scale":"Pain Scale 1–10?","call_doctor":"Call Doctor","where_hurt_hi":"कहाँ दर्द हो रहा है?","need_water_hi":"पानी चाहिए?","pain_scale_hi":"दर्द 1–10 कितना?","call_doctor_hi":"डॉक्टर को बुलाऊँ?","frames":"Frames","confidence":"Confidence","status":"Status","live":"LIVE","idle":"IDLE","reset":"Reset","stop":"Stop","start":"Start Recognition"},
 "Hindi":{"welcome":"भासा सेतु में आपका स्वागत है","subtitle":"स्वास्थ्य सेवा में हाथों और आवाज़ों को जोड़ना","continue":"हेल्थ ब्रिज पर जाएं →","select_lang":"अपनी भाषा चुनें","select_sub":"सभी UI, पहचान और आवाज़ तुरंत बदल जाएगी","proceed":"परामर्श पर जाएं →","vision_title":"रोगी विज़न स्ट्रीम","vision_sub":"लाइव ISL पहचान — एक संकेत स्थिर रखें","live_sign":"लाइव पहचान","transcript":"अनुवादित वाक्य","auto_speak":"स्वतः बोलें","doctor_title":"डॉक्टर कंसोल — रिवर्स अनुवाद","doctor_sub":"अंग्रेज़ी/हिंदी में लिखें → रोगी की भाषा में अनुवाद","doctor_ph":"सलाह, नुस्खा लिखें…","speak_patient":"🔊 रोगी को सुनाएं","quick":"त्वरित क्लिनिकल प्रॉम्प्ट","tips":"सुझाव","where_hurt":"कहाँ दर्द हो रहा है?","need_water":"पानी चाहिए?","pain_scale":"दर्द 1–10 कितना?","call_doctor":"डॉक्टर को बुलाऊँ?","where_hurt_hi":"कहाँ दर्द हो रहा है?","need_water_hi":"पानी चाहिए?","pain_scale_hi":"दर्द 1–10 कितना?","call_doctor_hi":"डॉक्टर को बुलाऊँ?","frames":"फ्रेम","confidence":"विश्वास","status":"स्थिति","live":"लाइव","idle":"निष्क्रिय","reset":"रीसेट","stop":"रोकें","start":"पहचान शुरू करें"},
 "Bengali":{"welcome":"ভাসা সেতুতে স্বাগতম","subtitle":"স্বাস্থ্যসেবায় হাত ও কণ্ঠস্বর সংযোগ","continue":"হেলথ ব্রিজে যান →","select_lang":"আপনার ভাষা চয়ন করুন","select_sub":"সমস্ত UI তৎক্ষণাৎ পরিবর্তন হবে","proceed":"পরামর্শে যান →","vision_title":"রোগী ভিশন স্ট্রিম","vision_sub":"লাইভ ISL সনাক্তকরণ","live_sign":"লাইভ সনাক্তকরণ","transcript":"অনূদিত বাক্য","auto_speak":"স্বয়ংক্রিয় বলা","doctor_title":"ডাক্তারের কনসোল","doctor_sub":"ইংরেজিতে লিখুন → রোগীর ভাষায় অনুবাদ","doctor_ph":"পরামর্শ লিখুন…","speak_patient":"🔊 রোগীকে শোনান","quick":"দ্রুত প্রম্পট","tips":"টিপস","where_hurt":"কোথায় ব্যথা?","need_water":"জল প্রয়োজন","pain_scale":"ব্যথা ১–১০?","call_doctor":"ডাক্তার ডাকুন","where_hurt_hi":"কোথায় ব্যথা?","need_water_hi":"জল প্রয়োজন","pain_scale_hi":"ব্যথা ১–১০?","call_doctor_hi":"ডাক্তার ডাকুন","frames":"ফ্রেম","confidence":"আত্মবিশ্বাস","status":"অবস্থা","live":"লাইভ","idle":"নিষ্ক্রিয়","reset":"রিসেট","stop":"থামুন","start":"শনাক্ত শুরু"},
 "Gujarati":{"welcome":"ભાષા સેતુમાં સ્વાગત છે","subtitle":"આરોગ્યમાં હાથ અને અવાજને જોડવા","continue":"હેલ્થ બ્રિજ પર જાઓ →","select_lang":"તમારી ભાષા પસંદ કરો","select_sub":"બધું UI તુરંત બદલાશે","proceed":"પરામર્શ પર જાઓ →","vision_title":"દર્દી વિઝન સ્ટ્રીમ","vision_sub":"લાઇવ ISL શોધ","live_sign":"લાઇવ શોધ","transcript":"અનુવાદિત વાક્ય","auto_speak":"ઓટો બોલો","doctor_title":"ડૉક્ટર કન્સોલ","doctor_sub":"અંગ્રેજીમાં લખો → દર્દીની ભાષામાં","doctor_ph":"સલાહ લખો…","speak_patient":"🔊 દર્દીને સંભળાવો","quick":"ઝડપી પ્રોમ્પ્ટ","tips":"ટિપ્સ","where_hurt":"ક્યાં દુખે છે?","need_water":"પાણી જોઈએ","pain_scale":"દુખાવો ૧–૧૦?","call_doctor":"ડૉક્ટરને બોલાવો","where_hurt_hi":"ક્યાં દુખે છે?","need_water_hi":"પાણી જોઈએ","pain_scale_hi":"દુખાવો ૧–૧૦?","call_doctor_hi":"ડૉક્ટરને બોલાવો","frames":"ફ્રેમ","confidence":"વિશ્વાસ","status":"સ્થિતિ","live":"લાઇવ","idle":"નિષ્ક્રિય","reset":"રીસેટ","stop":"રોકો","start":"શરૂ કરો"},
 "Tamil":{"welcome":"பாஷா சேதுவுக்கு வரவேற்கிறோம்","subtitle":"சுகாதாரத்தில் கைகளையும் குரல்களையும் இணைத்தல்","continue":"ஹெல்த் பிரிட்ஜுக்கு செல்ல →","select_lang":"உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்","select_sub":"அனைத்து UI உடனடியாக மாறும்","proceed":"ஆலோசனைக்கு செல்ல →","vision_title":"நோயாளி பார்வை","vision_sub":"நேரடி ISL கண்டறிதல்","live_sign":"நேரடி கண்டறிதல்","transcript":"மொழிபெயர்க்கப்பட்ட வாக்கியம்","auto_speak":"தானாக பேசு","doctor_title":"மருத்துவர் கன்சோல்","doctor_sub":"ஆங்கிலத்தில் எழுத → நோயாளி மொழியில்","doctor_ph":"ஆலோசனை எழுத…","speak_patient":"🔊 நோயாளிக்கு ஒலிக்கவும்","quick":"விரைவு தூண்டுதல்","tips":"குறிப்புகள்","where_hurt":"எங்கே வலிக்கிறது?","need_water":"தண்ணீர் வேண்டும்","pain_scale":"வலி 1–10?","call_doctor":"மருத்துவரை அழைக்கவும்","where_hurt_hi":"எங்கே வலிக்கிறது?","need_water_hi":"தண்ணீர் வேண்டும்","pain_scale_hi":"வலி 1–10?","call_doctor_hi":"மருத்துவரை அழைக்கவும்","frames":"பிரேம்கள்","confidence":"நம்பிக்கை","status":"நிலை","live":"நேரலை","idle":"செயலற்ற","reset":"மீட்டமை","stop":"நிறுத்து","start":"தொடங்கு"},
}
# fill rest with English fallback
# Add complete UI translations for languages that are not listed above.
I18N.update({
 "Telugu": {"welcome":"భాషా సేతుకు స్వాగతం","subtitle":"ఆరోగ్య సేవల్లో చేతులు మరియు స్వరాలను కలుపుతోంది","continue":"హెల్త్ బ్రిడ్జ్‌కు కొనసాగండి →","select_lang":"మీ భాషను ఎంచుకోండి","select_sub":"UI, గుర్తింపు మరియు వాయిస్ వెంటనే మారుతాయి","proceed":"సంప్రదింపుకు కొనసాగండి →","vision_title":"రోగి విజన్ స్ట్రీమ్","vision_sub":"లైవ్ ISL గుర్తింపు — ఒక సంకేతాన్ని స్థిరంగా ఉంచండి","live_sign":"లైవ్ గుర్తించిన సంకేతం","transcript":"అనువదించిన వాక్యం","auto_speak":"ఆటో స్పీక్","doctor_title":"డాక్టర్ కన్సోల్ — రివర్స్ అనువాదం","doctor_sub":"ఇంగ్లీష్/హిందీలో టైప్ చేయండి → రోగి భాషలోకి అనువదిస్తుంది","doctor_ph":"వైద్య సలహా, ప్రిస్క్రిప్షన్ టైప్ చేయండి…","speak_patient":"🔊 రోగికి వినిపించండి","quick":"త్వరిత క్లినికల్ ప్రాంప్ట్‌లు","tips":"చిట్కాలు","where_hurt":"ఎక్కడ నొప్పిగా ఉంది?","need_water":"నీరు కావాలా?","pain_scale":"నొప్పి 1–10 ఎంత?","call_doctor":"డాక్టర్‌ను పిలవాలా?","frames":"ఫ్రేమ్‌లు","confidence":"నమ్మకం","status":"స్థితి","live":"లైవ్","idle":"నిష్క్రియ","reset":"రీసెట్","stop":"ఆపు","start":"గుర్తింపు ప్రారంభించండి"},
 "Marathi": {"welcome":"भाषा सेतूमध्ये स्वागत आहे","subtitle":"आरोग्य सेवेत हात आणि आवाज जोडणे","continue":"हेल्थ ब्रिजवर जा →","select_lang":"तुमची भाषा निवडा","select_sub":"UI, ओळख आणि आवाज लगेच बदलेल","proceed":"सल्लामसलतीकडे जा →","vision_title":"रुग्ण व्हिजन स्ट्रीम","vision_sub":"लाइव्ह ISL ओळख — एक चिन्ह स्थिर ठेवा","live_sign":"लाइव्ह ओळखलेले चिन्ह","transcript":"अनुवादित वाक्य","auto_speak":"ऑटो स्पीक","doctor_title":"डॉक्टर कन्सोल — रिव्हर्स भाषांतर","doctor_sub":"इंग्रजी/हिंदीमध्ये टाइप करा → रुग्णाच्या भाषेत भाषांतर","doctor_ph":"वैद्यकीय सल्ला, प्रिस्क्रिप्शन टाइप करा…","speak_patient":"🔊 रुग्णाला ऐकवा","quick":"जलद क्लिनिकल प्रॉम्प्ट्स","tips":"टिप्स","where_hurt":"कुठे दुखत आहे?","need_water":"पाणी हवे आहे?","pain_scale":"वेदना 1–10 किती?","call_doctor":"डॉक्टरांना बोलवायचे?","frames":"फ्रेम्स","confidence":"विश्वास","status":"स्थिती","live":"लाइव्ह","idle":"निष्क्रिय","reset":"रीसेट","stop":"थांबा","start":"ओळख सुरू करा"},
 "Odia": {"welcome":"ଭାଷା ସେତୁକୁ ସ୍ୱାଗତ","subtitle":"ସ୍ୱାସ୍ଥ୍ୟସେବାରେ ହାତ ଓ ସ୍ୱରକୁ ଯୋଡ଼ିବା","continue":"ହେଲ୍ଥ ବ୍ରିଜକୁ ଯାଆନ୍ତୁ →","select_lang":"ଆପଣଙ୍କ ଭାଷା ବାଛନ୍ତୁ","select_sub":"ସମସ୍ତ UI, ଚିହ୍ନଟ ଏବଂ ଧ୍ୱନି ତୁରନ୍ତ ବଦଳିବ","proceed":"ପରାମର୍ଶକୁ ଯାଆନ୍ତୁ →","vision_title":"ରୋଗୀ ଭିଜନ ଷ୍ଟ୍ରିମ","vision_sub":"ଲାଇଭ ISL ଚିହ୍ନଟ — ଗୋଟିଏ ସଙ୍କେତ ସ୍ଥିର ରଖନ୍ତୁ","live_sign":"ଲାଇଭ ଚିହ୍ନଟ ସଙ୍କେତ","transcript":"ଅନୁବାଦିତ ବାକ୍ୟ","auto_speak":"ସ୍ୱୟଂଚାଳିତ ଧ୍ୱନି","doctor_title":"ଡାକ୍ତର କନସୋଲ — ପଛୁଆ ଅନୁବାଦ","doctor_sub":"ଇଂରାଜୀ/ହିନ୍ଦୀରେ ଲେଖନ୍ତୁ → ରୋଗୀଙ୍କ ଭାଷାକୁ ଅନୁବାଦ","doctor_ph":"ଚିକିତ୍ସା ପରାମର୍ଶ, ପ୍ରେସକ୍ରିପସନ ଲେଖନ୍ତୁ…","speak_patient":"🔊 ରୋଗୀଙ୍କୁ ଶୁଣାନ୍ତୁ","quick":"ତ୍ୱରିତ ଚିକିତ୍ସା ପ୍ରମ୍ପ୍ଟ","tips":"ସୁପାରିଶ","where_hurt":"କେଉଁଠି ଯନ୍ତ୍ରଣା ହେଉଛି?","need_water":"ପାଣି ଦରକାର କି?","pain_scale":"ଯନ୍ତ୍ରଣା 1–10 କେତେ?","call_doctor":"ଡାକ୍ତରଙ୍କୁ ଡାକିବି କି?","frames":"ଫ୍ରେମ","confidence":"ବିଶ୍ୱାସ ସ୍ତର","status":"ସ୍ଥିତି","live":"ଲାଇଭ","idle":"ନିଷ୍କ୍ରିୟ","reset":"ରିସେଟ","stop":"ବନ୍ଦ କରନ୍ତୁ","start":"ଚିହ୍ନଟ ଆରମ୍ଭ କରନ୍ତୁ"},
})

def t(key):
    lang=st.session_state.get("app_lang","English")
    return I18N.get(lang, I18N["English"]).get(key, I18N["English"].get(key,key))

def translate_doctor(text, target_lang):
    if not text.strip(): return text
    if target_lang in ["English","Hindi"]:
        # direct lang_map fallback is enough, use deep-translator for others
        pass
    try:
        from deep_translator import GoogleTranslator
        code=TRANS_CODE.get(target_lang,"en")
        return GoogleTranslator(source='auto', target=code).translate(text)
    except Exception as e:
        # Keep the original text if the online translator is unavailable.
        # The app still supports Odia TTS independently through Edge TTS.
        return text

# ============================================================
# DESIGN SYSTEM — Neo-Medical Dark Glassmorphism
# ============================================================
def inject_fonts(lang):
    font=FONT_MAP.get(lang,"Inter")
    # encode space
    fam=font.replace(" ","+")
    st.markdown(f'<link href="https://fonts.googleapis.com/css2?family={fam}:wght@400;600;700;800&display=swap" rel="stylesheet">', unsafe_allow_html=True)
    return font

# base CSS (glassmorphism, micro-animations, high contrast)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
[data-testid="stAppViewContainer"]{
  background:#0B0F19;
  background-image: radial-gradient(800px 400px at 20% 0%, rgba(30,27,75,0.55), transparent 60%),
                    radial-gradient(700px 500px at 90% 10%, rgba(6,78,59,0.45), transparent 60%),
                    radial-gradient(600px 400px at 50% 90%, rgba(6,182,212,0.08), transparent 70%);
}
[data-testid="stHeader"]{ background:rgba(11,15,25,0.6); backdrop-filter:blur(8px); }
h1,h2,h3{ color:#F8FAFC !important; }
p, label, span{ color:#F8FAFC; }
.small{ color:#94A3B8 !important; font-size:12px; }
.card{
  background:rgba(30,41,59,0.7); backdrop-filter:blur(12px);
  border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:18px;
  box-shadow:0 10px 30px rgba(0,0,0,0.35); transition:all 0.2s ease;
}
.card:hover{ transform:translateY(-2px); box-shadow:0 14px 36px rgba(0,0,0,0.45); }
.header-pill{
  background:rgba(16,185,129,0.14); border:1px solid #10B981; color:#D1FAE5;
  padding:6px 12px; border-radius:999px; font-weight:800; font-size:12px;
}
.badge-live{ background:rgba(16,185,129,0.18); border:1px solid #10B981; color:#A7F3D0; padding:4px 10px; border-radius:999px; font-weight:800; font-size:11px; }
.badge-idle{ background:rgba(239,68,68,0.12); border:1px solid #EF4444; color:#FECACA; padding:4px 10px; border-radius:999px; font-weight:800; font-size:11px; }
.pulse{ animation:pulse 1.6s infinite; }
@keyframes pulse{ 0%{box-shadow:0 0 0 0 rgba(16,185,129,0.6)} 70%{box-shadow:0 0 0 12px rgba(16,185,129,0)} 100%{box-shadow:0 0 0 0 rgba(16,185,129,0)} }
.fade-in-up{ animation:fadeInUp 0.7s ease both; }
@keyframes fadeInUp{ from{opacity:0; transform:translateY(14px)} to{opacity:1; transform:translateY(0)} }
.typewriter{ overflow:hidden; white-space:nowrap; border-right:3px solid #10B981; animation:typing 1.6s steps(24,end), blink 0.7s step-end infinite; }
@keyframes typing{ from{width:0} to{width:100%} }
@keyframes blink{ 50%{border-color:transparent} }
.glow-btn{ background:linear-gradient(90deg,#10B981,#06B6D4) !important; color:white !important; border:none !important; border-radius:12px !important; font-weight:800 !important; box-shadow:0 8px 24px rgba(16,185,129,0.35); transition:all 0.2s ease; }
.glow-btn:hover{ transform:translateY(-1px); box-shadow:0 12px 32px rgba(6,182,212,0.45); }
.lang-card{ background:rgba(30,41,59,0.7); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:14px; text-align:center; cursor:pointer; transition:all 0.2s ease; }
.lang-card:hover{ transform:translateY(-2px); border-color:#10B981; }
.lang-card.active{ border-color:#10B981; background:rgba(16,185,129,0.12); box-shadow:0 0 0 2px rgba(16,185,129,0.25); }
.speak-dot{ width:10px; height:10px; border-radius:50%; background:#F59E0B; display:inline-block; animation:pulse 1.2s infinite; margin-right:6px; }
.progress-wrap{ height:8px; background:rgba(255,255,255,0.08); border-radius:999px; overflow:hidden; }
.progress-bar{ height:100%; background:linear-gradient(90deg,#10B981,#06B6D4); transition:width 0.3s; }
.callout{ background:rgba(30,41,59,0.7); border:1px solid #10B981; border-radius:16px; padding:18px; backdrop-filter:blur(12px); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CACHED ML — preserve intact
# ============================================================
@st.cache_resource(show_spinner=False)
def load_model_cached():
    import tensorflow as tf
    if not MODEL_PATH.exists(): return None
    return tf.keras.models.load_model(str(MODEL_PATH))
@st.cache_resource(show_spinner=False)
def load_label_map_cached():
    with open(LABEL_MAP_PATH,"r",encoding="utf-8") as f:
        lm=json.load(f)
    if all(str(k).isdigit() for k in lm): return {int(k):v for k,v in lm.items()}
    return {int(v):k for k,v in lm.items()}
@st.cache_resource(show_spinner=False)
def load_lang_map():
    import csv
    p=PROJECT_ROOT/"data"/"patient_phrases.csv"
    m={}
    with open(p,encoding="utf-8") as f:
        for r in csv.DictReader(f):
            m[r["phrase_key"]]={"english":r["english"],"hindi":r["hindi"]}
    return m
LANG_MAP=load_lang_map()
SEQ_LEN, FEATS = 60,126
TH, HIST, VOTES, MIN_HAND, CONF_N = 0.60,8,5,45,3
HAND_CONNS=[(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(17,18),(18,19),(19,20),(0,17)]
def get_landmarks(results):
    left=np.zeros(63,dtype=np.float32); right=np.zeros(63,dtype=np.float32)
    if results.hand_landmarks:
        for lms,hd in zip(results.hand_landmarks, results.handedness):
            c=[]; 
            for lm in lms: c.extend([lm.x,lm.y,lm.z])
            arr=np.array(c,dtype=np.float32)
            lab=hd[0].category_name
            if lab=="Left": left=arr
            elif lab=="Right": right=arr
    return np.concatenate([left,right])
def normalize_sequence(seq):
    s=seq.copy()
    for i in range(s.shape[0]):
        f=s[i]; l=f[:63].reshape(21,3); r=f[63:].reshape(21,3)
        if np.any(l!=0): l=l-l[0]
        if np.any(r!=0): r=r-r[0]
        s[i]=np.concatenate([l.flatten(),r.flatten()])
    return s
async def gen_speech(text,voice,out): c=edge_tts.Communicate(text,voice); await c.save(out)
def create_speech(text,voice,out):
    try:
        loop=asyncio.new_event_loop(); loop.run_until_complete(gen_speech(text,voice,out)); loop.close(); return True
    except Exception as e: st.error(f"TTS failed: {e}"); return False
def speak_text(text, lang, fname, autoplay=False):
    if not text or not text.strip(): return None
    voice=VOICE_MAP.get(lang, VOICE_MAP["English"])
    out=str(AUDIO_DIR/fname)
    if create_speech(text,voice,out) and os.path.exists(out):
        # b64 autoplay for cinematic
        try:
            with open(out,"rb") as f: b64=base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay style="display:none"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        except: pass
        try: st.audio(out, format="audio/mp3", autoplay=autoplay)
        except TypeError: st.audio(out, format="audio/mp3")
        return out
    return None
def save_result(sign,conf):
    d=LANG_MAP.get(sign,{"english":sign.replace("_"," "),"hindi":sign.replace("_"," ")})
    # translate to current lang if not EN/HI
    lang=st.session_state.get("app_lang","English")
    txt=d.get("hindi" if lang=="Hindi" else "english", d["english"])
    # for other langs, translate on the fly
    if lang not in ["English","Hindi"]:
        txt=translate_doctor(d["english"], lang)
    obj={"sign":sign,"confidence":float(conf),"english":d["english"],"hindi":d["hindi"],"translated":txt,"ts":time.strftime("%H:%M:%S")}
    with open(RESULT_PATH,"w",encoding="utf-8") as f: json.dump(obj,f,ensure_ascii=False,indent=2)
    return obj
def read_result():
    if not RESULT_PATH.exists(): return None
    try:
        with open(RESULT_PATH,"r",encoding="utf-8") as f: return json.load(f)
    except: return None

class ISLProcessor(VideoProcessorBase):
    def __init__(self):
        self.model=load_model_cached(); self.idx2label=load_label_map_cached()
        opts=HandLandmarkerOptions(base_options=BaseOptions(model_asset_path=str(HAND_MODEL_PATH)), num_hands=2, min_hand_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.hands=HandLandmarker.create_from_options(opts)
        self.seq=deque(maxlen=SEQ_LEN); self.hist=deque(maxlen=HIST)
        self.cur="Waiting..."; self.cur_c=0.0; self.locked=None; self.locked_c=0.0; self.confirm=0; self.recognizing=True
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img=frame.to_ndarray(format="bgr24"); img=cv2.flip(img,1)
        rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        res=self.hands.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
        feats=get_landmarks(res)
        if res.hand_landmarks:
            h,w,_=img.shape
            for lms in res.hand_landmarks:
                for a,b in HAND_CONNS: cv2.line(img,(int(lms[a].x*w),int(lms[a].y*h)),(int(lms[b].x*w),int(lms[b].y*h)),(16,185,129),2)
                for lm in lms: cv2.circle(img,(int(lm.x*w),int(lm.y*h)),3,(6,182,212),-1)
        if self.recognizing:
            self.seq.append(feats)
            if len(self.seq)==SEQ_LEN and self.model is not None:
                arr=np.array(self.seq,dtype=np.float32)
                if np.sum(np.any(arr!=0,axis=1))<MIN_HAND:
                    self.cur="SHOW HAND PROPERLY"; self.cur_c=0; self.hist.clear(); self.confirm=0
                else:
                    norm=normalize_sequence(arr); probs=self.model.predict(np.expand_dims(norm,0),verbose=0)[0]
                    idx=int(np.argmax(probs)); conf=float(probs[idx]); lab=self.idx2label.get(idx,"Unknown")
                    self.cur=lab; self.cur_c=conf
                    if conf>=TH:
                        self.hist.append(idx); cnt=Counter(self.hist); common,votes=cnt.most_common(1)[0]
                        if votes>=VOTES:
                            if self.idx2label.get(common)==self.cur: self.confirm+=1
                            else: self.confirm=0
                            if self.confirm>=CONF_N:
                                self.locked=self.idx2label.get(common); self.locked_c=conf; self.recognizing=False
                                try: save_result(self.locked,self.locked_c)
                                except: pass
                    else: self.hist.clear(); self.confirm=0
        cv2.rectangle(img,(10,10),(380,92),(11,15,25),-1); cv2.rectangle(img,(10,10),(380,92),(16,185,129),1)
        cv2.putText(img,"BHASA SETU",(16,28),cv2.FONT_HERSHEY_SIMPLEX,0.55,(248,250,252),1)
        cv2.putText(img,"RECOGNIZING" if self.recognizing else "LOCKED",(16,50),cv2.FONT_HERSHEY_SIMPLEX,0.45,(16,185,129) if self.recognizing else (245,158,11),1)
        cv2.putText(img,f"Cur:{self.cur} {self.cur_c*100:.0f}%",(16,70),cv2.FONT_HERSHEY_SIMPLEX,0.38,(248,250,252),1)
        cv2.putText(img,f"Locked:{self.locked or '--'}",(16,86),cv2.FONT_HERSHEY_SIMPLEX,0.38,(148,163,184),1)
        return av.VideoFrame.from_ndarray(img, format="bgr24")
    def reset(self):
        self.seq.clear(); self.hist.clear(); self.cur="Waiting..."; self.cur_c=0; self.locked=None; self.locked_c=0; self.confirm=0; self.recognizing=True
        try:
            if RESULT_PATH.exists(): RESULT_PATH.unlink()
        except: pass

# ============================================================
# SESSION — Phase management
# ============================================================
if "phase" not in st.session_state: st.session_state.phase="splash"
if "app_lang" not in st.session_state: st.session_state.app_lang="English"
if "auto_speak" not in st.session_state: st.session_state.auto_speak=True
if "last_spoken" not in st.session_state: st.session_state.last_spoken=""
if "last_result" not in st.session_state: st.session_state.last_result=None
if "transcript" not in st.session_state: st.session_state.transcript=[]
if "doctor_text" not in st.session_state: st.session_state.doctor_text=""

# dynamic font injection
font=inject_fonts(st.session_state.app_lang)
st.markdown(f"<style>html, body, [class*='css']{{font-family:'{font}',Inter,system-ui,sans-serif}}</style>", unsafe_allow_html=True)

# ============================================================
# PHASE 1 — Cinematic Splash / Hero
# ============================================================
if st.session_state.phase=="splash":
    st.markdown("""
    <div class="fade-in-up" style="text-align:center; padding:60px 20px 30px 20px">
      <h1 class="typewriter" style="font-size:42px; font-weight:800; color:#F8FAFC; margin:18px auto; max-width:700px; text-shadow:0 0 30px rgba(16,185,129,0.25)">Welcome to BHASA SETU</h1>
      <p style="color:#94A3B8; font-size:18px; margin-top:10px">Bridging Hands and Voices in Healthcare</p>
      <div style="margin:18px auto; width:120px; height:3px; border-radius:999px; background:linear-gradient(90deg,#10B981,#06B6D4); box-shadow:0 0 18px rgba(16,185,129,0.6)"></div>
      <p style="color:#64748B; max-width:600px; margin:0 auto; font-size:13px">Assistive medical Indian Sign Language bridge — MediaPipe + LSTM • 46 signs • Real-time translation • Bi-directional doctor console</p>
    </div>
    """, unsafe_allow_html=True)
    # Auto audio welcome (edge-tts + autoplay)
    welcome_text="Welcome to Bhasa Setu. Bridging hands and voices in healthcare."
    # generate welcome audio once per session
    if "welcome_played" not in st.session_state:
        try:
            # use English voice for welcome
            out=str(AUDIO_DIR/"welcome.mp3")
            loop=asyncio.new_event_loop(); loop.run_until_complete(gen_speech(welcome_text, VOICE_MAP["English"], out)); loop.close()
            with open(out,"rb") as f: b64=base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.session_state.welcome_played=True
        except: pass
    st.markdown('<div style="text-align:center; margin-top:22px">', unsafe_allow_html=True)
    if st.button("Continue to Health Bridge →", key="splash_cont", help="Enter language selection"):
        st.session_state.phase="language"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    # glow orbs
    st.markdown('<div style="height:30px"></div><div style="text-align:center; color:#334155; font-size:11px">Press Continue to choose your language</div>', unsafe_allow_html=True)
    st.stop()

# ============================================================
# PHASE 2 — Interactive Language Selection
# ============================================================
if st.session_state.phase=="language":
    st.markdown(f"""
    <div class="fade-in-up" style="text-align:center; padding:30px 10px 10px 10px">
      <h2 style="color:#F8FAFC; font-weight:800">{t('select_lang')}</h2>
      <p style="color:#94A3B8">{t('select_sub')}</p>
    </div>
    """, unsafe_allow_html=True)
    langs=["English","Hindi","Bengali","Gujarati","Tamil","Telugu","Marathi","Kannada","Malayalam","Punjabi","Urdu","Odia"]
    # grid 4x3
    cols=st.columns(4)
    for i,lg in enumerate(langs):
        col=cols[i%4]
        with col:
            active = st.session_state.app_lang==lg
            # lang card
            if st.button(f"{'● ' if active else '○ '}{lg}\n{TRANS_CODE[lg]}", key=f"lang_{lg}", use_container_width=True):
                st.session_state.app_lang=lg
                # reload font instantly
                st.rerun()
            # visual active indicator via caption
            if active:
                st.markdown(f'<div style="text-align:center; color:#10B981; font-size:11px; font-weight:800">✓ {lg} — {FONT_MAP[lg]}</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    st.info(f"Selected: **{st.session_state.app_lang}** — Font: `{FONT_MAP[st.session_state.app_lang]}` — All UI will switch instantly")
    st.markdown('<div style="text-align:center; margin-top:14px">', unsafe_allow_html=True)
    if st.button(t("proceed"), key="proceed_dash", type="primary"):
        st.session_state.phase="dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("← Back to Splash", key="back_splash"):
        st.session_state.phase="splash"; st.rerun()
    st.stop()

# ============================================================
# PHASE 3 — Main Medical Translation Dashboard
# ============================================================
# Header for dashboard
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; background:rgba(30,41,59,0.7); backdrop-filter:blur(12px); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:12px 16px; margin-bottom:12px">
  <div><b style="color:#F8FAFC">🏥 BHASA SETU</b> <span style="color:#94A3B8">| {t('vision_title')}</span> <span style="color:#10B981; font-weight:700">• {st.session_state.app_lang}</span> <span style="font-family:'{font}'">({FONT_MAP[st.session_state.app_lang]})</span></div>
  <div><span class="header-pill">🟢 SYSTEM READY (46 Signs Active)</span></div>
</div>
""", unsafe_allow_html=True)

# two-way layout
left, right = st.columns([1.35,0.9], gap="medium")

# LEFT — Patient Vision Stream
with left:
    with st.container(border=True):
        st.markdown(f'<div style="color:#F8FAFC; font-weight:800">{t("vision_title")}</div><div class="small">{t("vision_sub")}</div>', unsafe_allow_html=True)
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        RTC_CFG=RTCConfiguration({"iceServers":[{"urls":["stun:stun.l.google.com:19302"]}]})
        ctx=webrtc_streamer(key="bhasa-cinematic", video_processor_factory=ISLProcessor, rtc_configuration=RTC_CFG, media_stream_constraints={"video":True,"audio":False}, async_processing=True)
        # controls
        b1,b2,b3=st.columns(3)
        with b1:
            if st.button(f"▶ {t('start')}", use_container_width=True, key="start_main"):
                st.toast("Allow camera permission")
        with b2:
            if st.button(f"⏹ {t('stop')}", use_container_width=True, key="stop_main"):
                st.toast("Use browser Stop button")
        with b3:
            if st.button(f"🔄 {t('reset')}", use_container_width=True, key="reset_main"):
                if ctx.video_processor: ctx.video_processor.reset(); st.session_state.last_spoken=""; st.toast("Reset")
                else:
                    if RESULT_PATH.exists(): RESULT_PATH.unlink()
                    st.session_state.last_spoken=""; st.toast("Reset")
        if ctx.video_processor:
            vp=ctx.video_processor; pct=int(vp.cur_c*100); frames=len(vp.seq)
            m1,m2,m3=st.columns(3)
            with m1: st.metric(t("confidence"), f"{pct}%")
            with m2: st.metric(t("frames"), f"{frames}/60")
            with m3:
                if ctx.state.playing: st.markdown('<span class="badge-live">● LIVE</span>', unsafe_allow_html=True)
                else: st.markdown('<span class="badge-idle">● IDLE</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="progress-wrap"><div class="progress-bar" style="width:{pct}%"></div></div><div class="small">{t("frames")}: {frames}/60 • Votes {len(vp.hist)}/{HIST} • Confirm {vp.confirm}/{CONF_N}</div>', unsafe_allow_html=True)
            # cumulative sentence + auto-speak in selected language script
            if vp.locked and vp.locked != st.session_state.last_spoken and st.session_state.auto_speak:
                res=read_result()
                if res:
                    # translated already in save_result per lang
                    txt=res.get("translated", res.get("hindi" if st.session_state.app_lang=="Hindi" else "english",""))
                    st.session_state.last_spoken=vp.locked
                    st.session_state.transcript.append({"sign":vp.locked,"text":txt,"ts":res.get("ts",""),"conf":vp.locked_c})
                    st.session_state.transcript=st.session_state.transcript[-20:]
                    st.session_state.last_result=res
                    # TTS in patient's language voice
                    lang=st.session_state.app_lang
                    # if lang not in VOICE_MAP fallback to Hindi/English
                    tts_lang=lang if lang in VOICE_MAP else "Hindi" if lang in ["Punjabi","Urdu"] else "English"
                    # for other langs, we still speak translated text with Hindi voice as fallback (or English)
                    with st.spinner(f"Speaking {lang}..."):
                        speak_text(txt, tts_lang, f"auto_{lang}_{vp.locked}.mp3", autoplay=True)
                    st.toast(f"Auto-spoke: {vp.locked}")
        else:
            st.progress(0)
            st.caption("Click START above camera and grant permission")
        # live predicted sign badge
        if ctx.video_processor:
            vp=ctx.video_processor
            st.markdown(f'<div class="small" style="margin-top:8px"><span class="speak-dot"></span>Live: <b style="color:#F8FAFC">{vp.cur}</b> {vp.cur_c*100:.0f}%</div>', unsafe_allow_html=True)
        # snapshot fallback
        with st.expander("📸 Snapshot fallback", expanded=False):
            snap=st.camera_input("Take a photo", label_visibility="collapsed")
            if snap:
                with st.spinner("Analyzing..."):
                    try:
                        data=snap.getvalue(); arr=np.frombuffer(data,np.uint8); img=cv2.imdecode(arr,cv2.IMREAD_COLOR)
                        rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                        opts=HandLandmarkerOptions(base_options=BaseOptions(model_asset_path=str(HAND_MODEL_PATH)), num_hands=2)
                        hands=HandLandmarker.create_from_options(opts)
                        mp_img=mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                        r=hands.detect(mp_img); feat=get_landmarks(r)
                        seq=np.tile(feat,(SEQ_LEN,1)); norm=normalize_sequence(seq)
                        m=load_model_cached(); idx2=load_label_map_cached()
                        probs=m.predict(np.expand_dims(norm,0),verbose=0)[0]
                        idx=int(np.argmax(probs)); conf=float(probs[idx]); lab=idx2.get(idx,"Unknown")
                        hands.close()
                        if conf>=0.55:
                            obj=save_result(lab,conf); st.session_state.last_result=obj
                            st.success(f"{lab} {conf*100:.1f}%")
                            lang=st.session_state.app_lang
                            txt=obj.get("translated", obj.get("hindi" if lang=="Hindi" else "english",""))
                            st.info(txt)
                            if st.session_state.auto_speak and lab!=st.session_state.last_spoken:
                                st.session_state.last_spoken=lab
                                st.session_state.transcript.append({"sign":lab,"text":txt,"ts":obj.get("ts",""),"conf":conf})
                                tts_lang=lang if lang in VOICE_MAP else "English"
                                speak_text(txt, tts_lang, f"snap_{lab}.mp3", autoplay=True)
                        else: st.warning(f"Low conf {lab} {conf*100:.1f}%")
                    except Exception as e: st.error(f"Snapshot failed: {e}")

with right:
    # Live Detected Sign — high-visibility
    with st.container(border=True):
        st.markdown(f'<div style="color:#F8FAFC; font-weight:800">{t("live_sign")}</div>', unsafe_allow_html=True)
        res=read_result()
        if res: st.session_state.last_result=res
        else: res=st.session_state.last_result
        if res:
            sign=res.get("sign","Unknown"); conf=res.get("confidence",0)
            st.markdown(f'<div class="callout"><div class="small">DETECTED ISL SIGN</div><div style="color:#F8FAFC; font-size:26px; font-weight:800">🖐️ {sign.replace("_"," ").title()}</div><div style="color:#10B981; font-weight:800">{conf*100:.1f}% • {res.get("ts","")}</div></div>', unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1: st.metric(t("confidence"), f"{conf*100:.1f}%")
            with c2: st.metric(t("status"), "LOCKED" if ctx.video_processor and not ctx.video_processor.recognizing else "REC")
        else:
            with st.status("Waiting for sign…", expanded=True) as s:
                st.write("Hold ONE sign steady 2–3s")
                time.sleep(0.3); s.update(label="Ready", state="complete")
            st.markdown('<div class="callout" style="border-color:rgba(255,255,255,0.08)"><div class="small">DETECTED ISL SIGN</div><div style="color:#94A3B8; font-size:22px">— Waiting —</div></div>', unsafe_allow_html=True)
    # Cumulative translated sentence box
    with st.container(border=True):
        st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center"><b style="color:#F8FAFC">{t("transcript")}</b><label style="color:#94A3B8; font-size:12px"><input type="checkbox" {"checked" if st.session_state.auto_speak else ""} disabled> {t("auto_speak")} {"ON" if st.session_state.auto_speak else "OFF"}</label></div>', unsafe_allow_html=True)
        # toggle
        st.session_state.auto_speak = st.toggle(t("auto_speak"), value=st.session_state.auto_speak, key="auto_toggle_dash")
        res=st.session_state.last_result or read_result()
        if res:
            txt=res.get("translated", res.get("hindi" if st.session_state.app_lang=="Hindi" else "english",""))
            st.markdown(f'<div style="background:rgba(11,15,25,0.6); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:12px; margin-top:8px"><b style="color:#F8FAFC; font-family:{font}">{txt}</b><br><span class="small">{res.get("sign","").replace("_"," ").title()} • {res.get("confidence",0)*100:.1f}% • {res.get("ts","")}</span></div>', unsafe_allow_html=True)
            if st.button("🔊 Speak Again", key="speak_transcript", use_container_width=True):
                lang=st.session_state.app_lang; tts_lang=lang if lang in VOICE_MAP else "English"
                with st.spinner("Speaking..."): speak_text(txt, tts_lang, f"transcript_{lang}.mp3", autoplay=True)
            if len(st.session_state.transcript)>1:
                with st.expander(f"History ({len(st.session_state.transcript)})"):
                    for it in reversed(st.session_state.transcript[-8:]):
                        st.markdown(f'<div style="background:rgba(30,41,59,0.7); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:8px; margin-bottom:6px"><b style="color:#F8FAFC">{it["sign"].replace("_"," ").title()}</b> — <span style="color:#F8FAFC; font-family:{font}">{it["text"]}</span><br><span class="small">{it["ts"]} • {it["conf"]*100:.0f}%</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:rgba(11,15,25,0.6); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:20px; text-align:center; color:#94A3B8">No translation yet</div>', unsafe_allow_html=True)
    # Quick Clinical Prompts — one source language, then exactly one translation.
    st.markdown(f'<div style="color:#F8FAFC; font-weight:700">⚡ {t("quick")}</div>', unsafe_allow_html=True)
    fixed_prompts = {
        "English": ["Where does it hurt?", "Do you need water?", "What is your pain level from 1 to 10?", "Shall I call the doctor?"],
        "Hindi": ["कहाँ दर्द हो रहा है?", "क्या आपको पानी चाहिए?", "दर्द 1 से 10 में कितना है?", "क्या मैं डॉक्टर को बुलाऊँ?"],
        "Odia": ["କେଉଁଠି ଯନ୍ତ୍ରଣା ହେଉଛି?", "ଆପଣଙ୍କୁ ପାଣି ଦରକାର କି?", "ଆପଣଙ୍କ ଯନ୍ତ୍ରଣା ୧ ରୁ ୧୦ ମଧ୍ୟରେ କେତେ?", "ମୁଁ ଡାକ୍ତରଙ୍କୁ ଡାକିବି କି?"]
    }
    source_prompts = ["Where does it hurt?", "Do you need water?", "What is your pain level from 1 to 10?", "Shall I call the doctor?"]
    lang = st.session_state.app_lang
    prompt_labels = fixed_prompts[lang] if lang in fixed_prompts else [translate_doctor(x, lang) for x in source_prompts]
    cols = st.columns(4)
    for i, label in enumerate(prompt_labels):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"clinical_prompt_{lang}_{i}"):
                tts_lang = lang if lang in VOICE_MAP else "English"
                with st.spinner("Speaking..."):
                    speak_text(label, tts_lang, f"prompt_{lang}_{i}.mp3", autoplay=True)

# ============================================================
# Doctor's Console — Bi-Directional (full width bottom)
# ============================================================
st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
with st.container(border=True):
    st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center"><div><b style="color:#F8FAFC; font-size:16px">👨‍⚕️ {t("doctor_title")}</b><div class="small">{t("doctor_sub")} • Selected patient lang: <b style="color:#F8FAFC">{st.session_state.app_lang} ({FONT_MAP[st.session_state.app_lang]})</b></div></div><span class="badge-live">● BI-DIRECTIONAL</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    dr_text=st.text_area(t("doctor_ph"), value=st.session_state.doctor_text, placeholder="Type clinical advice…", height=90, label_visibility="collapsed", key="doctor_box")
    st.session_state.doctor_text=dr_text
    # live translation preview
    if dr_text.strip():
        translated=translate_doctor(dr_text, st.session_state.app_lang)
        st.markdown(f'<div style="background:rgba(11,15,25,0.6); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:12px"><div class="small">Translated to {st.session_state.app_lang} • <span style="font-family:{font}">{translated}</span></div></div>', unsafe_allow_html=True)
        # auto-translate + speak button
        c1,c2,c3=st.columns([2,1,1])
        with c1:
            if st.button(f'{t("speak_patient")}', type="primary", use_container_width=True, key="dr_speak_main"):
                lang=st.session_state.app_lang; tts_lang=lang if lang in VOICE_MAP else "English"
                # translate first
                out_text=translate_doctor(dr_text, lang) if lang not in ["English","Hindi"] else (translate_doctor(dr_text, lang) if lang!="English" else dr_text)
                # if Hindi/English we already have voice, but ensure translation
                if lang=="Hindi" and dr_text.strip().isascii():
                    out_text=translate_doctor(dr_text, "Hindi")
                with st.spinner(f"Speaking {lang}..."):
                    speak_text(out_text, tts_lang, f"doctor_{lang}.mp3", autoplay=True)
                st.toast(f"Spoke to patient in {lang}")
        with c2:
            if st.button("🧹 Clear", use_container_width=True, key="dr_clear2"):
                st.session_state.doctor_text=""; st.rerun()
        with c3:
            if st.button("📋 Copy", use_container_width=True):
                st.toast("Copied")
    else:
        st.caption("Type above — live translation appears here")

# footer
st.markdown('<div style="text-align:center; color:#334155; font-size:11px; margin-top:10px">BHASA SETU • Integrated • Bi-Directional • Auto 🔊 • High Contrast</div>', unsafe_allow_html=True)
