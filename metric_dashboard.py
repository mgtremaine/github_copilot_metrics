#!/usr/bin/env python3
import cgi
import cgitb
import json
import mysql.connector

cgitb.enable()

print("Content-Type: text/html\n")

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

def fetch_data(config):
    connection = connect_to_database(config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT day, 
               breakdown, 
               total_suggestions_count, 
               total_acceptances_count, 
               total_active_users, 
               total_active_chat_users 
        FROM {config['dbtable']} 
        ORDER BY day DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows

def generate_dashboard(data):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GitHub Copilot Metrics Dashboard</title>
        <!-- Bootstrap CSS CDN -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <!-- Bootstrap Table CSS -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-table/1.18.3/bootstrap-table.min.css">
        <script>
            function toggleDetails(id) {
                var element = document.getElementById(id);
                if (element.style.display === 'none') {
                    element.style.display = 'block';
                } else {
                    element.style.display = 'none';
                }
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1 class="mt-5">GitHub Copilot Metrics Dashboard</h1>
            <table class="table table-bordered mt-3">
                <thead>
                    <tr>
                        <th>Day</th>
                        <th>Suggestions</th>
                        <th>Acceptances</th>
                        <th>Active Users</th>
                        <th>Active Chat Users</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
    """
    for index, row in enumerate(data):
        day_id = f"details-{index}"
        breakdown = json.loads(row['breakdown'])
        # Assuming breakdown now includes 'editor', 'lines_accepted', 'lines_suggested', 'active_users'
        details_html = """
        <table class='table'>
            <thead>
                <tr>
                    <th>Editor</th>
                    <th>Language</th>
                    <th>Lines Accepted</th>
                    <th>Lines Suggested</th>
                    <th>Active Users</th>
                </tr>
            </thead>
            <tbody>
        """ + "".join([
            f"""
            <tr>
                <td>{item['editor']}</td>
                <td>{item['language']}</td>
                <td>{item.get('lines_accepted', 'N/A')}</td>
                <td>{item.get('lines_suggested', 'N/A')}</td>
                <td>{item.get('active_users', 'N/A')}</td>
            </tr>
            """ for item in breakdown
        ]) + "</tbody></table>"
        html_content += f"""
                    <tr>
                        <td>{row['day']}</td>
                        <td>{row['total_suggestions_count']}</td>
                        <td>{row['total_acceptances_count']}</td>
                        <td>{row['total_active_users']}</td>
                        <td>{row['total_active_chat_users']}</td>
                        <td><a href="javascript:void(0);" onclick="toggleDetails('details-{index}')">View Details</a></td>
                    </tr>
                    <tr id="details-{index}" class="collapse">
                        <td colspan="6">{details_html}</td>
                    </tr>
        """
    html_content += """
                </tbody>
            </table>
        </div>
        <!-- Bootstrap and Bootstrap Table JS -->
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-table/1.18.3/bootstrap-table.min.js"></script>
    </body>
    </html>
    """
    return html_content

# Load the configuration
with open('config.json') as f:
    config = json.load(f)

data = fetch_data(config)
print(generate_dashboard(data))