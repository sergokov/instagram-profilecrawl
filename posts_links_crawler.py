import sys

from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

from util.chromedriver import init_chromedriver
from util.db import DatabaseAPI
from util.extractor import extract_user_posts_links
from util.settings import Settings


def main():
    if len(sys.argv) < 2:
        sys.exit('- Please provide profile to crawl and DB path!\n')
    user_name = sys.argv[1]
    db_path = sys.argv[2]
    proxy = sys.argv[3]

    chrome_options = Options()
    chrome_options.add_argument('--proxy-server=%s' % proxy)
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--lang=en-US')
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US'})

    capabilities = DesiredCapabilities.CHROME

    Settings.sleep_time_between_post_scroll = 3
    Settings.sleep_time_between_comment_loading = 3

    try:
        browser = init_chromedriver(chrome_options, capabilities)
    except Exception as exc:
        print(exc)
        sys.exit()

    try:
        print('Extracting posts links from ' + user_name)
        try:
            user_info, indexed_links, preview_images = extract_user_posts_links(browser, user_name,
                                                                                Settings.limit_amount)
            db = DatabaseAPI(db_path)
            db.insert_profile(user_name, user_info['bio'], user_info['bio_url'], user_info['alias'],
                              user_info['num_of_posts'], int(user_info['followers']['count']),
                              int(user_info['following']['count']), 1 if user_info['isprivate'] else 0)
            for link, index in indexed_links.items():
                db.insert_post(user_name, link, index, preview_images[link], '', 0, 0)
        except Exception as e:
            print("Error with user '{}': {}".format(user_name, e))
            sys.exit(1)

        print("\nFinished crawling profile links.")

    except KeyboardInterrupt:
        print('Aborted...')

    finally:
        # browser.delete_all_cookies()
        browser.close()


if __name__== "__main__":
  main()
