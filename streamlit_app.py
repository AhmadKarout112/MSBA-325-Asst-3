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

# Add filters
st.sidebar.header('Filters')
gov_options = ['All'] + sorted(df['Governorate'].dropna().unique().tolist())
selected_govs = st.sidebar.multiselect('Filter by Governorate(s)', gov_options, default=['All'])

# Filter towns based on selected governorates
if 'All' in selected_govs or len(selected_govs) == 0:
    available_towns = sorted(df['Town'].dropna().unique().tolist())
else:
    available_towns = sorted(df[df['Governorate'].isin(selected_govs)]['Town'].dropna().unique().tolist())

town_options = ['All'] + available_towns
selected_towns = st.sidebar.multiselect('Filter by Town(s)', town_options, default=['All'])

# Filter dataframe based on selections
filtered_df = df.copy()
if 'All' not in selected_govs and len(selected_govs) > 0:
    filtered_df = filtered_df[filtered_df['Governorate'].isin(selected_govs)]
if 'All' not in selected_towns and len(selected_towns) > 0:
    filtered_df = filtered_df[filtered_df['Town'].isin(selected_towns)]

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

# 2. Tourism Service Availability Heatmap
st.subheader('Tourism Service Availability by Governorate')

# Calculate service availability percentages
service_availability = filtered_df.groupby('Governorate').agg({
    'Hotels Exist': 'mean',
    'Restaurants Exist': 'mean',
    'Cafes Exist': 'mean',
    'Guest Houses Exist': 'mean',
    'Touristic Attractions Exist': 'mean',
    'Initiatives Exist': 'mean'
}).round(3) * 100  # Convert to percentages

service_availability = service_availability.reset_index()

# Melt data for heatmap
service_melted = service_availability.melt(
    id_vars=['Governorate'], 
    var_name='Service Type',
    value_name='Availability Percentage'
)

# Create heatmap
fig2 = px.imshow(
    service_availability.set_index('Governorate').T,
    labels=dict(x="Governorate", y="Service Type", color="Availability %"),
    title="Tourism Service Availability Heatmap (%)",
    color_continuous_scale='RdYlGn',
    aspect='auto'
)

fig2.update_layout(
    height=500,
    xaxis_tickangle=-45
)

# Add text annotations
for i, gov in enumerate(service_availability['Governorate']):
    for j, service in enumerate(['Hotels Exist', 'Restaurants Exist', 'Cafes Exist', 
                               'Guest Houses Exist', 'Touristic Attractions Exist', 'Initiatives Exist']):
        value = service_availability.loc[service_availability['Governorate'] == gov, service].iloc[0]
        fig2.add_annotation(
            x=i, y=j,
            text=f"{value:.1f}%",
            showarrow=False,
            font=dict(color="white" if value < 50 else "black", size=8)
        )

st.plotly_chart(fig2, use_container_width=True)


