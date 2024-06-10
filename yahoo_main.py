import os
import platform
import logging
import pandas as pd
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import requests
import config_reader

# reading yaml config file
config_data = config_reader.load_config("C:\\Python\\rpa_challange\\config\\app_config.yaml")
environment = "Development"

if environment == "Production":
    yahoo_news_url = config_data['production']['url']['yahoo_news_url']
else:
    yahoo_news_url = config_data['development']['url']['yahoo_news_url']
    chrome_driver_path = config_data['development']['file_path']['chrome_driver_path']
    log_folder_path = config_data['development']['file_path']['log_path']
    output_path = config_data['development']['file_path']['output_path']
    image_path = config_data['development']['file_path']['image_path']

def log_file_setup():
    today = date.today()
    today_date_folder = today.strftime("%m%d%Y")
    log_folder = os.path.join(log_folder_path, today_date_folder)
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    return log_folder

log_folder = log_file_setup()

if platform.system() == 'Windows':
    logging_file = os.path.join(os.getenv('HOMEDRIVE'), os.getenv('HOMEPATH'), log_folder, 'Process_log.log')
else:
    logging_file = os.path.join(os.getenv('HOME'), log_folder, 'Process_log.log')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s : %(levelname)s : %(message)s',
                    filename=logging_file,
                    filemode='a')

logging.info("** Yahoo Fetch News Scraper Started **")

# Setup Chrome options to avoid detection
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Initialize the WebDriver
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

def navigate_to_politics_section():
    try:
        driver.get(yahoo_news_url)
        time.sleep(2)  # Wait for the page to load
        logging.info(f"{yahoo_news_url} URL is loaded in the browser successfully")

        # Navigate to the Politics section
        politics_link = driver.find_element(By.LINK_TEXT, "Politics")
        politics_link.click()
        time.sleep(2)  # Wait for the page to load
        logging.info("Navigated to Politics section.")
    except Exception as e:
        logging.error(f"Error navigating to Politics section: {e}")

def collect_articles():
    articles = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        try:
            # Find all article elements on the page
            article_elements = driver.find_elements(By.XPATH, "//li[contains(@class, 'js-stream-content')]//h3/a")
            for element in article_elements:
                title = element.text
                url = element.get_attribute('href')
                if (title, url) not in articles:
                    articles.append((title, url))

            # Scroll down to load more articles
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Wait for the page to load

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        except NoSuchElementException as e:
            logging.error(f"Error finding article elements: {e}")
            break
    logging.info(f"Collected {len(articles)} articles.")
    return articles

def download_image(img_url, img_name, output_dir):
    try:
        response = requests.get(img_url)
        if response.status_code == 200:
            img_path = os.path.join(output_dir, img_name)
            with open(img_path, 'wb') as file:
                file.write(response.content)
            logging.info(f"Image downloaded: {img_path}")
            return img_path
        else:
            logging.error(f"Failed to download image: {img_url}")
            return None
    except Exception as e:
        logging.error(f"Error downloading image: {e}")
        return None

def scrape_article_data(articles):
    data = []
    if not os.path.exists(image_path):
        os.makedirs(image_path)

    for index, (title, url) in enumerate(articles, start=1):
        driver.get(url)
        time.sleep(2)  # Wait for the page to load

        try:
            # Extract date and time
            date_xpath = "/html/body/div[4]/div/div[2]/main/div[1]/div[2]/div/div/div/div/div/article/div/div/div/div/div/div/div/div/div[1]/div[1]/div/div[2]"
            date_element = driver.find_element(By.XPATH, date_xpath)
            date_text = date_element.text

            # Format the date information
            date_part, time_part_duration = date_text.split(' at ')
            article_time_part, duration_part = time_part_duration.split('·')
            date = date_part.strip()
            article_time = article_time_part.strip()
            duration = duration_part.strip()

            # Extract the main content of the article
            article_xpath = "//div[@class='caas-body']"
            content_element = driver.find_element(By.XPATH, article_xpath)
            content = content_element.text

            # Download the image
            img_xpath = "//img[@class='caas-img']"
            img_element = driver.find_element(By.XPATH, img_xpath)
            img_url = img_element.get_attribute('src')
            img_name = f"{title.replace(' ', '_')}.jpg"
            img_path = download_image(img_url, img_name, image_path)

            data.append({
                "Title": title,
                "URL": url,
                "Date": date,
                "Time": article_time,
                "Duration": duration,
                "Content": content,
                "Image": img_path
            })

            logging.info(f"Article {index} / {len(articles)}: {title}")
            logging.info(f"Date: {date}")
            logging.info(f"Time: {article_time}")
            logging.info(f"Duration: {duration}")
            logging.info(f"Content: {content}")
            logging.info(f"Image Path: {img_path}")
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"Error extracting article at {url}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error extracting article at {url}: {e}")
    return data

def save_to_csv(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = os.path.join(output_path, f"yahoo_news_{timestamp}.csv")
    df = pd.DataFrame(data)
    df.to_csv(output_file_path, index=False, encoding='utf-8')
    logging.info(f"Data saved to {output_file_path}")

def main():
    try:
        navigate_to_politics_section()
        articles = collect_articles()
        data = scrape_article_data(articles)
        save_to_csv(data)
    finally:
        driver.quit()
        logging.info("** Yahoo Fetch News Scraper process completed **")

if __name__ == "__main__":
    main()
