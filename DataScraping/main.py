import requests
from bs4 import BeautifulSoup
from scraper import scrape_and_insert_data
from connection import establish_connection
from fake_useragent import UserAgent

def get_fake_user_agent_response(requests,url) :
    try:
        user_agent = UserAgent() # Create a UserAgent object
        random_user_agent = user_agent.random # Generate a random user agent string
        headers = {"User-Agent": random_user_agent} # Set headers with the random user agent
        return requests.get(url, headers=headers, timeout=30, verify=False)
        # Process the response here
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)

def get_max_pages(soup):
    if len(soup.find("td", class_="middletext").find_all("a")) == 0:
        max_number_of_pages = 1
    else:
        if soup.find("td", class_="middletext").find_all("a")[-2].text == '»':
            max_number_of_pages = int(soup.find("td", class_="middletext").find_all("a")[-3].text)
        else:
            max_number_of_pages = int(soup.find("td", class_="middletext").find_all("a")[-2].text)
    return max_number_of_pages

def generate_category_urls(base_url, board_id, top_page_topics):
    category_urls = [base_url + str(board_id) + '.' + str(40*i) for i in range(top_page_topics)]

    list_of_topics = []

    for category_url in category_urls:

        try:
            response = get_fake_user_agent_response(requests,category_url)
            if response is not None and response.status_code == 200:
                html = response.text
                # Process the HTML content
            else:
                print(f"Request failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

        soup = BeautifulSoup(html, "html.parser")

        list_of_topics_in_one_page_elements = soup.find_all("div", {"class":"tborder"})[-2].find("table", {"class":"bordercolor"}).find_all("tr")[1:]
        list_of_topics_in_one_page = [a.find_all("span")[0].find("a").get("href")[:-2] for a in list_of_topics_in_one_page_elements]
        list_of_topics += list_of_topics_in_one_page

    return list_of_topics


def generate_page_urls(base_url, board_id, top_page_topics):
    list_of_topics = generate_category_urls(base_url, board_id, top_page_topics)
    
    url_list = []

    for topic_url in list_of_topics:
        response = requests.get(topic_url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        max_number_of_pages = get_max_pages(soup)

        for page_number in range(max_number_of_pages):
            url_list.append(topic_url + '.' + str(page_number * 20))
    return url_list


def main():
    print("***** START *****")

    database_table_name = 'bitcoin_talk'
    
    base_url = 'https://bitcointalk.org/index.php?board='
    board_id = 56
    top_page_topics = 2

    url_list = generate_page_urls(base_url, board_id, top_page_topics)

    print("All URLs are extracted!")
    print("Total URL number: " + str(len(url_list)))

    scrape_and_insert_data(url_list, database_table_name)

    print('Successfully completed!')
    print("***** FINISH *****")

if __name__ == "__main__":
    main()
