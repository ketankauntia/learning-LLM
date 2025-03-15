import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

def scrape_forum_posts(forum_url, file_name, max_posts=5):
    output_folder = "scraped_companies_data"
    os.makedirs(output_folder, exist_ok=True)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(forum_url)
    time.sleep(5)  # Allow JavaScript to load

    scraped_posts = []

    while len(scraped_posts) < max_posts:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        posts = soup.find_all("article", class_="boxed onscreen-post")

        for post in posts:
            if len(scraped_posts) >= max_posts:
                break
            
            # Extract username
            username_tag = post.find("a", class_="trigger-user-card")
            username = username_tag.text.strip() if username_tag else "Unknown"
            
            # Extract date
            date_tag = post.find("span", class_="relative-date")
            date = date_tag["title"] if date_tag else "Unknown"
            
            # Extract likes
            likes_tag = post.find("button", class_="widget-button btn-flat button-count like-count")
            likes = likes_tag.text.strip() if likes_tag else "0"
            
            # Extract post content
            content_tag = post.find("div", class_="cooked")
            if content_tag:
                for img in content_tag.find_all("img"):
                    img.decompose()  # Remove images
                content = content_tag.get_text(strip=True)
            else:
                content = ""
            
            scraped_posts.append({
                "post_id": len(scraped_posts) + 1,
                "username": username,
                "date": date,
                "likes": likes,
                "content": content
            })
        
        # Stop if no new posts are found
        if len(scraped_posts) >= max_posts:
            break
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for more posts to load

    driver.quit()

    output_path = os.path.join(output_folder, f"{file_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scraped_posts, f, ensure_ascii=False, indent=4)

    print(f"✅ Scraping finished! Total posts scraped: {len(scraped_posts)}")
    print(f"📂 Data saved at: {output_path}")

# Example usage:
forum_url = input("Enter the forum URL to scrape: ").strip()
file_name = input("Enter the filename (without extension): ").strip()
scrape_forum_posts(forum_url, file_name)

