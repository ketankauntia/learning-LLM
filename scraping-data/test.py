import os
import re
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

def scrape_forum_posts_5(forum_url, file_name):
    output_folder = "scraped_companies_data"
    os.makedirs(output_folder, exist_ok=True)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(forum_url)
    time.sleep(5)  # Allow time for JavaScript to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    posts = soup.find_all("article", class_="boxed onscreen-post")

    scraped_posts = []

    for post in posts:
        if len(scraped_posts) >= 5:
            break

        # 1) Username
        username_tag = post.select_one("span.first.username a") or post.find("a", class_="trigger-user-card")
        username = username_tag.get_text(strip=True) if username_tag else "Unknown"

        # 2) Date (relative + exact)
        date_tag = post.find("span", class_="relative-date")
        date_relative = date_tag.get_text(strip=True) if date_tag else "Unknown"
        date_time = date_tag["title"] if (date_tag and date_tag.has_attr("title")) else "Unknown"

        # 3) Likes (target the button inside div.double-button)
        likes = "0"
        like_button = post.select_one("div.double-button > button.widget-button.btn-flat.button-count.like-count")
        if like_button:
            # Remove any <svg> icons so get_text() only returns the numeric text node
            for svg in like_button.find_all("svg"):
                svg.decompose()
            raw_text = like_button.get_text(strip=True)  # e.g. "1"
            match = re.search(r'(\d+)', raw_text)
            if match:
                likes = match.group(1)

        # 4) Content
        content_tag = post.find("div", class_="cooked")
        if content_tag:
            for img in content_tag.find_all("img"):
                img.decompose()
            content = content_tag.get_text(strip=True)
        else:
            content = ""

        scraped_posts.append({
            "post_id": len(scraped_posts) + 1,
            "username": username,
            "date_relative": date_relative,
            "date_time": date_time,
            "likes": likes,
            "content": content
        })

    driver.quit()

    # Save JSON
    output_path = os.path.join(output_folder, f"{file_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scraped_posts, f, ensure_ascii=False, indent=4)

    print(f"✅ Scraping finished! Total posts scraped: {len(scraped_posts)}")
    print(f"📂 Data saved at: {output_path}")

# Example usage
if __name__ == "__main__":
    forum_url = input("Enter the forum URL to scrape: ").strip()
    file_name = input("Enter the filename (without extension): ").strip()
    scrape_forum_posts_5(forum_url, file_name)




# Scrapes all the posts with username, data, date-time. likes not wroking. and doesnt logs to teh console.

# import os
# import time
# import json
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from bs4 import BeautifulSoup
# from webdriver_manager.chrome import ChromeDriverManager

# def scrape_forum_posts_all(forum_url, file_name):
#     output_folder = "scraped_companies_data"
#     os.makedirs(output_folder, exist_ok=True)

#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")

#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#     driver.get(forum_url)
#     time.sleep(5)  # Allow JS to load

#     scraped_posts = []
#     prev_post_count = 0

#     while True:
#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         posts = soup.find_all("article", class_="boxed onscreen-post")

#         # Parse new posts
#         for post in posts:
#             # We'll identify each post by a unique data-post-id or combination of text
#             post_id_attr = post.get("data-post-id", None)
            
#             # Skip if we already scraped this post (avoid duplicates)
#             already_scraped = any(
#                 p.get("post_html_id") == post_id_attr 
#                 for p in scraped_posts
#             )
#             if already_scraped:
#                 continue

#             # 1) Extract username
#             username_tag = post.select_one("span.first.username a")
#             if not username_tag:
#                 username_tag = post.find("a", class_="trigger-user-card")
#             username = username_tag.text.strip() if username_tag else "Unknown"

#             # 2) Extract date (both relative and exact timestamp)
#             date_tag = post.find("span", class_="relative-date")
#             date_relative = date_tag.text.strip() if date_tag else "Unknown"
#             date_time = date_tag["title"] if date_tag and date_tag.has_attr("title") else "Unknown"

#             # 3) Extract likes
#             likes_tag = post.find("button", class_="widget-button btn-flat button-count like-count")
#             likes = likes_tag.text.strip() if likes_tag else "0"

#             # 4) Extract post content (remove images)
#             content_tag = post.find("div", class_="cooked")
#             if content_tag:
#                 for img in content_tag.find_all("img"):
#                     img.decompose()
#                 content = content_tag.get_text(strip=True)
#             else:
#                 content = ""

#             scraped_posts.append({
#                 # We'll store the original post_id from the HTML if it exists
#                 "post_html_id": post_id_attr,
#                 "username": username,
#                 "date_relative": date_relative,
#                 "date_time": date_time,
#                 "likes": likes,
#                 "content": content
#             })

#         # If the post count didn't increase after parsing, we've likely reached the end
#         if len(scraped_posts) == prev_post_count:
#             break

#         prev_post_count = len(scraped_posts)

#         # Scroll down to load more posts
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(3)

#     driver.quit()

#     # Assign a simple 1-based post_id for final JSON output
#     for idx, post_data in enumerate(scraped_posts, start=1):
#         post_data["post_id"] = idx

#     # Save JSON
#     output_path = os.path.join(output_folder, f"{file_name}.json")
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(scraped_posts, f, ensure_ascii=False, indent=4)

#     print(f"✅ Scraping finished! Total posts scraped: {len(scraped_posts)}")
#     print(f"📂 Data saved at: {output_path}")

# # Example usage
# if __name__ == "__main__":
#     forum_url = input("Enter the forum URL to scrape: ").strip()
#     file_name = input("Enter the filename (without extension): ").strip()
#     scrape_forum_posts_all(forum_url, file_name)

