import logging
import time

from selenium import webdriver

logger = logging.getLogger("parser")

def create_logger(log_filename):
    logger = logging.getLogger("parser")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('{}.log'.format(log_filename))
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def get_browser(is_headless=False):
    options = webdriver.ChromeOptions()

    if is_headless:
        options.add_argument('headless')
    # set the window size
    options.add_argument('window-size=1200x800')

    # initialize the driver
    browser = webdriver.Chrome(chrome_options=options)
    return browser


def authorize(browser, delay=3.0):
    some_link = "https://www.quora.com/What-game-feature-or-animation-makes-you-think-This-person-mustve-had-a-lot-of-fun-making-this"
    browser.get(some_link)
    time.sleep(delay)
    browser.find_element_by_class_name("header_signin_with_search_bar").click()
    time.sleep(delay)
    browser.find_element_by_partial_link_text("I Have").click()
    time.sleep(delay)
    login, password = browser.find_elements_by_class_name("header_login_text_box")
    login.send_keys('jester.ilia.night@gmail.com')
    password.send_keys("jes1989ter0603")
    time.sleep(delay)
    browser.find_element_by_class_name("login_shift_right").click()
    time.sleep(delay)


def scroll_down(browser, max_time_sec=5., load_time_wait=1.8, only_on_time=False, max_retry_iterations_count=2):
    time_start = time.time()
    src_updated = browser.page_source
    src = ""
    time_cur = time.time()
    browser.get_screenshot_as_file("iteration_0.png")
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    if only_on_time:
        while time_cur - time_start <= max_time_sec:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(load_time_wait)
            time_cur = time.time()
        logger.debug("scroll_down exit on time")
    else:
        retry_iterations = 0
        # if new screen equal the previous screen and we made enough tries to update(we increase tries count every
        # time when src==src_update)
        # or time is up
        while (src != src_updated or retry_iterations != max_retry_iterations_count) and \
                time_cur - time_start <= max_time_sec:
            src = src_updated
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(load_time_wait)
            src_updated = browser.page_source
            time_cur = time.time()
            if src == src_updated:
                logger.debug("src==src update, update retry_iterations {}".format(retry_iterations))
                browser.get_screenshot_as_file("iteration_{}.png".format(retry_iterations + 1))
                retry_iterations += 1

        if (src == src_updated):
            logger.debug("scroll_down exit on finish")
        else:
            logger.debug("scroll_down exit on time")
