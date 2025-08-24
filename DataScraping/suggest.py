from seleniumwire import webdriver  # Note the change here
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Initialize the WebDriver
driver = webdriver.Chrome()

try:
    # Open the NoteGPT YouTube summarizer page
    driver.get("https://notegpt.io/youtube-video-summarizer")

    # Maximize the window (optional)
    driver.maximize_window()

    # Wait until the input field for the YouTube link is present
    wait = WebDriverWait(driver, 30)
    youtube_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='youtube.com']")))

    # Enter the YouTube video link
    youtube_link.send_keys("https://www.youtube.com/watch?v=CO4E_9V6li0")  # Replace with your YouTube link

    # Wait for the "Generate Summary" button to be clickable
    generate_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.el-button.ng-script-btn.el-button--success")))
    generate_button.click()

    # Wait for the transcript to load
    time.sleep(10)  # Adjust based on loading time

    # Intercept the network requests to find the transcript data
    transcript_data = None
    for request in driver.requests:
        if request.response and 'transcript' in request.url:
            # Get the response body
            response_body = request.response.body.decode('utf-8')
            try:
                transcript_json = json.loads(response_body)
                # Check if the JSON contains transcript data
                if 'data' in transcript_json:
                    transcript_data = transcript_json['data']
                    break
            except json.JSONDecodeError:
                continue

    if transcript_data:
        # Build the full transcript text
        full_transcript = ''
        for entry in transcript_data:
            text = entry.get('text', '')
            full_transcript += f"{text}\n"

        # Save the transcript to a file
        with open('transcript.txt', 'w', encoding='utf-8') as file:
            file.write(full_transcript)

        print("Transcript saved to transcript.txt")
    else:
        print("Transcript data not found in network requests.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the driver after the process is completed
    driver.quit()
