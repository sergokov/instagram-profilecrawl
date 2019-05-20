import sys

from selenium.common.exceptions import NoSuchElementException

from util.db import DatabaseAPI
from util.extractor_posts import extract_post_info
from util.instalogger import InstaLogger
from util.proxy import ProxyRotator
from util.settings import Settings


def main():
    if len(sys.argv) < 3:
        sys.exit('- Please provide number of posts to crawl!\n')

    Settings.scrape_posts_likers = True
    Settings.sleep_time_between_post_scroll = 3
    Settings.sleep_time_between_comment_loading = 3
    Settings.sleep_time_between_post_crawl = 10

    profile = sys.argv[1]
    posts_to_crawl = sys.argv[2]
    db_path = sys.argv[3]
    db = DatabaseAPI(db_path)
    posts_links = db.load_posts_links(profile, posts_to_crawl)

    proxies_file = open("assets/proxy.list", "r")
    proxy_list = []
    if len(proxies_file.readline()) != 0:
        proxy_list = proxies_file.readline().split(',')
    proxy_rotator = ProxyRotator(proxy_list)

    for post_link in posts_links:
        proxy = proxy_rotator.next_proxy()
        post_info = _extract_post_info(proxy.browser, post_link)
        proxy_rotator.return_proxy(proxy)
        print(post_info)
        db.update_post(post_link, post_info['imgs'][0], post_info['likes']['count'], post_info['comments']['count'])
        for liker in post_info['likes']['list']:
            db.insert_liker(liker, post_link)
        for commenter in post_info['comments']['list']:
            db.insert_commenter(commenter, post_link, commenter)


def _extract_post_info(proxy_browser, post_link):
    try:

        caption, location_url, location_name, location_id, lat, lng, imgs, img_desc, tags, likes, comments_count, \
        date, user_commented_list, user_comments, mentions, user_liked_post, views = extract_post_info(proxy_browser, post_link)

        location = {
            'location_url': location_url,
            'location_name': location_name,
            'location_id': location_id,
            'latitude': lat,
            'longitude': lng,
        }

        return {
            'caption': caption,
            'location': location,
            'imgs': imgs,
            'imgdesc': img_desc,
            'date': date,
            'tags': tags,
            'likes': {
                'count': likes,
                'list': user_liked_post
            },
            'views': views,
            'url': post_link,
            'comments': {
                'count': comments_count,
                'list': user_comments
            },
            'mentions': mentions
        }
    except NoSuchElementException as err:
        InstaLogger.logger().error("Could not get information from post: " + post_link)
        InstaLogger.logger().error(err)
    except Exception as ex:
        InstaLogger.logger().error("Could not get information from post: " + post_link)
    return None


if __name__== "__main__":
    main()
