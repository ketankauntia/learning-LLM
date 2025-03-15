import os
import re
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

def scrape_forum_posts_all(forum_url, file_name):
    output_folder = "scraped_companies_data"
    os.makedirs(output_folder, exist_ok=True)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(forum_url)
    time.sleep(5)  # Let JavaScript load

    scraped_posts = []
    prev_post_count = 0

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        posts = soup.find_all("article", class_="boxed onscreen-post")

        for post in posts:
            post_id_attr = post.get("data-post-id", None)

            # Skip if we already scraped this post
            if any(p.get("post_html_id") == post_id_attr for p in scraped_posts):
                continue

            # 1) Username
            username_tag = post.select_one("span.first.username a") or post.find("a", class_="trigger-user-card")
            username = username_tag.get_text(strip=True) if username_tag else "Unknown"

            # 2) Date (relative + exact)
            date_tag = post.find("span", class_="relative-date")
            date_relative = date_tag.get_text(strip=True) if date_tag else "Unknown"
            date_time = date_tag["title"] if (date_tag and date_tag.has_attr("title")) else "Unknown"

            # 3) Likes (target button in div.double-button, remove <svg>)
            likes_button = post.select_one("div.double-button > button.widget-button.btn-flat.button-count.like-count")
            likes = "0"
            if likes_button:
                # Remove any <svg> icons so get_text() only returns numeric text node
                for svg in likes_button.find_all("svg"):
                    svg.decompose()
                raw_text = likes_button.get_text(strip=True)
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
                "post_html_id": post_id_attr,
                "username": username,
                "date_relative": date_relative,
                "date_time": date_time,
                "likes": likes,
                "content": content
            })

        # Check if new posts were actually found
        current_count = len(scraped_posts)
        if current_count == prev_post_count:
            # No new posts → break
            break
        prev_post_count = current_count

        # Scroll down to load more posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    driver.quit()

    # Assign a simple 1-based post_id for final JSON output
    for idx, post_data in enumerate(scraped_posts, start=1):
        post_data["post_id"] = idx

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
    scrape_forum_posts_all(forum_url, file_name)
