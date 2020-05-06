#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
import os
import time
from random import randint

from splinter import Browser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from random import randint

import requests

def save_screenshot(browser,save_ss):

    global screenshot_count

    #ScreenShot
    if (save_ss):
        screenshot_count = screenshot_count + 1
        browser.driver.save_screenshot("ss_" + str(screenshot_count) + ".png")

def wait_time(min_actions_wait_time,max_actions_wait_time):
    actions_wait_time = randint(min_actions_wait_time,max_actions_wait_time)
    time.sleep(actions_wait_time)

#Fixed Parameters
screenshot_count = 0
#TO DO: ADD AS PARAMETER ON GUI
publish_wait_time = 60

#MySQL Parameters
mysql_host = os.getenv('MYSQL_HOST','localhost')
mysql_port = os.getenv('MYSQL_PORT','3306')
mysql_db = os.getenv('MYSQL_DB','ezzyads')
mysql_user = os.getenv('MYSQL_USER','root')
mysql_password = os.getenv('MYSQL_PASSWORD','')

base_url="https://www.ezzyads.com/"
limit = os.getenv('LIMIT','100')

#Relation Top Level Category_Id (On Ezzyads DB)
categories = os.getenv('CATEGORIES','33,34').split(",")

size_x = int(os.getenv('SIZE_X',1366))
size_y = int(os.getenv('SIZE_Y',768))
ua = os.getenv('USER_AGENT',"Mozilla/5.0 (Windows NT 6.1; rv:64.0) Gecko/20100101 Firefox/64.0")

user = os.getenv('USER','hello@ezzyads.com')
password = os.getenv('PASSWORD','1qazxsw2QWE123****')

min_actions_wait_time = int(os.getenv('MIN_WAIT_TIME',30))
max_actions_wait_time = int(os.getenv('MAX_WAIT_TIME',60))

if (os.getenv('HEADLESS','1') == '1'):
    run_headless =  True
else:
    run_headless =  False

if (os.getenv('SAVE_SS','0') == '1'):
    save_ss =  True
else:
    save_ss =  False

#Setting Browser Options
res = str(size_x) + "," + str(size_y)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--window-size=%s' % res)
chrome_options.add_argument("--no-sandbox")

try:

    try:
        conn = mysql.connector.connect(
            host = mysql_host,
            port = mysql_port,
            user = mysql_user,
            passwd = mysql_password,
            database = mysql_db
        )

    except:
        print("Error Connecting To Database.")
        exit()

    print("Starting Browser. Going To Pinterest Page.")
    #Start Browser
    browser = Browser("chrome", headless=run_headless, incognito=True, user_agent=ua, options=chrome_options)
    browser.visit("https://www.pinterest.es/")
    browser.driver.maximize_window()

    wait_time(min_actions_wait_time,max_actions_wait_time)
    save_screenshot(browser,save_ss)

    print("Clicking Login Button.")
    #browser.find_by_xpath("//button[contains(.,'Log in')]").first.click()
    browser.find_by_xpath("//button[contains(.,'Iniciar sesión')]").first.click()
    wait_time(min_actions_wait_time,max_actions_wait_time)
    save_screenshot(browser,save_ss)

    print("Filling Login Information.")
    #Fill User And Password
    browser.find_by_id("email").type(user)
    browser.find_by_id("password").type(password)

    #Click On Login
    #browser.find_by_xpath("//button[contains(.,'Log in')]").first.click()
    browser.find_by_xpath("//button[contains(.,'Iniciar sesión')]").first.click()
    wait_time(min_actions_wait_time,max_actions_wait_time)
    save_screenshot(browser,save_ss)

    for category in categories:

        my_cursor = conn.cursor(dictionary=True)
        my_cursor.execute("""SELECT
                                A.postid,
                                COALESCE(A2.title,'') AS category,
                                COALESCE(A.title,'') AS title,
                                COALESCE(C.content,'') AS description,
                                SUBSTRING_INDEX(B.content, ' ', 1) AS image_url
                            FROM qa_posts AS A
                            INNER JOIN qa_categories AS A2 ON A.catidpath1 = A2.categoryid
                            INNER JOIN qa_postmetas AS B ON A.postid = B.postid AND B.title='qa_q_extra'
                            LEFT JOIN qa_postmetas AS C ON A.postid = C.postid AND C.title='qa_q_extra2'
                             WHERE
                                 COALESCE(A.on_pinterest,0) = 0
                                 AND DATE(A.created) < DATE(CURRENT_DATE() )
                                 AND A.catidpath1 = %s LIMIT %s;""",[category,int(limit)])

        my_result = my_cursor.fetchall()
        my_cursor.close()

        if (my_result):

            for result in my_result:

                r = requests.get(result["image_url"])

                if(r.status_code != "404"):
                    print("Post ID: ", str(result["postid"]) )
                    print("Posting To Pinterest: ", result["image_url"] )
                    post_id = str(result["postid"])
                    post_url = base_url + post_id + "/"
                    post_category = result["category"]
                    post_title = result["title"][:100]
                    post_description = result["description"][:500]
                    post_image = result["image_url"]

                    browser.visit("https://www.pinterest.es/pin-builder/")
                    wait_time(min_actions_wait_time,max_actions_wait_time)
                    save_screenshot(browser,save_ss)


                    print("Selecting Board: ", post_category)
                    browser.find_by_xpath("//button[@data-test-id='board-dropdown-select-button']").first.click()
                    wait_time(min_actions_wait_time,max_actions_wait_time)
                    save_screenshot(browser,save_ss)

                    browser.find_by_id("pickerSearchField").type(post_category)
                    wait_time(min_actions_wait_time,max_actions_wait_time)
                    save_screenshot(browser,save_ss)

                    browser.find_by_xpath("//div[@title='" + post_category  + "']").first.click()
                    #wait_time(min_actions_wait_time,max_actions_wait_time)
                    save_screenshot(browser,save_ss)

                    print("Setting Image.")
                    browser.find_by_xpath("//button[contains(.,'Save from site')]").first.click()
                    wait_time(min_actions_wait_time,max_actions_wait_time)
                    save_screenshot(browser,save_ss)

                    browser.find_by_id("pin-draft-website-link").type(post_url)
                    browser.find_by_xpath("//div[@data-test-id='website-link-submit-button']").first.click()
                    wait_time(min_actions_wait_time,max_actions_wait_time)
                    save_screenshot(browser,save_ss)

                    browser.find_by_xpath("//img[@src='" + post_image + "']").first.click()
                    wait_time(min_actions_wait_time,max_actions_wait_time)
                    save_screenshot(browser,save_ss)

                    browser.find_by_xpath("//button[contains(.,'Add to Pin')]").first.click()
                    wait_time(min_actions_wait_time,max_actions_wait_time)
                    save_screenshot(browser,save_ss)

                    print("Filling Title: ", post_title)
                    browser.find_by_xpath("//textarea[@placeholder='Add your title']").first.type(post_title)

                    print("Filling Description: ", post_description)
                    browser.find_by_xpath("//textarea[@placeholder='Tell everyone what your Pin is about']").first.type(post_description)

                    #print("Filling Link: ", post_url)
                    #browser.find_by_xpath("//textarea[@placeholder='Add a destination link']").first.type(post_url)

                    wait_time(min_actions_wait_time,max_actions_wait_time)
                    save_screenshot(browser,save_ss)
                    print("Publishing Pin.")
                    browser.find_by_xpath("//button[contains(.,'Publish')]").first.click()

                    my_cursor = conn.cursor()
                    q = """UPDATE qa_posts SET on_pinterest = 1 WHERE postid = %s;"""
                    my_cursor.execute(q,[post_id])
                    conn.commit()
                    my_cursor.close()

                    time.sleep(publish_wait_time)


    #Quit Browser
    browser.quit()
    if(conn.is_connected()):
        conn.close()

    exit()

except Exception as e:
    print(str(e))
    #DISABLE WHEN DEBUGGING. REENABLE AFTER DEBUGGING
    if(browser):
        browser.quit()