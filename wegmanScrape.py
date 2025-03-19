# requires pip-install of:
# 1) selenium, 2) beautifulsoup4, 3) webdriver_manager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import threading

def printItemDict(searchListDictionary):
    for key, value in searchListDictionary.items():
        print(value, end=' ')
        print(" " + key)

# Given a file containing a python list with names, load them into dictionary.
# Dictionary Format -->  "Ketchup": {"Cost": 0, "Location": 20},
def getDictFromGroceryList(filePathStr):
    guiFoodListFile = open(filePathStr)
    guiFoodList = eval(guiFoodListFile.readline())
    itemSearchList = {}
    for item in guiFoodList:
        itemSearchList[item] = {"Cost": 0, "Location": 20}
    return itemSearchList 

# Specify selenium browser information
def initializeWebDriver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    #options.add_argument("--headless=old")     # Uncomment this line to hide browser loads. Compatibility issue exists with new ChromeDriver headless argument.
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# returns a driver that has loaded wegman webpage for in-store shopping
def setupWegmansShopExperience():
    # -----------------------------------------------------------
    # Load main webpage and setup browsing session for in-store results 
    # -----------------------------------------------------------
    driver = initializeWebDriver()
    driver.get("https://shop.wegmans.com")
    # Button click window has a delay before it becomes valid to click, *independent* of page load status.
    # Force long delay is thus required.
    time.sleep(5) 
    homePageLoaded = False
    while not homePageLoaded:
        try:
            time.sleep(0.5) # wait for page to load
            driver.find_element(By.ID, "shopping-selector-shop-context-intent-instore").click()
            homePageLoaded = True
        except AttributeError:
            print("LOG: Home page wasn't loaded before click atttempt. Trying again.")
    # Button click for shopping in-store seems to also take awhile to propogate to website back-end after clicking. 
    # Wait a bit or we will get asked again on each load which will break flow.
    time.sleep(5)
    return driver 

def getWegmanItemDetails(driver, key, value):
    # -----------------------------------------------------------
# Search location and price information for all items in list
# -----------------------------------------------------------
    url = "https://shop.wegmans.com/search?search_term=" + key
    driver.get(url)
    resultFound = False
    time.sleep(1)
    while not resultFound:
        time.sleep(0.5) # give sufficient time for results to populate. Wait 0.5 secs each loop before try reading again.
        # Find cost and location of item. Catch exception if page load was too fast.
        try:
            soup = BeautifulSoup(driver.page_source,features="html.parser")
            main = soup.body.find('main', id="react-page")
            searchViewLayout = main.find('div', class_="css-kg2siz")
            shopProductItemsList = searchViewLayout.find('ul', class_='css-1qb57ou') # this is where everything really is!
            foodItemsArr = shopProductItemsList.findAll('li', class_='css-h5b5ap') # these are the actual food items
            # The 0-2nd search items sometimes have wegman special products with special HTML structure... which is not helpful for this demo. So we do 3rd item.
            itemLocation = foodItemsArr[3].find('span', class_="css-8uhtka") 
            itemCost = foodItemsArr[3].find('span', class_="css-zqx11d")
            #Load values of cost and location into dictionary
            value["Cost"] = itemCost.get_text()
            if (itemLocation.get_text() == "    Produce"): 
                value["Location"] = 18
            elif (itemLocation.get_text() == "   Fresh Bakery"): 
                value["Location"] = 19
            # If we encounter and aisle# greater than our estimated number range [1-17], group it into aisle 20. This is not realistic, but needed as we do not have a schematic of the store.
            # The comparison is done in ASCII to also group any other special locations, like "    beer" into aisle 20 for demo purposes without crashing, as we cannot be sure of how many locations like this there are. 
            elif ((itemLocation.get_text()[:2]).encode('ascii') < "01".encode('ascii') or (itemLocation.get_text()[:2]).encode('ascii') > "17".encode('ascii')): 
                value["Location"] = 20
            else:
                # Store default "01-17" string aisles directly from the website, casted to int.
                value["Location"] = int(itemLocation.get_text()[:2])
            resultFound = True
        except AttributeError:
            print("LOG: Item could not be found or page was not loaded fast enough. Trying Again")

def findAllItems(key, value):
    driver = setupWegmansShopExperience()
    getWegmanItemDetails(driver, key, value)
    driver.quit()

class multiThreadScrape(threading.Thread): 
    def __init__(self, key, value):
        threading.Thread.__init__(self)
        self.key = key
        self.value = value
    def run(self):
        findAllItems(self.key, self.value)

# *************************************************************
# *************************************************************
# Core Program Below
#
# Reads a file to get user-requested grocery list from 
# food-selection GUI. Then loads Wegman webpage and searches
# one-by-one for the pricing and store location information.
# 
# End Product is n-sized dictionary, "itemSearchList", of format: 
#   ...
#   "Ketchup": {"Cost": 0, "Location": 20},
#   ...
# *************************************************************
# *************************************************************

# Read in the grocery list outputted from GUI
#itemSearchList is a dictionary, but due to sleepyness I have misnomered it, and it is now called called cross-file...
def fullSearch():
    itemSearchList = getDictFromGroceryList("selected-foods.txt") 
    #printItemDict(itemSearchList)

    threads = []
    for key, value in itemSearchList.items():
        newThread = multiThreadScrape(key, value)
        newThread.start()
        threads.append(newThread)
        print("Starting new thread for item: " + key)

    for item in threads:
        item.join()
    #printItemDict(itemSearchList)
    return itemSearchList


