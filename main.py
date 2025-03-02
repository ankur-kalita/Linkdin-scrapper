import asyncio
import json
import pandas as pd
from pyppeteer import launch

# Load LinkedIn profile URLs from Excel
excel_file = "Assignment.xlsx"
df = pd.read_excel(excel_file, engine='openpyxl')
profile_urls = df.iloc[:, 0].dropna().tolist()  # Assuming first column contains URLs

async def scrape_linkedin():
    browser = await launch(
        headless=False,
        executablePath="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Change this path if needed
        args=["--no-sandbox"]
    )
    page = await browser.newPage()

    # Set a realistic user agent
    await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    )

    # Open LinkedIn login page
    await page.goto("https://www.linkedin.com/login", {"waitUntil": "networkidle2"})
    
    # Prompt user to log in manually
    input("🔵 Log in manually in the opened browser, then press ENTER here to continue...")

    scraped_data = []

    for url in profile_urls:
        print(f"🔍 Scraping: {url}")
        try:
            await page.goto(url, {"waitUntil": "networkidle2"})
            await asyncio.sleep(5)  # Wait for the page to fully load

            # Extract Name
            try:
                name_element = await page.querySelector(".text-heading-xlarge")
                name = await page.evaluate("(element) => element.innerText.trim()", name_element)
            except:
                name = "N/A"

            # Extract Bio
            try:
                bio_element = await page.querySelector(".text-body-medium.break-words")
                bio = await page.evaluate("(element) => element.innerText.trim()", bio_element)
            except:
                bio = "N/A"

            # Extract Social Links (Twitter, GitHub, etc.)
            try:
                social_links = {}
                contact_info_button = await page.querySelector("a[href*='contact-info']")
                if contact_info_button:
                    await contact_info_button.click()
                    await asyncio.sleep(2)  # Allow contact info popup to load
                    links = await page.querySelectorAll(".pv-contact-info__ci-container a")
                    for link in links:
                        text = await page.evaluate("(element) => element.innerText.trim()", link)
                        href = await page.evaluate("(element) => element.href", link)
                        social_links[text] = href
            except:
                social_links = {}

            # Extract Experience
            experience = {}
            try:
                exp_sections = await page.querySelectorAll(".pv-profile-section__list-item")
                for section in exp_sections:
                    company_element = await section.querySelector(".pv-entity__secondary-title")
                    role_element = await section.querySelector(".t-14.t-black.t-normal")

                    company = await page.evaluate("(element) => element.innerText.trim()", company_element) if company_element else "N/A"
                    role = await page.evaluate("(element) => element.innerText.trim()", role_element) if role_element else "N/A"

                    experience[company] = role
            except:
                experience = {}

            # Extract Education
            education = {}
            try:
                edu_sections = await page.querySelectorAll(".pv-education-entity")
                for section in edu_sections:
                    university_element = await section.querySelector(".pv-entity__school-name")
                    degree_element = await section.querySelector(".pv-entity__comma-item")

                    university = await page.evaluate("(element) => element.innerText.trim()", university_element) if university_element else "N/A"
                    degree = await page.evaluate("(element) => element.innerText.trim()", degree_element) if degree_element else "N/A"

                    education[university] = degree
            except:
                education = {}

            # Store Data
            scraped_data.append({
                "LinkedIn URL": url,
                "Name": name,
                "Bio": bio,
                "Socials": json.dumps(social_links),
                "Experience": json.dumps(experience),
                "Education": json.dumps(education)
            })

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")

    # Save Data to CSV
    output_csv = "scraped_output.csv"
    df_output = pd.DataFrame(scraped_data)
    df_output.to_csv(output_csv, index=False)

    print("✅ Scraping complete. Data saved to 'scraped_output.csv'")
    await browser.close()

# Run the scraper
asyncio.run(scrape_linkedin())
