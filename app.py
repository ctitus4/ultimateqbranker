import streamlit as st
import random
import json
import itertools
import pandas as pd

DATA_FILE = "nfl_qb_rankings.json"

# -----------------------
# Load / Save
# -----------------------
def load_qbs():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "Jordan Love":1500,"Caleb Williams":1500,"JJ McCarthy":1500,"Jared Goff":1500,
            "Dak Prescott":1500,"Jaxon Dart":1500,"Jalen Hurts":1500,"Jayden Daniels":1500,
            "Matt Stafford":1500,"Sam Darnold":1500,"Kyler Murray":1500,"Brock Purdy":1500,
            "Tyler Shough":1500,"Baker Mayfield":1500,"Bryce Young":1500,"Michael Penix":1500,
            "Josh Allen":1500,"Tua Tagovailoa":1500,"Drake Maye":1500,"Justin Fields":1500,
            "Cam Ward":1500,"Trevor Lawrence":1500,"CJ Stroud":1500,"Daniel Jones":1500,
            "Shedeur Sanders":1500,"Lamar Jackson":1500,"Aaron Rodgers":1500,"Joe Burrow":1500,
            "Justin Herbert":1500,"Geno Smith":1500,"Bo Nix":1500,"Patrick Mahomes":1500
        }

def save_qbs(d):
    with open(DATA_FILE,"w") as f:
        json.dump(d,f)

# -----------------------
# Elo
# -----------------------
def update_elo(a,b,w,k=32):
    ea = 1/(1+10**((b-a)/400))
    eb = 1-ea
    if w=="A":
        return a+k*(1-ea), b+k*(0-eb)
    else:
        return a+k*(0-ea), b+k*(1-eb)

# -----------------------
# Session setup
# -----------------------
if "ratings" not in st.session_state:
    st.session_state.ratings = load_qbs()

if "pairs" not in st.session_state:
    st.session_state.pairs = list(itertools.combinations(st.session_state.ratings.keys(),2))
    random.shuffle(st.session_state.pairs)

if "pair_index" not in st.session_state:
    st.session_state.pair_index = 0

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------
# Helpers
# -----------------------
def current_pair():
    if st.session_state.pair_index >= len(st.session_state.pairs):
        return None
    return st.session_state.pairs[st.session_state.pair_index]

pair = current_pair()

# -----------------------
# UI Header
# -----------------------
st.title("🏈 QB Elo Ranker")

total = len(st.session_state.pairs)
done = st.session_state.pair_index

st.progress(done/total)
st.write(f"Matchups completed: {done} / {total}")

# -----------------------
# Controls Row
# -----------------------
c1,c2,c3 = st.columns(3)

with c1:
    if st.button("🔄 Reset Rankings"):
        st.session_state.ratings = load_qbs()
        st.session_state.pair_index = 0
        st.session_state.history = []
        save_qbs(st.session_state.ratings)
        st.rerun()

with c2:
    if st.button("⏭ Skip"):
        st.session_state.pair_index += 1
        st.rerun()

with c3:
    if st.button("↩ Undo"):
        if st.session_state.history:
            last = st.session_state.history.pop()
            st.session_state.ratings = last["ratings"]
            st.session_state.pair_index -= 1
            save_qbs(st.session_state.ratings)
            st.rerun()

# -----------------------
# Matchup
# -----------------------
if pair is None:
    st.success("All matchups complete!")
    st.stop()

a,b = pair
st.subheader("Who do you prefer?")

col1,col2 = st.columns(2)

def choose(winner):
    old = st.session_state.ratings.copy()
    na,nb = update_elo(
        st.session_state.ratings[a],
        st.session_state.ratings[b],
        winner
    )
    st.session_state.ratings[a]=na
    st.session_state.ratings[b]=nb
    st.session_state.history.append({"ratings":old})
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
df["Elo"]=df["Elo"].round()

st.dataframe(df, use_container_width=True)

# -----------------------
# Export
# -----------------------
csv = df.to_csv(index=False).encode()
st.download_button(
    "⬇ Download Rankings CSV",
    csv,
    "qb_rankings.csv",
    "text/csv"
)
