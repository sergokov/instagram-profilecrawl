import os
import sqlite3
from os.path import join


class DatabaseAPI:
    def __init__(self, db_folder):
        self.db_path = join(db_folder, 'db', 'instapy.db')

    def insert_profile(self, name, bio, bio_url, alias_name, posts_num, follower, following, is_private):
        query = "INSERT INTO crawled_profile (name, bio, bio_url, alias_name, posts_num, follower, following, is_private) " \
                "VALUES ('{}', '{}', '{}', '{}', {}, {}, {}, {});"\
            .format(name, bio, bio_url, alias_name, posts_num, follower, following, is_private)

        connection = sqlite3.connect(self.db_path)
        with connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            try:
                cursor.execute(query)
            except Exception as e:
                query = "UPDATE crawled_profile SET posts_num={}, follower={}, following={}, is_private={};"\
                    .format(posts_num, follower, following, is_private)
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                cursor.execute(query)


    def insert_post(self, profile_name, link, crawling_order, preview_image_url, image_url, likes, comments):
        query = "INSERT INTO post (profile_name, link, crawling_order, preview_image_url, image_url, likes, comments, is_crawled) " \
                "VALUES ('{}', '{}', {}, '{}', '{}', {}, {}, 0);"\
            .format(profile_name, link, crawling_order, preview_image_url, image_url, likes, comments)

        connection = sqlite3.connect(self.db_path)
        with connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            try:
               cursor.execute(query)
            except Exception as e:
                print(e)

    def insert_liker(self, name, post_link):
        query = "INSERT INTO liker (name, post_link) VALUES ('{}', '{}');".format(name, post_link)

        connection = sqlite3.connect(self.db_path)
        with connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(query)

    def insert_commenter(self, name, post_link, comment):
        query = "INSERT INTO commenter (name, post_link, comment) VALUES ('{}', '{}', '{}');".format(name, post_link, comment)

        connection = sqlite3.connect(self.db_path)
        with connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(query)

    def load_posts_links(self, profile, posts_number, is_crawled = 0):
        query = "SELECT link FROM post WHERE profile_name = '{}' AND is_crawled = {} ORDER BY crawling_order LIMIT {};"\
            .format(profile, is_crawled, posts_number)

        results = []

        connection = sqlite3.connect(self.db_path)
        with connection:
            connection.row_factory = sqlite3.Row

            try:
                results = connection.execute(query).fetchall()
                results = [dict(row_proxy)['link'] for row_proxy in results]
            except Exception as e:
                print(e)

        return results

    def update_post(self, link, image_url, likes, comments):
        query = "UPDATE post SET image_url='{}', likes={}, comments={}, is_crawled=1 WHERE link='{}';"\
            .format(image_url, likes, comments, link)

        connection = sqlite3.connect(self.db_path)
        with connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(query)
