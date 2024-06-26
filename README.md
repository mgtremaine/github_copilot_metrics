# GitHub Copilot Metrics

## Overview

This project is designed to collect, analyze, and report metrics related to the usage of GitHub Copilot. It aims to provide insights into how developers interact with GitHub Copilot, including the number of suggestions accepted, lines of code generated, active users, and more. This data can help understand the tool's impact on developer productivity and code quality.

## Features

- **Data Collection**: Automated scripts to collect metrics from GitHub Copilot usage.
- **Database Integration**: Stores collected data in a SQL database for persistence and easy access.
- **Analysis Tools**: Includes tools for analyzing the collected data to extract meaningful insights.
- **Reporting**: Generates reports on GitHub Copilot usage metrics, including daily, weekly, and monthly summaries.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- MySQL or compatible SQL database
- Access to GitHub Copilot usage data

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/github_copilot_metrics.git
   ```
2. Navigate to the project directory:
   ```
   cd github_copilot_metrics
   ```
3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

### Configuration

1. Copy the `config.example.json` to `config.json` and fill in your database connection details and other configurations.

### Running the Application

1. To start data collection, run:
   ```
   python github_metrics.py 
   ```
    by default it will output raw json from the API.
2. To get help , run:
   ```
   python github_metrics.py -h
   ```
    this will show you the command line options you can pass.

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, and suggest features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
