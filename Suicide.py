import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit oldal beállítása
st.set_page_config(page_title="Európai Öngyilkossági Adatok Dashboard", layout="wide")
st.title("Európai Öngyilkossági Adatok Vizualizációja (1985-2016)")

# Fájl feltöltése a felületen keresztül
uploaded_file = st.sidebar.file_uploader("Excel fájl feltöltése (.xlsx)", type=["xlsx"])

@st.cache_data
def load_data(file):
    df = pd.read_excel(file, sheet_name="Munka2")
    df = df.dropna(subset=["suicides_no", "population"])
    df["suicide_rate"] = df["suicides_no"] / df["population"] * 100000
    return df

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Szűrők
    st.sidebar.header("Szűrők")
    selected_country = st.sidebar.multiselect(
        "Ország kiválasztása", options=sorted(df["country"].unique()), default=["Hungary", "Austria"]
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

    # 8. Összefoglalás
    st.subheader("8. Tanulságok")
    st.markdown("""
    - Az öngyilkossági ráta jelentősen változik országonként, nemek, életkor és gazdasági mutatók szerint.
    - A magasabb GDP nem minden esetben jelent alacsonyabb öngyilkossági arányt.
    - Az időbeli trendek fontosak lehetnek a mentális egészségpolitika alakításához.
    - A vizualizációk alapján az idős, férfi populáció a legveszélyeztetettebb.
    """)
else:
    st.warning("Kérlek, töltsd fel a `tisztitottEuropa.xlsx` fájlt a folytatáshoz.")