import time
import os
from selenium import webdriver
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tqdm import tqdm

# Ensure the data directory exists
data_dir = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(data_dir, exist_ok=True)

def save_fpds_content(links, original_data):
    try:
        service = SafariService()
        driver = webdriver.Safari(service=service)
        
        for i, link in enumerate(tqdm(links, desc="Downloading FPDS content")):
            retries = 3
            success = False
            while retries > 0 and not success:
                try:
                    driver.get(link)
                    WebDriverWait(driver, 120).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    page_source = driver.page_source
                    html_filename = os.path.join(data_dir, f"fpds_content_{i}.html")
                    text_filename = os.path.join(data_dir, f"fpds_content_{i}.txt")
                    
                    # Save the HTML content
                    with open(html_filename, "w", encoding="utf-8") as file:
                        file.write(page_source)
                    
                    # Save the original data and URL
                    with open(text_filename, "w", encoding="utf-8") as file:
                        file.write(f"Original URL: {link}\n\nOriginal Data:\n{original_data}\n")
                    
                    success = True
                except Exception as e:
                    retries -= 1
                    if retries == 0:
                        text_filename = os.path.join(data_dir, f"fpds_content_{i}.txt")
                        with open(text_filename, "w", encoding="utf-8") as file:
                            file.write(f"Original URL: {link}\n\nError: Failed to load page after 3 retries.\n")
                        print(f"Error fetching FPDS content for {link}: {e}")
                
                # Delay to limit the rate of requests
                time.sleep(1)
        
        driver.quit()
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")

def find_table(url):
    try:
        # Initialize the Safari WebDriver
        service = SafariService()
        driver = webdriver.Safari(service=service)
        driver.get(url)
        
        # Wait for the table to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # Click all "See More" elements to expand the data
        see_more_elements = driver.find_elements(By.XPATH, "//td[@colspan='6' and contains(@class, 'cursor-pointer') and text()='see more']")
        for element in see_more_elements:
            element.click()
            WebDriverWait(driver, 10).until(
                EC.staleness_of(element)
            )
        
        # Get the page source after JavaScript has rendered the content
        page_source = driver.page_source
        driver.quit()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return
    
    soup = BeautifulSoup(page_source, "html.parser")
    table = soup.find("table")
    
    if (table):
        print("Table found:")
        print(table.prettify())  # Prettify prints the table in a more readable format
        
        # Save the table to a file
        with open(os.path.join(data_dir, "dogetable.html"), "w", encoding="utf-8") as file:
            file.write(table.prettify())
        
        # Extract and follow fpds.gov links
        fpds_links = [a['href'] for a in table.find_all('a', href=True) if 'fpds.gov' in a['href']]
        save_fpds_content(fpds_links, table.prettify())
    else:
        print("No table found on the page.")

if __name__ == "__main__":
    url = "https://doge.gov/savings"
    find_table(url)