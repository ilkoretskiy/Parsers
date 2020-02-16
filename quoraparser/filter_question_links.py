import os
import json
import logging
import shutil
from quoraparser.utils import create_logger


logger = logging.getLogger("parser")

def exist_questions():
    path = "/Users/jesterilianight/Documents/sources/projects/quora_parser/result_processed"

    files = []
    for item in os.listdir(path):
        if "json" in item:
            files.append(item.split(".")[0])
    return files

def dump_new_questions(questions, dest_file):
    with open(dest_file, "w") as f:
        json.dump(questions, f, indent=2)


def main():
    processed_questions = exist_questions()
    unique_processed_questions = set(processed_questions)

    new_questions = []

    topics_dir = "./question_links"

    filtered_topics_dir = "./filtered_question_links"
    os.makedirs(filtered_topics_dir, exist_ok=True)

    json_files = os.listdir(topics_dir)
    topics_count  = len(json_files)
    for idx, item in enumerate(json_files):
        logger.info("Processing file {}; {} / {}".format(idx, item, topics_count))
        full_json_path = os.path.join(topics_dir, item)

        if ".json" in item:
            with open(full_json_path) as f:
                data = json.load(f)

            for question in data:
                if question in unique_processed_questions:
                    logger.info("\tSkip processed question {}".format(question))
                    continue
                else:
                    if "/unanswered/" in question:
                        logger.info("\tSkip unanswered question {}".format(question))
                        continue
                    else:
                        logger.info("\tProcess question {}".format(question))
                        new_questions.append(question)

        new_questions = list(set(new_questions))

        full_dest_json_path = os.path.join(filtered_topics_dir, item)
        shutil.move(full_json_path, full_dest_json_path)
        #write in temp file all questions
        #dump_new_questions(new_questions, "temp_new_questions.json")

    dump_new_questions(new_questions, "result.json")



if __name__ == "__main__":
    create_logger("filter_topic_links")
    main()