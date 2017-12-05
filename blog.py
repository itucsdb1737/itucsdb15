import psycopg2 as dbapi2
from post import Post
from flask import current_app as app


class Blog:
    def __init__(self):
        self.last_post_id = None

    def add_post(self, title, text, publish_date, writer, like_count):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO BLOG (TITLE, CONTENT, PUBLISH_DATE, WRITER, LIKE_COUNT) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (title, text, publish_date, writer, like_count,))
            connection.commit()
            cursor.close()

    def get_post_id(self, title, writer):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT ID FROM BLOG WHERE (TITLE = %s AND WRITER = %s)"""
            cursor.execute(query, (title, writer,))
            post = cursor.fetchone()
            return post

    def like_post(self, post_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE BLOG 
                       SET LIKE_COUNT = LIKE_COUNT+1
                       WHERE (ID = %s)"""
            cursor.execute(query, (post_id,))
            connection.commit()
            cursor.close()

    def update_post(self, title, content, post_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE BLOG 
                       SET TITLE = (%s),
                       CONTENT = (%s)
                       WHERE (ID = %s)"""
            cursor.execute(query, (title, content, post_id,))
            connection.commit()
            cursor.close()

    def dislike_post(self, post_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE BLOG 
                       SET LIKE_COUNT = LIKE_COUNT-1
                       WHERE (ID = %s)"""
            cursor.execute(query, (post_id,))
            connection.commit()
            cursor.close()

    def get_like_count(self,post_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT LIKE_COUNT FROM BLOG WHERE (ID = %s)"""
            cursor.execute(query, (post_id,))
            post = cursor.fetchone()
            return post

    def delete_post(self, post_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DELETE FROM BLOG WHERE (ID = (%s))"""
            cursor.execute(statement, (post_id,))
            connection.commit()
            cursor.close()

    def get_post_title(self, post_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT TITLE FROM BLOG WHERE (ID = (%s))"""
            cursor.execute(statement, (post_id,))
            title = cursor.fetchone()
            return title

    def get_post_content(self, post_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT CONTENT FROM BLOG WHERE (ID = (%s))"""
            cursor.execute(statement, (post_id,))
            content = cursor.fetchone()
            return content


    def get_all_posts(self):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT ID, TITLE, CONTENT, PUBLISH_DATE, WRITER, LIKE_COUNT FROM BLOG
                       ORDER BY ID DESC"""
            cursor.execute(query)
            all_posts = [(id, Post(title, content, publish_date, writer, like_count))
                        for id, title, content, publish_date, writer, like_count in cursor]

            connection.commit()
            cursor.close()
        return all_posts


