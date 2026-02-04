import streamlit as st
import os
import random
import base64
from dataclasses import dataclass
from typing import List, Dict, Optional
from dotenv import load_dotenv
from groq import Groq

# --- Configuration & Setup ---
load_dotenv()

st.set_page_config(
    page_title="Mystical Tarot Oracle",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Mystical Atmosphere ---
st.markdown("""
<style>
    /* General Dark Mystical Theme */
    .stApp {
        background-color: #0e0e12;
        color: #e0d2b4;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #bfa15f !important;
        font-family: 'Cinzel', serif;
        text-shadow: 2px 2px 4px #000000;
    }
    
    /* Card Container */
    .tarot-card-container {
        perspective: 1000px;
        margin: 10px;
        text-align: center;
        background-color: #1a1a24;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #332d20;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
        height: 100%; /* Ensure uniform height */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .tarot-card-img {
        width: 100%;
        max-width: 200px;
        border-radius: 10px;
        transition: transform 0.6s;
        box-shadow: 0 0 15px rgba(191, 161, 95, 0.2); 
    }
    
    /* Reversed Card Styling */
    .reversed {
        transform: rotate(180deg);
    }
    
    /* Captions */
    .card-caption {
        margin-top: 10px;
        font-size: 0.9em;
        color: #cfc0a5;
        font-style: italic;
    }
    .position-label {
        color: #8a7c5d;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 0.8em;
        margin-bottom: 5px;
    }

    /* Button Styling */
    .stButton>button {
        color: #0e0e12 !important; /* Force black text */
        background: linear-gradient(45deg, #cfb06d, #e6d2a0); /* Gold Gradient */
        border: 1px solid #bfa15f;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        width: 100%;
        padding: 0.5rem 1rem;
        font-size: 1.1em;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #e6d2a0, #cfb06d);
        box-shadow: 0 0 15px #bfa15f;
        transform: scale(1.02);
    }
    .stButton>button:active {
        background-color: #bfa15f;
        color: #fff !important;
    }
    
    /* Divider */
    hr {
        border-color: #332d20;
    }
</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---
def get_img_as_base64(file_path):
    """
    Reads a local image file and returns a base64 string focusing on web compatibility.
    """
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    return f"data:image/jpeg;base64,{encoded}"

# --- Data Structures ---

@dataclass
class Card:
    name_en: str
    name_cn: str
    image_base64: str
    meaning_up_en: str
    meaning_rev_en: str
    meaning_up_cn: str
    meaning_rev_cn: str

@dataclass
class DrawnCard:
    card: Card
    is_reversed: bool
    position_name_en: str
    position_name_cn: str

# --- Deck Initialization (Local Files) ---

SUITS = [
    ("Wands", "权杖", "Wands", "Wands"),
    ("Cups", "圣杯", "Cups", "Cups"),
    ("Swords", "宝剑", "Swords", "Swords"),
    ("Pentacles", "星币", "Pentacles", "Pents")
]

RANKS = [
    ("Ace", "王牌", "01"), ("Two", "2", "02"), ("Three", "3", "03"), ("Four", "4", "04"),
    ("Five", "5", "05"), ("Six", "6", "06"), ("Seven", "7", "07"), ("Eight", "8", "08"),
    ("Nine", "9", "09"), ("Ten", "10", "10"), ("Page", "侍从", "11"), ("Knight", "骑士", "12"),
    ("Queen", "皇后", "13"), ("King", "国王", "14")
]

def build_deck() -> List[Card]:
    deck = []
    
    # Major Arcana Mapping
    # Filenames: RWS_Tarot_00_Fool.jpg, RWS_Tarot_01_Magician.jpg, etc.
    majors_data = [
        ("The Fool", "愚者", "RWS_Tarot_00_Fool.jpg"),
        ("The Magician", "魔术师", "RWS_Tarot_01_Magician.jpg"),
        ("The High Priestess", "女祭司", "RWS_Tarot_02_High_Priestess.jpg"),
        ("The Empress", "皇后", "RWS_Tarot_03_Empress.jpg"),
        ("The Emperor", "皇帝", "RWS_Tarot_04_Emperor.jpg"),
        ("The Hierophant", "教皇", "RWS_Tarot_05_Hierophant.jpg"),
        ("The Lovers", "恋人", "RWS_Tarot_06_Lovers.jpg"),
        ("The Chariot", "战车", "RWS_Tarot_07_Chariot.jpg"),
        ("Strength", "力量", "RWS_Tarot_08_Strength.jpg"),
        ("The Hermit", "隐士", "RWS_Tarot_09_Hermit.jpg"),
        ("Wheel of Fortune", "命运之轮", "RWS_Tarot_10_Wheel_of_Fortune.jpg"),
        ("Justice", "正义", "RWS_Tarot_11_Justice.jpg"),
        ("The Hanged Man", "倒吊人", "RWS_Tarot_12_Hanged_Man.jpg"),
        ("Death", "死神", "RWS_Tarot_13_Death.jpg"),
        ("Temperance", "节制", "RWS_Tarot_14_Temperance.jpg"),
        ("The Devil", "恶魔", "RWS_Tarot_15_Devil.jpg"),
        ("The Tower", "高塔", "RWS_Tarot_16_Tower.jpg"),
        ("The Star", "星星", "RWS_Tarot_17_Star.jpg"),
        ("The Moon", "月亮", "RWS_Tarot_18_Moon.jpg"),
        ("The Sun", "太阳", "RWS_Tarot_19_Sun.jpg"),
        ("Judgement", "审判", "RWS_Tarot_20_Judgement.jpg"),
        ("The World", "世界", "RWS_Tarot_21_World.jpg"),
    ]
    
    base_path_major = os.path.join("Major Arcana")
    
    for name_en, name_cn, filename in majors_data:
        full_path = os.path.join(base_path_major, filename)
        img_b64 = get_img_as_base64(full_path)
        
        # Fallback if specific file missing
        if not img_b64:
             # Just a placeholder in case logic fails, but user said files are there.
             img_b64 = "" 

        deck.append(Card(
            name_en=name_en, name_cn=name_cn, image_base64=img_b64,
            meaning_up_en="Major Arcana Archetype", meaning_rev_en="Blocked Archetype",
            meaning_up_cn="大阿卡纳原型", meaning_rev_cn="原型受阻"
        ))
        
    # Minor Arcana
    # Path: Minor Arcana/{Suit Folder}/{SuitPrefix}{XX}.jpg
    base_path_minor = os.path.join("Minor Arcana")
    
    for suit_en, suit_cn, suit_folder, suit_prefix in SUITS:
        for i, (rank_en, rank_cn, rank_val) in enumerate(RANKS):
            name_en = f"{rank_en} of {suit_en}"
            name_cn = f"{suit_cn}{rank_cn}"
            
            # Construct filename: e.g., Cups/Cups01.jpg OR Pentacles/Pents01.jpg
            img_filename = f"{suit_prefix}{rank_val}.jpg" 
            full_path = os.path.join(base_path_minor, suit_folder, img_filename)
            
            img_b64 = get_img_as_base64(full_path)
            if not img_b64:
                img_b64 = ""
                
            deck.append(Card(
                name_en=name_en, name_cn=name_cn, image_base64=img_b64,
                meaning_up_en=f"Energy of {suit_en}", meaning_rev_en=f"Inverted {suit_en}",
                meaning_up_cn=f"{suit_cn}的正位能量", meaning_rev_cn=f"{suit_cn}的逆位能量"
            ))
            
    return deck

DECK = build_deck()
CARD_BACK_B64 = get_img_as_base64("card back design.jpg")

# --- Spreads Definitions ---
SPREADS = {
    "Single Card": {
        "positions_en": ["Guidance"],
        "positions_cn": ["指引"],
        "desc_en": "Quick insight or Yes/No.",
        "desc_cn": "快速指引或是非题。",
        "count": 1
    },
    "Three Card (Time)": {
        "positions_en": ["Past", "Present", "Future"],
        "positions_cn": ["过去", "现在", "未来"],
        "desc_en": "Linear time flow analysis.",
        "desc_cn": "时间流向分析。",
        "count": 3
    },
    "Three Card (Trinity)": {
        "positions_en": ["Mind", "Body", "Spirit"],
        "positions_cn": ["精神", "身体", "灵魂"],
        "desc_en": "Holistic self-analysis.",
        "desc_cn": "身心灵全方位分析。",
        "count": 3
    },
    "The Lovers": {
        "positions_en": ["You", "Them", "Dynamic", "Advice"],
        "positions_cn": ["你", "对方", "关系现状", "建议"],
        "desc_en": "Relationship analysis.",
        "desc_cn": "关系分析。",
        "count": 4
    },
    "Celtic Cross": {
        "positions_en": [
            "Present", "Challenge", "Past", "Recent Past", "Goals", "Future", 
            "Attitude", "Environment", "Hopes & Fears", "Outcome"
        ],
        "positions_cn": [
            "现状", "挑战", "过去", "近期", "目标", "未来", 
            "态度", "环境", "希望/恐惧", "结果"
        ],
        "desc_en": "Comprehensive traditional spread.",
        "desc_cn": "最传统的全方位深度分析。",
        "count": 10
    }
}

# --- Sidebar & Setup ---

with st.sidebar:
    st.header("🔮 Configuration | 设置")
    
    # Language
    lang = st.radio("Language | 语言", ["English", "Chinese"], index=0)
    is_cn = lang == "Chinese"
    
    # Model
    model = st.selectbox("AI Model", ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768"], index=0)
    
    st.markdown("---")
    
    # Spread Selection
    spread_name = st.selectbox(
        "Choose Spread | 选择牌阵", 
        list(SPREADS.keys()),
        index=0
    )
    spread_info = SPREADS[spread_name]
    st.info(spread_info["desc_cn"] if is_cn else spread_info["desc_en"])
    
    if st.button("Reset / New Reading | 重置"):
        for key in ['stage', 'drawn_cards', 'interpretation', 'question']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.stage = 'setup'
        st.rerun()

# --- Main App Logic ---

# Initialize Session State
if 'stage' not in st.session_state:
    st.session_state.stage = 'setup' # setup -> shuffling -> drawn
if 'drawn_cards' not in st.session_state:
    st.session_state.drawn_cards = []
if 'interpretation' not in st.session_state:
    st.session_state.interpretation = ""

# Header
st.title("🌌 Mystical Tarot Oracle")
st.markdown("*Ask the cards, and the universe shall answer.*" if not is_cn else "*问牌于心，宇宙自会有灵。*")

# API Key Check
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ GROQ_API_KEY not found in .env file. Please add it to unlock the Oracle." if not is_cn else "⚠️ 未找到 GROQ_API_KEY。请在 .env 文件中添加以解锁神谕。")

# Input
if st.session_state.stage == 'setup':
    st.markdown("### 1. Meditate on your question | 冥想你的问题")
    question = st.text_input(
        "Your Query | 你的困惑", 
        placeholder="What does fate hold for me? | 命运对我有什么安排？"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Centered Button
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if question and st.button("🔮 Begin Ritual | 开始仪式"):
            st.session_state.question = question
            st.session_state.stage = 'shuffling'
            st.rerun()

# Shuffling Phase
elif st.session_state.stage == 'shuffling':
    st.markdown("### 🌀 The Deck is Shuffling...", unsafe_allow_html=True)
    
    msg_en = "Focus your energy... When you feel the connection, click Stop."
    msg_cn = "集中精神... 当你感到感应时，点击停止。"
    st.markdown(f"*{msg_cn if is_cn else msg_en}*")
    
    st.divider()
    
    # Optimized Shuffling UI: Center aligned, Card Back
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if CARD_BACK_B64:
             st.markdown(f'<img src="{CARD_BACK_B64}" style="width:100%; border-radius:10px; box-shadow: 0 0 20px #bfa15f;">', unsafe_allow_html=True)
        else:
             st.text("Card Back Image Not Found")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("✋ Stop & Draw | 停止并抽牌", type="primary"):
            # Perform Draw logic
            count = SPREADS[spread_name]['count']
            selected_cards = random.sample(DECK, count)
            
            drawn_data = []
            positions = spread_info['positions_cn'] if is_cn else spread_info['positions_en']
            
            for i, card in enumerate(selected_cards):
                is_reversed = random.choice([True, False])
                pos_name = positions[i]
                drawn_data.append(DrawnCard(card, is_reversed, pos_name, pos_name))
                
            st.session_state.drawn_cards = drawn_data
            st.session_state.stage = 'drawn'
            st.rerun()

# Display & Interpret Phase
elif st.session_state.stage == 'drawn':
    st.markdown(f"### Question: **{st.session_state.question}**")
    
    # Display Cards
    count = len(st.session_state.drawn_cards)
    
    # Rows of 5
    cols_per_row = 5
    for i in range(0, count, cols_per_row):
        row_cards = st.session_state.drawn_cards[i:i+cols_per_row]
        cols = st.columns(cols_per_row)
        
        for idx, dc in enumerate(row_cards):
            with cols[idx]:
                st.markdown(f"""
                <div class="tarot-card-container">
                    <div class="position-label">{dc.position_name_cn if is_cn else dc.position_name_en}</div>
                    <img src="{dc.card.image_base64}" class="tarot-card-img {'reversed' if dc.is_reversed else ''}">
                    <div class="card-caption">
                        {dc.card.name_cn if is_cn else dc.card.name_en}<br>
                        ({'逆位' if is_cn and dc.is_reversed else '正位' if is_cn else 'Reversed' if dc.is_reversed else 'Upright'})
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    st.markdown("---")
    
    # Interpretation Button
    if st.button("📜 Consult the Oracle | 咨询神谕"):
        if not api_key:
            st.error("Please enter a valid Groq API Key in the sidebar.")
        else:
            client = Groq(api_key=api_key)
            
            # Construct Prompt
            card_details = []
            for dc in st.session_state.drawn_cards:
                orientation = "Reversed" if dc.is_reversed else "Upright"
                name = dc.card.name_cn if is_cn else dc.card.name_en
                card_details.append(f"- Position: {dc.position_name_en}, Card: {name}, Orientation: {orientation}")
            
            cards_text = "\n".join(card_details)
            lang_instruction = "Respond in CHINESE (Traditional/Mystical style)." if is_cn else "Respond in ENGLISH (Shakespearean/Mystical style)."
            
            system_prompt = f"""
            You are an Ancient Mystic Oracle. Your voice is ceremonial, archaic, and profound. 
            Do not speak like a modern AI. Speak of threads of fate, cosmic energies, and the weave of destiny.
            1. Analyze the cards drawn in the specific spread positions.
            2. Synthesize a comprehensive meaning linking the cards together.
            3. Respect strict Reversal meanings (Reversed = Internalized, blocked, or opposite energy).
            4. {lang_instruction}
            """
            
            user_prompt = f"""
            Question: {st.session_state.question}
            Spread: {spread_name}
            
            Cards Drawn:
            {cards_text}
            
            Interpret the path laid out before the seeker.
            """
            
            with st.spinner("The Oracle is gazing into the void... | 神谕正在凝视虚空..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        model=model,
                        temperature=0.7,
                        max_tokens=2048,
                    )
                    st.session_state.interpretation = chat_completion.choices[0].message.content
                except Exception as e:
                    st.error(f"The spirits remain silent (Error): {e}")

    # Display Result
    if st.session_state.interpretation:
        st.markdown("### 🔮 The Oracle Speaks")
        st.markdown(f">{st.session_state.interpretation}")

