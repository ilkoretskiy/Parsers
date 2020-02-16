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


def expand_more_links(browser):
    more_link = browser.find_elements_by_partial_link_text("(more)")
    for each in more_link:
        each.send_keys("\n")


def get_question(browser):
    qname =browser.find_elements_by_xpath("//div[@class='question_text_edit']")
    questions = []
    for q in qname:
        questions.append(q.text)
    #not sure if we could find links with more than 1 question
    first_question = questions[0]
    return first_question


def get_topics(browser):
    try:
        browser.find_element_by_class_name("view_more_topics_link").click()
        time.sleep(0.5)
    except Exception as e:
        pass

    topics_element = browser.find_elements_by_class_name("QuestionTopicListItem")
    topics = [topic.text for topic in topics_element]
    return topics


def get_username(answer):
    username = ""
    try:
        username = answer("a", "user")[0].text
    except Exception as e:
        pass
    return username


def get_credentials(answer):
    credentials = ""
    if len(answer("span", "NameCredential")) > 0:
        credentials = answer("span", "NameCredential")[0].text
    return credentials


def get_date(answer):
    date = answer("a", "answer_permalink")[0].text
    return date


def get_html_content(answer):
    html_content = str(answer("div", "ExpandedContent")[0]("div", "ui_qtext_expanded")[0])
    return html_content


def get_votes_count(answer):
    votes_count = -1
    try:
        votes_count = int(answer("span", "ui_button_count_optimistic_count")[0].text)
    except:
        pass
    return votes_count


def get_answer_info(answer):
    username = get_username(answer)
    credentials = get_credentials(answer)
    date = get_date(answer)
    html_content = get_html_content(answer)
    votes_count = get_votes_count(answer)

    answer_res = {
        "username": username,
        "credentials": credentials,
        "date": date,
        "html_content": html_content,
        "votes_count": votes_count
    }
    return answer_res


def get_answers(browser, task_id):
    html_source = browser.page_source
    soup = BeautifulSoup(html_source, features="lxml")
    answers = soup("div", {"class" : ["AnswerBase"]})
    return answers


def get_info_from_answers(answers):
    all_contents = []
    for idx, answer in enumerate(answers):
        #content = answers[0]("div", "ui_qtext_expanded")[0].contents
        #all_contents.append(content)
        try:
            answer_res = get_answer_info(answer)
            all_contents.append(answer_res)
        except Exception as e:
            logger.exception("Skip answer #{}".format(idx))

        #except Exception as e:
        #    logger.exception("{} one of answers ".format(task_id))

    return all_contents


def parse_page(browser, link, scroll_load_time_wait=2.0, on_page_get=None):
    # open page
    cur_id = uuid.uuid1()
    task_id = str(cur_id)
    logger.info("parse {}; {}".format(link, task_id))

    logger.info("{} open page ".format(task_id))
    browser.get(link)
    time.sleep(2.0)
    if on_page_get:
        on_page_get(browser, link)

    logger.info("{} scroll down ".format(task_id))
    scroll_down(browser, max_time_sec=10.0, load_time_wait=scroll_load_time_wait)
    expand_more_links(browser)

    logger.info("{} get_question ".format(task_id))
    question = get_question(browser)

    time.sleep(1)
    logger.info("{} get_topics ".format(task_id))
    topics = get_topics(browser)

    time.sleep(1)
    logger.info("{} get_answers ".format(task_id))

    answers = get_answers(browser, task_id)
    answers = get_info_from_answers(answers)

    logger.info("{} answers_count = {} ".format(task_id, len(answers)))
    result = {
        "question": question,
        "topics": topics,
        "answers": answers
    }
    # print (result)
    return result


def get_questions(filepath):
    with open(filepath) as f:
        data = json.load(f)
    return data

result_dir = "./parsed_questions"

def on_page_get(browser, link):
    question_title = link.split("/")[-1]
    question_title = question_title.lower()
    dump_img_file = os.path.join(result_dir, question_title) + ".png"
    browser.get_screenshot_as_file(dump_img_file)


def process_questions(browser, question_links, result_dir):
    count = len(question_links)

    for idx, link in enumerate(question_links):
        logger.info("Init processing {}: {} / {}".format(idx, link, count))
        try:
            question_title = link.split("/")[-1]
            question_title = question_title.lower()
            dump_file = os.path.join(result_dir, question_title) + ".json"

            # dump_img_file = os.path.join(result_dir, question_title) + ".png"

            if os.path.exists(dump_file):
                logger.info("skip {}".format(link))
            else:
                page_info = parse_page(browser, link, on_page_get=on_page_get)
                with open(dump_file, "w") as f:
                    json.dump(page_info, f, indent=2)

        except Exception as e:
            logger.exception("Global exception on link {}".format(link))
            error_file = os.path.join(result_dir, question_title) + ".png"
            print("writing to file")
            browser.get_screenshot_as_file(error_file)

def main():
    logger.info("Start")
    browser = get_browser(is_headless=False)
    logger.info("Authorize")
    authorize(browser, delay=10.0)
    browser.get_screenshot_as_file("question_parser_auth.png")

    logger.info("Get questions")
    input_questions_file = "result.json"
    question_links = get_questions(input_questions_file)



    logger.info("Process questions")
    os.makedirs(result_dir, exist_ok=True)
    process_questions(browser, question_links=question_links, result_dir=result_dir)


if __name__ == "__main__":
    create_logger("parse_questions")
    main()