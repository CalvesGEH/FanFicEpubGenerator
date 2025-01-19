import datetime
from slugify import slugify

class RoyalRoadChapter():
    def __init__(self):
        self.slug = None
        self.title = None
        self.url = None
        self.content = None
        self.published = None
        self.last_updated = datetime.datetime.now()

    def validate(self):
        # These are the only required fields
        if not self.title or type(self.title) != str:
            raise ValueError("Invalid title")
        if not self.url or type(self.url) != str:
            raise ValueError("Invalid url")
        if not self.content or type(self.content) != str:
            raise ValueError("Invalid content")
        if not self.last_updated or type(self.last_updated) != datetime.datetime:
            raise ValueError("Invalid last_updated")

    def __repr__(self):
        return f"RoyalRoadChapter({self.title}, {self.url})"

class RoyalRoadBook():
    def __init__(self, id):
        self.id = int(id)
        self.slug = None
        self.title = None
        self.description = None
        self.author = None
        self.num_chapters = 0
        self._chapters = []
        self.cover_url = 'http://www.royalroad.com/dist/img/nocover-new-min.png'
        self.genres = []

    @property
    def chapters(self):
        return self._chapters
    
    # Automatically set the number of chapters when setting chapters.
    @chapters.setter
    def chapters(self, value):
        if type(value) == list:
            self._chapters = value
            self.num_chapters = len(value)
        else:
            raise ValueError("Invalid type for chapters")

    def validate(self):
        # These are the only required fields
        if not self.id or type(self.id) != int:
            raise ValueError("Invalid id")
        if not self.title or type(self.title) != str:
            raise ValueError("Invalid title")
        if type(self.num_chapters) != int or self.num_chapters <= 0:
            raise ValueError("Invalid num_chapters")
        if not self.chapters:
            raise ValueError("Invalid chapters")
        if type(self.chapters) != list or type(self.chapters) != list or type(self.chapters[0]) != RoyalRoadChapter:
            raise ValueError("Invalid chapters")
    
        # Populate slug if we only have title.
        if not self.slug:
            self.slug = slugify(self.title)

        # Set the author to 'Unknown' if it's not provided.
        if not self.author:
            self.author = 'Unknown'

        return True

    def __repr__(self):
        return f"RoyalRoadBook({self.title}, {self.author}, {self.num_chapters})"