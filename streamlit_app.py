import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from geopy.geocoders import Nominatim
from collections import Counter
import plotly.express as px
import streamlit as st
from datetime import datetime


dfOperaciones = pd.read_csv('dfDefinitivo.csv',low_memory=False)

pd.options.plotting.backend = "plotly"

st.header("Dataframe Bombardeos SGM")



st.dataframe(dfOperaciones)

#10 aviones más utilizados
aparicion = dfOperaciones["Aircraft Series"].value_counts().reset_index()
aparicion.columns = ['Aircraft Series', 'Count'] 
top_10_aviones = aparicion.head(10)  # Obtener los 10 aviones más comunes

fig = px.bar(
    top_10_aviones,
    x='Aircraft Series', 
    y='Count',
    title='Top 10 aviones más usados',
    labels={'Aircraft Series': 'Tipo de avión', 'Count': 'Número de apariciones'},
    hover_data=['Aircraft Series', 'Count'], 
    color='Count', 
    color_continuous_scale='greens' 
)
st.plotly_chart(fig)

#10 ciudades
repeticiones = dfOperaciones['Target Country'].value_counts()
top_10_ciudades = repeticiones.head(10).reset_index()
top_10_ciudades.columns = ['Target City', 'count'] 
fig = px.bar(
    top_10_ciudades,
    x='Target City', 
    y='count',
    title='Top 10 ciudades más bombardeadas',
    labels={'Target City': 'Ciudad', 'count': 'Número de apariciones'},
    hover_data=['Target City', 'count'], 
    color='count', 
    color_continuous_scale='reds' 
)
st.plotly_chart(fig)



#Mapa Países 
country_counts = dfOperaciones['Target Country'].value_counts().reset_index()
country_counts.columns = ['Country', 'Count'] 

fig = px.scatter_geo(
    country_counts, 
    locations="Country",
    locationmode="country names",
    size="Count",  
    title="Distribución de Bombardeos por Países",
    projection="natural earth",  
    template="plotly_dark"  
)
fig.update_layout(
    showlegend=True,
    legend_title="Cantidad de Bombardeos",
    legend=dict(
        x=0.8,
        y=0.9,  
        traceorder='normal',
        font=dict(size=12),
        bgcolor='rgba(255, 255, 255, 0.5)', 
        bordercolor='Black',
        borderwidth=1
    ),
)
st.plotly_chart(fig, use_container_width=True)


#MAPA interactivo
dfOperaciones['Mission Date'] = pd.to_datetime(dfOperaciones['Mission Date'], errors='coerce')
min_date = dfOperaciones['Mission Date'].min().to_pydatetime()  
max_date = dfOperaciones['Mission Date'].max().to_pydatetime()  

if min_date is None or max_date is None:
    st.error("No se encontraron fechas válidas en el conjunto de datos.")
else:
    #slider 
    selected_range = st.slider(
        "Selecciona el rango de fechas:",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )

    # Filtrado por fecha
    df_filtrado = dfOperaciones[
        (dfOperaciones['Mission Date'] >= pd.Timestamp(selected_range[0])) &
        (dfOperaciones['Mission Date'] <= pd.Timestamp(selected_range[1]))
    ]

    # conteo de apariciones
    country_counts = df_filtrado['Target Country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count'] 

    fig = px.scatter_geo(
        country_counts,
        locations="Country",
        locationmode="country names",
        size="Count",
        title=f"Distribución de Bombardeos ({selected_range[0].strftime('%Y-%m-%d')} - {selected_range[1].strftime('%Y-%m-%d')})",
        projection="natural earth",
        template="plotly_dark"
    )
    fig.update_layout(
        showlegend=True,
        legend_title="Cantidad de Bombardeos",
        legend=dict(
            x=0.8,
            y=0.9,
            traceorder='normal',
            font=dict(size=12),
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='Black',
            borderwidth=1
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

#   Tendencias de bombardeos
dfOperaciones['Year'] = dfOperaciones['Mission Date'].dt.year
yearly_counts = dfOperaciones.groupby('Year').size().reset_index(name='Count')
x = yearly_counts['Year']
y = yearly_counts['Count']
coef = np.polyfit(x, y, 1) 
trendline = np.poly1d(coef)(x)

fig = px.line(
    yearly_counts,
    x='Year',
    y='Count',
    title='Tendencia de Bombardeos por Año',
    labels={'Year': 'Año', 'Count': 'Número de Bombardeos'}
)
fig.add_scatter(
    x=x,
    y=trendline,
    mode='lines',
    name='Línea de tendencia',
    line=dict(color='red', dash='dash')  
)

st.plotly_chart(fig)

