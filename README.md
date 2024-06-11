Here's a README file for your web scraping script:

---

# Yahoo News Scraper

This script navigates to Yahoo News' Politics section, scrapes article details including titles, URLs, dates, times, durations, contents, and images, and saves the collected data into a CSV file. The script reads configuration settings from a YAML file for customization and includes robust logging and error handling.

## Features

- Navigate to Yahoo News' Politics section
- Scrape article details: titles, URLs, dates, times, durations, contents, and images
- Save scraped data into a CSV file with a timestamped filename
- Download images and save them with the article title as the filename
- Robust logging for each action step
- Configurable via a YAML file for different environments

## Requirements

- Python 3.x
- Selenium
- Pandas
- PyYAML (for reading the configuration file)
- ChromeDriver (matching your installed Chrome version)

## Setup

1. **Install Required Packages:**

   ```bash
   pip install selenium pandas requests pyyaml
   ```

2. **Download ChromeDriver:**
   
   Ensure you have the ChromeDriver installed and its path specified in the configuration file. The ChromeDriver version must match your installed Chrome version. Download it from [ChromeDriver download page](https://sites.google.com/a/chromium.org/chromedriver/downloads).

3. **Configuration:**

   Create a YAML configuration file (`app_config.yaml`) with the following structure:

   ```yaml
   development:
     url:
       yahoo_news_url: "https://news.yahoo.com/"
     file_path:
       chrome_driver_path: "path/to/your/chromedriver"
       log_path: "path/to/log/folder/"
       output_path: "path/to/output/folder/"
       image_path: "path/to/image/folder/"
   production:
     url:
       yahoo_news_url: "https://news.yahoo.com/"
   ```

4. **Update the Script:**

   Ensure the script reads the correct paths and URLs from the YAML configuration file.

## Usage

1. **Run the Script:**

   ```bash
   python main.py
   ```

2. **Logging:**

   The script will create log files in the specified log folder. The log file will contain detailed information about each action taken by the script.

3. **Output:**

   The script will save the scraped data into a CSV file in the specified output folder. The CSV filename will include the current timestamp.

## Functions

- **log_file_setup:** Sets up the log file structure based on the current date.
- **navigate_to_politics_section:** Navigates to the Politics section of Yahoo News.
- **collect_articles:** Collects article titles and URLs.
- **download_image:** Downloads images and saves them with the article title as the filename.
- **scrape_article_data:** Scrapes article details including date, time, duration, content, and image.
- **save_to_csv:** Saves the scraped data into a CSV file with a timestamped filename.

## Error Handling

The script includes error handling for common issues such as missing elements and timeouts. Detailed error messages are logged for troubleshooting.

---

This README provides a comprehensive overview of the script, its setup, usage, and functionalities.
