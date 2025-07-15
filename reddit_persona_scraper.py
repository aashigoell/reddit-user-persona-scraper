import os
import praw
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="user persona scraper by /u/yourusername"
)

def fetch_user_content(username, limit=100):
    user = reddit.redditor(username)
    posts = []
    comments = []
    try:
        for submission in user.submissions.new(limit=limit):
            posts.append({
                "title": submission.title,
                "selftext": submission.selftext,
                "subreddit": str(submission.subreddit),
                "url": submission.url,
                "created": datetime.utcfromtimestamp(submission.created_utc).isoformat()
            })
            time.sleep(0.5)
        for comment in user.comments.new(limit=limit):
            comments.append({
                "body": comment.body,
                "subreddit": str(comment.subreddit),
                "link_url": comment.link_url,
                "created": datetime.utcfromtimestamp(comment.created_utc).isoformat()
            })
            time.sleep(0.5)
    except Exception as e:
        print(f"Error fetching data: {e}")
    return posts, comments

def generate_persona(posts, comments):
    persona = {
        "Interests": [],
        "Writing Style": "",
        "Active Subreddits": [],
        "Personality Indicators": [],
        "Potential Occupation/Field": "",
        "Content Engagement": ""
    }
    subreddit_count = {}
    total_length = 0
    for post in posts:
        subreddit_count[post['subreddit']] = subreddit_count.get(post['subreddit'], 0) + 1
        total_length += len(post['selftext'])
    for comment in comments:
        subreddit_count[comment['subreddit']] = subreddit_count.get(comment['subreddit'], 0) + 1
        total_length += len(comment['body'])
    persona['Active Subreddits'] = sorted(subreddit_count.items(), key=lambda x: x[1], reverse=True)[:5]
    if total_length / (len(posts) + len(comments) + 0.01) > 200:
        persona['Writing Style'] = "Elaborate and detailed"
    else:
        persona['Writing Style'] = "Concise and direct"
    persona['Interests'] = [s[0] for s in persona['Active Subreddits']]
    persona['Personality Indicators'] = ["Engages actively in discussions", "Willingness to share opinions"]
    persona['Potential Occupation/Field'] = "Technology enthusiast" if "technology" in persona['Interests'] else "General Reddit user"
    persona['Content Engagement'] = "High engagement" if len(posts) + len(comments) > 50 else "Moderate engagement"
    return persona

def save_persona(persona, username, posts, comments):
    filename = f"{username}_persona.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"User Persona for {username}\n\n")
        for k, v in persona.items():
            f.write(f"{k}: {v}\n\n")
        f.write("\nCitations:\n")
        for idx, post in enumerate(posts[:5]):
            f.write(f"Post {idx+1}: {post['title']} | URL: {post['url']}\n")
        for idx, comment in enumerate(comments[:5]):
            f.write(f"Comment {idx+1}: {comment['body'][:100]}... | Link: {comment['link_url']}\n")
    print(f"Persona saved to {filename}")

if __name__ == "__main__":
    reddit_profile_url = input("Enter Reddit profile URL: ").strip()
    if reddit_profile_url.endswith("/"):
        reddit_profile_url = reddit_profile_url[:-1]
    username = reddit_profile_url.split("/")[-1]
    posts, comments = fetch_user_content(username)
    persona = generate_persona(posts, comments)
    save_persona(persona, username, posts, comments)
