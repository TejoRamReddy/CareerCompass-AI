"""
CareerCompass AI — career dataset.

26 careers across three streams. Each career carries:
  vec       : 12 skill dimensions scored 0-5 (what the work demands)
  academic  : which school subjects actually predict success, weighted 0-1
  name_ta   : Tamil name
  blurb_ta  : Tamil description

The skill vectors are hand-scored approximations built for this project.
They are not a validated psychometric instrument, and the app says so.
"""

# Skill dimensions, in order. Every vector in this file follows this order.
DIMS = ["coding", "math", "science", "design", "communication", "business",
        "leadership", "empathy", "writing", "research", "handsOn", "creativity"]

DIM_LABELS = {
    "coding": "Coding", "math": "Math", "science": "Science", "design": "Design",
    "communication": "Communication", "business": "Business sense",
    "leadership": "Leadership", "empathy": "Empathy", "writing": "Writing",
    "research": "Research", "handsOn": "Hands-on building", "creativity": "Creativity",
}

DIM_LABELS_TA = {
    "coding": "நிரலாக்கம்", "math": "கணிதம்", "science": "அறிவியல்",
    "design": "வடிவமைப்பு", "communication": "தொடர்பாடல்", "business": "வணிக அறிவு",
    "leadership": "தலைமைத்துவம்", "empathy": "பரிவுணர்வு", "writing": "எழுத்து",
    "research": "ஆராய்ச்சி", "handsOn": "நேரடிப் பணி", "creativity": "படைப்பாற்றல்",
}

# Academic subjects collected at sign-up / profile time (marks out of 100).
ACADEMIC_SUBJECTS = ["math", "science", "language", "social", "computer"]

ACADEMIC_LABELS = {
    "math": "Mathematics", "science": "Science (Physics / Chemistry / Biology)",
    "language": "English / Language", "social": "Social science",
    "computer": "Computer science",
}

ACADEMIC_LABELS_TA = {
    "math": "கணிதம்", "science": "அறிவியல் (இயற்பியல் / வேதியியல் / உயிரியல்)",
    "language": "ஆங்கிலம் / மொழி", "social": "சமூக அறிவியல்",
    "computer": "கணினி அறிவியல்",
}

CATEGORIES_TA = {
    "Tech & Engineering": "தொழில்நுட்பம் & பொறியியல்",
    "Business, Law & Government": "வணிகம், சட்டம் & அரசு",
    "Medicine, Science & Creative": "மருத்துவம், அறிவியல் & படைப்பாற்றல்",
}

CAREERS = [
    # ---------------------------------------------------- Tech & Engineering --
    {"name": "Data Scientist", "category": "Tech & Engineering",
     "blurb": "Finds patterns in data to help organisations make better decisions.",
     "name_ta": "தரவு அறிவியலாளர்",
     "blurb_ta": "தரவுகளில் உள்ள வடிவங்களைக் கண்டறிந்து சிறந்த முடிவுகள் எடுக்க உதவுபவர்.",
     "vec": [5, 5, 2, 1, 2, 2, 1, 1, 1, 4, 1, 2],
     "academic": {"math": 1.0, "computer": 0.8, "science": 0.4, "language": 0.3, "social": 0.1}},
    {"name": "AI Engineer", "category": "Tech & Engineering",
     "blurb": "Builds and ships machine-learning systems into real products.",
     "name_ta": "செயற்கை நுண்ணறிவு பொறியாளர்",
     "blurb_ta": "இயந்திரக் கற்றல் அமைப்புகளை உருவாக்கி நிஜப் பயன்பாடுகளில் இணைப்பவர்.",
     "vec": [5, 5, 2, 1, 2, 1, 1, 1, 1, 4, 2, 3],
     "academic": {"math": 1.0, "computer": 1.0, "science": 0.4, "language": 0.2, "social": 0.1}},
    {"name": "Backend Developer", "category": "Tech & Engineering",
     "blurb": "Designs the systems and APIs that power apps behind the scenes.",
     "name_ta": "பின்தள மென்பொருள் உருவாக்குநர்",
     "blurb_ta": "செயலிகளை இயக்கும் பின்புல அமைப்புகளையும் APIகளையும் வடிவமைப்பவர்.",
     "vec": [5, 3, 1, 1, 2, 1, 1, 1, 1, 2, 3, 2],
     "academic": {"math": 0.6, "computer": 1.0, "science": 0.2, "language": 0.3, "social": 0.1}},
    {"name": "Cloud Engineer", "category": "Tech & Engineering",
     "blurb": "Keeps applications running reliably on scalable infrastructure.",
     "name_ta": "கிளவுட் பொறியாளர்",
     "blurb_ta": "செயலிகள் தடையின்றி இயங்க கிளவுட் உள்கட்டமைப்பை நிர்வகிப்பவர்.",
     "vec": [4, 3, 1, 1, 2, 2, 1, 1, 1, 2, 4, 1],
     "academic": {"math": 0.5, "computer": 1.0, "science": 0.2, "language": 0.3, "social": 0.1}},
    {"name": "Cybersecurity Analyst", "category": "Tech & Engineering",
     "blurb": "Finds and closes the gaps attackers would use against a system.",
     "name_ta": "இணையப் பாதுகாப்பு ஆய்வாளர்",
     "blurb_ta": "அமைப்புகளில் உள்ள பாதுகாப்பு ஓட்டைகளைக் கண்டறிந்து அடைப்பவர்.",
     "vec": [4, 3, 2, 1, 2, 1, 1, 1, 1, 3, 2, 2],
     "academic": {"math": 0.6, "computer": 1.0, "science": 0.3, "language": 0.3, "social": 0.2}},
    {"name": "Mechanical Engineer", "category": "Tech & Engineering",
     "blurb": "Designs and builds physical machines and mechanical systems.",
     "name_ta": "இயந்திரப் பொறியாளர்",
     "blurb_ta": "இயந்திரங்களையும் இயந்திர அமைப்புகளையும் வடிவமைத்து உருவாக்குபவர்.",
     "vec": [2, 4, 3, 2, 2, 1, 2, 1, 1, 2, 5, 3],
     "academic": {"math": 0.9, "science": 0.9, "computer": 0.3, "language": 0.2, "social": 0.1}},
    {"name": "Civil Engineer", "category": "Tech & Engineering",
     "blurb": "Plans and builds the infrastructure people rely on every day.",
     "name_ta": "கட்டுமானப் பொறியாளர்",
     "blurb_ta": "மக்கள் தினமும் நம்பியிருக்கும் உள்கட்டமைப்பை திட்டமிட்டு கட்டுபவர்.",
     "vec": [1, 4, 3, 2, 3, 2, 2, 2, 1, 2, 5, 2],
     "academic": {"math": 0.9, "science": 0.8, "computer": 0.2, "language": 0.3, "social": 0.2}},
    {"name": "Electrical Engineer", "category": "Tech & Engineering",
     "blurb": "Designs power and electrical systems for buildings and machines.",
     "name_ta": "மின் பொறியாளர்",
     "blurb_ta": "கட்டிடங்கள், இயந்திரங்களுக்கான மின் அமைப்புகளை வடிவமைப்பவர்.",
     "vec": [3, 4, 3, 1, 2, 1, 1, 1, 1, 2, 5, 2],
     "academic": {"math": 0.9, "science": 0.9, "computer": 0.4, "language": 0.2, "social": 0.1}},
    {"name": "Electronics Engineer", "category": "Tech & Engineering",
     "blurb": "Designs the circuits and hardware inside everyday devices.",
     "name_ta": "மின்னணுப் பொறியாளர்",
     "blurb_ta": "அன்றாட சாதனங்களுக்குள் இருக்கும் சுற்றுகளையும் வன்பொருளையும் வடிவமைப்பவர்.",
     "vec": [3, 4, 3, 1, 2, 1, 1, 1, 1, 3, 5, 2],
     "academic": {"math": 0.9, "science": 0.9, "computer": 0.5, "language": 0.2, "social": 0.1}},
    {"name": "UI/UX Designer", "category": "Tech & Engineering",
     "blurb": "Shapes how digital products look, feel, and work for real people.",
     "name_ta": "பயனர் அனுபவ வடிவமைப்பாளர்",
     "blurb_ta": "டிஜிட்டல் தயாரிப்புகள் மக்களுக்கு எப்படித் தோன்றும், இயங்கும் என வடிவமைப்பவர்.",
     "vec": [3, 1, 1, 5, 3, 2, 2, 3, 2, 2, 1, 5],
     "academic": {"math": 0.3, "computer": 0.6, "science": 0.2, "language": 0.6, "social": 0.4}},

    # -------------------------------------------- Business, Law & Government --
    {"name": "Chartered Accountant", "category": "Business, Law & Government",
     "blurb": "Keeps organisations financially accurate, compliant, and honest.",
     "name_ta": "பட்டயக் கணக்காளர்",
     "blurb_ta": "நிறுவனங்களின் கணக்குகளைத் துல்லியமாகவும் விதிமுறைப்படியும் பராமரிப்பவர்.",
     "vec": [1, 5, 1, 1, 2, 4, 2, 1, 1, 2, 1, 1],
     "academic": {"math": 1.0, "social": 0.5, "language": 0.4, "computer": 0.3, "science": 0.1}},
    {"name": "Marketing Manager", "category": "Business, Law & Government",
     "blurb": "Shapes how people discover and feel about a product or brand.",
     "name_ta": "சந்தைப்படுத்தல் மேலாளர்",
     "blurb_ta": "ஒரு தயாரிப்பை மக்கள் எப்படி அறிகிறார்கள், உணர்கிறார்கள் என்பதை வடிவமைப்பவர்.",
     "vec": [1, 2, 1, 3, 4, 4, 3, 3, 3, 2, 1, 4],
     "academic": {"math": 0.4, "language": 0.8, "social": 0.7, "computer": 0.3, "science": 0.1}},
    {"name": "HR Manager", "category": "Business, Law & Government",
     "blurb": "Builds the systems and culture that help people do their best work.",
     "name_ta": "மனிதவள மேலாளர்",
     "blurb_ta": "பணியாளர்கள் சிறப்பாகச் செயல்பட உதவும் அமைப்பையும் பண்பாட்டையும் உருவாக்குபவர்.",
     "vec": [1, 1, 1, 1, 4, 3, 3, 5, 2, 1, 1, 2],
     "academic": {"math": 0.3, "language": 0.8, "social": 0.8, "computer": 0.2, "science": 0.1}},
    {"name": "Entrepreneur", "category": "Business, Law & Government",
     "blurb": "Builds a business from an idea, taking on risk to solve a real problem.",
     "name_ta": "தொழில்முனைவோர்",
     "blurb_ta": "ஒரு யோசனையிலிருந்து நிறுவனத்தை உருவாக்கி, அபாயத்தை ஏற்று சிக்கலைத் தீர்ப்பவர்.",
     "vec": [2, 2, 1, 2, 4, 5, 5, 3, 2, 2, 2, 4],
     "academic": {"math": 0.5, "language": 0.6, "social": 0.6, "computer": 0.4, "science": 0.2}},
    {"name": "Financial Analyst", "category": "Business, Law & Government",
     "blurb": "Studies numbers to guide investment and business decisions.",
     "name_ta": "நிதி ஆய்வாளர்",
     "blurb_ta": "எண்களை ஆய்வு செய்து முதலீடு மற்றும் வணிக முடிவுகளுக்கு வழிகாட்டுபவர்.",
     "vec": [1, 5, 1, 1, 3, 5, 2, 1, 1, 3, 1, 1],
     "academic": {"math": 1.0, "social": 0.5, "language": 0.4, "computer": 0.4, "science": 0.1}},
    {"name": "Lawyer", "category": "Business, Law & Government",
     "blurb": "Argues cases and advises people on their rights and obligations.",
     "name_ta": "வழக்கறிஞர்",
     "blurb_ta": "வழக்குகளை வாதிட்டு, உரிமைகள் குறித்து மக்களுக்கு ஆலோசனை வழங்குபவர்.",
     "vec": [1, 2, 1, 1, 5, 3, 3, 2, 4, 4, 1, 2],
     "academic": {"math": 0.2, "language": 1.0, "social": 0.9, "computer": 0.1, "science": 0.1}},
    {"name": "Civil Services Officer", "category": "Business, Law & Government",
     "blurb": "Administers public policy and serves citizens through government.",
     "name_ta": "அரசுப் பணி அதிகாரி",
     "blurb_ta": "பொதுக் கொள்கைகளை நிர்வகித்து அரசு வழியாக மக்களுக்குச் சேவை செய்பவர்.",
     "vec": [1, 3, 2, 1, 5, 3, 4, 4, 3, 3, 1, 2],
     "academic": {"math": 0.4, "language": 0.9, "social": 1.0, "computer": 0.2, "science": 0.3}},
    {"name": "Policy Analyst", "category": "Business, Law & Government",
     "blurb": "Researches issues and shapes recommendations for public policy.",
     "name_ta": "கொள்கை ஆய்வாளர்",
     "blurb_ta": "பிரச்சினைகளை ஆராய்ந்து பொதுக் கொள்கைக்கான பரிந்துரைகளை உருவாக்குபவர்.",
     "vec": [1, 3, 2, 1, 4, 4, 3, 3, 3, 5, 1, 2],
     "academic": {"math": 0.5, "language": 0.8, "social": 1.0, "computer": 0.2, "science": 0.3}},

    # ------------------------------------------ Medicine, Science & Creative --
    {"name": "Doctor", "category": "Medicine, Science & Creative",
     "blurb": "Diagnoses and treats patients, often under real time pressure.",
     "name_ta": "மருத்துவர்",
     "blurb_ta": "நோயாளிகளைப் பரிசோதித்து சிகிச்சை அளிப்பவர், பெரும்பாலும் நேர அழுத்தத்தில்.",
     "vec": [1, 3, 5, 1, 4, 1, 3, 5, 2, 3, 3, 2],
     "academic": {"math": 0.4, "science": 1.0, "language": 0.5, "social": 0.3, "computer": 0.1}},
    {"name": "Biotechnologist", "category": "Medicine, Science & Creative",
     "blurb": "Applies biology in labs to develop new treatments and products.",
     "name_ta": "உயிரிதொழில்நுட்ப வல்லுநர்",
     "blurb_ta": "ஆய்வகத்தில் உயிரியலைப் பயன்படுத்தி புதிய சிகிச்சைகளை உருவாக்குபவர்.",
     "vec": [1, 3, 5, 1, 2, 1, 1, 1, 1, 5, 3, 2],
     "academic": {"math": 0.5, "science": 1.0, "language": 0.3, "social": 0.1, "computer": 0.3}},
    {"name": "Pharmacist", "category": "Medicine, Science & Creative",
     "blurb": "Ensures people get and understand the medicines they need.",
     "name_ta": "மருந்தாளுநர்",
     "blurb_ta": "தேவையான மருந்துகளை மக்கள் சரியாகப் பெற்று புரிந்துகொள்ள உதவுபவர்.",
     "vec": [1, 3, 5, 1, 3, 2, 1, 3, 1, 3, 3, 1],
     "academic": {"math": 0.4, "science": 1.0, "language": 0.4, "social": 0.2, "computer": 0.1}},
    {"name": "Research Scientist", "category": "Medicine, Science & Creative",
     "blurb": "Runs experiments to answer open questions in a field.",
     "name_ta": "ஆராய்ச்சி விஞ்ஞானி",
     "blurb_ta": "ஒரு துறையின் தீராத கேள்விகளுக்குப் பரிசோதனைகள் மூலம் பதில் தேடுபவர்.",
     "vec": [2, 4, 5, 1, 2, 1, 1, 1, 2, 5, 2, 2],
     "academic": {"math": 0.8, "science": 1.0, "language": 0.4, "social": 0.1, "computer": 0.4}},
    {"name": "Psychologist", "category": "Medicine, Science & Creative",
     "blurb": "Helps people understand and improve their mental well-being.",
     "name_ta": "உளவியலாளர்",
     "blurb_ta": "மன நலனைப் புரிந்துகொண்டு மேம்படுத்த மக்களுக்கு உதவுபவர்.",
     "vec": [1, 1, 2, 1, 5, 1, 2, 5, 3, 4, 1, 2],
     "academic": {"math": 0.3, "science": 0.5, "language": 0.8, "social": 0.9, "computer": 0.1}},
    {"name": "Graphic Designer", "category": "Medicine, Science & Creative",
     "blurb": "Turns ideas into visuals that communicate clearly and look good.",
     "name_ta": "வரைகலை வடிவமைப்பாளர்",
     "blurb_ta": "யோசனைகளைத் தெளிவாகவும் அழகாகவும் தொடர்பு கொள்ளும் காட்சிகளாக மாற்றுபவர்.",
     "vec": [1, 1, 1, 5, 3, 2, 1, 2, 2, 1, 1, 5],
     "academic": {"math": 0.2, "language": 0.5, "social": 0.3, "computer": 0.5, "science": 0.1}},
    {"name": "Content Writer", "category": "Medicine, Science & Creative",
     "blurb": "Turns ideas into words that inform, persuade, or entertain.",
     "name_ta": "உள்ளடக்க எழுத்தாளர்",
     "blurb_ta": "யோசனைகளைத் தகவல் தரும், நம்ப வைக்கும் வார்த்தைகளாக மாற்றுபவர்.",
     "vec": [1, 1, 1, 2, 3, 2, 1, 2, 5, 3, 1, 4],
     "academic": {"math": 0.1, "language": 1.0, "social": 0.6, "computer": 0.3, "science": 0.1}},
    {"name": "Animator", "category": "Medicine, Science & Creative",
     "blurb": "Brings characters and stories to life frame by frame.",
     "name_ta": "அசைவூட்டக் கலைஞர்",
     "blurb_ta": "கதாபாத்திரங்களையும் கதைகளையும் சட்டம் சட்டமாக உயிர்ப்பிப்பவர்.",
     "vec": [2, 1, 1, 5, 2, 1, 1, 2, 1, 1, 2, 5],
     "academic": {"math": 0.3, "language": 0.4, "social": 0.2, "computer": 0.6, "science": 0.1}},
]

assert len(CAREERS) == 26, "The deck and the site both say 26 careers — keep them in sync."

# Two concrete, doable learning actions per skill — used to build the roadmap.
SKILL_ACTIONS = {
    "coding": ["Build two small coding projects, like a to-do app or a simple game.",
               "Work through a free Python or JavaScript fundamentals course."],
    "math": ["Revise class 10–12 statistics and probability basics.",
             "Practice applied math problems for 20 minutes a few times a week."],
    "science": ["Take a free intro course in the relevant science subject.",
                "Do one small experiment or science project outside class."],
    "design": ["Learn Figma basics and redesign a screen from an app you use daily.",
               "Study five well-designed apps and note what makes them work."],
    "communication": ["Join a debate or public-speaking club for a term.",
                      "Practice explaining a technical topic to someone outside your field."],
    "business": ["Read one short business case study each week.",
                 "Try running a tiny side project or sale to learn the basics."],
    "leadership": ["Lead a small group project or club activity this term.",
                   "Take the initiative on one team assignment at college."],
    "empathy": ["Mentor or tutor a junior student for a few weeks.",
                "Practice active listening in everyday conversations."],
    "writing": ["Write one short article or blog post every two weeks.",
                "Get feedback on a piece of writing from a mentor or teacher."],
    "research": ["Read two articles or papers in a field you're curious about.",
                 "Run one small independent research project this term."],
    "handsOn": ["Build or repair something with your hands this month.",
                "Join a maker space, lab, or hands-on workshop."],
    "creativity": ["Keep a sketchbook or idea journal for two weeks.",
                   "Try one creative project outside your usual comfort zone."],
}

SKILL_ACTIONS_TA = {
    "coding": ["ஒரு To-do செயலி அல்லது எளிய விளையாட்டு போன்ற இரண்டு சிறிய திட்டங்களை உருவாக்குங்கள்.",
               "இலவச Python அல்லது JavaScript அடிப்படைப் பாடத்தை முடியுங்கள்."],
    "math": ["10–12ஆம் வகுப்பு புள்ளியியல், நிகழ்தகவு அடிப்படைகளைத் திரும்பப் படியுங்கள்.",
             "வாரத்தில் சில நாட்கள் 20 நிமிடம் கணிதப் பயிற்சி செய்யுங்கள்."],
    "science": ["சம்பந்தப்பட்ட அறிவியல் பாடத்தில் ஒரு இலவச அறிமுகப் பாடம் எடுங்கள்.",
                "வகுப்புக்கு வெளியே ஒரு சிறிய அறிவியல் பரிசோதனை செய்யுங்கள்."],
    "design": ["Figma அடிப்படைகளைக் கற்று, நீங்கள் தினமும் பயன்படுத்தும் செயலியின் ஒரு திரையை மறுவடிவமைப்பு செய்யுங்கள்.",
               "நன்கு வடிவமைக்கப்பட்ட ஐந்து செயலிகளை ஆராய்ந்து குறிப்பெடுங்கள்."],
    "communication": ["ஒரு பருவத்திற்கு பட்டிமன்றம் அல்லது பேச்சுக் கழகத்தில் சேருங்கள்.",
                      "ஒரு தொழில்நுட்பத் தலைப்பை வெளியாள் ஒருவருக்கு விளக்கிப் பழகுங்கள்."],
    "business": ["வாரத்திற்கு ஒரு சிறிய வணிக வழக்காய்வு படியுங்கள்.",
                 "ஒரு சிறு பக்கத் தொழில் அல்லது விற்பனையை முயற்சியுங்கள்."],
    "leadership": ["இந்தப் பருவத்தில் ஒரு சிறு குழுத் திட்டத்திற்குத் தலைமை ஏற்றுங்கள்.",
                   "ஒரு குழுப் பணியில் முன்முயற்சி எடுங்கள்."],
    "empathy": ["சில வாரங்களுக்கு ஒரு இளைய மாணவருக்கு வழிகாட்டுங்கள்.",
                "அன்றாட உரையாடல்களில் கவனமாகக் கேட்கப் பழகுங்கள்."],
    "writing": ["இரு வாரங்களுக்கு ஒரு முறை ஒரு சிறு கட்டுரை எழுதுங்கள்.",
                "உங்கள் எழுத்துக்கு ஆசிரியர் அல்லது வழிகாட்டியிடம் கருத்து பெறுங்கள்."],
    "research": ["நீங்கள் ஆர்வமுள்ள துறையில் இரண்டு கட்டுரைகளைப் படியுங்கள்.",
                 "இந்தப் பருவத்தில் ஒரு சிறு சுயாதீன ஆய்வு செய்யுங்கள்."],
    "handsOn": ["இந்த மாதம் ஏதாவது ஒன்றை உங்கள் கையால் செய்யுங்கள் அல்லது சரிசெய்யுங்கள்.",
                "ஒரு பட்டறை அல்லது ஆய்வகச் செயல்பாட்டில் சேருங்கள்."],
    "creativity": ["இரு வாரங்களுக்கு ஒரு ஓவியம்/யோசனைக் குறிப்பேடு வைத்திருங்கள்.",
                   "உங்கள் வழக்கத்திற்கு வெளியே ஒரு படைப்புத் திட்டம் முயலுங்கள்."],
}

# ---------------------------------------------------------------------------
# Fallback interview question bank.
#
# Used when no Gemini key is configured, or when Gemini is unreachable. Keeps
# the product usable offline and in a demo hall with no internet, and keeps
# the answers deterministic for tests.
# ---------------------------------------------------------------------------

FALLBACK_QUESTIONS = [
    {"id": "subjects",
     "en": "Tell me a little about yourself — which subjects do you actually enjoy, and why?",
     "ta": "உங்களைப் பற்றிச் சிறிது சொல்லுங்கள் — எந்தப் பாடங்கள் உங்களுக்குப் பிடிக்கும், ஏன்?"},
    {"id": "activities",
     "en": "Outside class, what do you find yourself doing for hours without noticing?",
     "ta": "வகுப்புக்கு வெளியே, நேரம் போவதே தெரியாமல் நீங்கள் என்ன செய்கிறீர்கள்?"},
    {"id": "workstyle",
     "en": "Think about a task you were proud of. Were you working alone, leading people, or helping someone one-to-one?",
     "ta": "நீங்கள் பெருமைப்பட்ட ஒரு பணியை நினைவுகூருங்கள். தனியாகச் செய்தீர்களா, குழுவை வழிநடத்தினீர்களா, அல்லது ஒருவருக்கு நேரடியாக உதவினீர்களா?"},
    {"id": "strengths",
     "en": "What do teachers or friends usually come to you for help with?",
     "ta": "ஆசிரியர்களோ நண்பர்களோ பொதுவாக எந்த விஷயத்திற்காக உங்களிடம் உதவி கேட்கிறார்கள்?"},
    {"id": "goal",
     "en": "Last one — what do you most want your work to give you in ten years?",
     "ta": "கடைசிக் கேள்வி — பத்து ஆண்டுகளில் உங்கள் பணி உங்களுக்கு எதைத் தர வேண்டும் என விரும்புகிறீர்கள்?"},
]

# Keyword → skill boost map. Powers the fallback profile extractor, and gives
# the Gemini extractor a sanity floor if it returns something unusable.
KEYWORD_BOOSTS = {
    "coding": ["code", "coding", "program", "programming", "python", "java", "software",
               "app", "computer", "algorithm", "puzzle", "நிரலாக்க", "கணினி", "புரோகிராம்"],
    "math": ["math", "maths", "mathematics", "statistics", "numbers", "calculus",
             "accounts", "data", "கணித", "எண்கள்", "புள்ளியியல்"],
    # "science" alone is deliberately absent: it would fire on "computer science".
    "science": ["physics", "chemistry", "biology", "botany", "zoology", "lab",
                "laboratory", "experiment", "dissect", "anatomy", "microscope",
                "medicine", "medical", "patients", "அறிவியல்", "இயற்பியல்",
                "வேதியியல்", "உயிரியல்"],
    "design": ["design", "designing", "figma", "ui", "ux", "poster", "visual",
               "drawing", "sketch", "வடிவமைப்", "ஓவிய"],
    "communication": ["speak", "speaking", "debate", "present", "presentation", "explain",
                      "talking", "anchor", "பேச", "பட்டிமன்ற", "விளக்க"],
    "business": ["business", "shop", "sell", "selling", "money", "startup", "profit",
                 "marketing", "commerce", "வணிக", "விற்பனை", "தொழில்"],
    "leadership": ["lead", "leader", "captain", "organise", "organize", "team", "club",
                   "secretary", "தலைமை", "குழு", "ஒருங்கிணை"],
    "empathy": ["help", "helping", "care", "caring", "counsel", "listen", "teach",
                "tutor", "patients", "உதவ", "பரிவு", "கவனி"],
    "writing": ["write", "writing", "essay", "story", "stories", "blog", "poem",
                "literature", "எழுத", "கதை", "கவிதை"],
    "research": ["research", "read", "reading", "analyse", "analyze", "investigate",
                 "study", "curious", "ஆராய்", "படிக்க"],
    "handsOn": ["build", "building", "repair", "fix", "fixing", "machine", "workshop",
                "circuit", "hardware", "robot", "கட்டு", "சரிசெய்", "இயந்திர"],
    "creativity": ["creative", "art", "music", "dance", "imagine", "idea", "craft",
                   "animation", "படைப்", "கலை", "இசை"],
}


# ---------------------------------------------------------------------------
# Teacher dashboard: workshops a teacher could run for a skill most of the
# class is short on. Parent dashboard: things a parent can do at home.
# Deliberately low-cost and doable without special equipment or money.
# ---------------------------------------------------------------------------

WORKSHOPS = {
    "coding": {"en": "Two-hour 'first program' lab: Python basics on the school computers.",
               "ta": "இரண்டு மணி நேர 'முதல் நிரல்' பயிலரங்கு: பள்ளிக் கணினிகளில் Python அடிப்படைகள்."},
    "math": {"en": "Weekly applied-maths clinic: statistics and probability with real data.",
             "ta": "வாராந்திர கணிதப் பயிற்சி: உண்மையான தரவுகளுடன் புள்ளியியல், நிகழ்தகவு."},
    "science": {"en": "Hands-on science demo day with simple lab experiments.",
                "ta": "எளிய ஆய்வக சோதனைகளுடன் அறிவியல் செயல்விளக்க நாள்."},
    "design": {"en": "Design sprint: redesign one school poster or app screen in a single session.",
               "ta": "வடிவமைப்பு முயற்சி: ஒரே அமர்வில் ஒரு பள்ளி சுவரொட்டி அல்லது செயலித் திரையை மறுவடிவமைக்கவும்."},
    "communication": {"en": "Debate and short-talk sessions, with peer feedback.",
                      "ta": "பட்டிமன்றம் மற்றும் சிறு உரை அமர்வுகள், சக மாணவர் கருத்துகளுடன்."},
    "business": {"en": "Mini-market day: students plan, price and sell something small.",
                 "ta": "சிறுசந்தை நாள்: மாணவர்கள் திட்டமிட்டு, விலை நிர்ணயித்து, ஒரு பொருளை விற்கிறார்கள்."},
    "leadership": {"en": "Rotate team leads on group projects so every student leads once.",
                   "ta": "குழுத் திட்டங்களில் தலைவர்களைச் சுழற்சி முறையில் மாற்றி, ஒவ்வொருவரும் ஒரு முறை வழிநடத்தட்டும்."},
    "empathy": {"en": "Peer-mentoring pairs: senior students tutor juniors for a term.",
                "ta": "சக வழிகாட்டல் இணைகள்: மூத்த மாணவர்கள் ஒரு பருவம் இளையோருக்குக் கற்பிக்கிறார்கள்."},
    "writing": {"en": "Fortnightly writing workshop with structured feedback.",
                "ta": "இருவாரங்களுக்கு ஒரு முறை எழுத்துப் பயிலரங்கு, கட்டமைக்கப்பட்ட கருத்துகளுடன்."},
    "research": {"en": "Mini research project: pick a question, find three sources, present findings.",
                 "ta": "சிறு ஆய்வுத் திட்டம்: ஒரு கேள்வியைத் தேர்ந்து, மூன்று ஆதாரங்களைத் தேடி, முடிவுகளை முன்வையுங்கள்."},
    "handsOn": {"en": "Maker afternoon: repair, build or wire something real.",
                "ta": "உருவாக்குநர் மதியம்: உண்மையான ஒன்றைச் சரிசெய்யவும், கட்டவும், மின்இணைப்புச் செய்யவும்."},
    "creativity": {"en": "Open-brief challenge with no single right answer.",
                   "ta": "ஒரே சரியான பதில் இல்லாத திறந்த சவால்."},
}

PARENT_TIPS = {
    "coding": {"en": "Ask them to show you something they've built. Curiosity from you matters more than understanding the code.",
               "ta": "அவர்கள் உருவாக்கிய ஒன்றைக் காட்டச் சொல்லுங்கள். நிரலைப் புரிந்துகொள்வதை விட உங்கள் ஆர்வமே முக்கியம்."},
    "math": {"en": "Bring everyday numbers into conversation: bills, discounts, travel times. Let them do the sums.",
             "ta": "அன்றாட எண்களைப் பேச்சில் கொண்டு வாருங்கள்: பில், தள்ளுபடி, பயண நேரம். கணக்கை அவர்களே போடட்டும்."},
    "science": {"en": "Encourage questions about how things work, and look up the answers together.",
                "ta": "பொருட்கள் எப்படி இயங்குகின்றன என்று கேள்வி கேட்க ஊக்குவியுங்கள்; பதிலை இணைந்து தேடுங்கள்."},
    "design": {"en": "Give them small real design jobs: a family invitation, a shop sign, a poster.",
               "ta": "சிறு உண்மையான வடிவமைப்பு வேலைகள் கொடுங்கள்: குடும்ப அழைப்பிதழ், கடைப் பலகை, சுவரொட்டி."},
    "communication": {"en": "Let them speak for the family in small situations, such as ordering or asking directions.",
                      "ta": "ஆர்டர் செய்தல், வழி கேட்டல் போன்ற சிறு சூழல்களில் குடும்பத்தின் சார்பாக அவர்கள் பேசட்டும்."},
    "business": {"en": "Involve them in a small household or shop decision, and ask what they would do.",
                 "ta": "வீட்டு அல்லது கடை சார்ந்த ஒரு சிறு முடிவில் அவர்களை ஈடுபடுத்தி, என்ன செய்வார்கள் எனக் கேளுங்கள்."},
    "leadership": {"en": "Let them plan a family event from start to finish.",
                   "ta": "ஒரு குடும்ப நிகழ்வை ஆரம்பம் முதல் முடிவு வரை அவர்கள் திட்டமிடட்டும்."},
    "empathy": {"en": "Talk about how other people felt in a situation, not just what happened.",
                "ta": "என்ன நடந்தது என்பதோடு, மற்றவர்கள் எப்படி உணர்ந்தார்கள் என்பதையும் பேசுங்கள்."},
    "writing": {"en": "Ask them to write short notes or letters for the family. Read them and respond.",
                "ta": "குடும்பத்திற்குச் சிறு குறிப்புகள் அல்லது கடிதங்கள் எழுதச் சொல்லி, படித்துப் பதில் சொல்லுங்கள்."},
    "research": {"en": "When they ask something you don't know, say 'let's find out' and do it together.",
                 "ta": "உங்களுக்குத் தெரியாததை அவர்கள் கேட்டால், 'சேர்ந்து கண்டுபிடிப்போம்' என்று சொல்லி இணைந்து தேடுங்கள்."},
    "handsOn": {"en": "Let them fix or build something at home, even if it takes longer than doing it yourself.",
                "ta": "வீட்டில் ஏதாவது ஒன்றைச் சரிசெய்ய அல்லது கட்டச் சொல்லுங்கள், நீங்களே செய்வதை விட நேரமானாலும்."},
    "creativity": {"en": "Make room for unstructured time and projects with no marks attached.",
                   "ta": "மதிப்பெண் இல்லாத, கட்டுப்பாடற்ற நேரத்திற்கும் திட்டங்களுக்கும் இடம் தாருங்கள்."},
}

PARENT_GENERAL_TIP = {
    "en": "Ask what they enjoyed about the interview before you ask about the results. These are suggestions, and the decision is theirs.",
    "ta": "முடிவுகளைப் பற்றிக் கேட்கும் முன், நேர்காணலில் எது பிடித்தது என்று கேளுங்கள். இவை பரிந்துரைகள் மட்டுமே; முடிவு அவர்களுடையது.",
}
