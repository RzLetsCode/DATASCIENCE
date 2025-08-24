from flask import Flask, request, jsonify
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
import re
import time
import urllib.parse
import logging
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB connection setup
username = urllib.parse.quote_plus("kjxsofttechpvtltd")
password = urllib.parse.quote_plus("Rz@Fas092311")
connection_string = f"mongodb+srv://kjxsofttechpvtltd:{password}@kjxwebsite.3mup0.mongodb.net/"

client = MongoClient(connection_string, tls=True)
db = client['LinkedinScrapper']
collection = db['Mentors data']

# Utility function to take screenshots and save them in a specified folder
def take_screenshot(driver, folder_path, file_name):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Create folder if it doesn't exist
    file_path = os.path.join(folder_path, f"{file_name}.png")
    driver.save_screenshot(file_path)
    logger.info(f"Screenshot saved at {file_path}")

def login(driver, email, password):
    logger.info("Navigating to LinkedIn login page.")
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    email_elem = driver.find_element(By.ID, "username")
    email_elem.send_keys(email)
    password_elem = driver.find_element(By.ID, "password")
    password_elem.send_keys(password)
    password_elem.submit()

    try:
        # Wait for successful login
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "global-nav-search")))
        logger.info(f"Successfully logged into LinkedIn. Current URL: {driver.current_url}")

    except Exception as e:
        logger.error(f"Login failed. Error: {str(e)}")
        take_screenshot(driver, "screenshots", "login_error")  # Take screenshot on error
        raise

def extract_user_id(profile_url):
    return profile_url.split('/')[-2]

def clean_text(text):
    return re.sub(r'<!---->', '', text)

def clean_full_name(full_name):
    return re.sub(r'^\(\d+\)\s*', '', full_name).strip()

def extract_profile_picture(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    profile_picture = soup.find('img', {'class': 'presence-entity__image'})
    return profile_picture['src'] if profile_picture else "Profile picture not found"

def extract_background_image(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    background_image_tag = soup.find('img', {'class': 'profile-background-image__image'})
    return background_image_tag['src'] if background_image_tag else "Background image not found"

def extract_skills(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    skill_elements = soup.find_all('a', {'data-field': 'skill_card_skill_topic'})
    return [clean_text(skill.find('span', {'aria-hidden': 'true'}).text.strip()) for skill in skill_elements]

def scrape_profile(driver, profile_url):
    logger.info(f"Scraping profile: {profile_url}")
    driver.get(profile_url)
    time.sleep(random.uniform(2, 5))  # Adding random delay to mimic human behavior

    try:
        html_content = driver.page_source
        user_id = extract_user_id(profile_url)

        full_name_match = re.search(r'(?<=<title>).+? \| LinkedIn', html_content)
        full_name = clean_text(full_name_match.group().replace(" | LinkedIn", "")) if full_name_match else "Full name not found"
        full_name = clean_full_name(full_name)

        headline_match = re.search(r'<div class="text-body-medium break-words"[^>]*>([^<]+)</div>', html_content)
        headline = clean_text(headline_match.group(1).strip()) if headline_match else "Headline not found"

        location_match = re.search(r'<span class="text-body-small inline t-black--light break-words"[^>]*>([^<]+)</span>', html_content)
        location = clean_text(location_match.group(1).strip()) if location_match else "Location not found"

        profile_picture_url = extract_profile_picture(html_content)
        background_image_url = extract_background_image(html_content)

        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract About Section
        about_header = soup.find('div', {'id': 'about'})
        about_text = "About section not found"
        if about_header:
            about_section = about_header.find_next('div', class_='display-flex ph5 pv3')
            if about_section:
                about_text = "\n".join(clean_text(child.get_text(strip=True)) for child in about_section.children if child.name is not None)

        # Extract Experience Section
        experience_pattern = re.compile(r'<div id="experience".*?</section>', re.DOTALL)
        experience_section = experience_pattern.search(html_content)
        experiences = []
        if experience_section:
            experience_html = experience_section.group()
            item_pattern = re.compile(r'<li class="artdeco-list__item.*?</li>', re.DOTALL)
            items = item_pattern.findall(experience_html)
            for item in items:
                experience = {'position': '', 'company': '', 'duration': '', 'location': ''}
                company_match = re.search(r'data-field="experience_company_logo".*?<span aria-hidden="true">(.*?)</span>', item, re.DOTALL)
                if company_match:
                    experience['position'] = clean_text(re.sub(r'<.*?>', '', company_match.group(1)).strip())
                position_matches = re.findall(r'<span aria-hidden="true">(.*?)</span>', item)
                if position_matches:
                    experience['company'] = clean_text(position_matches[1].strip())
                duration_match = re.search(r'<span class="pvs-entity__caption-wrapper" aria-hidden="true">(.*?)</span>', item)
                if duration_match:
                    experience['duration'] = clean_text(re.sub(r'<.*?>', '', duration_match.group(1)).strip())
                location_matches = re.findall(r'<span aria-hidden="true">(.*?)</span>', item)
                if len(location_matches) > 2:
                    experience['location'] = clean_text(location_matches[-1].strip())
                experiences.append(experience)

        # Extract Education Section
        education_pattern = re.compile(r'<div id="education".*?</section>', re.DOTALL)
        education_section = education_pattern.search(html_content)
        educations = []
        if education_section:
            education_html = education_section.group()
            entry_pattern = re.compile(r'<li class="artdeco-list__item.*?</li>', re.DOTALL)
            entries = entry_pattern.findall(education_html)
            for entry in entries:
                education = {'university': '', 'degree': '', 'field_of_study': '', 'years': ''}
                university_match = re.search(r'<span aria-hidden="true">(.*?)</span>', entry)
                if university_match:
                    education['university'] = clean_text(university_match.group(1)).strip()
                degree_field_match = re.search(r'<span aria-hidden="true">(.*?), (.*?)</span>', entry)
                if degree_field_match:
                    education['degree'] = clean_text(degree_field_match.group(1)).strip()
                    education['field_of_study'] = clean_text(degree_field_match.group(2)).strip()
                years_match = re.search(r'<span class="pvs-entity__caption-wrapper" aria-hidden="true">(.*?)</span>', entry)
                if years_match:
                    education['years'] = clean_text(years_match.group(1)).strip()
                educations.append(education)

        # Extract Skills
        skills = extract_skills(html_content)

        profile_data = {
            "User ID": user_id,
            "Full Name": full_name,
            "Headline": headline,
            "Location": location,
            "Profile Picture URL": profile_picture_url,
            "Background Image URL": background_image_url,
            "About Section": about_text,
            "Experience": experiences,
            "Education": educations,
            "Skills": skills
        }

        logger.info(f"Profile data scraped: {profile_data}")

        # Insert the profile data into MongoDB and capture the inserted_id
        insert_result = collection.insert_one(profile_data)
        profile_data['_id'] = str(insert_result.inserted_id)  # Convert ObjectId to string

        return profile_data
    except Exception as e:
        logger.error(f"Error scraping profile {profile_url}: {str(e)}")
        take_screenshot(driver, "screenshots", f"profile_scrape_error_{profile_url.split('/')[-2]}")  # Take screenshot on error
        raise

@app.route('/scrape_profiles', methods=['POST'])
def scrape_profiles():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        profile_links = data.get('profile_links')

        if not email or not password or not profile_links:
            logger.error("Missing required parameters.")
            return jsonify({"error": "Please provide email, password, and profile_links"}), 400 

        # Set Chrome options
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/google-chrome"  # Adjust if necessary
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--incognito")

        logger.info("Initializing WebDriver with specified ChromeDriver path.")

        service = Service("/usr/local/bin/chromedriver")  # Path to ChromeDriver on Linux server
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("WebDriver initialized successfully.")
        
        login(driver, email, password)

        all_profile_data = []
        for link in profile_links:
            try:
                profile_data = scrape_profile(driver, link)
                all_profile_data.append(profile_data)
            except Exception as scrape_error:
                logger.error(f"Error scraping profile {link}: {str(scrape_error)}")
                continue

        logger.info("Scraping completed successfully.")
        return jsonify(all_profile_data)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        if 'driver' in locals():
            driver.quit()
            logger.info("WebDriver session ended.")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)