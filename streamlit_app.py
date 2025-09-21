# Streamlit App: Animated Tourism Visualizations
import plotly.express as px
import pandas as pd
import streamlit as st
import numpy as np

# Load your data (adjust path as needed)
df = pd.read_csv('data/551015b5649368dd2612f795c2a9c2d8_20240902_115953.csv')

# Clean and rename columns for clarity
new_column_names = {
	'Existence of initiatives and projects in the past five years to improve the tourism sector - exists': 'Initiatives Exist',
	'Existence of cafes - does not exist': 'No Cafes',
	'Tourism Index': 'Tourism Index',
	'Existence of touristic attractions that can be expolited and developed - does not exist': 'No Touristic Attractions',
	'Existence of touristic attractions prone to be exploited and developed - exists': 'Touristic Attractions Exist',
	'Total number of hotels': 'Total Hotels',
	'Town': 'Town',
	'Total number of cafes': 'Total Cafes',
	'Observation URI': 'Observation URI',
	'Existence of hotels - does not exist': 'No Hotels',
	'Existence of restaurants - does not exist': 'No Restaurants',
	'Existence of cafes - exists': 'Cafes Exist',
	'references': 'references',
	'Existence of hotels - exists': 'Hotels Exist',
	'refArea': 'refArea',
	'Total number of guest houses': 'Total Guest Houses',
	'Total number of restaurants': 'Total Restaurants',
	'publisher': 'publisher',
	'dataset': 'dataset',
	'Existence of guest houses - exists': 'Guest Houses Exist',
	'Existence of guest houses - does not exist': 'No Guest Houses',
	'Existence of restaurants - exists': 'Restaurants Exist'
}
df.rename(columns=new_column_names, inplace=True)

# Clean up the 'refArea' column
df['refArea'] = df['refArea'].str.replace('https://dbpedia.org/page/', '', regex=False)
df['refArea'] = df['refArea'].str.replace('http://dbpedia.org/resource/', '', regex=False)
df['refArea'] = df['refArea'].str.replace('Miniyehâ\x80\x93Danniyeh_District', 'Miniyha', regex=False)

# Preprocess Governorate column (after cleaning refArea)
df['Governorate'] = df['refArea'].str.replace('_Governorate|_District.*', '', regex=True)
df['Governorate'] = df['Governorate'].str.replace('_', ' ')

# Calculate total amenities using new column names after renaming
df['Total_Amenities'] = (
	df['Total Hotels'].fillna(0) +
	df['Total Restaurants'].fillna(0) +
	df['Total Cafes'].fillna(0) +
	df['Total Guest Houses'].fillna(0)
)

# Streamlit App Title
st.title('Lebanon Tourism Data Visualizations')


# Add filter for governorate only
st.sidebar.header('Filters')
gov_options = ['All'] + sorted(df['Governorate'].dropna().unique().tolist())
selected_govs = st.sidebar.multiselect('Filter by Governorate(s)', gov_options, default=['All'])

# Filter dataframe based on governorate selection only
filtered_df = df.copy()
if 'All' not in selected_govs and len(selected_govs) > 0:
    filtered_df = filtered_df[filtered_df['Governorate'].isin(selected_govs)]

# Create Tourism Ecosystem Score
filtered_df['Tourism_Ecosystem_Score'] = (
    (filtered_df['Total Hotels'] > 0).astype(int) +
    (filtered_df['Total Restaurants'] > 0).astype(int) +
    (filtered_df['Total Cafes'] > 0).astype(int) +
    (filtered_df['Total Guest Houses'] > 0).astype(int) +
    filtered_df['Initiatives Exist'] +
    filtered_df['Touristic Attractions Exist']
)

# 1. Tourism Infrastructure Composition by Governorate (Stacked Bar Chart)
st.subheader('Tourism Infrastructure by Governorate')

# Aggregate data by governorate
gov_infrastructure = filtered_df.groupby('Governorate').agg({
    'Total Hotels': 'sum',
    'Total Restaurants': 'sum', 
    'Total Cafes': 'sum',
    'Total Guest Houses': 'sum'
}).reset_index()

# Create stacked bar chart
fig1 = px.bar(
    gov_infrastructure,
    x='Governorate',
    y=['Total Hotels', 'Total Restaurants', 'Total Cafes', 'Total Guest Houses'],
    title='Tourism Infrastructure Distribution',
    labels={'value': 'Number of Facilities', 'variable': 'Facility Type'},
    color_discrete_map={
        'Total Hotels': '#1f77b4',
        'Total Restaurants': '#ff7f0e', 
        'Total Cafes': '#2ca02c',
        'Total Guest Houses': '#d62728'
    }
)
fig1.update_layout(
    xaxis_title='Governorate',
    yaxis_title='Number of Tourism Facilities',
    xaxis_tickangle=-45,
    height=500,
    barmode='stack'
)
st.plotly_chart(fig1, use_container_width=True)




# 2. Initiatives vs Governorate (Grouped Bar Chart: Count Only)
import plotly.graph_objects as go

st.subheader('Towns With vs Without Initiatives by Governorate')

# Count of towns by governorate and initiatives status
initiatives_gov = filtered_df.groupby(['Governorate', 'Initiatives Exist']).size().reset_index(name='Town Count')
initiatives_gov['Initiatives Status'] = initiatives_gov['Initiatives Exist'].map({0: 'No Initiatives', 1: 'Has Initiatives'})

fig_gov = go.Figure()
colors = ['#FF6B6B', '#4ECDC4']

for i, status_label in enumerate(['No Initiatives', 'Has Initiatives']):
    subset = initiatives_gov[initiatives_gov['Initiatives Status'] == status_label]
    fig_gov.add_trace(go.Bar(
        name=status_label,
        x=subset['Governorate'],
        y=subset['Town Count'],
        marker_color=colors[i],
        offsetgroup=i,
        legendgroup=status_label
    ))

fig_gov.update_layout(
    title='Number of Towns With vs Without Initiatives by Governorate',
    xaxis_title='Governorate',
    yaxis_title='Number of Towns',
    barmode='group',
    height=500
)

st.plotly_chart(fig_gov, use_container_width=True)

