import time
import sys
import random
from models import SQLHandler, Translator, TextHandler

checkpoint = None

def print_status(start_time, total_chars, request_counter):
    end_time = time.time()
    delta_sec = (end_time - start_time)
    run_time_hours = round(((delta_sec / 60) / 60), 2)
    chars_per_min = round((total_chars / (delta_sec / 60)),2)
    requests_per_min = round((request_counter / (delta_sec / 60)),2)
    s = ("\nAlgo ran with stats:\nTotal run time: {}hours\n"
         "Total src_lang chars: {}\n"
         "Total requests: {}\n"
         "{} chars per minute\n"
         "{} requests per minute").format(run_time_hours, total_chars, request_counter,
                                          chars_per_min, requests_per_min)
    print(s)

def calc_idle_time(time_limit):
    """
    Calculates the remaining time, the algo needs to be idle.
    Using the checkpoint time updated when function was visited last.

    :param time_limit: The minimum time in seconds that neets to lay between two API calls.
    :return remaining idle time (float):
    """
    global checkpoint
    if checkpoint:
        now = time.time()
        delta = now - checkpoint
        checkpoint = now
        if delta > time_limit:
            return 0
        if delta <= time_limit:
            raw_idle_time = time_limit - delta
            adj_idle_time = raw_idle_time + random.randint(0, 10)
            return adj_idle_time
    else:
        checkpoint = time.time()
        return time_limit

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

        # portionize the text to translate
        # because if text is too long, google neglects it
        # splitting is done at [\n].
        portions = text_handler.portionize(text)

#        # LANGUAGE DETECTION
#        # is algorithm is not sure about the language
#        # it has to be entered manually.
#        src_lang, is_reliable = translator.detect_lang(text)
#        if not is_reliable:
#            os.system('say "Not certain which language that is. Please decide."')
#            print("Job ID: {}\n".format(job_id))
#            print("Text:\n{}".format(text))
#            src_lang = input("Please enter source language abbreviation after scheme in CLD3 github:")

        # if the source language is english, nothing needs to be done
        # (maybe just copying the value)
        # else, we translate all portions, re-assemble them to a text
        # and store this as the english translation
        if src_lang != 'en':
            src_portions, dst_portions = [], []
            for portion in portions:
                # for testing start slowly
                idle_time = calc_idle_time(time_limit)
                if idle_time > 0:
                    print("Translating soo much text is exhausting... Giv me a {} sec break.. zzZZZ zzzZZZZ".format(
                        idle_time))
                time.sleep(idle_time)
                request_counter += 1

                try:
                    _, src_portion, dst_portion = translator.translate(portion)
                except Exception as e:
                    print_status(start_time, total_chars, request_counter)
                    raise Exception(str(e))

                src_portions.append(src_portion)
                dst_portions.append(dst_portion)
            src_text = text_handler.assemble_portions(src_portions)
            text_en = text_handler.assemble_portions(dst_portions)
        else:
            src_text = text
            text_en = text

        # this check enables us to see if the text, google translator used as a base for the translation
        # operation comes close to the length of the text in original language of the database.
        # this is important so see, Google neglected any text for translation or if otherwise the
        # text changed during preparation.
        l_orig = len(text)
        l_trans = len(src_text)

        if l_trans > l_orig * 0.95 and l_trans < l_orig * 1.05:
            pass
        else:
            print(("PLEASE COPY THIS AND SEND IT TO MARTIN\n"
                   "- - - - - - - - - - - - - - - - - - - - - - -"
                   "TEXT ORIG AND TEXT PORTIONS INPUT INEQUALITY"))
            print(("Warning: original length: {} and "
                   "translation source length: {} differ by {}%").format(l_orig,
                                                                         l_trans,
                                                                         (abs(l_orig - l_trans) / l_orig) * 100))

            print("TEXT_ORIG:\n{}".format(text))
            print("TEXT_PORTIONS_INPUT:\n{}".format(src_text))
            print("- - - - - - - - - - - - - - - - - - - - - - -")
            continue

        # PRINT STATUS
        # every 20 requests, print the current status
        if job_counter % 20 == 0:
            print_status(start_time, total_chars, request_counter)

        try:
            data_handler.update_column(table=table, id=job_id, col="text_en", data=text_en)
        except Exception as e:
            print_status(start_time, total_chars, request_counter)
            raise Exception(str(e))

if __name__ == '__main__':
    args = sys.argv
    assert len(args) > 1, "Function takes one input argument - seconds per request"
    assert type(args[1]) == int or type(args[1]) == float, "Input argument has to be an integer"
    assert args[1] > 0, "Values below 0sec per request not accepted. A good value is e.g. ..."
    main(args[1])


