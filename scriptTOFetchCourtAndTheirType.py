from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import simplematch
import re
from unicodedata import normalize


def normalize_text(raw_text):
    return re.sub("\s\s+", " ", normalize("NFKD", raw_text.strip()))
# Create a new instance of the Firefox WebDriver (you can use other browsers too)
driver = webdriver.Chrome()

# Navigate to the webpage containing the <select> element
url = "https://drt.etribunals.gov.in/front/drt_case_status.php"
driver.get(url)  # Replace with your webpage URL

# Locate the <select> element by its ID, name, XPath, or other locator strategies
select_element = driver.find_element(by=By.ID,value="schemaname" )  # Replace with your locator

# Create a Select object from the <select> element
select = Select(select_element)

# Get all selected options

select_element.click()

# Get all visible options
# visible_options = [ (option.text,option.get_attribute("value")) for option in select.options if option.is_displayed()]

format = {
        "title": "CAT - Lucknow",
        "case_types": [
            {
            "name": "Original Application",
            "value": "1",
            "key": "O.A."
            }
        ],
        "enabled": True,
        "metadata": {
            "url": "https://cgat.gov.in/#/lucknow",
            "value":"3"
        },
        "type": "tribunals",
        "cli_slug": "tribunals",
        "unique_id": "tribunal-lucknow"
        }
visible_options = [ (option.text,option.get_attribute("value")) for option in select.options if option.is_displayed()]
all_rows = []
with open("courts1.py","w+") as f:
    for title,value in visible_options:
        id = ""
        if simplematch.test("DEBT RECOVERY APPELLATE TRIBUNAL - *", title):
           type = "drt"
           unique_id = "drat-"+simplematch.match("DEBT RECOVERY APPELLATE TRIBUNAL - {}", title)[0].lower()
        elif simplematch.test("DEBTS RECOVERY TRIBUNAL *", title):
          type = "drat"
          if simplematch.test("*(DRT *)",title):
             data = simplematch.match("DEBTS RECOVERY TRIBUNAL {name}(DRT {num})", title)
             unique_id = "drt-" +normalize_text(data["name"]).lower()+ "-" + data["num"]
          else:   
             unique_id = "drt-"+simplematch.match("DEBTS RECOVERY TRIBUNAL {}", title)[0].lower()
        else:
           continue     
        row = {"title":title,"case_type":[],"enabled":True,"metadata":{"url": "https://drt.etribunals.gov.in/front/drt_case_status.php","value":value},"type":type,"cli_slug":type,"unique_id":unique_id}
        select_element = driver.find_element(by=By.ID,value="schemaname" )  # Replace with your locator

        # Create a Select object from the <select> element
        select = Select(select_element)
        select.select_by_visible_text(title)
        wait = WebDriverWait(driver, 10)
        reloaded_element = wait.until(EC.presence_of_element_located((By.ID, "case_type")))
        select_element1 = driver.find_element(by=By.ID,value="case_type" )
        select1 = Select(select_element1)
        for option in select1.options:
            if option.is_displayed():
                caseType = {"name":option.text,"value":option.get_attribute("value")} 
                row['case_type'].append(caseType)
        all_rows.append(row)    
    f.write(str(all_rows))            

    # visible_options1 = [ [option.text,option.get_attribute("value")] for option in select1.options if option.is_displayed()]
# Print the visible option values

# Close the browser window

# for i in range(1,len(visible_options)):
#     url = "https://drt.etribunals.gov.in/front/drt_case_status.php"
#     select_element = driver.find_element(by=By.ID,value="schemaname" )  # Replace with your locator

#     # Create a Select object from the <select> element
#     select = Select(select_element)
#     print(visible_options[i][0])
#     select.select_by_visible_text(visible_options[i][0])
#     wait = WebDriverWait(driver, 10)
#     reloaded_element = wait.until(EC.presence_of_element_located((By.ID, "case_type")))
#     select_element1 = driver.find_element(by=By.ID,value="case_type" )
#     select1 = Select(select_element1)
#     visible_options1 = [ [option.text,option.get_attribute("value")] for option in select1.options if option.is_displayed()]
#     print(visible_options1)

# driver.quit()