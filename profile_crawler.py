#!/usr/bin/env python3.5
"""Goes through all usernames and collects their information"""
import sys
from time import sleep

import math
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from util.extractor import get_user_info
from util.account import login
from util.chromedriver import init_chromedriver
from util.cli_helper import get_all_user_names
from util.datasaver import Datasaver
from util.exceptions import PageNotFound404, NoInstaProfilePageFound
from util.instalogger import InstaLogger
from util.settings import Settings
from util.util import web_adress_navigator


def main():
    chrome_options = Options()
    chromeOptions = webdriver.ChromeOptions()
    prefs = {'profile.managed_default_content_settings.images': 2, 'disk-cache-size': 4096}
    chromeOptions.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--lang=en-US')
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US'})

    capabilities = DesiredCapabilities.CHROME

    Settings.scrape_posts_likers = True
    Settings.sleep_time_between_post_scroll = 3.5
    Settings.sleep_time_between_comment_loading = 3.5

    try:
        browser = init_chromedriver(chrome_options, capabilities)
    except Exception as exc:
        print(exc)
        sys.exit()

    try:
        usernames = get_all_user_names()

        for username in usernames:
            print('Extracting information from ' + username)
            information = []
            try:
                if len(Settings.login_username) != 0:
                    login(browser, Settings.login_username, Settings.login_password)
                information = extract_posts_links(browser, username, Settings.limit_amount)
            except:
                print("Error with user " + username)
                sys.exit(1)

            Datasaver.save_profile_json(username, information)

            print("\nFinished. The json file and nicknames of users who commented were saved in profiles directory.\n")

    except KeyboardInterrupt:
        print('Aborted...')

    finally:
        browser.delete_all_cookies()
        browser.close()


def extract_posts_links(browser, username, limit_amount):
    InstaLogger.logger().info('Extracting information from ' + username)
    """Get all the information for the given username"""

    try:
        user_link = "https://www.instagram.com/{}/".format(username)
        web_adress_navigator(browser, user_link)
    except PageNotFound404 as e:
        raise NoInstaProfilePageFound(e)

    num_of_posts_to_do = 999999

    try:
        userinfo = get_user_info(browser, username)
        if limit_amount < 1:
            limit_amount = 999999
        num_of_posts_to_do = min(limit_amount, userinfo['num_of_posts'])
    except Exception as err:
        InstaLogger.logger().error("Couldn't get user profile. - Terminating")
        quit()

    """Get all posts from user"""
    indexed_links = dict()
    preview_imgs = {}

    try:
        body_elem = browser.find_element_by_tag_name('body')

        previouslen = 0
        breaking = 0

        print("number of posts to do: ", num_of_posts_to_do)
        num_of_posts_to_scroll = 12 * math.ceil(num_of_posts_to_do / 12)
        print("Getting first", num_of_posts_to_scroll,
              "posts but checking ", num_of_posts_to_do,
              " posts only, if you want to change this limit, change limit_amount value in crawl_profile.py\n")
        while (len(indexed_links) < num_of_posts_to_do):

            prev_divs = browser.find_elements_by_tag_name('main')
            links_elems = [div.find_elements_by_tag_name('a') for div in prev_divs]
            links = sum([[link_elem.get_attribute('href')
                          for link_elem in elems] for elems in links_elems], [])

            for elems in links_elems:
                for link_elem in elems:

                    href = link_elem.get_attribute('href')
                    try:
                        if "/p/" in href:
                            try:
                                img = link_elem.find_element_by_tag_name('img')
                                src = img.get_attribute('src')
                                preview_imgs[href] = src
                            except NoSuchElementException:
                                print("img exception 132")
                                continue
                    except Exception as err:
                        print(err)

            for link in links:
                if "/p/" in link:
                    if (len(indexed_links) < num_of_posts_to_do):
                        if link not in indexed_links:
                            indexed_links[link] = len(indexed_links)
            print("Scrolling profile ", len(indexed_links), "/", num_of_posts_to_scroll)
            body_elem.send_keys(Keys.END)
            sleep(Settings.sleep_time_between_post_scroll)

            ##remove bellow part to never break the scrolling script before reaching the num_of_posts
            if (len(indexed_links) == previouslen):
                breaking += 1
                print("breaking in ", 4 - breaking,
                      "...\nIf you believe this is only caused by slow internet, increase sleep time 'sleep_time_between_post_scroll' in settings.py")
            else:
                breaking = 0
            if breaking > 3:
                print("Not getting any more posts, ending scrolling")
                sleep(2)
                break
            previouslen = len(indexed_links)
            ##

    except NoSuchElementException as err:
        InstaLogger.logger().error('Something went terribly wrong')

    return indexed_links


if __name__== "__main__":
  main()
