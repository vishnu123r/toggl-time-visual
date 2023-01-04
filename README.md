# TogglTrack Time Data Management and Visualization
This project is a system for tracking and categorizing your time using TogglTrack and a PostgreSQL database. The collected data is visualized in a Dash app, which displays daily averages and graphically represents certain categories of activities. Only selected activities (such as PhD, Financial, Sleep, No Value, and Survival) are shown in the app, although other activities were also tracked. The Dash app displays the daily averages for these activities over the past seven days and historically. The 'Offense' graph shows the combined time spent on Financial and PhD activities, while the 'Defense' graph shows the time spent on No Value, Sleep, and Survival activities.

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

## Currently Working
- Deploying the app to Heroku
- Setting up and connecting a Postgres Database to Heroku
- UI/UX and frontend improvements

## Future Plans
- Incorporate other activites tracked using TogglTrack and create better visualizations
- An integration app where we can view other types of personal data (e.g., habits, workouts etc.)
- Build models based on the collected data (e.g., productivity vs the time spent)

## Things I learned
- PostgreSQL Database
- Dash
- Python
- API
- HTML/ CSS
- OOP

## Author
Ramanah Visnupriyan
