# TogglTrack Time Data Management and Visualization
This project fetches time data from TogglTrack, saves it to a PostgreSQL database, and visualizes the data as a Dash app. Time spent is recorded using the toggle track app and is categorised under different activities such as Sleep, PhD etc. This project visualises the collected data using graphs as Dash App. 

Only chosen activities (PhD, Financial, Sleep, No Value, and Survival) is used displyed in the app even though other activities were tracked as well. The daily averages (last seven days and historical) for each of these activities as displayed as well. The graph 'Offense' shows the time spent on financial and Phd in combination. The graph 'Defence' refers to time specnt on No value, Sleep and survival. 

The following gif shows the Dash app with graphs based on dummy data. 

![Dash](https://user-images.githubusercontent.com/31379285/210161714-76761996-4864-4f59-a8d3-42a9e1baab07.gif)

## Features
- Fetch time data from TogglTrack using the TogglTrack API
- Save data to a PostgreSQL database for easy storage and retrieval
- Visualize the data using a Dash app, with graphs and charts

## Prerequisites
In order to use this project, you will need to have the following software and accounts set up:
- Python 3.7 or higher
- TogglTrack account
- PostgreSQL database

You may also need to install additional libraries, such as 'pandas' and 'dash', depending on the specific projects you are working on. These can be easily installed using pip.

## Getting Started
- Clone the repository to your local machine: git clone https://github.com/vishnu123r/toggl-time-visual.git 
- Navigate to the project directory: cd toggl-time-visual
- Install any necessary libraries using pip install -r requirements.txt
- Set up your TogglTrack API key and PostgreSQL database credentials as environment variables
- Run the script to fetch and save the data: main.py
- View the Dash app by opening the URL specified in the terminal output

## Known Issues
- UI/UX and frontend requires improvement
- Deploying the app to Heroku
- Setting up and connecting a Postgres Database to Heroku

## Future Plans
- Incorporate other activites tracked using TogglTrack and create better visualizations
- An integration app where we can view other types of personal data (e.g., habits, workouts etc.)
- Build models based on the collected data (e.g., productivity vs the time spent)

## Author
Ramanah Visnupriyan
