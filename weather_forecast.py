import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup # for webscrapping
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Suppress InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

global_css = """
<style>
[class="main st-emotion-cache-bm2z3a ea3mdgi8"] {
background-image: url("https://img.freepik.com/free-photo/sun-rays-cloudy-sky_23-2148824930.jpg?t=st=1718187293~exp=1718190893~hmac=8ce224b483d4c7d3b4976cc376973f936dd9523e7a583097f496787dfdeafa9f&w=740");
background-size: cover;
}
</style
"""
st.markdown(global_css, unsafe_allow_html=True)

st.title("Weather Forecast")

# headless browser so it will not launch the website
options = Options()
options.add_argument('--headless')

date_url = "https://www.google.com/search?q=today%27s+date&oq=todays&gs_lcrp=EgZjaHJvbWUqEwgDEEUYChg7GEMYsQMYgAQYigUyBggAEEUYOTISCAEQABgUGIcCGLEDGMkDGIAEMg8IAhAAGAoYgwEYsQMYgAQyEwgDEEUYChg7GEMYsQMYgAQYigUyDAgEEAAYChixAxiABDIPCAUQABgUGIcCGJIDGIAEMg8IBhAAGAoYgwEYsQMYgAQyCQgHEAAYChiABDIPCAgQABgKGIMBGLEDGIAEMg8ICRAAGAoYgwEYsQMYgATSAQg0MTY1ajBqN6gCALACAA&sourceid=chrome&ie=UTF-8"
weather_url = "https://www.nea.gov.sg/corporate-functions/weather"

chromedriver_path = "/Users/dsaid/Downloads/chromedriver-mac-arm64/chromedriver"

# Initialize Chrome WebDriver with the specified path
date_driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
weather_driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)

date_driver.get(date_url)
date_driver.implicitly_wait(10)
date_content = date_driver.page_source
date_soup = BeautifulSoup(date_content, 'html.parser')
date = date_soup.find(class_="vk_bk dDoNo FzvWSb").text
st.write(f'## {date}')

weather_driver.get(weather_url)
weather_driver.implicitly_wait(10) # wait for 10 seconds for the elements to load
html_content = weather_driver.page_source
weather_soup = BeautifulSoup(html_content, 'html.parser')
day_forecast_box = weather_soup.find(id="weather_desc")
temperature_box = weather_soup.find(id="temperature")
wind_direction_box = weather_soup.find(id="wind_direction")
wind_speed_box = weather_soup.find(id="wind_speed")

data = {
    "24-hour Weather Forecast": [day_forecast_box.text],
    "Temperature Range": [temperature_box.text],
    "Wind Direction": [wind_direction_box.text],
    "Wind Speed": [wind_speed_box.text]
}
df = pd.DataFrame(data).transpose()
html_table = df.to_html(header=False, classes='centered-table')

# center the box horizontally within its parent container and the content in the box is also centered
styled_table = f"""
<div style='text-align: center;'>
    <div style='display: inline-block; text-align: center; background-color: white;'>
        {html_table}
    </div>
</div>
"""
st.markdown(styled_table, unsafe_allow_html=True)

# 4 day weather forecast
st.write("##### Which days would you like to see?")

days = []
days_box = weather_soup.find_all(class_="day")
for day_box in days_box:
    day = day_box.text
    days.append(day)
days = days[:4]

selected_options = []
for option in days:
    selected = st.checkbox(option) 
    if selected:
        selected_options.append(option) # getting the list of selection options

for selected_option in selected_options:
    option_information = []
    for day_box in days_box:
        # if that day is selected, extract all the weather details from the website
        if day_box.text == selected_option:
            parent_div = day_box.find_parent("div", class_="stats-data--4days__item")
            info = parent_div.find(class_="info").text
            option_information.append(info)

            temp_box = parent_div.find(class_="temperature")
            for item in temp_box.find_all(class_="info"): # finds the temperature and wind information
                option_information.append(item.text.replace("\n", ""))

    option_df = pd.DataFrame(option_information, ["Weather Information", "Temperature", "Wind Information"])
    option_html = option_df.to_html(header=False)

    styled_table = f"""
    <div>
        <div style='display: inline-block; text-align: center; background-color: white;'>
            {option_html}
        </div>
    </div>
    """
    st.write(f"##### {selected_option}:")
    st.markdown(styled_table, unsafe_allow_html=True)     



# getting the weather in each specific location
weather_grid = weather_soup.find(id="weather-grid")

if weather_grid:
    locations = []
    urls = []
    # iterate over each <span> element in the weather grid
    for item in weather_grid.find_all('span'):
        location = item.get('id') # location
        location = location.replace("_", " ")
        img_content = item.find('img')
        url = f"https://www.nea.gov.sg{img_content.get('src')}" # image displaying the weather

        locations.append(location)
        urls.append(url)

        # def display_image(url):
        #     response = requests.get(url, verify=False)
        #     img = Image.open(BytesIO(response.content))
        #     return img

    area = st.selectbox("Choose an area", locations)
    ind = locations.index(area) # getting which index the item appears in the list
    weather = urls[ind]

    st.write(f'The weather in {area} now is:')
    st.markdown(f"<div style='text-align: center;'><img src='{url}' alt='Weather Image'></div>", unsafe_allow_html=True)

    # df = pd.DataFrame(table_data, columns=["Location", "Weather"])
