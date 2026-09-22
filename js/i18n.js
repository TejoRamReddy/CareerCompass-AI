/* ==========================================================================
   English and Tamil UI strings.

   Any element with data-i18n="key" gets its text swapped on language change.
   Placeholders use data-i18n-placeholder. The choice is remembered in
   localStorage and sent to the backend so the interview and results come
   back in the same language.
   ========================================================================== */

const STRINGS = {
  en: {
    'nav.demo': 'Try the interview',
    'nav.signin': 'Sign in',
    'nav.signout': 'Sign out',
    'nav.dashboard': 'Dashboard',
    'lang.toggle': 'தமிழ்',

    'demo.title': 'Tell me about yourself, in your own words.',
    'demo.lede': 'This is a conversation, not a quiz. Answer in a sentence or two — there are no options to pick from and no right answers.',
    'demo.start': 'Start the interview',
    'demo.placeholder': 'Type your answer…',
    'demo.send': 'Send',
    'demo.thinking': 'Thinking…',
    'demo.question': 'Question',
    'demo.of': 'of about',
    'demo.finish': 'See my matches',
    'demo.retake': 'Start over',
    'demo.you': 'You',
    'demo.ai': 'Counsellor',
    'demo.emptyAnswer': 'Type an answer first.',
    'demo.offline': "Can't reach the server. Check that the backend is running, then start over.",

    'demo.badge.gemini': 'Live Gemini interview',
    'demo.badge.fallback': 'Scripted interview (no Gemini key set)',
    'demo.badge.checking': 'Connecting…',
    'demo.badge.offline': 'Backend unreachable',
    'demo.explain.gemini': 'Each question is written by Gemini in response to what you just said, and your profile is read out of the conversation rather than looked up from a table.',
    'demo.explain.fallback': 'No Gemini key is set on the server, so the interview follows a fixed set of open questions and your profile is extracted from your own words by keyword. Everything else — scoring, database, results — is identical.',
    'demo.explain.offline': 'The backend at the configured address is not responding. Start it locally with <code>python app.py</code> in <code>/backend</code>, or set your deployed URL in <code>js/config.js</code>.',

    'results.tag': 'your results',
    'results.title': "Here's what fits, based on what you told me.",
    'results.match': 'fit',
    'results.similarity': 'raw similarity',
    'results.gap': 'Skill gap',
    'results.needed': 'needed',
    'results.roadmap': 'Suggested next steps',
    'results.why': 'Why this one',
    'results.saved': 'Saved to your account.',
    'results.notSaved': 'Sign in to save this and share it with a parent or teacher.',
    'results.scoringNote': 'Fit blends how closely your profile matches the work (cosine similarity) with how your marks line up with the subjects the career leans on. It is a similarity score, not a probability of success.',

    'academics.title': 'Your marks (optional)',
    'academics.lede': 'Out of 100. This is 30% of the score — leave it blank and your answers carry all of it.',
    'academics.skip': 'Skip this',
    'academics.save': 'Use these marks',

    'auth.signin': 'Sign in',
    'auth.signup': 'Create an account',
    'auth.name': 'Full name',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.passwordHint': 'At least 8 characters.',
    'auth.role': 'I am a',
    'auth.student': 'Student',
    'auth.teacher': 'Teacher',
    'auth.parent': 'Parent',
    'auth.branch': 'Branch or stream',
    'auth.college': 'School or college',
    'auth.classCode': 'Class code',
    'auth.classCodeHintTeacher': 'Make one up and share it with your students, e.g. CS2027.',
    'auth.classCodeHintStudent': 'Optional. Your teacher will give you this.',
    'auth.haveAccount': 'Already have an account? Sign in',
    'auth.noAccount': "New here? Create an account",
    'auth.working': 'Just a moment…',

    'dash.teacher': 'Your class',
    'dash.parent': "Your child's results",
    'dash.students': 'students',
    'dash.completed': 'have finished the interview',
    'dash.topCareers': 'Most common top matches',
    'dash.commonGaps': 'Skills most of the class needs to build',
    'dash.noStudents': 'No students have signed up with this class code yet. Share the code with them.',
    'dash.notTaken': 'Not taken yet',
    'dash.linkTitle': 'Link to your child',
    'dash.linkHint': "Ask your child for the share code on their account page.",
    'dash.linkButton': 'Link',
    'dash.noChildren': 'No children linked yet. Enter a share code above.',
    'dash.shareCode': 'Your share code',
    'dash.shareCodeHint': 'Give this to a parent so they can see your results.',

    'nav.share': 'Share',

    'demo.confidenceBefore': 'Before we start: how sure are you about your career choice right now?',
    'demo.confidenceScale': '1 = not at all sure, 5 = very sure',
    'demo.badge.degraded': 'Gemini is set up but not responding, using scripted interview',
    'demo.explain.degraded': "A Gemini key is configured on the server, but Gemini isn't answering right now (a wrong model name, quota, or network problem). The interview is using fixed open questions and keyword profiling instead. Scoring, database and results work the same.",

    'results.engine.gemini': 'Interview, profile and explanations by Gemini',
    'results.engine.fallback': 'Scripted interview, Gemini was not used for this run',
    'results.consistency': 'Consistency check',
    'results.consistency.high': 'Your examples backed up what you said you enjoy.',
    'results.consistency.medium': 'Some of what you said was backed by examples and some was not. Retaking with a specific example for each interest will sharpen the result.',
    'results.consistency.low': 'Most answers were general. Retake it with a real example for each interest and the matches will get more accurate.',
    'results.consistency.none': "The scripted interview can't cross-check your answers. Gemini does this when it is running.",

    'feedback.title': 'Help us improve',
    'feedback.rating': 'How useful were these results?',
    'feedback.confidenceAfter': 'How sure are you about your career choice now?',
    'feedback.wouldAct': 'Would you act on the top 3 careers shown?',
    'feedback.yes': 'Yes',
    'feedback.maybe': 'Maybe',
    'feedback.no': 'No',
    'feedback.comment': 'Anything to add? (optional)',
    'feedback.send': 'Send feedback',
    'feedback.thanks': 'Thank you. This helps us improve.',
    'feedback.pickRating': 'Pick a rating from 1 to 5 first.',

    'dash.workshops': 'Workshop ideas for what the class needs',
    'dash.attempts': 'Runs',
    'dash.fitChange': 'Fit change',
    'dash.progress': 'Progress over time',
    'dash.skillChange': 'Skills that moved most since the first run',
    'dash.tips': 'How to support at home',
    'dash.noProgress': 'Progress appears after a second interview.',
    'dash.fitRuns': 'Interview runs',

    'share.title': 'Put CareerCompass on every phone in the room',
    'share.lede': 'Show this page on a projector. Students scan the code with their phone camera and land straight on the interview. Nothing to install.',
    'share.qrAlt': 'QR code for the CareerCompass interview',
    'share.link': 'Or type this address:',
    'share.install': 'Install it like an app',
    'share.installAndroid': 'Android (Chrome): open the site, tap the three dots, then "Install app" or "Add to Home screen".',
    'share.installIphone': 'iPhone (Safari): tap Share, then "Add to Home Screen".',
    'share.installNote': 'It opens full screen from the home screen, like an app. It is a web app, not a Play Store download.',
    'share.noBackend': "Couldn't generate the QR code because the backend isn't reachable. The address below still works.",
    'share.copy': 'Copy link',
    'share.copied': 'Copied',
  },

  ta: {
    'nav.demo': 'நேர்காணலை முயற்சிக்க',
    'nav.signin': 'உள்நுழைய',
    'nav.signout': 'வெளியேற',
    'nav.dashboard': 'டாஷ்போர்டு',
    'lang.toggle': 'English',

    'demo.title': 'உங்கள் சொந்த வார்த்தைகளில் உங்களைப் பற்றிச் சொல்லுங்கள்.',
    'demo.lede': 'இது ஒரு உரையாடல், தேர்வு அல்ல. ஓரிரு வாக்கியங்களில் பதில் சொல்லுங்கள் — தேர்வு செய்ய விருப்பங்களும் இல்லை, சரியான பதில்களும் இல்லை.',
    'demo.start': 'நேர்காணலைத் தொடங்கு',
    'demo.placeholder': 'உங்கள் பதிலை எழுதுங்கள்…',
    'demo.send': 'அனுப்பு',
    'demo.thinking': 'யோசிக்கிறேன்…',
    'demo.question': 'கேள்வி',
    'demo.of': '/ சுமார்',
    'demo.finish': 'என் பொருத்தங்களைப் பார்',
    'demo.retake': 'மீண்டும் தொடங்கு',
    'demo.you': 'நீங்கள்',
    'demo.ai': 'ஆலோசகர்',
    'demo.emptyAnswer': 'முதலில் ஒரு பதிலை எழுதுங்கள்.',
    'demo.offline': 'சேவையகத்தை அணுக முடியவில்லை. பின்தளம் இயங்குகிறதா எனப் பார்த்து மீண்டும் தொடங்குங்கள்.',

    'demo.badge.gemini': 'நேரடி Gemini நேர்காணல்',
    'demo.badge.fallback': 'எழுதப்பட்ட நேர்காணல் (Gemini சாவி அமைக்கப்படவில்லை)',
    'demo.badge.checking': 'இணைக்கிறது…',
    'demo.badge.offline': 'பின்தளம் கிடைக்கவில்லை',
    'demo.explain.gemini': 'ஒவ்வொரு கேள்வியையும் நீங்கள் சொன்னதற்கேற்ப Gemini எழுதுகிறது; உங்கள் சுயவிவரம் அட்டவணையிலிருந்து அல்ல, உரையாடலிலிருந்தே உருவாக்கப்படுகிறது.',
    'demo.explain.fallback': 'சேவையகத்தில் Gemini சாவி இல்லை. எனவே நிலையான திறந்த கேள்விகள் கேட்கப்படுகின்றன; உங்கள் சொந்த வார்த்தைகளிலிருந்து முக்கியச் சொற்கள் மூலம் சுயவிவரம் உருவாக்கப்படுகிறது. மதிப்பீடு, தரவுத்தளம், முடிவுகள் அனைத்தும் ஒரே மாதிரிதான்.',
    'demo.explain.offline': 'அமைக்கப்பட்ட முகவரியில் பின்தளம் பதிலளிக்கவில்லை. <code>/backend</code>-ல் <code>python app.py</code> இயக்குங்கள், அல்லது <code>js/config.js</code>-ல் உங்கள் URL-ஐ அமையுங்கள்.',

    'results.tag': 'உங்கள் முடிவுகள்',
    'results.title': 'நீங்கள் சொன்னதன் அடிப்படையில் இவை பொருந்துகின்றன.',
    'results.match': 'பொருத்தம்',
    'results.similarity': 'மூலப் ஒற்றுமை',
    'results.gap': 'திறன் இடைவெளி',
    'results.needed': 'தேவை',
    'results.roadmap': 'அடுத்த படிகள்',
    'results.why': 'ஏன் இது',
    'results.saved': 'உங்கள் கணக்கில் சேமிக்கப்பட்டது.',
    'results.notSaved': 'இதைச் சேமித்து பெற்றோர் அல்லது ஆசிரியருடன் பகிர உள்நுழையுங்கள்.',
    'results.scoringNote': 'பொருத்தம் என்பது உங்கள் சுயவிவரம் அந்தப் பணியுடன் எவ்வளவு ஒத்துப்போகிறது (cosine similarity) என்பதையும், உங்கள் மதிப்பெண்கள் அந்தத் துறைக்குத் தேவையான பாடங்களுடன் எப்படிப் பொருந்துகின்றன என்பதையும் இணைக்கிறது. இது ஒரு ஒற்றுமை மதிப்பெண், வெற்றிக்கான நிகழ்தகவு அல்ல.',

    'academics.title': 'உங்கள் மதிப்பெண்கள் (விருப்பத்தேர்வு)',
    'academics.lede': '100-க்கு. இது மதிப்பெண்ணில் 30% — காலியாக விட்டால் உங்கள் பதில்களே முழு எடையையும் எடுக்கும்.',
    'academics.skip': 'இதைத் தவிர்',
    'academics.save': 'இந்த மதிப்பெண்களைப் பயன்படுத்து',

    'auth.signin': 'உள்நுழைய',
    'auth.signup': 'கணக்கைத் தொடங்கு',
    'auth.name': 'முழுப் பெயர்',
    'auth.email': 'மின்னஞ்சல்',
    'auth.password': 'கடவுச்சொல்',
    'auth.passwordHint': 'குறைந்தது 8 எழுத்துகள்.',
    'auth.role': 'நான் ஒரு',
    'auth.student': 'மாணவர்',
    'auth.teacher': 'ஆசிரியர்',
    'auth.parent': 'பெற்றோர்',
    'auth.branch': 'பிரிவு / துறை',
    'auth.college': 'பள்ளி அல்லது கல்லூரி',
    'auth.classCode': 'வகுப்புக் குறியீடு',
    'auth.classCodeHintTeacher': 'ஒன்றை உருவாக்கி மாணவர்களுடன் பகிருங்கள், எ.கா. CS2027.',
    'auth.classCodeHintStudent': 'விருப்பத்தேர்வு. உங்கள் ஆசிரியர் இதைத் தருவார்.',
    'auth.haveAccount': 'ஏற்கனவே கணக்கு உள்ளதா? உள்நுழையுங்கள்',
    'auth.noAccount': 'புதியவரா? கணக்கைத் தொடங்குங்கள்',
    'auth.working': 'ஒரு நிமிடம்…',

    'dash.teacher': 'உங்கள் வகுப்பு',
    'dash.parent': 'உங்கள் பிள்ளையின் முடிவுகள்',
    'dash.students': 'மாணவர்கள்',
    'dash.completed': 'நேர்காணலை முடித்துள்ளனர்',
    'dash.topCareers': 'அதிகம் வரும் முதல் பொருத்தங்கள்',
    'dash.commonGaps': 'வகுப்பில் பலருக்கும் வளர்க்க வேண்டிய திறன்கள்',
    'dash.noStudents': 'இந்த வகுப்புக் குறியீட்டில் இன்னும் யாரும் சேரவில்லை. குறியீட்டைப் பகிருங்கள்.',
    'dash.notTaken': 'இன்னும் எடுக்கவில்லை',
    'dash.linkTitle': 'உங்கள் பிள்ளையுடன் இணையுங்கள்',
    'dash.linkHint': 'உங்கள் பிள்ளையின் கணக்குப் பக்கத்தில் உள்ள பகிர்வுக் குறியீட்டைக் கேளுங்கள்.',
    'dash.linkButton': 'இணை',
    'dash.noChildren': 'இன்னும் யாரும் இணைக்கப்படவில்லை. மேலே ஒரு குறியீட்டை உள்ளிடுங்கள்.',
    'dash.shareCode': 'உங்கள் பகிர்வுக் குறியீடு',
    'dash.shareCodeHint': 'உங்கள் முடிவுகளைப் பார்க்க பெற்றோரிடம் இதைக் கொடுங்கள்.',

    'nav.share': 'பகிர',

    'demo.confidenceBefore': 'தொடங்கும் முன்: உங்கள் தொழில் தேர்வைப் பற்றி இப்போது எவ்வளவு உறுதியாக இருக்கிறீர்கள்?',
    'demo.confidenceScale': '1 = சற்றும் உறுதி இல்லை, 5 = மிகவும் உறுதி',
    'demo.badge.degraded': 'Gemini அமைக்கப்பட்டுள்ளது, ஆனால் பதிலளிக்கவில்லை; எழுதப்பட்ட நேர்காணல் பயன்படுகிறது',
    'demo.explain.degraded': 'சேவையகத்தில் Gemini சாவி உள்ளது, ஆனால் Gemini இப்போது பதிலளிக்கவில்லை (தவறான மாடல் பெயர், வரம்பு, அல்லது இணையச் சிக்கல்). நிலையான திறந்த கேள்விகளும் முக்கியச் சொல் அடிப்படையிலான சுயவிவரமும் பயன்படுகின்றன. மதிப்பீடு, தரவுத்தளம், முடிவுகள் அனைத்தும் ஒரே மாதிரிதான்.',

    'results.engine.gemini': 'நேர்காணல், சுயவிவரம், விளக்கங்கள்: Gemini',
    'results.engine.fallback': 'எழுதப்பட்ட நேர்காணல்; இந்த முறை Gemini பயன்படுத்தப்படவில்லை',
    'results.consistency': 'பதில்களின் நிலைத்தன்மை',
    'results.consistency.high': 'நீங்கள் விரும்புவதாகச் சொன்னவற்றை உங்கள் எடுத்துக்காட்டுகள் உறுதிப்படுத்தின.',
    'results.consistency.medium': 'சிலவற்றுக்கு எடுத்துக்காட்டுகள் இருந்தன, சிலவற்றுக்கு இல்லை. ஒவ்வொரு ஆர்வத்துக்கும் ஒரு குறிப்பிட்ட எடுத்துக்காட்டுடன் மீண்டும் முயன்றால் முடிவு துல்லியமாகும்.',
    'results.consistency.low': 'பெரும்பாலான பதில்கள் பொதுவாக இருந்தன. ஒவ்வொரு ஆர்வத்துக்கும் உண்மையான எடுத்துக்காட்டுடன் மீண்டும் முயலுங்கள்; பொருத்தங்கள் இன்னும் சரியாக இருக்கும்.',
    'results.consistency.none': 'எழுதப்பட்ட நேர்காணலால் உங்கள் பதில்களைச் சரிபார்க்க முடியாது. Gemini இயங்கும்போது இது நடக்கும்.',

    'feedback.title': 'எங்களை மேம்படுத்த உதவுங்கள்',
    'feedback.rating': 'இந்த முடிவுகள் எவ்வளவு பயனுள்ளவை?',
    'feedback.confidenceAfter': 'உங்கள் தொழில் தேர்வைப் பற்றி இப்போது எவ்வளவு உறுதியாக இருக்கிறீர்கள்?',
    'feedback.wouldAct': 'காட்டப்பட்ட முதல் 3 தொழில்களின் மீது நடவடிக்கை எடுப்பீர்களா?',
    'feedback.yes': 'ஆம்',
    'feedback.maybe': 'இருக்கலாம்',
    'feedback.no': 'இல்லை',
    'feedback.comment': 'சேர்க்க ஏதாவது உள்ளதா? (விருப்பத்தேர்வு)',
    'feedback.send': 'கருத்தை அனுப்பு',
    'feedback.thanks': 'நன்றி. இது எங்களை மேம்படுத்த உதவும்.',
    'feedback.pickRating': 'முதலில் 1 முதல் 5 வரை ஒரு மதிப்பீட்டைத் தேர்ந்தெடுங்கள்.',

    'dash.workshops': 'வகுப்புக்குத் தேவையானவற்றுக்கான பயிலரங்கு யோசனைகள்',
    'dash.attempts': 'முறைகள்',
    'dash.fitChange': 'பொருத்த மாற்றம்',
    'dash.progress': 'காலப்போக்கில் முன்னேற்றம்',
    'dash.skillChange': 'முதல் முறையிலிருந்து அதிகம் மாறிய திறன்கள்',
    'dash.tips': 'வீட்டில் எப்படி ஆதரிப்பது',
    'dash.noProgress': 'இரண்டாவது நேர்காணலுக்குப் பிறகு முன்னேற்றம் தெரியும்.',
    'dash.fitRuns': 'நேர்காணல் முறைகள்',

    'share.title': 'அறையிலுள்ள ஒவ்வொரு தொலைபேசியிலும் CareerCompass',
    'share.lede': 'இந்தப் பக்கத்தை புரொஜெக்டரில் காட்டுங்கள். மாணவர்கள் தொலைபேசிக் கேமராவால் குறியீட்டை ஸ்கேன் செய்தால் நேராக நேர்காணலுக்குச் செல்வார்கள். எதையும் நிறுவ வேண்டியதில்லை.',
    'share.qrAlt': 'CareerCompass நேர்காணலுக்கான QR குறியீடு',
    'share.link': 'அல்லது இந்த முகவரியை உள்ளிடுங்கள்:',
    'share.install': 'செயலி போல நிறுவுங்கள்',
    'share.installAndroid': 'Android (Chrome): தளத்தைத் திறந்து, மூன்று புள்ளிகளைத் தொட்டு "Install app" அல்லது "Add to Home screen" தேர்ந்தெடுங்கள்.',
    'share.installIphone': 'iPhone (Safari): Share-ஐத் தொட்டு "Add to Home Screen" தேர்ந்தெடுங்கள்.',
    'share.installNote': 'முகப்புத் திரையிலிருந்து செயலி போல முழுத் திரையில் திறக்கும். இது ஒரு வலைச் செயலி, Play Store பதிவிறக்கம் அல்ல.',
    'share.noBackend': 'பின்தளம் கிடைக்காததால் QR குறியீட்டை உருவாக்க முடியவில்லை. கீழுள்ள முகவரி தொடர்ந்து வேலை செய்யும்.',
    'share.copy': 'இணைப்பை நகலெடு',
    'share.copied': 'நகலெடுக்கப்பட்டது',
  },
};

window.CC = window.CC || {};

CC.lang = localStorage.getItem(CC.storageKeys.lang) === 'ta' ? 'ta' : 'en';

CC.t = function (key) {
  const table = STRINGS[CC.lang] || STRINGS.en;
  return table[key] || STRINGS.en[key] || key;
};

CC.applyI18n = function (root) {
  const scope = root || document;
  document.documentElement.lang = CC.lang;
  document.body && document.body.classList.toggle('lang-ta', CC.lang === 'ta');

  scope.querySelectorAll('[data-i18n]').forEach((el) => {
    const value = CC.t(el.dataset.i18n);
    if (el.dataset.i18nHtml !== undefined) el.innerHTML = value;
    else el.textContent = value;
  });
  scope.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    el.placeholder = CC.t(el.dataset.i18nPlaceholder);
  });
};

CC.setLang = function (lang) {
  CC.lang = lang === 'ta' ? 'ta' : 'en';
  localStorage.setItem(CC.storageKeys.lang, CC.lang);
  CC.applyI18n();
  document.dispatchEvent(new CustomEvent('cc:langchange', { detail: CC.lang }));
};

CC.mountLangToggle = function () {
  document.querySelectorAll('[data-lang-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => CC.setLang(CC.lang === 'ta' ? 'en' : 'ta'));
  });
};
