import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit oldal beállítása
st.set_page_config(page_title="Európai Öngyilkossági Adatok Dashboard", layout="wide")

# Oldalak
page = st.sidebar.selectbox("Oldal kiválasztása", ["Projektbemutató", "Vizualizációk"])

# Fájl feltöltése a vizualizációhoz
uploaded_file = st.sidebar.file_uploader("Excel fájl feltöltése (.xlsx)", type=["xlsx"])

@st.cache_data
def load_data(file):
    df = pd.read_excel(file, sheet_name="Munka2")
    df = df.dropna(subset=["suicides_no", "population"])
    df["suicide_rate"] = df["suicides_no"] / df["population"] * 100000
    return df

if page == "Projektbemutató":
    st.title("Projektbemutató – Európai Öngyilkossági Adatok Vizualizációja")

    st.subheader("1. Miről szól ez a projekt?")
    st.markdown("""
    Ez az interaktív dashboard az európai országok öngyilkossági adatait mutatja be 1985 és 2016 között. 
    Célunk, hogy segítsünk jobban megérteni, hogyan alakulnak az öngyilkossági arányok különböző szempontok szerint: 
    nem, korosztály, generáció, valamint gazdasági mutatók, például a GDP és a HDI alapján. 
    Az adatok vizuális megjelenítése segít átlátni az összefüggéseket.
    """)

    st.subheader("2. Milyen adatokat használtunk?")
    st.markdown("""
    A „tisztitottEuropa.xlsx” fájl 33 európai ország több mint 30 évre visszamenő öngyilkossági és gazdasági adatait tartalmazza. 
    Az adatok megbízható forrásokból – például a WHO és a Világbank adatbázisaiból – származnak, és tisztítás után egységes formában kerültek feldolgozásra.
    """)

    st.subheader("3. Miért fontosak ezek az adatok?")
    st.markdown("""
    Az öngyilkosság nemcsak személyes tragédia, hanem komoly társadalmi kérdés is. Mentális egészség, gazdasági helyzet, kulturális háttér – mind befolyásolják. 
    Az ilyen jellegű adatok elemzése segíthet megelőző intézkedések kialakításában és a figyelem felhívásában.
    """)

    st.subheader("4. Kiknek szól a projekt?")
    st.markdown("""
    - Döntéshozóknak, akik prevenciós programokat terveznek
    - Mentálhigiénés szakembereknek, pszichológusoknak
    - Adatkutatóknak, szociológusoknak
    - És bárkinek, akit érdekel a téma
    """)

    st.subheader("5. Mit tanulhatunk belőle?")
    st.markdown("""
    - Mely országokban a legmagasabb az öngyilkossági arány
    - Hogyan különbözik a férfiak és nők helyzete
    - Melyik életkorban a leggyakoribbak ezek az esetek
    - Hogyan hatnak rá a gazdasági körülmények (GDP, HDI)
    - A legveszélyeztetettebbek az idősebb férfiak, különösen a volt szocialista országokban
    """)

    st.subheader("6. Automatizálhatóság és skálázhatóság")
    st.markdown("""
    A dashboard új adatokkal is könnyen frissíthető – csak egy új Excel fájlt kell feltölteni.
    """)

    st.subheader("7. Fejlesztési lehetőségek")
    st.markdown("""
    - Térképes megjelenítés
    - Prediktív modellek
    - Élő adatkapcsolat pl. WHO-tól
    - Interaktív adatfeltöltés saját elemzésekhez
    """)

elif page == "Vizualizációk" and uploaded_file is not None:
    df = load_data(uploaded_file)

    # Szűrők
    st.sidebar.header("Szűrők")
    selected_country = st.sidebar.multiselect(
        "Ország kiválasztása", options=sorted(df["country"].unique()), default=["Hungary", "Romania"]
    )
    selected_years = st.sidebar.slider(
        "Év kiválasztása",
        min_value=int(df["year"].min()),
        max_value=int(df["year"].max()),
        value=(1990, 2016)
    )

    filtered_df = df[
        (df["country"].isin(selected_country)) &
        (df["year"] >= selected_years[0]) &
        (df["year"] <= selected_years[1])
    ]

    st.title("Európai Öngyilkossági Adatok Vizualizációja (1985–2016)")

    # 1. Időbeli alakulás
    st.subheader("1. Öngyilkosságok időbeli alakulása")
    time_fig = px.line(
        filtered_df.groupby(["year", "country"]).sum().reset_index(),
        x="year", y="suicides_no", color="country", markers=True,
        labels={"suicides_no": "Öngyilkosságok száma"},
        title="Öngyilkosságok száma évente"
    )
    st.plotly_chart(time_fig, use_container_width=True)

    # 2. Nemek szerinti megoszlás
    st.subheader("2. Nemek szerinti megoszlás")
    gender_fig = px.histogram(
        filtered_df, x="sex", y="suicides_no", color="sex", barmode="group",
        histfunc="sum", labels={"suicides_no": "Öngyilkosságok száma"}
    )
    st.plotly_chart(gender_fig, use_container_width=True)

    # 3. Korosztály - Boxplot
    st.subheader("3. Korosztályok szerinti eloszlás")
    age_fig = px.box(
        filtered_df, x="age", y="suicide_rate", color="age",
        labels={"suicide_rate": "100 ezer főre jutó öngyilkosság"}
    )
    st.plotly_chart(age_fig, use_container_width=True)

    # 4. Nemzedékek
    st.subheader("4. Nemzedékek szerinti vizsgálat")
    gen_fig = px.bar(
        filtered_df, x="generation", y="suicides_no", color="generation",
        labels={"suicides_no": "Öngyilkosságok száma"},
        title="Öngyilkosságok nemzedékek szerint"
    )
    st.plotly_chart(gen_fig, use_container_width=True)

    # 5. Országok rangsora
    st.subheader("5. Országok összehasonlítása")
    rank_fig = px.bar(
        df[df["year"] == selected_years[1]].groupby("country").sum().reset_index(),
        x="country", y="suicides_no",
        title=f"Öngyilkosságok száma {selected_years[1]}-ben",
        labels={"suicides_no": "Öngyilkosságok száma"}
    )
    st.plotly_chart(rank_fig, use_container_width=True)

    # 6. GDP kapcsolat
    st.subheader("6. GDP és öngyilkosság kapcsolata")
    gdp_fig = px.scatter(
        filtered_df, x="gdp_per_capita ($)", y="suicide_rate",
        size="population", color="country",
        title="GDP per fő és öngyilkossági ráta kapcsolata",
        labels={"gdp_per_capita ($)": "GDP per fő", "suicide_rate": "Öngyilkossági ráta"}
    )
    st.plotly_chart(gdp_fig, use_container_width=True)

    # 7. HDI kapcsolat
    st.subheader("7. HDI és öngyilkosság kapcsolata")
    hdi_df = filtered_df.dropna(subset=["HDI for year"])
    hdi_fig = px.scatter(
        hdi_df, x="HDI for year", y="suicide_rate", color="country",
        title="HDI és öngyilkossági ráta kapcsolata",
        labels={"HDI for year": "HDI", "suicide_rate": "Öngyilkossági ráta"}
    )
    st.plotly_chart(hdi_fig, use_container_width=True)

else:
    st.warning("Kérlek, válaszd ki a 'Vizualizációk' oldalt és töltsd fel a `tisztitottEuropa.xlsx` fájlt a folytatáshoz.")
