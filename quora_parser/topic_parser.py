from bs4 import BeautifulSoup
import urllib.request as req
import urllib.request
import http.cookiejar
import json
import os
import pandas as pd
import logging
import time
import uuid

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from quoraparser.utils import scroll_down, get_browser, authorize, create_logger

logger = logging.getLogger("parser")

def get_topic_links(browser, topic_link, max_time_sec=200, load_time_wait=4.0, only_on_time=False):
    browser.get(topic_link)
    scroll_down(browser,
                max_time_sec=max_time_sec,
                load_time_wait=load_time_wait,
                only_on_time=only_on_time,
                max_retry_iterations_count=10
                )
    post_elems = browser.find_elements_by_xpath("//a[@class='question_link']")
    qlinks = []
    for post in post_elems:
        qlink = post.get_attribute("href")
        qlinks.append(qlink)
    return qlinks

def get_topics():
    with open("dumped_topics.json") as f:
        data = json.load(f)
    return data

def get_topic_url(url_without_manage):
    new_url = url_without_manage + "/all_questions"
    return new_url

def main():
    result_dir = "./question_links/"
    os.makedirs(result_dir, exist_ok=True)

    browser = get_browser(is_headless=True)
    authorize(browser)


    topics = get_topics()
    for idx, topic in enumerate(topics):
        try:
            logger.info("Processing #{} {} ".format(idx, topic))
            text, url = topic
            url_without_manage = url[:url.find("/manage")]

            new_url = get_topic_url(url_without_manage)

            logger.info("Get questions from  {}".format(new_url))
            links = get_topic_links(browser, new_url)
            logger.info("len = {}".format(len(links)))

            question_title = url_without_manage.split("/")[-1]
            question_title = question_title.lower()
            dump_file = os.path.join(result_dir, question_title) + ".json"

            with open(dump_file, "w") as f:
                json.dump(links, f, indent=2)

        except Exception as e :
            logger.exception("Can't process #{} {}".format(idx, topic))



if __name__ == "__main__":
    create_logger("got_link_by_topic")
    main()