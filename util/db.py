import os
from os.path import join

from sqlalchemy import create_engine, Boolean
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey


class DatabaseAPI:
    DB_PATH = 'assets/db'
    PROFILE = 'profile'
    POST = 'post'
    LIKER = 'liker'
    COMMENTER = 'commenter'
    db_engine = None

    def __init__(self):
        db_path = join(self.DB_PATH, 'profile_crawl.db')
        self.db_engine = create_engine('sqlite:///{PATH}'.format(PATH=db_path))
        if not os.path.isfile(db_path):
            self.create_db_tables()

    def create_db_tables(self):
        metadata = MetaData()
        profile = Table(self.PROFILE, metadata,
                        Column('name', String, primary_key=True),
                        Column('bio', String, nullable=True),
                        Column('bio_url', String, nullable=True),
                        Column('alias_name', String, nullable=True),
                        Column('posts_num', Integer, nullable=True),
                        Column('follower', Integer, nullable=True),
                        Column('following', Integer, nullable=True),
                        Column('is_private', Boolean, nullable=True)
                      )

        post = Table(self.POST, metadata,
                        Column('profile_name', None, ForeignKey('profile.name')),
                        Column('link', String, primary_key=True),
                        Column('indx', Integer, nullable=False),
                        Column('preview_image_url', String, nullable=True),
                        Column('image_url', String, nullable=True),
                        Column('likes', Integer, nullable=True),
                        Column('comments', Integer, nullable=True),
                        Column('is_crawled', Boolean, nullable=False)
                      )

        liker = Table(self.LIKER, metadata,
                        Column('name', String, nullable=False, primary_key=True),
                        Column('post_link', None, ForeignKey('post.link'), primary_key=True)
                      )

        commenter = Table(self.COMMENTER, metadata,
                        Column('name', String, nullable=False, primary_key=True),
                        Column('post_link', None, ForeignKey('post.link'), primary_key=True),
                        Column('comment', String, nullable=False, primary_key=True)
                      )
        try:
            metadata.create_all(self.db_engine)
            print("Tables created")
        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)

    def insert_profile(self, name, bio, bio_url, alias_name, posts_num, follower, following, is_private):
        query = "INSERT INTO {}(name, bio, bio_url, alias_name, posts_num, follower, following, is_private) " \
                "VALUES ('{}', '{}', '{}', '{}', {}, {}, {}, {}) ON CONFLICT (name) " \
                "DO UPDATE SET bio='{}', bio_url='{}', alias_name='{}', posts_num={}, follower={}, " \
                "following={}, is_private={};"\
            .format(self.PROFILE, name, bio, bio_url, alias_name, posts_num, follower, following, is_private,
                    bio, bio_url, alias_name, posts_num, follower, following, is_private)

        with self.db_engine.connect() as connection:
            try:
                connection.execute(query)
                connection.commit()
                connection.close()
            except Exception as e:
                print(e)

    def insert_post(self, profile_name, link, index, preview_image_url, image_url, likes, comments):
        query = "INSERT INTO {}(profile_name, link, indx, preview_image_url, image_url, likes, comments, is_crawled) " \
                "VALUES ('{}', '{}', {}, '{}', '{}', {}, {}, false) ON CONFLICT (link) " \
                "DO UPDATE SET profile_name='{}', preview_image_url='{}', image_url='{}', likes={}, comments={}, is_crawled=true;"\
            .format(self.POST, profile_name, link, index, preview_image_url, image_url, likes, comments, profile_name,
                    preview_image_url, image_url, likes, comments)

        with self.db_engine.connect() as connection:
            try:
                connection.execute(query)
                connection.commit()
                connection.close()
            except Exception as e:
                print(e)

    def insert_liker(self, name, post_link):
        query = "INSERT INTO {}(name, post_link) VALUES ('{}', '{}') ON CONFLICT (name, post_link) DO NOTHING;"\
            .format(self.LIKER, name, post_link)

        with self.db_engine.connect() as connection:
            try:
                connection.execute(query)
                connection.commit()
                connection.close()
            except Exception as e:
                print(e)

    def insert_commenter(self, name, post_link, comment):
        query = "INSERT INTO {}(name, post_link, comment) VALUES ('{}', '{}', '{}') " \
                "ON CONFLICT (name, post_link, comment) DO NOTHING;".format(self.COMMENTER, name, post_link, comment)

        with self.db_engine.connect() as connection:
            try:
                connection.execute(query)
                connection.commit()
                connection.close()
            except Exception as e:
                print(e)

    def load_posts_links(self, profile, posts_number, is_crawled = False):
        # query = "SELECT link FROM {} WHERE profile_name = '{}' AND is_crawled = {} ORDER BY indx LIMIT {};"\
        #     .format(self.POST, profile, is_crawled, posts_number)

        query = "SELECT link FROM {} WHERE profile_name = '{}' ORDER BY indx LIMIT {};"\
            .format(self.POST, profile, posts_number)

        results = []

        with self.db_engine.connect() as connection:
            try:
                results = connection.execute(query).fetchall()
                results = [row_proxy.items()[0][1] for row_proxy in results]
                connection.commit()
                connection.close()
            except Exception as e:
                print(e)

        return results

    def update_post(self, link, image_url, likes, comments):
        query = "UPDATE {} SET image_url='{}', likes={}, comments={}, is_crawled=true WHERE link='{}';"\
            .format(self.POST, image_url, likes, comments, link)

        with self.db_engine.connect() as connection:
            try:
                connection.execute(query)
                connection.commit()
                connection.close()
            except Exception as e:
                print(e)
