import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random
import json
from datetime import datetime, date
import time
import hashlib

# Configure page
st.set_page_config(
    page_title="PersonaVista - Personality Development App",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for black background and styling

st.markdown("""
<style>
    /* Existing styles */

    input, textarea {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
        border: 1px solid #555 !important;
    }

    input::placeholder, textarea::placeholder {
        color: red !important;  /* 🔴 red placeholders */
    }

</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    if 'users_db' not in st.session_state:
        st.session_state.users_db = {}
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False

# User authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, email):
    if username in st.session_state.users_db:
        return False
    
    st.session_state.users_db[username] = {
        'password': hash_password(password),
        'email': email,
        'personality_data': {},
        'quiz_results': {},
        'mood_journal': [],
        'daily_challenges': {},
        'created_date': datetime.now().isoformat()
    }
    return True

def authenticate_user(username, password):
    if username in st.session_state.users_db:
        return st.session_state.users_db[username]['password'] == hash_password(password)
    return False

# Personality quiz questions and MBTI mapping
PERSONALITY_QUESTIONS = [
    {
        "question": "How do you prefer to spend your free time?",
        "options": ["Socializing with friends", "Reading a book alone", "Exploring new places", "Working on personal projects"],
        "traits": ["Extroversion", "Introversion", "Openness", "Conscientiousness"]
    },
    {
        "question": "When making decisions, you rely more on:",
        "options": ["Logic and analysis", "Feelings and values", "Past experiences", "Future possibilities"],
        "traits": ["Thinking", "Feeling", "Sensing", "Intuition"]
    },
    {
        "question": "In group projects, you typically:",
        "options": ["Take the lead", "Support others", "Focus on details", "Generate creative ideas"],
        "traits": ["Extroversion", "Agreeableness", "Conscientiousness", "Openness"]
    },
    {
        "question": "You feel most energized when:",
        "options": ["Around many people", "In quiet environments", "Trying new things", "Following routines"],
        "traits": ["Extroversion", "Introversion", "Openness", "Conscientiousness"]
    },
    {
        "question": "Your ideal vacation would be:",
        "options": ["Adventure travel", "Peaceful retreat", "Cultural exploration", "Planned itinerary"],
        "traits": ["Openness", "Introversion", "Openness", "Conscientiousness"]
    },
    {
        "question": "When facing conflict, you:",
        "options": ["Address it directly", "Avoid confrontation", "Seek compromise", "Analyze all angles"],
        "traits": ["Extroversion", "Agreeableness", "Agreeableness", "Thinking"]
    },
    {
        "question": "You're most motivated by:",
        "options": ["Recognition and praise", "Personal satisfaction", "Helping others", "Solving complex problems"],
        "traits": ["Extroversion", "Conscientiousness", "Agreeableness", "Thinking"]
    },
    {
        "question": "Your workspace is typically:",
        "options": ["Organized and neat", "Creative and messy", "Minimalist", "Functional"],
        "traits": ["Conscientiousness", "Openness", "Introversion", "Thinking"]
    },
    {
        "question": "When learning something new, you prefer:",
        "options": ["Hands-on practice", "Theoretical understanding", "Group discussions", "Self-study"],
        "traits": ["Sensing", "Intuition", "Extroversion", "Introversion"]
    },
    {
        "question": "Your biggest strength is:",
        "options": ["Leadership", "Empathy", "Creativity", "Analytical thinking"],
        "traits": ["Extroversion", "Agreeableness", "Openness", "Thinking"]
    }
]

MBTI_TYPES = {
    "INTJ": "The Architect - Strategic and innovative thinkers",
    "INTP": "The Thinker - Quiet and analytical problem-solvers",
    "ENTJ": "The Commander - Bold and imaginative leaders",
    "ENTP": "The Debater - Smart and curious innovators",
    "INFJ": "The Advocate - Inspiring and idealistic visionaries",
    "INFP": "The Mediator - Poetic and compassionate idealists",
    "ENFJ": "The Protagonist - Charismatic and inspiring leaders",
    "ENFP": "The Campaigner - Enthusiastic and creative free spirits",
    "ISTJ": "The Logistician - Practical and fact-minded reliable workers",
    "ISFJ": "The Protector - Warm-hearted and dedicated supporters",
    "ESTJ": "The Executive - Excellent administrators and natural organizers",
    "ESFJ": "The Consul - Extraordinarily caring and social people",
    "ISTP": "The Virtuoso - Bold and practical experimenters",
    "ISFP": "The Adventurer - Flexible and charming artists",
    "ESTP": "The Entrepreneur - Smart and energetic problem-solvers",
    "ESFP": "The Entertainer - Spontaneous and enthusiastic performers"
}

def calculate_personality_scores(answers):
    scores = {
        "Extroversion": 0,
        "Introversion": 0,
        "Openness": 0,
        "Conscientiousness": 0,
        "Agreeableness": 0,
        "Thinking": 0,
        "Feeling": 0,
        "Sensing": 0,
        "Intuition": 0
    }
    
    for i, answer in answers.items():
        question = PERSONALITY_QUESTIONS[i]
        trait = question["traits"][answer]
        scores[trait] += 1
    
    return scores

def determine_mbti(scores):
    mbti = ""
    
    # Extroversion vs Introversion
    mbti += "E" if scores["Extroversion"] > scores["Introversion"] else "I"
    
    # Sensing vs Intuition
    mbti += "S" if scores["Sensing"] > scores["Intuition"] else "N"
    
    # Thinking vs Feeling
    mbti += "T" if scores["Thinking"] > scores["Feeling"] else "F"
    
    # Judging vs Perceiving (using Conscientiousness as proxy for Judging)
    mbti += "J" if scores["Conscientiousness"] > 2 else "P"
    
    return mbti

def generate_personality_suggestions(scores, mbti_type):
    suggestions = []
    
    # Base suggestions on dominant traits
    dominant_traits = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    suggestion_templates = {
        "Extroversion": [
            "Join social clubs or networking groups",
            "Take on leadership roles in team projects",
            "Practice public speaking or presentations",
            "Engage in group fitness activities"
        ],
        "Introversion": [
            "Schedule regular quiet time for reflection",
            "Develop deep, meaningful one-on-one relationships",
            "Practice mindfulness and meditation",
            "Create a peaceful personal workspace"
        ],
        "Openness": [
            "Try creative hobbies like painting or writing",
            "Travel to new and unfamiliar places",
            "Learn about different cultures and philosophies",
            "Experiment with new technologies or methods"
        ],
        "Conscientiousness": [
            "Set clear goals and create action plans",
            "Use productivity tools and time management systems",
            "Develop consistent daily routines",
            "Take on organizing responsibilities"
        ],
        "Agreeableness": [
            "Volunteer for charitable causes",
            "Practice active listening skills",
            "Mediate conflicts between others",
            "Focus on team harmony and collaboration"
        ],
        "Thinking": [
            "Engage in logical puzzles and problem-solving",
            "Study analytical subjects like mathematics or science",
            "Practice critical thinking exercises",
            "Participate in debates or discussions"
        ],
        "Feeling": [
            "Express emotions through art or journaling",
            "Practice empathy and emotional intelligence",
            "Help others with their emotional needs",
            "Focus on values-based decision making"
        ]
    }
    
    for trait, score in dominant_traits:
        if trait in suggestion_templates and score > 0:
            suggestions.extend(random.sample(suggestion_templates[trait], min(3, len(suggestion_templates[trait]))))
    
    # Add MBTI-specific suggestions
    mbti_suggestions = {
        "INTJ": ["Develop strategic planning skills", "Study complex systems", "Work on independent projects"],
        "INTP": ["Explore theoretical concepts", "Engage in philosophical discussions", "Solve complex puzzles"],
        "ENTJ": ["Take leadership courses", "Start a business or initiative", "Mentor others"],
        "ENTP": ["Brainstorm innovative solutions", "Network with diverse people", "Explore multiple interests"],
        "INFJ": ["Practice counseling skills", "Write in a journal", "Advocate for causes you believe in"],
        "INFP": ["Express creativity through art", "Support humanitarian causes", "Explore personal values"],
        "ENFJ": ["Teach or mentor others", "Organize community events", "Develop communication skills"],
        "ENFP": ["Try new experiences regularly", "Connect with inspiring people", "Pursue passion projects"],
        "ISTJ": ["Create detailed plans and schedules", "Study historical subjects", "Maintain traditions"],
        "ISFJ": ["Care for others' wellbeing", "Preserve important memories", "Create stable environments"],
        "ESTJ": ["Take on management roles", "Organize events or projects", "Study business administration"],
        "ESFJ": ["Host social gatherings", "Support community activities", "Focus on relationship building"],
        "ISTP": ["Learn practical skills", "Work with tools or machinery", "Solve hands-on problems"],
        "ISFP": ["Explore artistic expression", "Spend time in nature", "Help individuals personally"],
        "ESTP": ["Engage in physical activities", "Take calculated risks", "Live in the moment"],
        "ESFP": ["Perform or entertain others", "Try new experiences", "Celebrate life's moments"]
    }
    
    if mbti_type in mbti_suggestions:
        suggestions.extend(mbti_suggestions[mbti_type])
    
    return suggestions[:20]

# Navigation functions
def show_back_button():
    if st.button("← Back", key="back_btn", help="Go back to main menu"):
        st.session_state.page = 'dashboard'
        st.rerun()

def navigate_to(page):
    st.session_state.page = page
    st.rerun()

# Login/Registration Page
def show_auth_page():
    st.title("🧠 PersonaVista")
    st.subheader("Discover Your True Self")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_btn"):
            if authenticate_user(username, password):
                st.session_state.current_user = username
                st.session_state.page = 'dashboard'
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Register")
        new_username = st.text_input("Username", key="reg_username")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register", key="reg_btn"):
            if new_password != confirm_password:
                st.error("Passwords don't match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            elif create_user(new_username, new_password, new_email):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists")

# Dashboard
def show_dashboard():
    st.title(f"Welcome back, {st.session_state.current_user}! 🌟")
    
    # Logout button
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.current_user = None
            st.session_state.page = 'login'
            st.rerun()
    
    st.markdown("### Choose your personality development journey:")
    
    # Feature grid
    features = [
        {"name": "🧩 Personality Quiz", "desc": "Discover your personality type with our comprehensive assessment", "page": "quiz"},
        {"name": "📊 Personality Analysis", "desc": "View detailed analysis and visualizations of your personality", "page": "analysis"},
        {"name": "🗺️ Personality Map", "desc": "Compare your personality with ideal traits", "page": "personality_map"},
        {"name": "🎮 Mini Games", "desc": "Fun games to develop your personality traits", "page": "games"},
        {"name": "🧘 Relaxation Tools", "desc": "Breathing exercises and relaxation techniques", "page": "relaxation"},
        {"name": "💡 Suggestion Engine", "desc": "Personalized recommendations for books, careers, and hobbies", "page": "suggestions"},
        {"name": "🏆 Daily Challenges", "desc": "Daily personality development challenges", "page": "challenges"},
        {"name": "📝 Mood Journal", "desc": "Track your mood and reflect on your journey", "page": "journal"},
        {"name": "💬 Quotes & Affirmations", "desc": "Inspirational quotes based on your personality", "page": "quotes"}
    ]
    
    cols = st.columns(3)
    for i, feature in enumerate(features):
        with cols[i % 3]:
            if st.button(f"{feature['name']}\n{feature['desc']}", key=f"feat_{i}", use_container_width=True):
                navigate_to(feature['page'])

# Personality Quiz
def show_quiz():
    show_back_button()
    st.title("🧩 Personality Assessment")
    
    if not st.session_state.quiz_completed:
        st.write("Answer these questions to discover your personality type:")
        
        # Progress bar
        current_question = len(st.session_state.quiz_answers)
        progress = current_question / len(PERSONALITY_QUESTIONS)
        st.progress(progress)
        st.write(f"Question {current_question + 1} of {len(PERSONALITY_QUESTIONS)}")
        
        if current_question < len(PERSONALITY_QUESTIONS):
            question_data = PERSONALITY_QUESTIONS[current_question]
            
            st.subheader(f"Q{current_question + 1}: {question_data['question']}")
            
            answer = st.radio(
                "Choose your answer:",
                range(len(question_data['options'])),
                format_func=lambda x: question_data['options'][x],
                key=f"q_{current_question}"
            )
            
            if st.button("Next Question", key=f"next_{current_question}"):
                st.session_state.quiz_answers[current_question] = answer
                if current_question + 1 == len(PERSONALITY_QUESTIONS):
                    st.session_state.quiz_completed = True
                    # Save results to user data
                    scores = calculate_personality_scores(st.session_state.quiz_answers)
                    mbti = determine_mbti(scores)
                    suggestions = generate_personality_suggestions(scores, mbti)
                    
                    user_data = st.session_state.users_db[st.session_state.current_user]
                    user_data['quiz_results'] = {
                        'scores': scores,
                        'mbti': mbti,
                        'suggestions': suggestions,
                        'date': datetime.now().isoformat()
                    }
                    user_data['personality_data'] = scores
                st.rerun()
    else:
        st.success("Quiz completed! 🎉")
        st.write("You can now view your personality analysis and other features.")
        if st.button("View Analysis"):
            navigate_to('analysis')

# Personality Analysis
def show_analysis():
    show_back_button()
    st.title("📊 Your Personality Analysis")
    
    user_data = st.session_state.users_db[st.session_state.current_user]
    
    if 'quiz_results' not in user_data:
        st.warning("Please complete the personality quiz first!")
        if st.button("Take Quiz"):
            navigate_to('quiz')
        return
    
    results = user_data['quiz_results']
    scores = results['scores']
    mbti = results['mbti']
    
    # MBTI Type Display
    st.subheader(f"Your MBTI Type: {mbti}")
    st.write(f"**{MBTI_TYPES.get(mbti, 'Unknown Type')}**")
    
    # Personality Scores Pie Chart
    st.subheader("Personality Trait Distribution")
    
    # Filter out zero scores for cleaner visualization
    filtered_scores = {k: v for k, v in scores.items() if v > 0}
    
    fig = px.pie(
        values=list(filtered_scores.values()),
        names=list(filtered_scores.keys()),
        title="Your Personality Traits",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig)
    
    # Bar Chart for detailed view
    st.subheader("Detailed Trait Scores")
    fig_bar = px.bar(
        x=list(scores.keys()),
        y=list(scores.values()),
        title="Personality Trait Scores",
        color=list(scores.values()),
        color_continuous_scale='viridis'
    )
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig_bar)
    
    # Suggestions
    st.subheader("Personalized Suggestions")
    suggestions = results['suggestions']
    
    for i, suggestion in enumerate(suggestions[:10], 1):
        st.write(f"{i}. {suggestion}")

# Personality Map
def show_personality_map():
    show_back_button()
    st.title("🗺️ Personality Map")
    
    user_data = st.session_state.users_db[st.session_state.current_user]
    
    if 'quiz_results' not in user_data:
        st.warning("Please complete the personality quiz first!")
        return
    
    scores = user_data['quiz_results']['scores']
    
    # Ideal personality profile (balanced)
    ideal_scores = {
        "Extroversion": 3,
        "Introversion": 2,
        "Openness": 4,
        "Conscientiousness": 4,
        "Agreeableness": 3,
        "Thinking": 2,
        "Feeling": 3,
        "Sensing": 2,
        "Intuition": 3
    }
    
    # Create comparison chart
    st.subheader("Your Personality vs Ideal Balance")
    
    traits = list(scores.keys())
    your_values = [scores.get(trait, 0) for trait in traits]
    ideal_values = [ideal_scores.get(trait, 0) for trait in traits]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=your_values,
        theta=traits,
        fill='toself',
        name='Your Personality',
        line_color='cyan'
    ))
    fig.add_trace(go.Scatterpolar(
        r=ideal_values,
        theta=traits,
        fill='toself',
        name='Ideal Balance',
        line_color='orange',
        opacity=0.6
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    
    st.plotly_chart(fig)
    
    # Analysis
    st.subheader("Gap Analysis")
    st.write("Areas for development:")
    
    for trait in traits:
        your_score = scores.get(trait, 0)
        ideal_score = ideal_scores.get(trait, 0)
        gap = ideal_score - your_score
        
        if gap > 1:
            st.write(f"📈 **{trait}**: Consider developing this trait more (+{gap} points)")
        elif gap < -1:
            st.write(f"📉 **{trait}**: You're strong in this area ({abs(gap)} points above ideal)")

# Mini Games
def show_games():
    show_back_button()
    st.title("🎮 Personality Development Games")
    
    game_type = st.selectbox("Choose a game:", 
                            ["Would You Rather", "Moral Dilemmas", "Fantasy Quotes", "Personality Quiz Game"])
    
    if game_type == "Would You Rather":
        show_would_you_rather()
    elif game_type == "Moral Dilemmas":
        show_moral_dilemmas()
    elif game_type == "Fantasy Quotes":
        show_fantasy_quotes()
    elif game_type == "Personality Quiz Game":
        show_personality_quiz_game()

def show_would_you_rather():
    st.subheader("🤔 Would You Rather?")
    
    scenarios = [
        ("Be able to read minds", "Be able to see the future"),
        ("Have unlimited creativity", "Have unlimited intelligence"),
        ("Lead a team of 100 people", "Work alone on important projects"),
        ("Travel back in time", "Travel to the future"),
        ("Be famous for your achievements", "Be anonymous but help many people"),
        ("Always tell the truth", "Always be tactful"),
        ("Have perfect memory", "Have perfect intuition"),
        ("Be extremely organized", "Be extremely spontaneous")
    ]
    
    if 'wyr_scenario' not in st.session_state:
        st.session_state.wyr_scenario = random.choice(scenarios)
    
    scenario = st.session_state.wyr_scenario
    st.write(f"**Would you rather...**")
    
    choice = st.radio("", [scenario[0], scenario[1]], key="wyr_choice")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Next Scenario"):
            st.session_state.wyr_scenario = random.choice(scenarios)
            st.rerun()
    
    with col2:
        if st.button("See Insight"):
            insights = {
                scenarios[0]: "This choice reflects your preference for understanding others vs. planning ahead.",
                scenarios[1]: "This shows whether you value artistic expression or analytical thinking more.",
                scenarios[2]: "This indicates your leadership style and social preferences.",
                scenarios[3]: "This reveals your relationship with time and change.",
                scenarios[4]: "This shows your values regarding recognition vs. impact.",
                scenarios[5]: "This reflects your communication style and values.",
                scenarios[6]: "This indicates whether you trust logic or intuition more.",
                scenarios[7]: "This shows your approach to structure vs. flexibility."
            }
            st.info(insights.get(scenario, "Every choice reveals something about your personality!"))

def show_moral_dilemmas():
    st.subheader("⚖️ Moral Dilemmas")
    
    dilemmas = [
        {
            "situation": "You find a wallet with $500 and an ID. No one is around.",
            "options": ["Return it immediately", "Take the money, return the wallet", "Keep everything", "Try to find the owner personally"],
            "insight": "This reveals your moral compass and integrity levels."
        },
        {
            "situation": "Your friend asks you to lie to their partner about where they were last night.",
            "options": ["Lie to help your friend", "Refuse and stay out of it", "Tell your friend to be honest", "Tell the partner the truth"],
            "insight": "This shows how you balance loyalty vs. honesty."
        },
        {
            "situation": "You can save either one person you know or five strangers.",
            "options": ["Save the person you know", "Save the five strangers", "Try to save everyone", "Cannot decide"],
            "insight": "This reveals your decision-making process under pressure."
        }
    ]
    
    if 'dilemma_index' not in st.session_state:
        st.session_state.dilemma_index = 0
    
    dilemma = dilemmas[st.session_state.dilemma_index % len(dilemmas)]
    
    st.write(f"**Situation:** {dilemma['situation']}")
    choice = st.radio("What would you do?", dilemma['options'])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Next Dilemma"):
            st.session_state.dilemma_index += 1
            st.rerun()
    
    with col2:
        if st.button("Get Insight"):
            st.info(dilemma['insight'])

def show_fantasy_quotes():
    st.subheader("✨ Fantasy Quotes Challenge")
    
    quotes = [
        {"quote": "The cave you fear to enter holds the treasure you seek.", "author": "Joseph Campbell"},
        {"quote": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle"},
        {"quote": "The only impossible journey is the one you never begin.", "author": "Tony Robbins"},
        {"quote": "Be yourself; everyone else is already taken.", "author": "Oscar Wilde"},
        {"quote": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein"}
    ]
    
    if 'quote_index' not in st.session_state:
        st.session_state.quote_index = 0
    
    quote_data = quotes[st.session_state.quote_index % len(quotes)]
    
    st.markdown(f"### *\"{quote_data['quote']}\"*")
    st.markdown(f"**— {quote_data['author']}**")
    
    st.write("**Reflect on this quote:**")
    reflection = st.text_area("How does this quote apply to your life?", key="quote_reflection")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Next Quote"):
            st.session_state.quote_index += 1
            st.rerun()
    
    with col2:
        if reflection and st.button("Save Reflection"):
            user_data = st.session_state.users_db[st.session_state.current_user]
            if 'reflections' not in user_data:
                user_data['reflections'] = []
            user_data['reflections'].append({
                'quote': quote_data['quote'],
                'author': quote_data['author'],
                'reflection': reflection,
                'date': datetime.now().isoformat()
            })
            st.success("Reflection saved!")

def show_personality_quiz_game():
    st.subheader("🧠 Quick Personality Insights")
    
    quick_questions = [
        {"q": "Your ideal Friday night:", "opts": ["Party with friends", "Movie at home", "Trying something new", "Working on a project"]},
        {"q": "You make decisions based on:", "opts": ["Logic", "Emotions", "Experience", "Intuition"]},
        {"q": "In a crisis, you:", "opts": ["Take charge", "Support others", "Stay calm", "Find solutions"]},
        {"q": "Your communication style:", "opts": ["Direct", "Diplomatic", "Enthusiastic", "Thoughtful"]}
    ]
    
    if 'mini_quiz_answers' not in st.session_state:
        st.session_state.mini_quiz_answers = {}
    
    for i, q_data in enumerate(quick_questions):
        st.write(f"**{q_data['q']}**")
        answer = st.radio("", q_data['opts'], key=f"mini_q_{i}")
        st.session_state.mini_quiz_answers[i] = answer
        st.write("")
    
    if st.button("Get Mini Analysis"):
        st.subheader("Quick Insights:")
        insights = [
            "You prefer social vs. solitary activities",
            "You use logical vs. emotional decision-making",
            "You take leadership vs. supportive roles",
            "You communicate directly vs. diplomatically"
        ]
        
        for i, insight in enumerate(insights):
            answer = st.session_state.mini_quiz_answers.get(i, "No answer")
            st.write(f"• {insight}: **{answer}**")

# Relaxation Tools
def show_relaxation():
    show_back_button()
    st.title("🧘 Relaxation Tools")
    
    tool = st.selectbox("Choose a relaxation technique:", 
                       ["Breathing Exercise", "Progressive Muscle Relaxation", "Mindfulness Timer", "Nature Sounds"])
    
    if tool == "Breathing Exercise":
        show_breathing_exercise()
    elif tool == "Progressive Muscle Relaxation":
        show_muscle_relaxation()
    elif tool == "Mindfulness Timer":
        show_mindfulness_timer()
    elif tool == "Nature Sounds":
        show_nature_sounds()

def show_breathing_exercise():
    st.subheader("🫁 Breathing Exercise")
    st.write("Follow the breathing pattern: 4 seconds in, 4 seconds hold, 4 seconds out")
    
    if 'breathing_active' not in st.session_state:
        st.session_state.breathing_active = False
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.breathing_active:
            if st.button("Start Breathing Exercise"):
                st.session_state.breathing_active = True
                st.rerun()
        else:
            if st.button("Stop Exercise"):
                st.session_state.breathing_active = False
                st.rerun()
    
    if st.session_state.breathing_active:
        # Animated breathing guide
        placeholder = st.empty()
        
        for cycle in range(5):  # 5 breathing cycles
            # Inhale
            for i in range(4):
                with placeholder.container():
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="width: {100 + i*20}px; height: {100 + i*20}px; 
                             background: radial-gradient(circle, #4CAF50, #2E7D32);
                             border-radius: 50%; margin: 0 auto; 
                             display: flex; align-items: center; justify-content: center;
                             font-size: 24px; color: white; font-weight: bold;">
                            INHALE
                        </div>
                        <p style="margin-top: 20px; font-size: 18px;">Breathe in slowly...</p>
                    </div>
                    """, unsafe_allow_html=True)
                time.sleep(1)
            
            # Hold
            for i in range(4):
                with placeholder.container():
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="width: 180px; height: 180px; 
                             background: radial-gradient(circle, #FF9800, #F57C00);
                             border-radius: 50%; margin: 0 auto; 
                             display: flex; align-items: center; justify-content: center;
                             font-size: 24px; color: white; font-weight: bold;">
                            HOLD
                        </div>
                        <p style="margin-top: 20px; font-size: 18px;">Hold your breath...</p>
                    </div>
                    """, unsafe_allow_html=True)
                time.sleep(1)
            
            # Exhale
            for i in range(4):
                with placeholder.container():
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="width: {180 - i*20}px; height: {180 - i*20}px; 
                             background: radial-gradient(circle, #2196F3, #1976D2);
                             border-radius: 50%; margin: 0 auto; 
                             display: flex; align-items: center; justify-content: center;
                             font-size: 24px; color: white; font-weight: bold;">
                            EXHALE
                        </div>
                        <p style="margin-top: 20px; font-size: 18px;">Breathe out slowly...</p>
                    </div>
                    """, unsafe_allow_html=True)
                time.sleep(1)
        
        st.session_state.breathing_active = False
        st.success("Breathing exercise completed! 🌟")

def show_muscle_relaxation():
    st.subheader("💪 Progressive Muscle Relaxation")
    st.write("Tense and relax each muscle group for 5 seconds")
    
    muscle_groups = [
        "Forehead and scalp",
        "Eyes and cheeks", 
        "Mouth and jaw",
        "Neck and shoulders",
        "Arms and hands",
        "Chest and upper back",
        "Abdomen",
        "Lower back and hips",
        "Thighs",
        "Calves and feet"
    ]
    
    if st.button("Start Relaxation"):
        for i, group in enumerate(muscle_groups):
            st.write(f"**Step {i+1}: {group}**")
            st.write("Tense these muscles for 5 seconds, then relax...")
            time.sleep(2)  # Shorter delay for demo
        st.success("Progressive muscle relaxation completed!")

def show_mindfulness_timer():
    st.subheader("⏰ Mindfulness Timer")
    
    duration = st.slider("Select duration (minutes):", 1, 30, 5)
    
    if st.button("Start Mindfulness Session"):
        st.info(f"Mindfulness session started for {duration} minutes")
        st.write("Focus on your breathing and stay present in the moment...")
        
        # Simple countdown display
        with st.empty():
            for remaining in range(duration * 60, 0, -1):
                mins, secs = divmod(remaining, 60)
                st.markdown(f"### Time remaining: {mins:02d}:{secs:02d}")
                time.sleep(1)
        
        st.success("Mindfulness session completed! 🧘‍♀️")

def show_nature_sounds():
    st.subheader("🌿 Nature Sounds")
    st.write("Imagine these peaceful nature sounds while you relax:")
    
    sounds = [
        "🌊 Ocean waves",
        "🌧️ Gentle rain",
        "🐦 Forest birds",
        "🔥 Crackling fire",
        "💨 Mountain wind"
    ]
    
    selected_sound = st.selectbox("Choose a nature sound:", sounds)
    
    if st.button("Play Sound (Visualization)"):
        st.success(f"Now playing: {selected_sound}")
        st.write("Close your eyes and imagine this peaceful sound surrounding you...")
        
        # Visual representation
        if "Ocean" in selected_sound:
            st.markdown("🌊🌊🌊 *Gentle waves lapping against the shore* 🌊🌊🌊")
        elif "rain" in selected_sound:
            st.markdown("🌧️💧 *Soft raindrops on leaves* 💧🌧️")
        elif "birds" in selected_sound:
            st.markdown("🐦🎵 *Melodic bird songs in the forest* 🎵🐦")
        elif "fire" in selected_sound:
            st.markdown("🔥✨ *Warm crackling of a cozy fire* ✨🔥")
        elif "wind" in selected_sound:
            st.markdown("💨🍃 *Gentle breeze through the trees* 🍃💨")

# Suggestion Engine
def show_suggestions():
    show_back_button()
    st.title("💡 Personalized Suggestion Engine")
    
    user_data = st.session_state.users_db[st.session_state.current_user]
    
    if 'quiz_results' not in user_data:
        st.warning("Please complete the personality quiz first!")
        return
    
    mbti = user_data['quiz_results']['mbti']
    scores = user_data['quiz_results']['scores']
    
    st.subheader(f"Suggestions for {mbti} personality type:")
    
    category = st.selectbox("Choose category:", 
                           ["Books", "Hobbies", "Career Paths", "Games", "Learning Resources", "Social Activities"])
    
    suggestions_db = {
        "Books": {
            "INTJ": ["Thinking, Fast and Slow", "The Art of War", "Sapiens", "1984"],
            "ENFP": ["Big Magic", "The Alchemist", "Wild", "Eat Pray Love"],
            "ISTJ": ["Good to Great", "The 7 Habits", "Getting Things Done", "Atomic Habits"],
            "ESFP": ["The Happiness Project", "Yes Please", "Bossypants", "Wild"]
        },
        "Hobbies": {
            "INTJ": ["Chess", "Strategy games", "Programming", "Reading philosophy"],
            "ENFP": ["Creative writing", "Photography", "Travel blogging", "Improv theater"],
            "ISTJ": ["Gardening", "Model building", "Historical research", "Organizing"],
            "ESFP": ["Dancing", "Party planning", "Fashion", "Social media content creation"]
        },
        "Career Paths": {
            "INTJ": ["Software architect", "Research scientist", "Strategic consultant", "Systems analyst"],
            "ENFP": ["Marketing creative", "Counselor", "Entrepreneur", "Journalist"],
            "ISTJ": ["Accountant", "Project manager", "Administrator", "Quality assurance"],
            "ESFP": ["Event coordinator", "Sales representative", "Teacher", "Performer"]
        },
        "Games": {
            "INTJ": ["Complex strategy games", "Puzzle games", "Chess variants", "Simulation games"],
            "ENFP": ["Party games", "Collaborative games", "Creative games", "Adventure games"],
            "ISTJ": ["Logic puzzles", "Traditional board games", "Solitaire variants", "Organization games"],
            "ESFP": ["Social games", "Active games", "Music games", "Improvisational games"]
        }
    }
    
    # Get suggestions for the category
    if category in suggestions_db:
        mbti_suggestions = suggestions_db[category].get(mbti, [])
        
        # Add some general suggestions based on personality scores
        general_suggestions = []
        if scores.get("Openness", 0) > 3:
            general_suggestions.extend(["Creative workshops", "Art classes", "Cultural events"])
        if scores.get("Extroversion", 0) > scores.get("Introversion", 0):
            general_suggestions.extend(["Networking events", "Group activities", "Public speaking"])
        
        all_suggestions = mbti_suggestions + general_suggestions
        
        st.subheader(f"{category} Recommendations:")
        for i, suggestion in enumerate(all_suggestions[:8], 1):
            st.write(f"{i}. {suggestion}")
    
    # Additional personalized suggestions
    st.subheader("Based on your personality traits:")
    trait_suggestions = generate_personality_suggestions(scores, mbti)
    
    for i, suggestion in enumerate(trait_suggestions[:5], 1):
        st.write(f"• {suggestion}")

# Daily Challenges
def show_challenges():
    show_back_button()
    st.title("🏆 Daily Personality Challenges")
    
    user_data = st.session_state.users_db[st.session_state.current_user]
    today = date.today().isoformat()
    
    if 'daily_challenges' not in user_data:
        user_data['daily_challenges'] = {}
    
    # Generate today's challenge if not exists
    if today not in user_data['daily_challenges']:
        challenges = [
            "Start a conversation with someone new today",
            "Practice active listening in all your conversations",
            "Take on a small leadership role in a group setting",
            "Try a creative activity for 30 minutes",
            "Help someone without being asked",
            "Practice mindfulness for 10 minutes",
            "Write down 3 things you're grateful for",
            "Step out of your comfort zone in a small way",
            "Give a genuine compliment to 3 people",
            "Organize one area of your living/work space"
        ]
        
        user_data['daily_challenges'][today] = {
            'challenge': random.choice(challenges),
            'completed': False,
            'reflection': ''
        }
    
    today_challenge = user_data['daily_challenges'][today]
    
    st.subheader(f"Today's Challenge ({datetime.now().strftime('%B %d, %Y')})")
    st.markdown(f"### 🎯 {today_challenge['challenge']}")
    
    if not today_challenge['completed']:
        reflection = st.text_area("How did you complete this challenge? (Reflect on your experience)")
        
        if st.button("Mark as Completed"):
            today_challenge['completed'] = True
            today_challenge['reflection'] = reflection
            st.success("Challenge completed! Well done! 🌟")
            st.rerun()
    else:
        st.success("✅ Challenge completed!")
        if today_challenge['reflection']:
            st.write("**Your reflection:**")
            st.write(today_challenge['reflection'])
    
    # Challenge history
    st.subheader("Challenge History")
    completed_challenges = [(date_str, data) for date_str, data in user_data['daily_challenges'].items() 
                           if data['completed']]
    
    if completed_challenges:
        st.write(f"You've completed {len(completed_challenges)} challenges!")
        
        for date_str, challenge_data in sorted(completed_challenges, reverse=True)[:7]:
            with st.expander(f"{date_str}: {challenge_data['challenge'][:50]}..."):
                st.write(f"**Challenge:** {challenge_data['challenge']}")
                if challenge_data['reflection']:
                    st.write(f"**Reflection:** {challenge_data['reflection']}")
    else:
        st.write("No completed challenges yet. Start with today's challenge!")

# Mood Journal
def show_journal():
    show_back_button()
    st.title("📝 Mood & Reflection Journal")
    
    user_data = st.session_state.users_db[st.session_state.current_user]
    
    if 'mood_journal' not in user_data:
        user_data['mood_journal'] = []
    
    tab1, tab2 = st.tabs(["New Entry", "Journal History"])
    
    with tab1:
        st.subheader("Create New Journal Entry")
        
        col1, col2 = st.columns(2)
        with col1:
            mood = st.selectbox("How are you feeling today?", 
                               ["😄 Great", "😊 Good", "😐 Okay", "😔 Down", "😤 Frustrated", "😰 Anxious", "🤔 Confused"])
        
        with col2:
            energy = st.slider("Energy Level (1-10)", 1, 10, 5)
        
        journal_text = st.text_area("Write about your day, thoughts, or feelings:", 
                                   placeholder="What happened today? How did you handle challenges? What are you grateful for?")
        
        if st.button("Save Entry"):
            if journal_text:
                entry = {
                    'date': datetime.now().isoformat(),
                    'mood': mood,
                    'energy': energy,
                    'text': journal_text
                }
                user_data['mood_journal'].append(entry)
                st.success("Journal entry saved! 📖")
                st.rerun()
            else:
                st.warning("Please write something in your journal entry.")
    
    with tab2:
        st.subheader("Your Journal History")
        
        if user_data['mood_journal']:
            # Mood tracking chart
            if len(user_data['mood_journal']) > 1:
                df_mood = pd.DataFrame(user_data['mood_journal'])
                df_mood['date'] = pd.to_datetime(df_mood['date'])
                df_mood['mood_numeric'] = df_mood['mood'].map({
                    "😄 Great": 5, "😊 Good": 4, "😐 Okay": 3, 
                    "😔 Down": 2, "😤 Frustrated": 2, "😰 Anxious": 1, "🤔 Confused": 2
                })
                
                fig = px.line(df_mood, x='date', y='mood_numeric', 
                             title='Mood Tracking Over Time', markers=True)
                fig.update_yaxis(ticktext=["Anxious", "Down", "Okay", "Good", "Great"], 
                               tickvals=[1, 2, 3, 4, 5])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig)
            
            # Recent entries
            st.subheader("Recent Entries")
            for entry in sorted(user_data['mood_journal'], key=lambda x: x['date'], reverse=True)[:5]:
                date_obj = datetime.fromisoformat(entry['date'])
                with st.expander(f"{entry['mood']} - {date_obj.strftime('%B %d, %Y at %I:%M %p')}"):
                    st.write(f"**Energy Level:** {entry['energy']}/10")
                    st.write(f"**Entry:** {entry['text']}")
        else:
            st.write("No journal entries yet. Create your first entry above!")

# Quotes and Affirmations
def show_quotes():
    show_back_button()
    st.title("💬 Quotes & Affirmations")
    
    user_data = st.session_state.users_db[st.session_state.current_user]
    
    # Get user's MBTI type if available
    mbti = "ENFP"  # Default
    if 'quiz_results' in user_data:
        mbti = user_data['quiz_results']['mbti']
    
    tab1, tab2, tab3 = st.tabs(["Daily Quote", "Affirmations", "Motivational"])
    
    with tab1:
        st.subheader("Quote of the Day")
        
        personality_quotes = {
            "INTJ": [
                "The cave you fear to enter holds the treasure you seek. - Joseph Campbell",
                "Logic will get you from A to B. Imagination will take you everywhere. - Einstein",
                "In the depths of winter, I finally learned that there was in me an invincible summer. - Camus"
            ],
            "ENFP": [
                "Be yourself; everyone else is already taken. - Oscar Wilde",
                "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
                "Life is either a daring adventure or nothing at all. - Helen Keller"
            ],
            "ISTJ": [
                "Success is the sum of small efforts repeated day in and day out. - Robert Collier",
                "The secret of getting ahead is getting started. - Mark Twain",
                "Quality is never an accident; it is always the result of intelligent effort. - John Ruskin"
            ],
            "ESFP": [
                "Life is short. Smile while you still have teeth. - Unknown",
                "Happiness is not something ready made. It comes from your own actions. - Dalai Lama",
                "The best way to cheer yourself up is to try to cheer somebody else up. - Mark Twain"
            ]
        }
        
        quotes = personality_quotes.get(mbti, personality_quotes["ENFP"])
        today_quote = quotes[datetime.now().day % len(quotes)]
        
        st.markdown(f"### *\"{today_quote.split(' - ')[0]}\"*")
        st.markdown(f"**— {today_quote.split(' - ', 1)[1]}**")
        
        if st.button("Get New Quote"):
            st.session_state.quote_refresh = random.choice(quotes)
            st.rerun()
    
    with tab2:
        st.subheader("Personal Affirmations")
        
        affirmations = {
            "INTJ": [
                "I trust my vision and my ability to make it reality",
                "My analytical mind helps me solve complex problems",
                "I am confident in my strategic thinking abilities"
            ],
            "ENFP": [
                "I embrace my creativity and share it with the world",
                "My enthusiasm inspires others around me",
                "I trust my intuition to guide me toward opportunities"
            ],
            "ISTJ": [
                "I am reliable and others can count on me",
                "My attention to detail creates excellence in everything I do",
                "I build strong foundations for lasting success"
            ],
            "ESFP": [
                "I bring joy and positivity to every situation",
                "My authentic self is worthy of love and respect",
                "I live fully in each moment and appreciate life's beauty"
            ]
        }
        
        user_affirmations = affirmations.get(mbti, affirmations["ENFP"])
        
        st.write("**Your personalized affirmations:**")
        for i, affirmation in enumerate(user_affirmations, 1):
            st.write(f"{i}. *{affirmation}*")
            
        st.write("\n**Practice:** Repeat these affirmations daily, especially in the morning or before challenging situations.")
    
    with tab3:
        st.subheader("Motivational Boost")
        
        motivational_quotes = [
            "You are braver than you believe, stronger than you seem, and smarter than you think.",
            "The only way to do great work is to love what you do.",
            "Your limitation—it's only your imagination.",
            "Great things never come from comfort zones.",
            "Dream it. Wish it. Do it.",
            "Success doesn't just find you. You have to go out and get it.",
            "The harder you work for something, the greater you'll feel when you achieve it.",
            "Don't stop when you're tired. Stop when you're done."
        ]
        
        if st.button("Need Motivation?"):
            quote = random.choice(motivational_quotes)
            st.success(f"💪 {quote}")
        
        st.write("**Quick Motivation:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("I need encouragement"):
                st.balloons()
                st.success("You've got this! Every step forward is progress! 🌟")
        
        with col2:
            if st.button("I'm feeling overwhelmed"):
                st.info("Take a deep breath. Break big tasks into smaller ones. You don't have to do everything at once. 🧘‍♀️")

# Main application logic
def main():
    init_session_state()
    
    # Route to appropriate page
    if st.session_state.current_user is None:
        show_auth_page()
    else:
        if st.session_state.page == 'dashboard':
            show_dashboard()
        elif st.session_state.page == 'quiz':
            show_quiz()
        elif st.session_state.page == 'analysis':
            show_analysis()
        elif st.session_state.page == 'personality_map':
            show_personality_map()
        elif st.session_state.page == 'games':
            show_games()
        elif st.session_state.page == 'relaxation':
            show_relaxation()
        elif st.session_state.page == 'suggestions':
            show_suggestions()
        elif st.session_state.page == 'challenges':
            show_challenges()
        elif st.session_state.page == 'journal':
            show_journal()
        elif st.session_state.page == 'quotes':
            show_quotes()
        else:
            show_dashboard()

if __name__ == "__main__":
    main()
