from api import RoyalRoadAPI
from common import get_config, get_logger
from common import helpers
import epub

config = get_config()
log = get_logger(__name__)

class RoyalRoadScheduler():
    def __init__(self):
        self.api = RoyalRoadAPI()
        self.last_chapter_check = 0
        
    def run(self):
        log.info(f'Running RoyalRoadScheduler...')
        #TODO: Implement chapter checking, instead of downloading entire book every time.

        fictions = []
        if config.ROYAL_ROAD_DOWNLOAD_FOLLOWS:
            log.debug(f'Getting followed fictions and adding to fiction list.')
            fictions.extend(self.api.get_followed_fictions())
        if config.ROYAL_ROAD_DOWNLOAD_FILE:
            log.debug(f'Reading fictions from {config.ROYAL_ROAD_DOWNLOAD_FILE}.')
            fictions.extend(helpers.parse_fiction_ids_from_file(config.ROYAL_ROAD_DOWNLOAD_FILE))

        log.debug(f'Fictions to download: {fictions}')
        for fiction in fictions:
            log.info(f'Downloading chapters for fiction ID: {fiction}.')
            book = self.api.get_full_fiction(fiction)
            log.info(f'Creating epub for {book.slug} (ID:{fiction}) and saving to {config.INGEST_DIR}.')
            epub_book = epub.create_epub(book)
            book_file = f'{config.INGEST_DIR}/{book.slug}.epub'
            log.debug(f'Saving epub to {book_file}.')
            epub.save_epub(epub_book, book_file)
            log.info(f'Epub saved to {book_file}.')

        log.info(f'RoyalRoadScheduler complete.')
