'''
location_dashboard.py
'''
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
st.set_page_config(layout="wide")


df = pd.read_csv('./cache/tickets_in_top_locations.csv')


st.title('Top Locations for Parking Tickets within Syracuse')
st.caption('This dashboard shows the parking tickets that were issued in the top locations with $1,000 or more in total aggregate violation amounts.')

locations = df['location'].unique()

location = st.selectbox('Select a location:', locations)
if location:
    filtered_df = df[df['location'] == location]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total tickets issued", filtered_df.shape[0])
        fig1, ax1 = plt.subplots()
        ax1.set_title('Tickets Issued by Hour of Day')
        sns.barplot(data=filtered_df, x="hourofday", y="count", estimator="sum", hue="hourofday", ax=ax1)
        st.pyplot(fig1)

    with col2:
        st.metric("Total amount", f"$ {filtered_df['amount'].sum()}")
        fig2, ax2 = plt.subplots()
        ax2.set_title('Tickets Issued by Day of Week')
        sns.barplot(data=filtered_df, x="dayofweek", y="count", estimator="sum", hue="dayofweek", ax=ax2)
        st.pyplot(fig2)

    st.map(filtered_df[['lat', 'lon']])