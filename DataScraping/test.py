from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    video_url = request.json.get('video_url')
    if not video_url:
        return jsonify({'error': 'No video URL provided'}), 400

    # Initialize Chrome options for incognito mode
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")  # Run in headless mode if desired
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Open the NoteGPT YouTube summarizer page
        driver.get("https://notegpt.io/youtube-video-summarizer")

        # Maximize the window (optional)
        driver.maximize_window()

        # Wait until the input field for the YouTube link is present
        wait = WebDriverWait(driver, 30)
        youtube_link = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder*='youtube.com']")))

        # Enter the YouTube video link
        youtube_link.send_keys(video_url)

        # Wait for the "Generate Summary" button to be clickable
        generate_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.el-button.ng-script-btn.el-button--success")))
        generate_button.click()

        # Wait for the transcript container to appear
        transcript_container = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.ng-transcript")))

        # Find the inner scrollable div
        scrollable_div = transcript_container.find_element(By.CSS_SELECTOR, "div[style*='overflow-y: auto']")

        # Initialize a list to store transcript texts in order
        transcript_texts = []

        # Scroll to the top of the scrollable div
        driver.execute_script("arguments[0].scrollTop = 0;", scrollable_div)

        # Wait for initial content to load
        time.sleep(2)

        # Get the total scroll height
        total_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        viewport_height = driver.execute_script("return arguments[0].clientHeight", scrollable_div)

        # Initialize scroll position
        scroll_position = 0
        scroll_increment = 6000  # Adjust as needed
        last_position = -1

        while scroll_position < total_height:
            # Scroll down by increment
            driver.execute_script("arguments[0].scrollTop = arguments[1];", scrollable_div, scroll_position)
            time.sleep(0.1)  # Adjust as needed

            # Extract visible transcript items at current scroll position
            transcript_divs = scrollable_div.find_elements(By.CSS_SELECTOR, "div.ng-transcript-item-text")
            for div in transcript_divs:
                text = div.text.strip()
                if text and text not in transcript_texts:
                    transcript_texts.append(text)

            # Update scroll position
            scroll_position += scroll_increment

            # Update total_height in case it changes due to dynamic loading
            new_total_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            if new_total_height != total_height:
                total_height = new_total_height

            # Check if we've reached the bottom
            if scroll_position >= total_height or scroll_position == last_position:
                break

            last_position = scroll_position

        # Ensure all elements are fully loaded
        time.sleep(2)

        # Combine all transcript texts in order
        full_transcript = "\n".join(transcript_texts)

        # Return the transcript as JSON response
        return jsonify({'transcript': full_transcript}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the driver after the process is completed
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
