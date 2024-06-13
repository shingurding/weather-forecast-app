import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import date
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

# getting today's day and date
date = datetime.today().date()
formatted_date = date.strftime("%d %B %Y")
day = date.strftime("%A")
st.write(f'## {day}, {formatted_date}')

current_dir = os.path.dirname(os.path.abspath(__file__))
chromedriver_path = os.path.join(current_dir, 'bin', 'chromedriver')

# headless browser so it will not launch the website
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(chromedriver_path)

weather_url = "https://www.nea.gov.sg/corporate-functions/weather"
try:
    weather_driver = webdriver.Chrome(service=service, options=options)
    weather_driver.get(weather_url)
    weather_driver.implicitly_wait(10) # wait for 10 seconds for the elements to load
    weather_driver.quit()
except Exception as e:
    st.error(f"An error occurred: {e}")

# Initialize Chrome WebDriver with the specified path
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
    <div style='display: inline-block; text-align: center; border: 1px solid black;'>
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

all_options = []
for selected_option in selected_options:
    option_information = []
    for day_box in days_box:
        # if that day is selected, extract all the weather details from the website
        if day_box.text == selected_option:
            option_information.append(selected_option) # add the day

            parent_div = day_box.find_parent("div", class_="stats-data--4days__item")
            info = parent_div.find(class_="info").text
            option_information.append(info) # add the weather information

            temp_box = parent_div.find(class_="temperature")
            for item in temp_box.find_all(class_="info"): # finds the temperature and wind information
                option_information.append(item.text.replace("\n", "")) # add the temperature and wind speed

    information_str = "<br>".join(option_information)
    all_options.append(information_str)

all_options_df = pd.DataFrame(all_options).transpose()
all_options_html = all_options_df.to_html(header=False, index=False, escape=False)

styled_table = f"""
<div style='text-align: center;'>
    <div style='display: inline-block; text-align: center; border: 1px solid black;'>
        {all_options_html}
    </div>
</div>
"""
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
 
st.write("## UV Index")
uv_box = weather_soup.find("div", class_="section--white has-match-height weather-widget row")
uv_index = uv_box.find(class_="circle__container").text
uv_condition = uv_box.find(class_="text").text

uv_color = ''
if int(uv_index) <= 2:
    uv_color = 'green'
elif int(uv_index) <= 5:
    uv_color = 'yellow'
elif int(uv_index) <= 7:
    uv_color = 'orange'
elif int(uv_index) <= 10:
    uv_color = 'red'
else: 
    uv_color = 'purple'

circle_style = f"""
<style>
    .circle {{
        width: 120px;
        height: 120px;
        border-radius: 50%;
        font-size: 50px;
        color: {uv_color};
        display: flex;
        justify-content: center;
        align-items: center;
        border: 8px solid {uv_color};
    }}

    .condition {{
        font-size: 30px;
        color: {uv_color}; 
        justify-content: center;
    }}
</style>

<div class='circle';>
    {uv_index}
</div>

<div class='condition';>
    {uv_condition}
</div>
"""
st.markdown(circle_style, unsafe_allow_html=True)
