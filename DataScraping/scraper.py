import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from connection import establish_connection
from fake_useragent import UserAgent

def get_fake_user_agent_response(requests,url) :
    user_agent = UserAgent() # Create a UserAgent object
    random_user_agent = user_agent.random # Generate a random user agent string
    headers = {"User-Agent": random_user_agent} # Set headers with the random user agent
    return requests.get(url, headers=headers)

nltk.download("vader_lexicon")

def extract_post_text(post_div_element):
    post_text = ''
    for content in post_div_element.contents:
        if isinstance(content, str):
            post_text += content
        elif content.name == 'div' and 'quoteheader' in content.get('class', []):
            continue
        elif content.name == 'div' and 'quote' in content.get('class', []):
            continue
        else:
            post_text += content.text
    return post_text

def scrape_and_insert_data(url_list, database_table_name):
    connection = establish_connection()
    cursor = connection.cursor()
    
    print('Sentiment model is downloaded and connected to the database.')

    for url in url_list:
        try:
            response = get_fake_user_agent_response(requests,url)
            if response.status_code == 200:
                html = response.text
                # Process the HTML content
            else:
                print(f"Request failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

        soup = BeautifulSoup(html, "html.parser")

        print("START URL: " + str(url))
        
        #####################################################################################################################
        ### SCRAPPING - START
        #####################################################################################################################

        form_elements = soup.find("form", {"name":"quickModForm", "id":"quickModForm"}).find_all('tr', attrs={'class': True})

        element_classes_list = [elem.get('class')[0] for elem in form_elements]
        elements_list = [elem for elem in form_elements if elem.get('class')[0] == element_classes_list[0]]

        return_data = []

        for idx, elem in enumerate(elements_list):
            post_div_element = elements_list[idx].find("td", {"class":"td_headerandpost"}).find("div", {"class":"post"})

            post_no_quote = extract_post_text(post_div_element)

            sid = SentimentIntensityAnalyzer()
            sentiment_scores = sid.polarity_scores(post_no_quote)

            post_timestamp = re.search(r'(.*?)Last edit:', elements_list[idx].find_all("div", {"class": "smalltext"})[1].text)

            if post_timestamp:
                post_timestamp_str = post_timestamp.group(1).strip()
            else:
                post_timestamp_str = elements_list[idx].find_all("div", {"class": "smalltext"})[1].text

            post_data = {}

            post_id = elements_list[idx].find_all("td", {"valign":"middle"})[1].find("div", {"class":"subject"}).find("a").get("href")
            
            post_data["post_id"] = re.search(r'msg(\d+)#msg\d+$', post_id).group(1)
            post_data["post_url"] = elements_list[idx].find_all("td", {"valign":"middle"})[0].find("a").get('href')
            post_data["post_timestamp"] = post_timestamp_str
            post_data["post_page"] = [int(b_element.text.strip()) for b_element in soup.find("td", class_="middletext").find_all("b") if b_element.text.strip().isdigit()][0]
            post_data["post_author"] = elements_list[idx].find("td", {"class":"poster_info"}).find("b").find("a").text
            post_data["post_full"] = elements_list[idx].find("td", {"class":"td_headerandpost"}).find("div", {"class":"post"}).text
            post_data["post_no_quote"] = post_no_quote
            post_data["topic_name"] = re.search(r'Topic:\s*(.*?)\s*\(', soup.find("td", {"valign": "middle", "id": "top_subject"}).text).group(1).strip()

            #sentiment_scores['neu'] ### If it is wanted, use it!
            post_data["sentiment_compound"] = sentiment_scores['compound']
            post_data["sentiment_positive"] = sentiment_scores['pos']
            post_data["sentiment_negative"] = sentiment_scores['neg']

            post_data["inserted_timestamp"] = datetime.today().strftime('%Y-%m-%d')
            return_data.append(post_data)


        #####################################################################################################################
        ### SCRAPPING - FINISH
        #####################################################################################################################

        with connection.cursor() as cursor:
            select_query = f"SELECT post_id FROM {database_table_name}"
            cursor.execute(select_query)
            existing_post_ids = {row[0] for row in cursor.fetchall()}

            for data in return_data:
                if int(data['post_id']) not in existing_post_ids:
                    insert_query = f"""
                    INSERT INTO {database_table_name} (post_id, post_url, post_timestamp, post_page, post_author,
                                              post_full, post_no_quote, topic_name, sentiment_compound,
                                              sentiment_positive, sentiment_negative, inserted_timestamp)
                    VALUES (%(post_id)s, %(post_url)s, %(post_timestamp)s, %(post_page)s, %(post_author)s,
                            %(post_full)s, %(post_no_quote)s, %(topic_name)s, %(sentiment_compound)s,
                            %(sentiment_positive)s, %(sentiment_negative)s, %(inserted_timestamp)s)
                    """
                    cursor.execute(insert_query, data)

        connection.commit()

    connection.close()
