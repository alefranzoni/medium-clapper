"""
This module contains the implementation of a scraper for Medium based on Playwright.
The scraper is designed to read and clap all articles published by a given user on Medium.
"""
import re
import sys
import time
import requests
from playwright.sync_api import sync_playwright
from modules.argument_manager import ArgumentOptions
from modules.file_utils import (
    ExcludedReturnType,
    append_and_save_articles_to_local,
    check_data_directory,
    get_articles_from_local,
    get_excluded_users,
    local_articles_file_exists,
    save_articles_to_local,
)
from modules.session_utils import add_cookies, save_cookies

BASE_URL = "https://www.medium.com/{}"
BASE_FEED_URL = "https://api.rss2json.com/v1/api.json?rss_url=https://medium.com/feed/{}"
BASE_POST_URL = "https://medium.com/{0}/{1}"
NAME_PATTERN = r'<title>([^-]+) – Medium<'
WRITTEN_BY_PATTERN = r'Written by <!--.*?-->(.*?)</span>'
FEED_ARTICLES_PATTERN = (r'rel="noopener follow" href="/(@[^\?]+)\?source=collection_home-'
                         r'[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>'
                         r'[^>]+>[^>]+>[^>]+>[^>]+><a[^/]+([^\?]+)\?')
FEED_ARTICLES_PATTERN_ALT = (r'rel="noopener follow" href="/([^/]+)/([^\?]+)\?source=user_profile-'
                             r'[^>]+><div[^>]+><h2')

class Scraper:
    """
    Medium scraper based on Playwright.
    Contains the logic able to scrape a given user in order to read 
    and clap all its published articles. 
    """

    def __init__(self, arguments):
        """Initialize the Scraper object."""
        print("🚀 The environment is getting ready...")
        self.args = arguments
        self.logged_name = ''
        self.target = self.args.get(ArgumentOptions.TARGET)
        self.main_scroll_delay = self._get_main_scroll_delay()
        self.main_scroll_retries = self._get_main_scroll_retries()
        self.article_scroll_delay = 0.5
        self.article_scroll_retries = 3
        self.articles = []
        self.browser = sync_playwright().start()

    def close(self):
        """Close the browser."""
        self.browser.close()
        print("✅ Done, thanks for using Medium Clapper!")
        print("⭐ Star the project on GitHub", "\n- https://github.com/alefranzoni/medium-clapper")

    def start(self):
        """Start the process to login, read and clap published articles from target."""
        self.browser = self.browser.firefox.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        add_cookies(context=self.context)
        self._login()
        self._get_logged_name()
        print(f"🌎 Navigating to {self.target} Medium profile")
        self._navigate(BASE_URL.format(self.target))
        self._check_for_new_articles()
        self._read_articles()
        self.close()

    def _navigate(self, url, wait_until="domcontentloaded"):
        """Navigates to specified url."""
        self.page.goto(url, wait_until=wait_until)

    def _login(self):
        """Handles the Medium login."""
        login_state = self._check_login_state()
        while login_state is False:
            login_state = self._check_login_state()

    def _get_logged_name(self):
        """Gets the full name of the logged user."""
        self._navigate(BASE_URL.format('me'))
        match = re.search(NAME_PATTERN, self.page.content())
        self.logged_name = match.group(1).strip()

    def _check_login_state(self):
        """
        Check the login status.
        If the user is not logged in, wait for a successful login.
        """
        print("🔒 Checking credentials status...")
        login_selector = self.page.query_selector("button[data-testid='headerSignUpButton']")
        if login_selector is not None:
            input("🔑 Login is required. Sign in and press [Enter] to continue...")

            save_cookies(context=self.context)
            self._navigate(BASE_URL.format(self.target))
            return False
        print("🔓 Successful login")
        return True

    def _check_for_new_articles(self):
        """Checks for new articles."""
        print("🔍 Cheking for new articles...")
        check_data_directory(self.target)
        if not local_articles_file_exists(self.target):
            self._get_articles()
        else:
            self._update_articles()

    def _get_articles(self):
        """Retrieves all the articles from targeted profile and save it to local file."""
        self._get_articles_from_feed()
        save_articles_to_local(user=self.target, data=self.articles)

    def _get_articles_from_feed(self):
        """
        Retrieves all articles from the given user's feed.
        These are saved in the object articles property (self).
        """
        self._scroll_to_bottom(self.main_scroll_delay, self.main_scroll_retries)
        articles = re.findall(FEED_ARTICLES_PATTERN, self.page.content())
        if not articles:
            articles = re.findall(FEED_ARTICLES_PATTERN_ALT, self.page.content())
        excluded_users = get_excluded_users(return_type=ExcludedReturnType.IDS)
        self.articles = []
        for article_data in articles:
            if article_data[0] not in excluded_users:
                self.articles.append({'guid': self._get_hash(article_data[1]), 'clapped': False})

    def _scroll_to_bottom(self, scroll_delay, scroll_retries, is_main=True):
        """Scroll current page to the bottom."""
        if is_main:
            print(f"⏳ Wait, getting articles from {self.target}...")
        scroll_attempt = 0
        while scroll_attempt <= scroll_retries:
            current_scroll_max = self.page.evaluate('window.scrollMaxY')
            self._scroll_page(scroll_delay=scroll_delay, scroll_tries=scroll_attempt)
            updated_scroll_max = self.page.evaluate('window.scrollMaxY')
            if current_scroll_max == updated_scroll_max:
                scroll_attempt += 1
            else:
                scroll_attempt = 0

    def _scroll_page(self, scroll_delay, scroll_tries):
        """Scrolls the current page."""
        self.page.evaluate('window.scroll(0, window.scrollMaxY)')
        delay = 0 if ((scroll_delay - scroll_tries/5 <= 0)) else ((scroll_delay - scroll_tries/5))
        time.sleep(delay)

    def _get_hash(self, article):
        """Retries the article's hash."""
        return article.split('-')[-1].replace(f'/{self.target}/', '')

    def _get_last_articles_from_rss(self):
        """
        Retrieves the user's last ten articles from feed.
        This method uses the RSS feed from Medium.
        """
        excluded_users = get_excluded_users(return_type=ExcludedReturnType.NAMES)
        response = requests.get(BASE_FEED_URL.format(self.target), timeout=10)
        if response.status_code == 200:
            data = response.json()
        else:
            print(f"😱 An error occurred while trying to get the latest articles from {self.target}.")
            print(f'<error: {response.status_code}>')
            sys.exit()
        items = data['items']

        return [item['guid'].split('/')[-1] for item in items if item['author'] not in excluded_users]

    def _update_articles(self):
        """Retrieves the new articles from the network and updates the local articles file."""
        local_articles = get_articles_from_local(self.target)
        local_current_guids = [article['guid'] for article in local_articles]
        last_articles_from_rss = self._get_last_articles_from_rss()
        new_articles = [guid for guid in last_articles_from_rss if guid not in local_current_guids]
        new_articles_count = len(new_articles)

        if new_articles_count != 0:
            suffix = '+' if new_articles_count == 10 else ''
            print(f"📰 New articles have been found ({new_articles_count}{suffix})")
            print("🔍 Fetching new ones...")
            if new_articles_count == 10:
                self._get_articles_from_feed()
                new_articles = [item['guid'] for item in self.articles if item['guid'] not in local_current_guids]
        append_and_save_articles_to_local(user=self.target, append_to=local_articles, to_append=new_articles)

    def _read_articles(self):
        """Read and clap all the articles that are not already viewed."""
        self.articles = get_articles_from_local(self.target)
        pending_articles = any(item['clapped'] is False for item in self.articles)
        pending_articles_count = sum(item['clapped'] is False for item in self.articles)
        read_count = 1
        if pending_articles:
            for item in self.articles:
                if item['clapped'] is False:
                    print(f"\r👏 Reading and clapping articles ({read_count} of {pending_articles_count})", end="", flush=True)
                    self._navigate(BASE_POST_URL.format(self.target, item['guid']))
                    self._clap()
                    self._scroll_to_bottom(self.article_scroll_delay, self.article_scroll_retries, False)
                    self._wait_reading_time()
                    item['clapped'] = True
                    save_articles_to_local(user=self.target, data=self.articles)
                    read_count += 1
            print(f"\r👏 Reading and clapping articles ({pending_articles_count} of {pending_articles_count}", end="\n", flush=True)
        else:
            print("🤩 Great, you're all caught up!")

    def _clap(self):
        """Claps the current opened article."""
        written_by = re.search(WRITTEN_BY_PATTERN, self.page.content()).group(1).strip()
        if written_by != self.logged_name:
            header_clap_button = self.page.wait_for_selector("button[data-testid='headerClapButton']")
            header_clap_button.scroll_into_view_if_needed()
            header_clap_button.click()
            remaining_claps = self._get_remaining_claps()
            for _ in range(remaining_claps):
                header_clap_button.click()

    def _get_claps_count(self):
        """
        Searches for a 'div' element with a specific animation style on the page. 
        Returns the first matching 'div' or None if no match is found.
        """
        target_animation = 'animation: 400ms ease-out 500ms 1 normal none running k'
        divs = self.page.query_selector_all("div")
        for div in divs:
            style = self.page.evaluate('(div) => div.getAttribute("style")', div)
            if style and target_animation in style:
                return int(div.text_content().replace("+", ""))
        return None

    def _get_remaining_claps(self):
        """Calculates and returns the number of claps remaining to be given."""
        claps_count = self._get_claps_count()
        claps_to_give = self.args.get(ArgumentOptions.CLAPS) - 1
        max_claps = 50
        if not claps_count:
            return claps_to_give
        if claps_count == max_claps:
            return 0
        return min(claps_to_give, max_claps - claps_count)

    def _wait_reading_time(self):
        """
        Waits until reading time has finished. 
        This method emulates the time reading the article before continue to the next one.
        """
        footer_clap_buttons = self.page.query_selector_all("button[data-testid='footerClapButton']")
        for btn in footer_clap_buttons:
            if btn.is_visible():
                btn.scroll_into_view_if_needed()
        time.sleep(self.args.get(ArgumentOptions.READ_TIME))

    def _get_main_scroll_retries(self, default=3):
        """
        Get the number of retries for scrolling the modal. The default number of retries is 5.
        If SCROLL_RETRIES argument is provided, it will be added to the default number of retries.
        """
        if self.args.get(ArgumentOptions.SCROLL_RETRIES) != default:
            default += self.args.get(ArgumentOptions.SCROLL_RETRIES)
        return default

    def _get_main_scroll_delay(self, default=0.85):
        """
        Get the delay time for scrolling the modal. The default delay time is 0.85 seconds.
        If the SCROLL_DELAY argument is provided, it will be added to the default delay time.
        """
        if not self.args.get(ArgumentOptions.SCROLL_DELAY) != default:
            default += self.args.get(ArgumentOptions.SCROLL_DELAY)
        return default
