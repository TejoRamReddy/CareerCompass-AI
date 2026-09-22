# CareerCompass AI

> "Every student deserves a compass, not a coin flip."

Career guidance for students in Tamil Nadu — especially first-generation,
Tamil-medium and rural students — built by **Team Pixel Pioneers** for a
**StartupTN** hackathon problem statement.

A student has a short conversation with the app, in English or Tamil. Gemini
writes each question in response to the last answer, reads a skill profile out
of the conversation, and the recommendation engine ranks 26 careers against
that profile plus the student's marks. They get three matches with a reason
for each, a skill gap, and a roadmap. Teachers see how a class is leaning;
parents see one child's result, and only if the child shares a code.

---

## Quick start

Two terminals. Python 3.10+.

**Terminal 1 — the API**

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # then paste your Gemini key into .env
python app.py                 # http://localhost:5000
```

**Terminal 2 — the site**

```bash
python -m http.server 8000    # from the project root
```

Open <http://localhost:8000/demo.html>.

**Check your Gemini key works** (do this once, before a demo):

```bash
cd backend && python check_gemini.py
```

It runs the same calls the app makes, prints what came back, and if the model
name has been retired it lists the ones your key can actually use.

Without a Gemini key everything still runs — the interview falls back to a
fixed set of open questions and the profile is extracted from the student's
own words by keyword. The badge at the top of the demo page says which engine
is live, so it's never ambiguous.

Run the tests:

```bash
cd backend && pytest        # 63 tests, no network, no key needed
```

---

## What's real

| | |
|---|---|
| **Interview** | Gemini writes each follow-up from the previous answer. No question list in the code, no options to click. Falls back to scripted open questions if Gemini is unavailable. |
| **Profile extraction** | Gemini scores 12 skill dimensions from the conversation and cites the phrase that justified each score. Not an answer→boost lookup table. |
| **Ranking** | scikit-learn `cosine_similarity` over a pandas DataFrame of 26 career vectors. |
| **Weighted scoring** | 70% interview profile, 30% academic marks, configurable in `.env`. Marks also produce a per-career academic fit. |
| **Explanations** | Gemini writes one sentence per career, quoting what the student actually said. |
| **Accounts** | Students, teachers and parents. Name, branch, college. PBKDF2-HMAC-SHA256 password hashing, JWT sessions. |
| **Dashboards** | Teacher: class aggregate. Parent: one child, by share code. |
| **Tamil** | Interface, interview, results, skill gap and roadmap. Switchable mid-session. |
| **Consistency check** | Gemini asks for a specific recent example around question 4 or 5, then rates how well the answers backed up the claimed interests (high / medium / low) and flags what wasn't backed up. The scripted engine can't do this and says so on the results page. |
| **Feedback** | After results: usefulness (1-5), confidence before and after (1-5), would-you-act-on-the-top-3. Stored per session and summarised in `/api/stats`. |
| **Teacher dashboard** | Class distribution, common skill gaps, a workshop idea for each of the top three gaps, runs per student and fit change. Never transcripts. |
| **Parent dashboard** | Matches and roadmap, progress over time (needs 2+ runs), the skills that moved most, and home-support tips tied to that child's gaps. Never transcripts. |
| **Mobile** | Installable web app (manifest + service worker) with a QR page for classrooms. |
| **Database** | SQLite: users, links, careers, sessions, submissions, feedback. Every interview is stored. |

The career vectors are hand-scored approximations built for this project, not
a validated psychometric instrument. The app says so on the results page.

---

## About the match percentages

The earlier version reported raw cosine similarity as a "match %", and every
career came back at 81–87%. That's an artefact: all 26 career vectors are
all-positive, so cosine similarity between any student and any career sits in
a narrow high band. A poor fit looked like a good one.

Two changes:

1. **Raw `similarity` and calibrated `fit` are reported separately.** Fit
   rescales the score across the band cosine actually occupies
   (`SIMILARITY_FLOOR`/`SIMILARITY_CEILING` in `.env`), then blends in academic
   fit.
2. **Neither is called a probability.** The results page says, in both
   languages, that this is a similarity score.

For a student who talks about coding and maths, with strong maths and computer
science marks, fit now runs from 89% at the top to 19% at the bottom of the
26. That spread is the point.

---

## Project structure

```
careercompass-ai/
├── index.html                 Showcase page
├── demo.html                  The interview
├── login.html                 Sign in / sign up
├── share.html                 QR code + install instructions for a classroom
├── dashboard.html             Teacher, parent and student views
├── css/
│   ├── style.css              Design system (unchanged)
│   ├── demo.css               Interview and results
│   └── app.css                Accounts, dashboards, Tamil typography
├── js/
│   ├── config.js              ← resolves the API base. Edit for deployment.
│   ├── i18n.js                English + Tamil strings
│   ├── api.js                 Fetch wrapper, token handling
│   ├── demo.js                The conversation
│   ├── auth.js                Sign in / sign up
│   ├── dashboard.js           Teacher / parent / student dashboards
│   ├── share.js               QR code page
│   ├── pwa.js                 Registers the service worker
│   └── main.js                Landing page interactions
├── backend/
│   ├── app.py                 Flask factory, routes, rate limiting
│   ├── auth.py                Hashing, JWT, role decorators
│   ├── db.py                  Schema and seeding
│   ├── careers_data.py        26 careers, EN + TA, academic weights
│   ├── matching.py            numpy / pandas / scikit-learn engine
│   ├── gemini.py              Gemini client (server-side only)
│   ├── interview.py           Interview orchestration + fallbacks
│   ├── dashboards.py          Teacher and parent endpoints
│   ├── check_gemini.py        Verifies your key, model and prompts against the real API
│   ├── tests/test_api.py      63 tests, including a mock Google server
│   ├── requirements.txt
│   ├── Procfile
│   └── .env.example
├── render.yaml                Render blueprint
├── manifest.webmanifest       Makes the site installable on a phone
├── sw.js                      Service worker (app shell only, never /api)
└── assets/                    App icons
```

---

## The API key

The Gemini key lives in `backend/.env` and is read by `config.py`. It is never
sent to the browser — every Gemini call goes through the backend. `.env` is
gitignored.

The key is sent to Google in an `x-goog-api-key` header, never in a URL, and
any error text is scrubbed of it before it reaches a log or `/api/health`.

**If a key has ever been pasted into a screenshot, a chat, or a commit, delete
it in Google AI Studio and create a new one.** Anyone who sees it can spend
against your quota.

---

## Deploying

### Backend → Render

1. Push this repo to GitHub.
2. Render → **New → Blueprint** → pick the repo. `render.yaml` does the rest.
3. In the dashboard set two variables:
   - `GEMINI_API_KEY` — your key
   - `ALLOWED_ORIGINS` — your site's URL, e.g. `https://your-username.github.io`
4. Note the service URL, e.g. `https://careercompass-ai-api.onrender.com`.

The free tier sleeps after inactivity, so the first request after a quiet spell
takes 30–60 seconds. Hit `/api/health` a minute before a demo to wake it.

### Frontend → GitHub Pages

1. Open `js/config.js` and set `PRODUCTION_API_BASE` to the Render URL.
2. Commit and push.
3. Settings → Pages → deploy from `main`, folder `/ (root)`.

To test a deployed page against a different API without editing anything, append
`?api=https://some-other-api.onrender.com` to the URL.

---

## API reference

| Endpoint | Method | Auth | What it does |
|---|---|---|---|
| `/api/health` | GET | — | Status. `geminiConfigured` = a key exists; `geminiReachable` = a live call just succeeded (cached 60s) |
| `/api/careers?lang=` | GET | — | All 26 careers, localised |
| `/api/stats` | GET | — | Submissions stored, most common top match |
| `/api/auth/register` | POST | — | Create a student, teacher or parent account |
| `/api/auth/login` | POST | — | Returns a signed token |
| `/api/auth/me` | GET | token | The current account |
| `/api/auth/academics` | POST | student | Save marks |
| `/api/auth/language` | POST | token | Save language preference |
| `/api/interview/start` | POST | optional | Opens a session, returns the first question |
| `/api/interview/reply` | POST | optional | Sends an answer, returns the next question |
| `/api/interview/finish` | POST | optional | Scores the conversation, saves the submission |
| `/api/match` | POST | optional | Score a whole transcript in one call |
| `/api/feedback` | POST | — | Rating, confidence after, would-act, comment for a finished session |
| `/api/qr?url=` | GET | — | QR code (SVG) for a URL on an allowed origin |
| `/api/me/history` | GET | student | Past runs |
| `/api/teacher/class` | GET | teacher | Class aggregate |
| `/api/parent/link` | POST | parent | Link to a child with a share code |
| `/api/parent/children` | GET | parent | Linked children and their results |

CORS is restricted to `ALLOWED_ORIGINS`. Requests are rate limited per IP
(40/min, 8/min on auth routes). All input is length-capped and validated.

---

## Pitch deck vs. this repository

Everything the deck presents as built (Phase 1) is here. What is *not* here:

**Phase 2, labelled as future in the deck:** Devil's Advocate, Career Twin,
Career Simulation, AI Career Coach, live NCS / O\*NET data, the consent flow,
resume analyser, resume / internship / scholarship matching, voice counselor,
languages beyond Tamil, the Random Forest model.

**Adoption items that are outreach, not code:** Naan Mudhalvan and Skill
Development Centre integration, career awareness camps, placement-cell
integration.

**One deliberate difference:** the deck says "Android application". What's
built is an installable web app (add to home screen), not a Play Store APK.
It opens full screen and works on any Android phone with Chrome, but say
"installable web app" if asked.

Things the code does that the deck's wording could be sharper about:

- Interview text is sent to Google's Gemini API to run the interview. "No data
  shared with third parties" should say "not sold, and only sent to Gemini to
  run the interview".
- "Never the same script twice" is true with a Gemini key. Without one, the
  fallback asks a fixed set of open questions.
- The skill gap is need minus have on a 0-5 scale, not cosine similarity.

---

## Privacy

A teacher sees who has finished, which careers keep coming up, and which skills
the class needs — never a transcript. A parent sees one child's matches and
roadmap, only after that child hands over a share code, and never the
transcript either. What a student says in the interview stays with the student.

---

## Team — Pixel Pioneers

K. Tejo Ram · Kevin Adithya · Lalitha · Mageshwaran

## License

Built for a hackathon problem statement. Fork it for learning; please credit
Team Pixel Pioneers if you reuse the idea or content.
