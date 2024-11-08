# type: ignore
# flake8: noqa
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
import pandas as pd
import altair as alt
import time

import warnings
warnings.filterwarnings('ignore')
alt.renderers.enable("png")
#
#
#
import requests
from bs4 import BeautifulSoup
#
#
#
#
#
#
#
# Step 1: Fetch the webpage
url = "https://oig.hhs.gov/fraud/enforcement/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Step 2: Scrape required data
titles = []
dates = []
categories = []
links = []

for action in soup.select('header.usa-card__header'):

    title_tag = action.select_one('h2.usa-card__heading a')
    title = title_tag.text.strip()
    link = "https://oig.hhs.gov" + title_tag['href']
    date_tag = action.select_one('div.font-body-sm.margin-top-1 span')
    date = date_tag.text.strip()
    cat_tag = action.select_one('div.font-body-sm.margin-top-1 ul')
    categories.append(cat_tag.text.strip())
    titles.append(title)
    links.append(link)
    dates.append(date)

```
#
df = pd.DataFrame({
    'Title': titles,
    'Date': dates,
    'Category': categories,
    'Link': links
})
print(df.head())
```
#
agencies = []
for link in df['Link']:
    detail_response = requests.get(link)
    detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
    agency_tag = detail_soup.select(
        'ul.usa-list.usa-list--unstyled.margin-y-2 li')
    second_li = agency_tag[1]

    agency = second_li.contents[1].strip()
    agencies.append(agency)
# df['Agency'] = agencies
print(agencies)
```
#
df['Agency'] = agencies
print(df.head())
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
from datetime import datetime
import time


def scrape_enforcement_actions(month, year):
    if year < 2013:
        print("Year must be 2013 or later.")
        return

    start_date = datetime(year, month, 1)

    base_url = "https://oig.hhs.gov/fraud/enforcement/?page="
    actions_data = []
    page_number = 1
    done = False

    while not done:
        url = f"{base_url}{page_number}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        actions = soup.select('header.usa-card__header')

        for action in actions:
            date_tag = action.select_one('div.font-body-sm.margin-top-1 span')
            date = date_tag.text.strip()
            print(date)
            action_date = datetime.strptime(date, "%B %d, %Y")

            if start_date <= action_date:
                title_tag = action.select_one('h2.usa-card__heading a')
                title = title_tag.text.strip()
                print(title)
                link = "https://oig.hhs.gov" + title_tag['href']
                category = action.select_one(
                    'li.display-inline-block.usa-tag.text-no-lowercase').text.strip()
                agency = scrape_agency(link)
                print(agency)

                actions_data.append({
                    'Title': title,
                    'Date': action_date.strftime("%Y-%m-%d"),
                    'Category': category,
                    'Link': link,
                    'Agency': agency
                })
            elif action_date < start_date:
                done = True
                break

        page_number += 1
        time.sleep(1)

        # Save to CSV
    df = pd.DataFrame(actions_data)
    file_name = f"enforcement_actions_{year}_{month}.csv"
    df.to_csv(file_name, index=False)
    print(f"Data saved to {file_name}")


#
#
#
from bs4.element import Tag

def scrape_agency(link):
    detail_response = requests.get(link)
    detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
    agency_tag = detail_soup.select(
        'ul.usa-list.usa-list--unstyled.margin-y-2 li')
    second_li = agency_tag[1]
    if not isinstance(second_li.contents[1], Tag):
        agency = second_li.contents[1].strip()
    else:
        agency = 'NaN'
    return agency
#
#
#
#
#
#scrape_enforcement_actions(1, 2021)
#
#
#
#
#
#
#
filepath = "enforcement_actions_2021_1.csv"
data = pd.read_csv(filepath)
data.head()
#
#
#
import altair as alt
from altair_saver import save
#
#
#
# Change "Date" into datetime format
data['Date'] = pd.to_datetime(data['Date'])

# Aggregate by month and year
monthly_actions = data.groupby(data['Date'].dt.to_period(
    "M")).size().reset_index(name='count')
monthly_actions['Date'] = monthly_actions['Date'].dt.to_timestamp()

# Plot with Altair
chart1 = alt.Chart(monthly_actions).mark_line().encode(
    x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m')),
    y=alt.Y('count:Q', title='Number of Enforcement Actions'),
    tooltip=['Date:T', 'count:Q']
).properties(
    title='Number of Enforcement Actions Over Time (Monthly Aggregation)',
    width=400,
    height=200
)
chart1.save('chart1.svg')

#
#
#
#
#
#
#
#
#
# Change "Date" into datetime format
data['Date'] = pd.to_datetime(data['Date'])

# Aggregate by month and year, and by category
monthly_actions = (
    data[data['Category'].isin(
        ['Criminal and Civil Actions', 'State Enforcement Agencies'])]
    .groupby([data['Date'].dt.to_period("M"), 'Category'])
    .size()
    .reset_index(name='Count')
)

# Convert 'Date' back to timestamp for plotting
monthly_actions['Date'] = monthly_actions['Date'].dt.to_timestamp()

# Plot with Altair
chart2 = alt.Chart(monthly_actions).mark_line().encode(
    x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m')),
    y=alt.Y('Count:Q', title='Number of Enforcement Actions'),
    color=alt.Color('Category:N', title='Category'),
    tooltip=['Date:T', 'Count:Q', 'Category:N']
).properties(
    title='Number of Enforcement Actions Over Time by Category',
    width=400,
    height=200
).interactive()

# chart2

chart2.save('chart2.svg')

#
#
#
#
#
#
#
# Change "Date" into datetime format
data['Date'] = pd.to_datetime(data['Date'])

data_criminal_civil = data[data['Category'].isin(
    ['Criminal and Civil Actions'])]

# Define a function to categorize based on keywords in 'Title'


def categorize_title(title):
    if any(keyword in title.lower() for keyword in ['drug', 'narcotics', 'enforcement', 'trafficking']):
        return 'Drug Enforcement'
    elif any(keyword in title.lower() for keyword in ['health', 'insurance', 'hospital', 'medicare', 'medicaid']):
        return 'Health Care Fraud'
    elif any(keyword in title.lower() for keyword in ['bank', 'financial', 'investment', 'securities']):
        return 'Financial Fraud'
    elif any(keyword in title.lower() for keyword in ['bribery', 'corruption', 'bribe']):
        return 'Bribery/Corruption'
    else:
        return 'Other'


# Apply categorization function to the Title column
data_criminal_civil['Topic'] = data_criminal_civil['Title'].apply(
    categorize_title)

data_criminal_civil.head()
#
#
#
# Aggregate by month and year, and by topic
monthly_actions = (
    data_criminal_civil
    .groupby([data_criminal_civil['Topic'], data_criminal_civil['Date'].dt.to_period("M")])
    .size()
    .reset_index(name='Count')
)

# Convert 'Date' back to timestamp for plotting
monthly_actions['Date'] = monthly_actions['Date'].dt.to_timestamp()

# Plot with Altair
chart3 = alt.Chart(monthly_actions).mark_line().encode(
    x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m')),
    y=alt.Y('Count:Q', title='Number of Categories'),
    color=alt.Color('Topic:N', title='Topic'),
    tooltip=['Date:T', 'Count:Q', 'Topic:N']
).properties(
    title='Number of Criminal and Civil Actions Over Time by Topic',
    width=400,
    height=200
).interactive()

#chart3

chart3.save('chart3.svg')
#
#
#
#
#
#
#
#
#
#
#
filepath = "enforcement_actions_2021_1.csv"
data = pd.read_csv(filepath)
data.head()
```
#
data_state = data[data["Agency"].str.contains("State of", case=False, na=False)]
data_state = data_state.reset_index(drop=True)
data_state.head()
#
#
#
import geopandas as gpd
# Load the shapefile
states_gdf = gpd.read_file("cb_2018_us_state_500k/cb_2018_us_state_500k.shp")  # Replace with the actual path to your shapefile
states_gdf.head()
#
#
#
state_count = (
    data_state
    .groupby('Agency')
    .size()
    .reset_index(name='Count')
)
state_count.head()

```
#
state_count["Agency_Name"] = state_count['Agency'].str.replace(r'^State of ', '', regex=True)
#
#
#
# Ensure state names/abbreviations match in both DataFrames
merged_gdf = states_gdf.merge(state_count, left_on='NAME', right_on='Agency_Name', how='right')

merged_gdf.head()
#
#
#
#
import matplotlib.pyplot as plt

# Plotting the map
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
merged_gdf.plot(column='Count', cmap='Blues', linewidth=0.8, edgecolor='0.8', legend=True, ax=ax)
ax.set_title("Number of Enforcement Actions by State", fontsize=15)
ax.set_axis_off()
plt.show()

#
#
#
#
#
filepath = "enforcement_actions_2021_1.csv"
data = pd.read_csv(filepath)
filepath = "US_Attorney_Districts_Shapefile_simplified_20241108.csv"
district = pd.read_csv(filepath)
#
#
#
data_district = data[data["Agency"].str.contains("District", case=False, na=False)]
data_district = data_district.reset_index(drop=True)

district_count = (
    data_district
    .groupby('Agency')
    .size()
    .reset_index(name='Count')
)
#
#
#
print(district_count.iloc[106])
```
#
def extract_district(agency):
    if 'Attorney’s Office, ' in agency:  # Case with 'Attorney’s Office, '
        return agency.split("Attorney’s Office, ")[-1]
    elif 'Attorney\'s Office, ' in agency:  # Case with 'Attorney\'s Office, '
        return agency.split("Attorney's Office, ")[-1]
    elif 'U.S. Attorney’s Office;' in agency:  # Case with 'U.S. Attorney’s Office;'
        return agency.split("U.S. Attorney’s Office;")[-1]
    elif 'U.S. Attorney’s Office' in agency:  # Case with 'U.S. Attorney’s Office;'
        return agency.split("U.S. Attorney’s Office")[-1]
    elif "U.S. Attorney General," in agency:
        return agency.split("U.S. Attorney General,")[-1]
    elif "U.S. Attorneyĺs Office," in agency:
        return agency.split("U.S. Attorneyĺs Office,")[-1]
    else:  # For cases without the expected prefixes
        return agency

# Apply the function to the 'Agency' column
district_count['Agency_Name'] = district_count['Agency'].apply(extract_district)

district_count.head()
#
#
#
district.rename(columns={'Judicial District': 'Judicial_District'}, inplace=True)

# Ensure state names/abbreviations match in both DataFrames
merged = district.merge(district_count, left_on='Judicial_District', right_on='Agency_Name', how='right')

merged_gdf.head()
#
#
#
#
#
#
#
#
#
#
#

#
#
#
#
#
#
#
#
