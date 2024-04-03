import spacy
import torch
import json
import numpy as np
from transformers import BertTokenizer, BertModel

nlp = spacy.load("en_core_web_sm")

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

with open('piazza.json', 'r') as file:
    data = json.load(file)

def preprocess_text(data):
    processed_posts = []
    processed_comments_replies = []

    for entry in data:
        post_text = entry["text"]
        doc = nlp(post_text)
        tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
        processed_post = ' '.join(tokens)
        processed_posts.append(processed_post)

        comments = []
        replies = []
        for comment_entry in entry["comments"]:
            comment_text = comment_entry["text"]
            doc = nlp(comment_text)
            tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
            processed_comment = ' '.join(tokens)
            comments.append(processed_comment)

            try:
                for reply_entry in comment_entry["replies"]:
                    reply_text = reply_entry["text"]
                    doc = nlp(reply_text)
                    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
                    processed_reply = ' '.join(tokens)
                    replies.append(processed_reply)
            except:
                replies.append([])

        processed_comments_replies.append((comments, replies))

    return processed_posts, processed_comments_replies

def generate_bert_embeddings(texts):
    if not texts or not texts[0]:  # Check if texts is empty or if the inner list is empty
        return None

    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    
    embeddings = outputs.last_hidden_state[:, 0, :].numpy()

    return embeddings

posts, comments_replies = preprocess_text(data)
post_embeddings = generate_bert_embeddings(posts)

reply_embeddings = []
comment_data = []
count = 0

for comments, replies in comments_replies:
    comment_emb = generate_bert_embeddings(comments)
    for reply in replies:
        reply_emb = generate_bert_embeddings(reply)
        reply_embeddings.append(reply_emb)
    comment_data.append({"comment_embedding":comment_emb, "reply_embeddings": reply_embeddings})

matched_data = []

for i, (post, (comments, replies)) in enumerate(zip(posts, comments_replies)):
    post_data = {
        "post_text": post,
        "post_embedding": post_embeddings[i],
        "comments": []
    }
    
    for comment, comment_info in zip(comments, comment_data):
        comment_emb = comment_info["comment_embedding"]
        reply_embeddings = comment_info["reply_embeddings"]
        comment_data_info = {
            "comment_text": comment,
            "comment_embedding": comment_emb,
            "replies": []
        }
        
        for reply, reply_emb in zip(replies, reply_embeddings):
            reply_data = {
                "reply_text": reply,
                "reply_embedding": reply_emb
            }
            comment_data_info["replies"].append(reply_data)
        
        post_data["comments"].append(comment_data_info)

    matched_data.append(post_data)

def convert_to_json_serializable(data):
    if isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, dict):
        return {key: convert_to_json_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_json_serializable(item) for item in data]
    else:
        return data

matched_data_serializable = convert_to_json_serializable(matched_data)

output_file = "embeddings.json"
with open(output_file, "w") as json_file:
    json.dump(matched_data_serializable, json_file, indent=4)

print(f"Embeddings have been stored in '{output_file}'.")