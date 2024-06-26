#!/usr/bin/env python3

#github_metrics.py is a Python script that retrieves GitHub Copilot usage metrics for an organization or enterprise, and provides options to output the data in various formats.
#Author: Mike Tremaine <mgt@stellarcore.net>
#Date: 2024-06-26
#Revision: 1.0
#License: MIT

import json
import requests
import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

#add command line options to call the functions 
# -g = create_bargraph, -o = output_metrics, -c = output_csv, -s = output_sql
import argparse


def create_bargraph(data):

    # Group data by days, up to 3 days per group
    days = sorted(list(set(item['day'] for item in data)))
    day_groups = [days[i:i+3] for i in range(0, len(days), 3)]

    for group in day_groups:
        # Filter data for the current group of days
        group_data = [item for item in data if item['day'] in group]

        # Continue with the plotting logic for each group
        labels = sorted(list(set(f"{breakdown['language']}/{breakdown['editor']}" for item in group_data for breakdown in item['breakdown'])))
        suggestions_counts_filtered = []
        acceptances_counts_filtered = []
        bar_labels = []

        for day in group:
            for label in labels:
                s_count = sum(breakdown['suggestions_count'] for item in group_data if item['day'] == day for breakdown in item['breakdown'] if f"{breakdown['language']}/{breakdown['editor']}" == label)
                a_count = sum(breakdown['acceptances_count'] for item in group_data if item['day'] == day for breakdown in item['breakdown'] if f"{breakdown['language']}/{breakdown['editor']}" == label)
                if s_count != 0 or a_count != 0:
                    bar_labels.append(f"{day}\n{label}")
                    suggestions_counts_filtered.append(s_count)
                    acceptances_counts_filtered.append(a_count)

        x = np.arange(len(bar_labels))  # the label locations
        width = 0.35  # the width of the bars
        fig_width = max(20, len(bar_labels) * 0.5)  # Adjust the multiplier as needed for spacing
        fig, ax = plt.subplots(figsize=(fig_width, 10))
        # Base layer for suggestions
        rects1 = ax.bar(x, suggestions_counts_filtered, width, label='Suggestions Count')
        # Overlay for acceptances
        rects2 = ax.bar(x, acceptances_counts_filtered, width, bottom=0, label='Acceptances Count')

        # Add labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel('Day\nLanguage/Editor')
        ax.set_ylabel('Count')
        ax.set_title(f'Suggestions and Acceptances Count for {", ".join(group)}')
        ax.set_xticks(x)
        ax.set_xticklabels(bar_labels, fontsize=10)
        ax.legend()

        # Dynamically rotate the x-axis labels based on the number of labels
        rotation_angle = 45 if len(bar_labels) > 10 else 0
        plt.xticks(rotation=rotation_angle)

        plt.tight_layout()
        plt.show()

def connect_to_database(config):
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=config['dbhost'],
            user=config['dbuser'],
            password=config['dbpass'],
            database=config['dbname']
        )
        return connection
    except mysql.connector.Error as error:
        print(f"Failed to connect to database: {error}")
        return None
    
def output_csv(data, filename='output.csv'):
    # Convert the JSON payload to a DataFrame
    df = pd.json_normalize(data, record_path=['breakdown'], meta=['day'], errors='ignore')

    # Output the DataFrame to a CSV file
    df.to_csv(filename, index=False)
    print(f"CSV file '{filename}' has been created.")

def output_metrics(data):
    #Todo pass date range to filter data
    # Output the json response data in a human-readable format
    for item in data:
        print(f"Date: {item['day']}")
        print(f"Total Suggestions Count: {item.get('total_suggestions_count', 0)}")
        print(f"Total Acceptances Count: {item.get('total_acceptances_count', 0)}")
        print(f"Total Lines Suggested: {item.get('total_lines_suggested', 0)}")
        print(f"Total Lines Accepted: {item.get('total_lines_accepted', 0)}")
        print(f"Total Active Users: {item.get('total_active_users', 0)}")
        print(f"Total Chat Acceptances: {item.get('total_chat_acceptances', 0)}")
        print(f"Total Chat Turns: {item.get('total_chat_turns', 0)}")
        print(f"Total Active Chat Users: {item.get('total_active_chat_users', 0)}")
        for breakdown in item.get('breakdown', []):
            print(f"  Language: {breakdown.get('language', '')}")
            print(f"  Editor: {breakdown.get('editor', '')}")
            print(f"  Suggestions Count: {breakdown.get('suggestions_count', 0)}")
            print(f"  Acceptances Count: {breakdown.get('acceptances_count', 0)}")
            print(f"  Lines Suggested: {breakdown.get('lines_suggested', 0)}")
            print(f"  Lines Accepted: {breakdown.get('lines_accepted', 0)}")
            print(f"  Active Users: {breakdown.get('active_users', 0)}")

def create_sql_table(connection, table):
    """
    Create a SQL table if it doesn't exist, with `day` as the primary key and a JSON field for `breakdown`.
    
    Parameters:
    - connection: The database connection object.
    - table: The name of the table to create.
    """
    cursor = connection.cursor()
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table} (
        day DATE PRIMARY KEY,
        breakdown JSON,
        total_suggestions_count INT,
        total_acceptances_count INT,
        total_lines_suggested INT,
        total_lines_accepted INT,
        total_active_users INT,
        total_chat_acceptances INT,
        total_chat_turns INT,
        total_active_chat_users INT
    );
    """
    try:
        cursor.execute(create_table_sql)
        connection.commit()
        print(f"Table '{table}' created successfully.")
    except mysql.connector.Error as error:
        print(f"Failed to create table: {error}")
    finally:
        cursor.close()

def output_sql(config, data):
    """
    Insert or update data in a MySQL table, using `day` as the primary key and storing `breakdown` as a JSON field.
    """
    connection = connect_to_database(config)
    table = config['dbtable']

    if connection is not None:
        cursor = connection.cursor()
        # Check if the table exists and create it if not
        cursor.execute(f"SHOW TABLES LIKE '{table}';")
        result = cursor.fetchone()
        if not result:
            create_sql_table(connection, table)

        for item in data:
            day = item['day']
            breakdown_json = json.dumps(item.get('breakdown', []))
            # Prepare other data fields
            values = (
                day,
                breakdown_json,
                item.get('total_suggestions_count', 0),
                item.get('total_acceptances_count', 0),
                item.get('total_lines_suggested', 0),
                item.get('total_lines_accepted', 0),
                item.get('total_active_users', 0),
                item.get('total_chat_acceptances', 0),
                item.get('total_chat_turns', 0),
                item.get('total_active_chat_users', 0)
            )
            sql = f"""
            INSERT INTO {table} (day, breakdown, total_suggestions_count, total_acceptances_count, total_lines_suggested, total_lines_accepted, total_active_users, total_chat_acceptances, total_chat_turns, total_active_chat_users)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                breakdown = VALUES(breakdown),
                total_suggestions_count = VALUES(total_suggestions_count),
                total_acceptances_count = VALUES(total_acceptances_count),
                total_lines_suggested = VALUES(total_lines_suggested),
                total_lines_accepted = VALUES(total_lines_accepted),
                total_active_users = VALUES(total_active_users),
                total_chat_acceptances = VALUES(total_chat_acceptances),
                total_chat_turns = VALUES(total_chat_turns),
                total_active_chat_users = VALUES(total_active_chat_users);
            """
            try:
                cursor.execute(sql, values)
                connection.commit()
            except mysql.connector.Error as error:
                print(f"Failed to insert/update data: {error}")

        cursor.close()
        connection.close()
    else:
        print("Database connection was not established.")


if __name__ == "__main__":
    #Parse commmand line options
    parser = argparse.ArgumentParser(description='Get GitHub Copilot usage metrics.')
    parser.add_argument('-g', '--graph', action='store_true', help='Create a bar graph of the suggestions and acceptances count by day and language/editor.')   
    parser.add_argument('-o', '--output', action='store_true', help='Output the GitHub Copilot usage metrics in a human-readable format.')  
    parser.add_argument('-c', '--csv', action='store_true', help='Output the GitHub Copilot usage metrics to a csv file. Filename will be in the format <org_name>_YYYYMMDD.csv.')  
    parser.add_argument('-s', '--sql', action='store_true', help='Output the GitHub Copilot usage metrics to a mysql table. Use the config.json file for the database connection.')  
    args = parser.parse_args()

    # Load the configuration
    with open('config.json') as f:
        config = json.load(f)

    # Prepare the headers
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {config['bearer_token']}",
        "X-Accepted-GitHub-Permissions": "contents=read",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Make the request
    #switch if config['type'] == 'org'
    if config['type'] == 'org':
        response = requests.get(f"https://api.github.com/orgs/{config['org']}/copilot/usage", headers=headers)
    else:
        response = requests.get(f"https://api.github.com/enterprises/{config['org']}/copilot/usage", headers=headers)

    # Parse the response
    data = response.json()

    # Call the functions based on the command line options
    if args.output:
        output_metrics(data)    

    if args.graph:
        create_bargraph(data)

    if args.csv:
        #get current machine date in YYYYMMDD format
        org_name = config['org'];
        output_csv(data, f'{org_name}_{datetime.datetime.now().strftime("%Y%m%d")}.csv')

    if args.sql:
        output_sql(config, data)

    #print data this is default pipe it a file if you want to save it
    print(data)

