# Package/Python Imports
from bs4 import BeautifulSoup
from multiprocessing import Pool
import os
from random import randint
import re
import requests
import sys
import time
import urllib.parse

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from common import get_config, get_logger
from networking import parse_cookies
from .Types import RoyalRoadBook, RoyalRoadChapter


config = get_config()
log = get_logger(__name__)


class RoyalRoadAPI():
    def __init__(self):
        self.request_headers = {}

        # Authentication Variables
        self.authenticated = False
        self.authenticated_user_id = None
        self.authenticated_cookies = None


    def request_secure_page(self, url, retries=0) -> BeautifulSoup | None:
        """
        Request a secure page from RoyalRoad. If not authenticated, login first. If the request fails with a forbidden
        status code, attempt to login again and retry the request up to x retries.

        Args:
            url (str): The URL of the page to request.
            retries (int): The number of times to retry the request if it fails with a forbidden status code. Default is 0.

        Returns:
            BeautifulSoup: The parsed HTML of the requested page. If the request fails, None is returned.
        """
        log.debug(f"Requesting secure page: {url} with {retries} retries.")
        if not self.authenticated:
            log.debug("Not authenticated. Attempting to login first.")
            if not self.login():
                log.debug("Failed to login.")
                return None
        try:
            req = requests.get(url, headers=self.request_headers, cookies=self.authenticated_cookies)
            req.raise_for_status()
            return BeautifulSoup(req.text, "lxml")
        except requests.exceptions.RequestException as e:
            if retries <= 0:
                log.error(f"Failed to request secure page. {e}")
            elif req.status_code == 403:
                log.warning("Failed to request secure page. Forbidden.")
                self.authenticated = False # Reset authenticated flag to retry login
                return self.request_secure_page(url, retries - 1)
            elif req.status_code == 404:
                log.error("Failed to request secure page. Not Found.")
            elif req.status == 429:
                log.warning("Failed to request secure page. Too many requests.")
                time.sleep(randint(5, 10))
                return self.request_secure_page(url, retries - 1)
            log.error(f"Failed to request secure page. {e}")
            return None


    def login(self):
        """
        Login to RoyalRoad using the provided username and password ENV variables. Populates headers with the
        necessary cookies for authenticated requests, sets the authenticated flag to True and saves the authenticated
        user's ID. Returns True if login was successful, False otherwise.

        Returns:
            bool: True if login was successful, False otherwise.
        """
        url = 'https://www.royalroad.com/account/login'
        rememberme = 'false'
        headers = self.request_headers

        if not config.ROYAL_ROAD_EMAIL or not config.ROYAL_ROAD_PASSWORD:
            log.error("Attempt to login without specifying credentials. Please set the ROYAL_ROAD_EMAIL and ROYAL_ROAD_PASSWORD environment variables.")
            return False

        log.info(f'Attempting to login to RoyalRoad using credentials (Email: {config.ROYAL_ROAD_EMAIL}, Password: {config.ROYAL_ROAD_PASSWORD}).')

        # Initial login page
        req = requests.get(url)
        response_headers = req.headers
        html = req.text
        soup = BeautifulSoup(html, 'lxml')
        cookies = response_headers['Set-Cookie']
        cookies_dict = parse_cookies(cookies)
        requesttoken = soup.find('input', attrs={'name': '__RequestVerificationToken'}).get('value', None)
        if not requesttoken:
            log.error('Failed to get request token from login page.')
            return False
        returnurl = '/home'

        # Login form
        urlencoded = urllib.parse.quote_plus(f'returnurl={returnurl}&Email={config.ROYAL_ROAD_EMAIL}&Password={config.ROYAL_ROAD_PASSWORD}&__RequestVerificationToken={requesttoken}&Remember={rememberme}')
        content_length = str(len(urlencoded))
        headers = headers | {'cache-control': 'max-age=0',
                    'content-length': content_length, #the string length of the post data url encoded
                    'content-type': 'application/x-www-form-urlencoded',
                    'origin': 'https://www.royalroad.com',
                    'referer': 'https://www.royalroad.com/account/login'}

        data = {'ReturnUrl': returnurl,
                'Email': config.ROYAL_ROAD_EMAIL,
                'Password': config.ROYAL_ROAD_PASSWORD,
                '_RequestVerificationToken': requesttoken,
                'Remember': rememberme}

        try:
            login_request = requests.post(url, headers=headers, data=data, allow_redirects=False)
            login_request.raise_for_status()
            cookies_dict = cookies_dict | parse_cookies(login_request.headers['Set-Cookie'])
        except requests.exceptions.RequestException as e:
            log.error(f'Failed to login. {e}')
            return False

        log.info(f'Successfully Logged In as "{config.ROYAL_ROAD_EMAIL}".')
        self.authenticated = True
        self.authenticated_cookies = cookies_dict

        log.debug(f'Grabbing user ID for "{config.ROYAL_ROAD_EMAIL}".')
        soup = self.request_secure_page("https://www.royalroad.com/home")
        self.authenticated_user_id = soup.find("ul", attrs={"class":"dropdown-menu dropdown-menu-default"}).find("a").get("href").split("/")[-1].strip()
        log.debug(f'User ID for {config.ROYAL_ROAD_EMAIL}: {self.authenticated_user_id}')
        return True
    

    def request_page(self, url, retries=0) -> BeautifulSoup | None:
        """
        Request a page from RoyalRoad. If the request fails with a forbidden status code, attempt to request the page using
        request_secure_page instead. Retry the request up to x retries. If the request fails, returns None.

        Args:
            url (str): The URL of the page to request.
            retries (int): The number of times to retry the request if it fails with a forbidden status code. Default is 0.

        Returns:
            BeautifulSoup: The parsed HTML of the requested page. If the request fails, None is returned.
        """
        log.debug(f"Requesting page: {url} with {retries} retries.")
        try:
            req = requests.get(url, headers=self.request_headers)
            req.raise_for_status()
            return BeautifulSoup(req.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            if retries <= 0:
                log.error(f"Failed to request page. {e}")
            elif req.status_code == 403:
                log.warning("Forbidden to request page. Retrying with request_secure_page.")
                self.authenticated = False # Reset authenticated flag to retry login
                return self.request_secure_page(url, retries)
            elif req.status_code == 404:
                log.error("Failed to request page. Not Found.")
                return self.request_page(url, retries - 1)
            elif req.status == 429:
                log.warning("Failed to request secure page. Too many requests.")
                time.sleep(randint(5, 10))
                return self.request_page(url, retries - 1)
            log.error(f"Failed to request page. {e}")
            return None
        

    def get_followed_fictions(self) -> list:
        """
        Get the fictions that the authenticated user is following. Will automatically login if not already authenticated.
        Returns a list of ids if successful, None otherwise.
        """
        url = f"https://www.royalroad.com/my/follows"
        soup = self.request_secure_page(url) # This will login automatically.
        if not soup:
            log.error("Failed to get followed fictions. Request failed.")
            return None
        fiction_href_tags = [i.a['href'] for i in soup.find_all('h2', class_='fiction-title')]
        return [i.split('/')[-2] for i in fiction_href_tags] # These are in format of '/fiction/12345/fiction-slug'


    def get_full_fiction(self, fiction_id) -> RoyalRoadBook | None:
        """
        Gets a full fiction from RoyalRoad. This includes all chapters, the cover image, and metadata. Returns a
        RoyalRoadBook object if successful, None otherwise.
        """
        book_obj = RoyalRoadBook(fiction_id)
        soup = self.request_page(f'https://www.royalroad.com/fiction/{fiction_id}')
        if not soup:
            log.error('Failed to get fiction. HTML request failed.')
            return None
        
        book_obj.title = self.get_fiction_title(soup=soup)
        book_obj.cover_url = self.get_fiction_cover_image(soup=soup)
        book_obj.author = self.get_fiction_author(soup=soup)
        book_obj.description = self.get_fiction_description(soup=soup)
        book_obj.genres = self.get_fiction_genres(soup=soup)
        book_obj.chapters = self.get_fiction_chapters(soup=soup)

        try:
            book_obj.validate()
        except ValueError as e:
            log.error(f'Failed to validate fiction book. {e}')
            return None

        return book_obj


    def get_fiction_title(self, fiction_id=None, soup=None) -> str | None:
        """
        Gets the title of a fiction from RoyalRoad. Can either take in a BeautifulSoup object of the 
        fiction page at '/fiction/{id}' or just the fiction_id and it will requests the page automatically.
        Raises a ValueError if both fiction_id and soup are None.
        Returns the title as a string if successful, None otherwise.

        Args:
            fiction_id (int): The ID of the fiction to get the title of. Default is None.
            soup (BeautifulSoup): The BeautifulSoup object of the fiction page. Default is None.

        Returns:
            str | None: The title of the fiction as a string. None if the request failed.
        """
        if not soup and not fiction_id:
            raise ValueError('Both fiction_id and soup cannot be None.')
        if not soup:
            soup = self.request_page(f'https://www.royalroad.com/fiction/{fiction_id}')
            if not soup:
                log.error('Failed to get fiction title. HTML request failed.')
                return None
        h1_tags = soup.find('h1') # Title should always be the first/only h1 tag on the page.
        if not h1_tags:
            log.error('Failed to get fiction title. No h1 tags found.')
            return None
        return h1_tags.text.strip()
    

    def get_fiction_cover_image(self, fiction_id=None, soup=None) -> str | None:
        """
        Gets the cover image URL of a fiction from RoyalRoad. Can either take in a BeautifulSoup object of the
        fiction page at '/fiction/{id}' or just the fiction_id and it will requests the page automatically.
        Raises a ValueError if both fiction_id and soup are None. Returns the cover image URL as a string if successful,
        None otherwise.

        Args:
            fiction_id (int): The ID of the fiction to get the cover image URL of. Default is None.
            soup (BeautifulSoup): The BeautifulSoup object of the fiction page. Default is None.

        Returns:
            str | None: The cover image URL of the fiction as a string. None if the request failed.
        """
        if not soup and not fiction_id:
            raise ValueError('Both fiction_id and soup cannot be None.')
        if not soup:
            soup = self.request_page(f'https://www.royalroad.com/fiction/{fiction_id}')
            if not soup:
                log.error('Failed to get fiction cover image. HTML request failed.')
                return None
        cover_image = soup.find('img', attrs={'data-type': 'cover'}).get('src', None)
        if not cover_image or cover_image.lower() in ['/dist/img/nocover-new-min.png', 'undefined']:
            return 'http://www.royalroad.com/dist/img/nocover-new-min.png' # convert it to an external source
        else:
            return cover_image.split("?")[0] # Remove any query parameters


    def get_fiction_author(self, fiction_id=None, soup=None) -> str | None:
        """
        Gets the author of a fiction from RoyalRoad. Can either take in a BeautifulSoup object of the
        fiction page at '/fiction/{id}' or just the fiction_id and it will requests the page automatically.
        Raises a ValueError if both fiction_id and soup are None. Returns the author as a string if successful,
        None otherwise.

        Args:
            fiction_id (int): The ID of the fiction to get the author of. Default is None.
            soup (BeautifulSoup): The BeautifulSoup object of the fiction page. Default is None.

        Returns:
            str | None: The author of the fiction as a string. None if the request failed or if the author element is empty.
        """
        if not soup and not fiction_id:
            raise ValueError('Both fiction_id and soup cannot be None.')
        if not soup:
            soup = self.request_page(f'https://www.royalroad.com/fiction/{fiction_id}')
            if not soup:
                log.error('Failed to get fiction author. HTML request failed.')
                return None
        author_tag = soup.find('h4').find('a', href=re.compile('profile'))
        if not author_tag or author_tag.text == '':
            log.error('Failed to get fiction author. Author element is empty or missing.')
            return None
        return author_tag.text.strip()
    

    def get_fiction_description(self, fiction_id=None, soup=None) -> str | None:
        """
        Gets the description of a fiction from RoyalRoad. Can either take in a BeautifulSoup object of the
        fiction page at '/fiction/{id}' or just the fiction_id and it will requests the page automatically.
        Raises a ValueError if both fiction_id and soup are None. Returns the description as a string if successful,
        None otherwise.

        Args:
            fiction_id (int): The ID of the fiction to get the description of. Default is None.
            soup (BeautifulSoup): The BeautifulSoup object of the fiction page. Default is None.

        Returns:
            str | None: The description of the fiction as a string. None if the request failed or if the description element is empty.
        """
        if not soup and not fiction_id:
            raise ValueError('Both fiction_id and soup cannot be None.')
        if not soup:
            soup = self.request_page(f'https://www.royalroad.com/fiction/{fiction_id}')
            if not soup:
                log.error('Failed to get fiction description. HTML request failed.')
                return None
        description_element = soup.find('div', class_='description')
        if not description_element or description_element.text == '':
            log.error('Failed to get fiction description. Description element is empty or missing.')
        return description_element.text.strip()
    

    def get_fiction_chapters(self, fiction_id=None, soup=None) -> list[RoyalRoadChapter] | None:
        """
        Gets all of the chapters of a fiction from RoyalRoad. Can either take in a BeautifulSoup object of the
        fiction page at '/fiction/{id}' or just the fiction_id and it will requests the page automatically.
        Raises a ValueError if both fiction_id and soup are None. Returns a list of RoyalRoadChapter objects, None otherwise.

        Args:
            fiction_id (int): The ID of the fiction to get the description of. Default is None.
            soup (BeautifulSoup): The BeautifulSoup object of the fiction page. Default is None.

        Returns:
            list[RoyalRoadChapter] | None: A list of the fiction's chapters. None if the request failed or if there are no chapters.
        """
        if not soup and not fiction_id:
            raise ValueError('Both fiction_id and soup cannot be None.')
        if not soup:
            soup = self.request_page(f'https://www.royalroad.com/fiction/{fiction_id}')
            if not soup:
                log.error('Failed to get fiction chapter links. HTML request failed.')
                return None
        list_object_tags = soup.find_all('tr', style='cursor: pointer')
        if not list_object_tags:
            log.error('Failed to get fiction chapter links. No chapter links found.')
            return None
        
        chapter_links = [chapter_link.get('data-url', None) for chapter_link in list_object_tags]
        if not chapter_links:
            log.error('Failed to get fiction chapter links. No chapter links found.')
            return None
        for chapter in chapter_links:
            if not chapter:
                log.warning(f'Failed to get chapter link for chapter {i}. Will skip this chapter page.')
        chapter_links = [chapter for chapter in chapter_links if chapter[0]] # Remove any None values

        process_pool = Pool(config.MAX_NUM_THREADS)
        chapters = process_pool.map(self.get_chapter, chapter_links)

        # If any of the chapters are None, warn the user that we failed to get some chapters.
        for chapter in chapters:
            if not chapter:
                log.warning('Failed to get some chapters. Some chapters may be missing.')
        return [chapter for chapter in chapters if chapter] # Remove any None values
        

    def get_fiction_genres(self, fiction_id=None, soup=None) -> list[str] | None:
        """
        Gets all of the genres of a fiction from RoyalRoad. Can either take in a BeautifulSoup object of the
        fiction page at '/fiction/{id}' or just the fiction_id and it will requests the page automatically.
        Raises a ValueError if both fiction_id and soup are None. Returns the genres as a list if successful,
        None otherwise.

        Args:
            fiction_id (int): The ID of the fiction to get the description of. Default is None.
            soup (BeautifulSoup): The BeautifulSoup object of the fiction page. Default is None.

        Returns:
            list[str] | None: A list of genres. None if the request failed or if there are no genres.
        """
        if not soup and not fiction_id:
            raise ValueError('Both fiction_id and soup cannot be None.')
        if not soup:
            soup = self.request_page(f'https://www.royalroad.com/fiction/{fiction_id}')
            if not soup:
                log.error('Failed to get fiction genres. HTML request failed.')
                return None
        genre_tags_element = soup.find('span', class_='tags')
        if not genre_tags_element or genre_tags_element.text == '':
            log.error('Failed to get fiction genres. No genre tags found.')
            return None
        return genre_tags_element.text.strip().split('\n')
    

    def get_chapter(self, link, chapter_num=None) -> RoyalRoadChapter | None:
        """
        Gets the information and content for a chapter. Returns a RoyalRoadChapter object if successful, None otherwise.

        Args:
            link (str): The link of the chapter to get the content of. 
                        Should be in the format of '/fiction/{id}/chapter/{chapter_id}/{chapter_slug}'.
            chapter_num (int): The chapter number. Will not be set if not provided.

        Returns:
            RoyalRoadChapter | None: The chapter content as a RoyalRoadChapter object. None if the request failed.
        """
        url = f'https://www.royalroad.com{link}'
        soup = self.request_page(url)
        if not soup:
            log.error(f'Failed to get chapter {url}. HTML request failed.')
            return None
        
        chapter = RoyalRoadChapter()
        chapter.url = url
        chapter.slug = url.split('/')[-1].strip()
        chapter.chapter_number = chapter_num

        title_element = soup.find('h1', style='margin-top: 10px', class_='font-white')
        if not title_element or title_element.text == '':
            log.error('Failed to get chapter title. Title element is missing or empty.')
            return None
        chapter.title = title_element.text.strip()

        content_elements = soup.find('div', class_='chapter-inner chapter-content')
        if not content_elements or content_elements.text == '':
            log.error('Failed to get chapter content. Content element is missing or empty.')
            return None
        chapter.content = content_elements.text.strip()

        published_time_element = soup.find('time')
        if not published_time_element:
            log.warning('Failed to get chapter published time. Published time element is missing.')
        else:
            chapter.published = published_time_element.get('datetime', None)

        try:
            chapter.validate()
        except ValueError as e:
            log.error(f'Failed to validate chapter. {e}')
            return None

        return chapter