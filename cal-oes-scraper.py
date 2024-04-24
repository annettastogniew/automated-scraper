# # Imports
# scraper libraries
import json
import requests
import pandas as pd
import os
# google sheets libraries
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from time import gmtime, strftime
import sys

# # Google sheets setup
# google sheets authentication
try:
    credentials = os.environ["AUTH_CREDENTIALS"]
except KeyError:
    credentials = "Token not available!"
sys.stdout.write("TOKEN: ")
sys.stdout.write(credentials)
gc = gspread.authorize(credentials)
# access sheet
sht = gc.open_by_url('https://docs.google.com/spreadsheets/d/1WVH-SQ0ziAxLeEm2dm5P3i31Mmr9jmWYWwcMRd6vZGc/edit?usp=sharing')
tab = sht.worksheet("test")


# # Constants
# api url
url = "https://services.arcgis.com/BLN4oKB0N1YSgvY8/arcgis/rest/services/Power_Outages_(View)/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
# counties to pull data for
bay_counties = ["ALAMEDA", "CONTRA COSTA", "MARIN", "NAPA", "SAN FRANCISCO", "SAN MATEO", "SANTA CLARA", "SOLANO", "SONOMA"]


# # Scrape
# fetch url
r = requests.get(url)
# put features from geojson into df
data = json.loads(r.content)
df = pd.DataFrame.from_dict(data["features"])
# expand properties column into multiple columns
properties_df = pd.DataFrame.from_dict(list(df["properties"]))
df.drop(columns="properties", inplace=True)
# append properties column to original df
df = pd.concat([df, properties_df], axis=1)
# filter for bay area counties
bay_df = df.loc[df["County"].isin(bay_counties)]
# filter for PGE outages
pge_df = bay_df.loc[df["UtilityCompany"] == "PGE"]
pge_df.to_csv("oes_pge_outages.csv")


# # Push to Google sheets
# clear existing data, push data from dataframe
tab.clear()
set_with_dataframe(tab, pge_df)


