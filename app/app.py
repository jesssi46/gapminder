import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px 

st.title('Gapminder')

st.write("Unlocking Lifetimes: Visualizing Progress in Longevity and Poverty Eradication")

df = pd.DataFrame()
files = ["pop.csv", "lex.csv", "ny_gnp_pcap_pp_cd.csv"]
datasets = ["pop", "lex", "gni"]
kpi = ["population", "lex", "gni"]
magnitudes = {'B': 1000000000, 'M': 1000000, 'k': 1000, np.NAN:1}

@st.cache_data
#creating function to load and process the datasets as cached objects
def load_data():
    #reading files
    df_p = pd.read_csv(files[0])
    df_l = pd.read_csv(files[1])
    df_g = pd.read_csv(files[2])
    #unpivoting dataframes
    df_p = df_p.melt(id_vars="country",var_name='Year', value_name=kpi[0])
    df_l = df_l.melt(id_vars="country",var_name='Year', value_name=kpi[1])
    df_g = df_g.melt(id_vars="country",var_name='Year', value_name=kpi[2])
    #ensure the year is of the integer country (however would be best to sort by country year but then there are some blanks when ffil)
    df_p['Year'] = df_p['Year'].astype(int)
    df_l['Year'] = df_l['Year'].astype(int)
    df_g['Year'] = df_g['Year'].astype(int)
    df_p = df_p.sort_values(by='country',ascending=True)
    df_l = df_l.sort_values(by='country',ascending=True)
    df_g = df_g.sort_values(by='country',ascending=True)
    #ffills with the previous value for the right country
    df_p.ffill(inplace=True)
    df_l.ffill(inplace=True)
    df_g.ffill(inplace=True)

    #in case the KPI contains text we will try to extract the magnitude and multiply by the right order, if not then just continue
    try:
        #extracts the magnitude
        df_p['magnitude'] = df_p.iloc[:,2].str.extract(r'([a-zA-Z]+)')
        df_g['magnitude'] = df_g.iloc[:,2].str.extract(r'([a-zA-Z]+)')
        #extracts the numerical part
        df_p['population'] = df_p['population'].str.extract(r'(\d+)').astype(int)
        df_g['gni'] = df_g['gni'].str.extract(r'(\d+)').astype(int)
        #multiplies the numerical part for the corresponding magnitude order
        df_p['population'] = df_p['population']*df_p['magnitude'].map(magnitudes)
        df_g['gni'] = df_g['gni'] * df_g['magnitude'].map(magnitudes)

    except:
        pass
    del(df_p["magnitude"])
    del(df_g["magnitude"])
    #mergin the datasets
    df = pd.merge(df_p, df_l, on=['country', 'Year'])
    #invoking the merging function
    df = pd.merge(df, df_g, on=['country', 'Year'])

    return df

df = load_data()

# Create an expander
with st.expander("Slider Settings"):
    # Add a filter to the sidebar
    year_filter = st.sidebar.slider("Year", min_value=min(df["Year"].astype(int)), max_value=max(df["Year"].astype(int)), value=2020, step=1,)

    country_filter = st.sidebar.multiselect('country:', df['country'].unique())

# Apply filter to the DataFrame
if year_filter != 'All':
    filtered_df = df[df["Year"] == year_filter]
if country_filter:
    filtered_df = filtered_df[filtered_df['country'].isin(country_filter)]

# Plotly bubble chart
fig = px.scatter(
    filtered_df,
    x='gni',
    y='lex',
    size='population',
    hover_name='country',
    color='country',
    log_x=True, # Set the x-axis to logarithmic scale
    title='Life Expectancy and GNI'
)

st.plotly_chart(fig)
