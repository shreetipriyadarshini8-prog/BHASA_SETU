import csv
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

output_file = os.path.join(PROJECT_ROOT, "isl_verification_60.csv")

phrases = [
    ("P001","fever","I have a fever","मुझे बुखार है","ମୋତେ ଜ୍ୱର ହୋଇଛି"),
    ("P002","headache","I have a headache","मुझे सिरदर्द है","ମୋର ମୁଣ୍ଡ ବିନ୍ଧୁଛି"),
    ("P003","cough","I have a cough","मुझे खांसी है","ମୋତେ କାଶ ହେଉଛି"),
    ("P004","dizzy","I feel dizzy","मुझे चक्कर आ रहा है","ମୋତେ ମୁଣ୍ଡ ବୁଲାଉଛି"),
    ("P005","cold","I have a cold","मुझे सर्दी है","ମୋତେ ଥଣ୍ଡା ହୋଇଛି"),
    ("P006","shivering","I am shivering","मुझे कंपकंपी हो रही है","ମୋତେ ଥରଥର ଲାଗୁଛି"),
    ("P007","weak","I feel weak","मुझे कमजोरी महसूस हो रही है","ମୋତେ ଦୁର୍ବଳ ଲାଗୁଛି"),
    ("P008","tired","I feel tired","मुझे थकान महसूस हो रही है","ମୋତେ ଥକା ଲାଗୁଛି"),
    ("P009","very_sick","I feel very sick","मुझे बहुत बीमार महसूस हो रहा है","ମୋତେ ବହୁତ ଅସୁସ୍ଥ ଲାଗୁଛି"),

    ("P010","stomach_pain","I have stomach pain","मेरे पेट में दर्द है","ମୋ ପେଟରେ ବ୍ୟଥା ହେଉଛି"),
    ("P011","chest_pain","I have chest pain","मेरे सीने में दर्द है","ମୋ ଛାତିରେ ବ୍ୟଥା ହେଉଛି"),
    ("P012","body_pain","I have body pain","मेरे शरीर में दर्द है","ମୋ ଦେହରେ ବ୍ୟଥା ହେଉଛି"),
    ("P013","back_pain","I have back pain","मेरी पीठ में दर्द है","ମୋ ପିଠିରେ ବ୍ୟଥା ହେଉଛି"),
    ("P014","neck_pain","I have neck pain","मेरी गर्दन में दर्द है","ମୋ ବେକରେ ବ୍ୟଥା ହେଉଛି"),
    ("P015","joint_pain","I have joint pain","मेरे जोड़ों में दर्द है","ମୋ ଗଣ୍ଠିରେ ବ୍ୟଥା ହେଉଛି"),
    ("P016","toothache","I have a toothache","मेरे दांत में दर्द है","ମୋ ଦାନ୍ତରେ ବ୍ୟଥା ହେଉଛି"),
    ("P017","eye_pain","My eyes hurt","मेरी आँखों में दर्द है","ମୋ ଆଖିରେ ବ୍ୟଥା ହେଉଛି"),
    ("P018","ear_pain","My ears hurt","मेरे कान में दर्द है","ମୋ କାନରେ ବ୍ୟଥା ହେଉଛି"),
    ("P019","throat_pain","My throat hurts","मेरे गले में दर्द है","ମୋ ଗଳାରେ ବ୍ୟଥା ହେଉଛି"),

    ("P020","vomiting","I feel like vomiting","मुझे उल्टी जैसा लग रहा है","ମୋତେ ବାନ୍ତି ଲାଗୁଛି"),
    ("P021","diarrhea","I have diarrhea","मुझे दस्त हो रहे हैं","ମୋତେ ଝାଡ଼ା ହେଉଛି"),
    ("P022","sore_throat","I have a sore throat","मेरे गले में दर्द है","ମୋ ଗଳାରେ ବ୍ୟଥା ହେଉଛି"),
    ("P023","runny_nose","I have a runny nose","मेरी नाक बह रही है","ମୋ ନାକରୁ ପାଣି ବାହାରୁଛି"),
    ("P024","breathing_difficulty","I have difficulty breathing","मुझे सांस लेने में कठिनाई हो रही है","ମୋତେ ନିଶ୍ୱାସ ନେବାରେ କଷ୍ଟ ହେଉଛି"),
    ("P025","cannot_breathe","I cannot breathe properly","मैं ठीक से सांस नहीं ले पा रहा हूँ","ମୁଁ ଠିକ୍ ଭାବରେ ନିଶ୍ୱାସ ନେଇ ପାରୁନାହିଁ"),

    ("P026","hurts_here","It hurts here","यहाँ दर्द हो रहा है","ଏଠାରେ ବ୍ୟଥା ହେଉଛି"),
    ("P027","mild_pain","The pain is mild","हल्का दर्द है","ବ୍ୟଥା ହାଲୁକା ଅଟେ"),
    ("P028","severe_pain","I am having severe pain","मुझे बहुत तेज दर्द हो रहा है","ମୋତେ ବହୁତ ତୀବ୍ର ବ୍ୟଥା ହେଉଛି"),
    ("P029","constant_pain","The pain is constant","दर्द लगातार हो रहा है","ବ୍ୟଥା ଲଗାତାର ହେଉଛି"),
    ("P030","comes_and_goes","The pain comes and goes","दर्द आता-जाता रहता है","ବ୍ୟଥା ଆସୁଛି ଓ ଯାଉଛି"),
    ("P031","started_today","It started today","यह आज शुरू हुआ है","ଏହା ଆଜି ଆରମ୍ଭ ହୋଇଛି"),
    ("P032","started_yesterday","It started yesterday","यह कल शुरू हुआ है","ଏହା ଗତକାଲି ଆରମ୍ଭ ହୋଇଛି"),
    ("P033","started_two_days_ago","It started two days ago","यह दो दिन पहले शुरू हुआ है","ଏହା ଦୁଇ ଦିନ ପୂର୍ବରୁ ଆରମ୍ଭ ହୋଇଛି"),
    ("P034","one_week","I have had this for a week","मुझे यह समस्या एक सप्ताह से है","ମୋତେ ଏହି ସମସ୍ୟା ଏକ ସପ୍ତାହ ହେଲାଣି"),
    ("P035","getting_worse","It is getting worse","यह और खराब हो रहा है","ଏହା ଆହୁରି ଖରାପ ହେଉଛି"),
    ("P036","getting_better","It is getting better","यह बेहतर हो रहा है","ଏହା ଭଲ ହେଉଛି"),
    ("P037","started_suddenly","It started suddenly","यह अचानक शुरू हुआ","ଏହା ହଠାତ୍ ଆରମ୍ଭ ହେଲା"),
    ("P038","started_slowly","It started slowly","यह धीरे-धीरे शुरू हुआ","ଏହା ଧୀରେ ଧୀରେ ଆରମ୍ଭ ହେଲା"),

    ("P039","taking_medicine","I am taking medicine","मैं दवा ले रहा हूँ","ମୁଁ ଔଷଧ ଖାଉଛି"),
    ("P040","daily_medicine","I take this medicine every day","मैं यह दवा हर दिन लेता हूँ","ମୁଁ ଏହି ଔଷଧ ପ୍ରତିଦିନ ଖାଏ"),
    ("P041","need_medicine","I need my medicine","मुझे अपनी दवा चाहिए","ମୋତେ ମୋ ଔଷଧ ଦରକାର"),
    ("P042","lost_medicine","I lost my medicine","मेरी दवा खो गई है","ମୋ ଔଷଧ ହଜିଯାଇଛି"),
    ("P043","medicine_allergy","I am allergic to medicine","मुझे दवा से एलर्जी है","ମୋତେ ଔଷଧରେ ଆଲର୍ଜି ହୁଏ"),
    ("P044","food_allergy","I am allergic to food","मुझे कुछ खाने की चीजों से एलर्जी है","ମୋତେ କିଛି ଖାଦ୍ୟରେ ଆଲର୍ଜି ହୁଏ"),
    ("P045","diabetes","I have diabetes","मुझे मधुमेह है","ମୋତେ ମଧୁମେହ ଅଛି"),
    ("P046","high_blood_pressure","I have high blood pressure","मुझे उच्च रक्तचाप है","ମୋର ଉଚ୍ଚ ରକ୍ତଚାପ ଅଛି"),
    ("P047","problem_before","I have had this problem before","मुझे पहले भी यह समस्या हुई है","ମୋତେ ପୂର୍ବରୁ ମଧ୍ୟ ଏହି ସମସ୍ୟା ହୋଇଛି"),
    ("P048","operation_before","I had an operation before","मेरा पहले ऑपरेशन हुआ था","ମୋର ପୂର୍ବରୁ ଅପରେସନ ହୋଇଥିଲା"),
    ("P049","pregnant","I am pregnant","मैं गर्भवती हूँ","ମୁଁ ଗର୍ଭବତୀ ଅଛି"),

    ("P050","doctor","I need a doctor","मुझे डॉक्टर चाहिए","ମୋତେ ଡାକ୍ତର ଦରକାର"),
    ("P051","need_doctor","I need to see a doctor","मुझे डॉक्टर को दिखाना है","ମୋତେ ଡାକ୍ତରଙ୍କୁ ଦେଖାଇବାକୁ ପଡିବ"),
    ("P052","help","Please help me","कृपया मेरी मदद करें","ଦୟାକରି ମୋତେ ସାହାଯ୍ୟ କରନ୍ତୁ"),
    ("P053","need_help","I need help","मुझे मदद चाहिए","ମୋତେ ସାହାଯ୍ୟ ଦରକାର"),
    ("P054","call_doctor","Please call a doctor","कृपया डॉक्टर को बुलाइए","ଦୟାକରି ଡାକ୍ତରଙ୍କୁ ଡାକନ୍ତୁ"),
    ("P055","water","I need water","मुझे पानी चाहिए","ମୋତେ ପାଣି ଦରକାର"),
    ("P056","call_ambulance","Please call an ambulance","कृपया एम्बुलेंस बुलाइए","ଦୟାକରି ଆମ୍ବୁଲାନ୍ସ ଡାକନ୍ତୁ"),
    ("P057","bleeding","I am bleeding","मुझे खून बह रहा है","ମୋ ଦେହରୁ ରକ୍ତ ବାହାରୁଛି"),
    ("P058","fainted","I fainted","मैं बेहोश हो गया था","ମୁଁ ବେହୋସ ହୋଇଯାଇଥିଲି"),
    ("P059","emergency_help","I need emergency help","मुझे तुरंत मदद चाहिए","ମୋତେ ତୁରନ୍ତ ସାହାଯ୍ୟ ଦରକାର"),
    ("P060","take_to_hospital","Please take me to the hospital","कृपया मुझे अस्पताल ले जाइए","ଦୟାକରି ମୋତେ ହସ୍ପିଟାଲ ନେଇଯାଆନ୍ତୁ")
]

os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)

    writer.writerow([
        "phrase_id",
        "phrase_key",
        "english",
        "hindi",
        "odia",
        "best_isl_sign",
        "video_url",
        "match_type",
        "status",
        "notes"
    ])

    for phrase in phrases:
        writer.writerow(list(phrase) + ["", "", "", "Pending", ""])

print("=" * 50)
print("BHASA SETU — VERIFICATION FILE")
print("=" * 50)
print(f"Total phrases: {len(phrases)}")
print(f"Created: {output_file}")
print("=" * 50)