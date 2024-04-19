#!/usr/bin/env python
# coding: utf-8

# # Imports

# In[12]:


# scraper libraries
import json
import requests
import pandas as pd


# In[13]:


# google sheets libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from time import gmtime, strftime


# # Google sheets setup

# In[14]:


# google sheets authentication
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('auth.json', scope)
gc = gspread.authorize(credentials)


# In[15]:


# access sheet
sht = gc.open_by_url('https://docs.google.com/spreadsheets/d/1WVH-SQ0ziAxLeEm2dm5P3i31Mmr9jmWYWwcMRd6vZGc/edit?usp=sharing')
tab = sht.worksheet("test")


# # Constants

# In[16]:


# api url
url = "https://services.arcgis.com/BLN4oKB0N1YSgvY8/arcgis/rest/services/Power_Outages_(View)/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"


# In[17]:


# counties to pull data for
bay_counties = ["ALAMEDA", "CONTRA COSTA", "MARIN", "NAPA", "SAN FRANCISCO", "SAN MATEO", "SANTA CLARA", "SOLANO", "SONOMA"]


# # Scrape

# In[18]:


# fetch url
r = requests.get(url)
# put features from geojson into df
data = json.loads(r.content)
df = pd.DataFrame.from_dict(data["features"])


# In[19]:


# expand properties column into multiple columns
properties_df = pd.DataFrame.from_dict(list(df["properties"]))
df.drop(columns="properties", inplace=True)
# append properties column to original df
df = pd.concat([df, properties_df], axis=1)


# In[20]:


# filter for bay area counties
bay_df = df.loc[df["County"].isin(bay_counties)]


# In[21]:


# filter for PGE outages
pge_df = bay_df.loc[df["UtilityCompany"] == "PGE"]
pge_df.to_csv("oes_pge_outages_actions.csv")


# # Push to Google sheets

# In[22]:


# clear existing data, push data from dataframe
tab.clear()
set_with_dataframe(tab, pge_df)

