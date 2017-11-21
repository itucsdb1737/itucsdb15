
class Game:
    def __init__(self, title, producer, publish_date, content, category, price):
        self.title = title
        self.producer = producer
        self.publish_date = publish_date
        self.content = content
        self.like_count = 0
        self.category = category
        self.price = price