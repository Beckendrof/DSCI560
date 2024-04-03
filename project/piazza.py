from piazza_api import Piazza
from bs4 import BeautifulSoup
import json
import re
import os
import time
from dotenv import load_dotenv

load_dotenv()

p = Piazza()
email = os.getenv('USERNAME')
password = os.getenv("PASSWORD")
p.user_login(email=email, password=password)

class_id = 'lll6cacyxjfg3'
network = p.network(class_id)

data = []

posts = network.iter_all_posts(limit=100)
for k, post in enumerate(posts):
    time.sleep(1)
    post_text = BeautifulSoup(post['history'][0]['content'], 'html.parser').get_text()
    post_text = re.sub(r'\s+', ' ', post_text)  
    post_text = re.sub(r'[\n\r\u2028\u2029]', '', post_text)  
    post_data = {
        'text': post_text,
        'comments': []
    }

    for i, comment in enumerate(post['children']):
        try:
            comment_text = BeautifulSoup(comment['subject'], 'html.parser').get_text()
            comment_text = re.sub(r'\s+', ' ', comment_text)  
            comment_text = re.sub(r'[\n\r\u2028\u2029]', '', comment_text)  
            comment_data = {'text': comment_text, 'replies': []}

            if comment['children']:
                for j, reply in enumerate(comment['children']):
                    reply_text = BeautifulSoup(reply['subject'], 'html.parser').get_text()
                    reply_text = re.sub(r'\s+', ' ', reply_text)  
                    reply_text = re.sub(r'[\n\r\u2028\u2029]', '', reply_text)  
                    comment_data['replies'].append({'text': reply_text})

            post_data['comments'].append(comment_data)
        except:
            for reply in comment['history']:
                reply_content = reply['content']
                reply_content = re.sub(r'\s+', ' ', reply_content)  
                reply_content = re.sub(r'[\n\r\u2028\u2029]', '', reply_content)  
                post_data['comments'].append({'text': reply_content})

    data.append(post_data)

# Write data to JSON file
with open('piazza.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)
