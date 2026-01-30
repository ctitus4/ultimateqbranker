import streamlit as st
import random
import itertools
import json
import pandas as pd

# -----------------------
# QB List
# -----------------------
qbs = [
    "Jordan Love","Caleb Williams","JJ McCarthy","Jared Goff","Dak Prescott",
    "Jaxon Dart","Jalen Hurts","Jayden Daniels","Matt Stafford","Sam Darnold",
    "Kyler Murray","Brock Purdy","Tyler Shough","Baker Mayfield","Bryce Young",
    "Michael Penix","Josh Allen","Tua Tagovailoa","Drake Maye","Justin Fields",
    "Cam Ward","Trevor Lawrence","CJ Stroud","Daniel Jones","Shedeur Sanders",
    "Lamar Jackson","Aaron Rodgers","Joe Burrow","Justin Herbert","Geno Smith",
    "Bo Nix","Patrick Mahomes"
]

DATA_FILE = "nfl_qb_rankings.json"

# -----------------------
# Load / Save
# -----------------------
def load_qbs():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {qb: 1500 for qb in qbs}

def save_qbs(d):
    with open(DATA_FILE,"w") as f:
        json.dump(d,f)

# -----------------------
# Elo Update
# -----------------------
def update_elo(a,b,w,k=32):
    ea = 1/(1+10**((b-a)/400))
    eb = 1-ea
    if w=="A":
        return a+k*(1-ea), b+k*(0-eb)
    else:
        return a+k*(0-ea), b+k*(1-eb)

# -----------------------
# Session State Setup
# -----------------------
if "ratings" not in st.session_state:
    st.session_state.ratings = load_qbs()

if "pairs" not in st.session_state:
    st.session_state.pairs = list(itertools.combinations(qbs,2))
    random.shuffle(st.session_state.pairs)

if "pair_index" not in st.session_state:
    st.session_state.pair_index = 0

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------
# RESET BUTTON
# -----------------------
if st.button("🔄 Reset All Rankings"):
    st.session_state.ratings = {qb: 1500 for qb in qbs}
    st.session_state.pairs = list(itertools.combinations(qbs, 2))
    random.shuffle(st.session_state.pairs)
    st.session_state.pair_index = 0
    st.session_state.history = []
    save_qbs(st.session_state.ratings)
    st.success("All rankings have been reset to 1500!")
    st.rerun()

# -----------------------
# Current Pair
# -----------------------
def current_pair():
    if st.session_state.pair_index >= len(st.session_state.pairs):
        return None
    return st.session_state.pairs[st.session_state.pair_index]

pair = current_pair()

if pair is None:
    st.success("All matchups complete!")
    st.stop()

a,b = pair

# -----------------------
# Header + Progress
# -----------------------
st.title("🏈 Ultimate QB Ranker")
total = len(st.session_state.pairs)
done = st.session_state.pair_index

st.progress(done/total)
st.write(f"Matchups completed: {done} / {total}")

# -----------------------
# Controls: Undo / Skip
# -----------------------
c1,c2 = st.columns(2)

with c1:
    if st.button("↩ Undo"):
        if st.session_state.history:
            last = st.session_state.history.pop()
            st.session_state.ratings = last["ratings"]
            st.session_state.pair_index -= 1
            save_qbs(st.session_state.ratings)
            st.rerun()

with c2:
    if st.button("⏭ Skip"):
        st.session_state.pair_index += 1
        st.rerun()

# -----------------------
# Matchup Buttons
# -----------------------
st.subheader("Who do you prefer?")

col1,col2 = st.columns(2)

def choose(winner):
    old = st.session_state.ratings.copy()
    na, nb = update_elo(
        st.session_state.ratings[a],
        st.session_state.ratings[b],
        winner
    )
    st.session_state.ratings[a]=na
    st.session_state.ratings[b]=nb
    st.session_state.history.append({"ratings": old})
    save_qbs(st.session_state.ratings)
    st.session_state.pair_index += 1
    st.rerun()

with col1:
    if st.button(a):
        choose("A")

with col2:
    if st.button(b):
        choose("B")

# -----------------------
# Rankings Table
# -----------------------
st.divider()
st.subheader("Current Rankings")

ranked = sorted(st.session_state.ratings.items(),
                key=lambda x:x[1], reverse=True)

df = pd.DataFrame(ranked, columns=["QB","Elo"])
df["Elo"] = df["Elo"].round()
st.dataframe(df, use_container_width=True)

# -----------------------
# Export CSV
# -----------------------
csv = df.to_csv(index=False).encode()
st.download_button(
    "⬇ Download Rankings CSV",
    csv,
    "qb_rankings.csv",
    "text/csv"
)

