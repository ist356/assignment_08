# IST356 Assignment 08 (assignment_08)

## Meta Section

### Prerequisites

Before starting this assignment you must get the requirements installed. 

**NOTE: This should be done already as part of the visualization unit.**

Install the assignemnt python requirements:

1. From VS Code, open a terminal: Menu => Terminal => New Terminal
2. In the terminal, type and enter: `pip install -r requirements.txt`

### Running Tests

There are some code and tests already working in this assignment. These are sanity checks to ensure VS Code is configured properly.

1. Open **Testing** in the activity bar: Menu => View => Testing
2. Open the **>** by clicking on it next to **assignment_06**. Keep clicking on **>** until you see **test_should_pass** in each  **test_????.py** file
4. Click the Play button `|>` next to **test_should_pass** to execute the test. 
5. A green check means the test code ran and the test has passed.
6. A red X means the test code ran but the test has failed. When a test fails you will be given an error message and stack trace with line numbers.

### Debugging

Odds are you will need to use some debugging strategies in this assignment. 

To debug a test:

- call the test function in the `if __name__ == '__main__':` block at the bottom of the test file.
- then set a breakpoint in the test function and run the test as you would any other python program.
- run the file with debugging: Menu => Run => Start Debugging

## Assignment: Visualizing Parking Tickets

In this assignment you will practice ETL (Extract-Transform-Load) for data visualization. Despite clean datasets being built from our data pipeline, it is quite common to have to transform data further before it can be visualized. This assignment will demonstrate this concept.

### Dataset

The dataset we will use is an open dataset of parking tickets issued in Syracuse, NY. The dataset is available on the Syracuse Open Data Portal: [https://data.syrgov.net](https://data.syrgov.net/). The dataset provided has already been cleaned, columns have been engineered, and the locations have been geocoded.

The file `final_cuse_parking_violations.csv` is the the output from a previous ETL pipeline and will serve as the source data for our visualizations. The dataset is keyed on parking ticket number (there is one row per parking ticket), and there are 15,787 rows in the dataset.

Among the source columns there are engineered columns:
- dayofweek and hourofday from the date/time of the ticket
- lat and lon from the geocoded location of the ticket

### The objective

You will create two streamlit dashboards in this assignment.  The first dashboard will visualize where the top tickets are issued.

The second dashboard will allow the user to select a location then visualize the distribution of tickets by day of the week and hour of the day.

Before your can visualize the data, you will need transform it further. There are too many locations for a practical visualization, so you must limit the dataset to "top locations", which is defined as any location with $1,000 or more in parking tickets. 


## The Approach

Once again, we will take a bottom up approach. **Commit your code after each part.** Push when you are done with the code and the reflection.

### Part 1: Complete the functions in etl.py

First you must create an ETL program to extract the datasets we need for visualization. The `etl.py` file contains the functions you need to complete.

In summary your program must:

input this one file

- ./cache/final_cuse_parking_violations.csv

output these three files

- ./cache/top_locations.csv 
- ./cache/top_locations_mappable.csv
- ./cache/tickets_in_top_locations.csv

in `etl.py` There is a function for each file you need to create:

`def top_locations(violations_df : pd.DataFrame, threshold=1000):`

Return a dataframe of the locations of parking tickets with $1,000 or more in total aggregate violation amounts.  
This dataframe is keyed on location (1 row per location) and has two columns: location and amount.  
There should be 135 rows in this dataframe.

`def top_locations_mappable(violations_df : pd.DataFrame, threshold=1000):`

get top locations then add lat and long from the original dataframe.  
Again this dataframe is keyed on location (1 row per location) and 4 columns: location, lat, lon, amount  
Make sure you have the same number of rows as the top_locations dataframe


`def tickets_in_top_locations(violations_df : pd.DataFrame, threshold=1000):`

Return a dataframe of the parking tickets that were issued in the top locations.  
This dataframe is keyed on ticket number and has the same columns as the original dataframe.  
It should just be a subset of the original dataframe where the location one of the top locations.  
There should be 8,109 rows in this dataframe.

Finally your: `if __name__ == '__main__'`

should read in the input dataframe, call your functions, and write the output dataframes to CSV files.

**IMPORTANT NOTE:**

The tests in `test_etl.py` verify your functions by checking column names and row counts only. They do not check the data in the dataframes.

### Part 2: Complete the two dashboard programs

#### map_dashboard.py

This data dashboard will visualize the top locations on a heatmap. Each location should plotted with circle  representing the amount of fines issued at that location. If you use geopandas this will be very little code.

Here's an animation of the dashboard in action:

[https://imgur.com/jsqmgHo](https://imgur.com/jsqmgHo)

#### location_dashboard.py

This dashboard will visualize the top locations where parking tickets are issued. It should be based on tne dataset which has one row per ticket.

The dashboard should have the following components:

Inputs:

- Dropdown: Select a location from the top locations

After selection of location is made:

- Metric total tickets issued at this location
- Metric total amount in fines of tickets issued at this location
- Bar Chart: Show the distribution of tickets by day of the week
- Line Chart: Show the distribution of tickets by hour of the day
- Map: Show the location selected on a map

Use columns to maximize the space on the dashboard.

Here's an animation of the dashboard in action:

[https://imgur.com/vBsA0tI](https://imgur.com/vBsA0tI)

## Turning it in

### Commit Requirements

If you followed directions, you should have your 2 git commits minimum. Its okay to have more, but you should have at least 2.

- commit after completing Part 1
- commit after completing Part 2

### Pushing your code

When you are done, push your code to GitHub.

- Make sure tests pass and code works as expected
- Write your reflection in `reflection.md`
- Commit your changes: VS Code -> menu -> View -> Source Control -> Enter Commit message -> Click "Commit"
- Push your changes: VS Code -> menu -> View -> Source Control -> Click "Sync Changes"

## Grading

🤖 Beep, Boop. This assignment is bot-graded! When you push your code to GitHub, my graderbot is notified there is something to grade. The bot then takes the following actions:

1. Your assignment repository is cloned from Github
2. The bot checks your code and commits according to guidelines outlined in `assignment-criteria.json` (it runs tests, checking code correctness, etc.)
3. The bot reads your `reflection.md` and provides areas for improvement (based on the instructions in the file).
4. A grade is assigned by the bot. Feedback is generated including justification for the grade given.
5. The grade and feedback are posted to Blackboard.

You are welcome to review the bot's feedback and improve your submission as often as you like.

**NOTE: ** Consider this an experiment in the future of education. The graderbot is an AI teaching assistant. Like a human grader, it will make mistakes. Please feel free to question the bots' feedback! Do not feel as if you should gamify the bot. Talk to me! Like a person, we must teach it how to do its job effectively. 
