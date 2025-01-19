from ebooklib import epub
import hashlib
import requests

from api.Types import RoyalRoadBook
from common import get_logger, get_config

logger = get_logger(__name__)
config = get_config()

def create_epub(book: RoyalRoadBook) -> epub.EpubBook:
   """
   Create an epub from a RoyalRoadBook object.
   
   Args:
      book (RoyalRoadBook): The book to create the epub from.

   Returns:
      epub.EpubBook: The epub object.
   """
   # All epub metadata needs to be strings.
   epub_book = epub.EpubBook()
   # Get uuid hash of book id
   epub_book.set_identifier(hashlib.md5(str(book.id).encode()).hexdigest())
   # epub_book.set_identifier(str(uuid.uuid4()))
   epub_book.set_title(book.title)
   epub_book.set_language('en')
   epub_book.add_author(book.author)
   epub_book.add_metadata('RR', 'book-id', str(book.id)) # Using 'RR' as a namespace for RoyalRoad metadata

   # These are the optional RoyalRoadBook fields
   if book.description:
      epub_book.add_metadata('DC', 'description', str(book.description))
   if book.genres:
      epub_book.add_metadata('DC', 'subject', '\n'.join(book.genres))
   if book.cover_url:
      epub_book.set_cover(f'{book.slug}-cover.jpg', requests.get(book.cover_url).content)

   # Add chapters
   for chapter in book.chapters:
      epub_chapter = epub.EpubHtml(title=chapter.title, file_name=f'{chapter.slug}.xhtml', lang='en')
      # Convert all newlines into separate paragraphs
      content = chapter.content.replace('\n', '</p><p>')
      epub_chapter.content = f'<h1>{chapter.title}</h1><p>{content}</p>'
      epub_book.add_item(epub_chapter)
      epub_book.spine.append(epub_chapter)

   # add default NCX and Nav file
   epub_book.add_item(epub.EpubNcx())
   epub_book.add_item(epub.EpubNav())

   return epub_book

def save_epub(epub_book: epub.EpubBook, filename: str) -> bool:
   """
   Save an epub to a file.

   Args:
      epub_book (epub.EpubBook): The epub to save.
      filename (str): The filename to save the epub to.

   Returns:
      Whether or not the save was successful.
   """
   return epub.write_epub(filename, epub_book, {})