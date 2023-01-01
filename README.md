# TogglTrack Time Data Management and Visualization
This project fetches time data from TogglTrack, saves it to a PostgreSQL database, and visualizes the data as a Dash app. 

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
- Clone the repository to your local machine: git clone https://github.com/<your-username>/toggltrack-time-data.git
- Navigate to the project directory: cd toggl-time-visual
- Install any necessary libraries using pip install -r requirements.txt
- Set up your TogglTrack API key and PostgreSQL database credentials as environment variables
- Run the script to fetch and save the data: main.py
- View the Dash app by opening the URL specified in the terminal output

## Author
Ramanah Visnupriyan

## Known Issues
- UI/UX and frontend requires improvement
- Deploying the app to Heroku
- Setting and connecting a Postgres Database to Heroku

## Future Plans
- An integration app where we can view other types of personal data (e.g., habits, workouts etc.)
- Build models based on the collected data (e.g., productivity vs the time spent)
