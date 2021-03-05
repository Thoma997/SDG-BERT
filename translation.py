import time
import sys
from models import SQLHandler, Translator, TextHandler, TimeWatcher
import helpers
import handlers

def main(time_limit):
    """
    Main script to translate entries in the job_postings table of the master_thesis database into english language.

    :param idle_time: Defines the amount of time in seconds that lays between each API call.
    :return:
    """
    print(("**********************************\n"
           "---------START TRANSLATION--------\n"
           "-THANK YOU FOR YOUR PARTICIPATION-\n"
           "**********************************"))
    # creating the translator and data handler object
    # connect to desired database
    translator = Translator()
    text_handler = TextHandler()
    data_handler = SQLHandler()
    time_watcher = TimeWatcher(time_limit)

    # true unless None returned by data handler
    row_return_flag = True
    total_chars = 0
    job_counter = 0
    request_counter = 0
    start_time = time.time()
    table = "job_postings"
    while row_return_flag:

        # fetch one single random row from the database
        # which is another language then english
        job_id, date_posted, company, job_title, meta, text, src_lang, text_en = data_handler.fetch_random_not_english_indeed_row()
        job_counter += 1
        total_chars += len(text)

        text_en = handlers.handle_translation(text, time_watcher, text_handler, translator)

        if not text_en:
            continue

        # PRINT STATUS
        # every 20 requests, print the current status
        if job_counter % 20 == 0:
            print(helpers.translation_status(start_time, total_chars, request_counter))

        try:
            data_handler.update_column(table=table, id=job_id, col="text_en", data=text_en)
        except Exception as e:
            print(helpers.translation_status(start_time, total_chars, request_counter))
            raise Exception(str(e))

if __name__ == '__main__':
    args = sys.argv
    time_limit = float(args[1])
    assert len(args) > 1, "Function takes one input argument - seconds per request"
    assert time_limit > 0, "Values below 0sec per request not accepted. A good value is e.g. ..."
    main(time_limit)
