import streamlit as st
import pandas as pd


df = pd.read_csv('./cache/src_cuse_parking_violations.csv')
df['lat'] = df['coords'].apply(lambda x: float(x.split(',')[0].strip().strip("(").strip("'")))
df['lon'] = df['coords'].apply(lambda x: float(x.split(',')[-1].strip().strip(")").strip("'")))
df['count'] = 1
df2 = df[['ticket_number','issued_date', 'location', 'description', 'status', 'dayofweek', 'hour', 'lat', 'lon', 'count', 'amount']]
st.write(df.columns)
st.dataframe(df2)
df2.to_csv('./cache/final_cuse_parking_violations.csv', index=False)
