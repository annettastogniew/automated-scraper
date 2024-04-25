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

# # Google sheets setup
# google sheets authentication
try:
    credentials = json.loads(os.environ["AUTH_CREDENTIALS"])
except KeyError:
    credentials = "Token not available!"
gc = gspread.service_account_from_dict(credentials)
# access sheet
sht = gc.open_by_url('https://docs.google.com/spreadsheets/d/1d1L7Z7V-FUmIn0lztepKghokTojieBG1WJ2fIM_uQLg/edit?usp=sharing')
tab = sht.worksheet("Cal OES data")


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
# expand geometry column into multiple columns
geometry_df = pd.DataFrame.from_dict(list(df["geometry"]))
# expand coordinates to individual columns
geometry_df["latitude"] = geometry_df["coordinates"].apply(lambda x: x[0])
geometry_df["longitude"] = geometry_df["coordinates"].apply(lambda x: x[1])
geometry_df.drop(columns="coordinates", inplace=True)
# drop original geometry and properties columns
df.drop(columns=["geometry", "properties"], inplace=True)
# append properties and geometry columns to original df
df = pd.concat([df, properties_df, geometry_df], axis=1)
# filter for bay area counties
bay_df = df.loc[df["County"].isin(bay_counties)]
bay_df.to_csv("cal-oes-scraper/oes_pge_outages.csv")


# # Push to Google sheets
# clear existing data, push data from dataframe
tab.clear()
set_with_dataframe(tab, bay_df)


