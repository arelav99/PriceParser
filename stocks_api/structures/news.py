from datetime import datetime

class News:
    def __init__(
        self,
        title: str,
        link: str,
        date_time: datetime,
        uuid: str,
        source: str
    ):
        self.title = title
        self.link = link
        self.date_time = date_time
        self.uuid = uuid
        self.source = source

    def __str__(self):
        return f"{self.title};\n {self.link};\n Written on {self.date_time}; UUID - {self.uuid}"
