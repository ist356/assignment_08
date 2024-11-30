import pandas as pd
import streamlit as st 


def top_locations(violations_df : pd.DataFrame, threshold=1000) -> pd.DataFrame:
    amount_by_location_df = violations_df.pivot_table(index='location', values='amount', aggfunc='sum').sort_values(by='amount', ascending=False)
    amount_by_location_df['location'] = amount_by_location_df.index
    amount_by_location_df.reset_index(drop=True, inplace=True)
    return amount_by_location_df[amount_by_location_df['amount'] >= threshold]


def top_locations_mappable(violations_df : pd.DataFrame, threshold=1000) -> pd.DataFrame:
    top_locations_df = top_locations(violations_df, threshold)
    violations_pre_merge_df = violations_df[['location', 'lat', 'lon']].drop_duplicates(subset=['location'])
    merged_df = pd.merge(top_locations_df, violations_pre_merge_df, on='location')
    return merged_df.drop_duplicates()


def tickets_in_top_locations(violations_df : pd.DataFrame, threshold=1000)  -> pd.DataFrame:
    top_locations_df = top_locations(violations_df)
    merged_df = pd.merge(top_locations_df[['location']], violations_df, on='location')
    return merged_df

if __name__ == '__main__':
    '''
    Main ETL job. 
    '''
    print("Running ETL job...")
    print("Reading violations data from ./cache/final_cuse_parking_violations.csv")
    violations_df = pd.read_csv('./cache/final_cuse_parking_violations.csv')
    
    top_locations_df = top_locations(violations_df)
    print("Writing top locations to ./cache/top_locations.csv")
    top_locations_df.to_csv('./cache/top_locations.csv', index=False)
    
    top_locations_mappable_df = top_locations_mappable(violations_df)
    print("Writing mappable top locations to ./cache/top_locations_mappable.csv")
    top_locations_mappable_df.to_csv('./cache/top_locations_mappable.csv', index=False)

    tickets_in_top_locations_df = tickets_in_top_locations(violations_df, top_locations_df)
    print("Writing tickets in top locations to ./cache/tickets_in_top_locations.csv")
    tickets_in_top_locations_df.to_csv('./cache/tickets_in_top_locations.csv', index=False)