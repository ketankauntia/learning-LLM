from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# Setup Selenium (Headless mode to run in the background)
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Forum URL
url = ""
driver.get(url)

# Allow JavaScript to load
time.sleep(5)

scraped_posts = []
previous_post_count = 0

# Keep scrolling until no new posts load
while True:
    # Get page source after JS execution
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find all posts inside the discussion
    posts_container = soup.find("div", class_="posts-wrapper")
    if posts_container:
        posts = posts_container.find_all("div", class_="cooked")  # Extract actual post content
        
        for post in posts[len(scraped_posts):]:  # Get only new posts
            scraped_posts.append({"post_id": len(scraped_posts) + 1, "content": post.get_text(strip=True)})

    print(f"🔍 Scraped {len(scraped_posts)} posts so far...")

    # Stop if no new posts are loaded
    if len(scraped_posts) == previous_post_count:
        print("✅ No more posts to load. Scraping complete.")
        break

    previous_post_count = len(scraped_posts)

    # Scroll down to load more posts
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Wait for new posts to load

# Save data as JSON
with open("", "w", encoding="utf-8") as f:
    json.dump(scraped_posts, f, ensure_ascii=False, indent=4)

print(f"✅ Scraping finished! Total posts scraped: {len(scraped_posts)}")

# Close Selenium
driver.quit()

