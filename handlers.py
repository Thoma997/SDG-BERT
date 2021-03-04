import extractors
import helpers
import time

def handle_listing(page, platform, url, sql_handler):
    if platform == 'indeed':
        title = extractors.extract_element_text(page, 'h1', {'class': 'jobsearch-JobInfoHeader-title'})
        company = extractors.extract_element_text(page, 'div', {'class': 'jobsearch-CompanyReview--heading'})
        if not company:
            company = extractors.extract_element_text(page, 'div', {'class': 'icl-u-lg-mr--sm icl-u-xs-mr--xs'})
        job_meta_header = extractors.extract_element_text(page, 'span', {'class': 'jobsearch-JobMetadataHeader-item'})
        desc = extractors.extract_element_text(page, 'div', {'id': 'jobDescriptionText'})
        url = extractors.extract_element_attr_value(page, 'meta', {'id': 'indeed-share-url'}, 'content')
        job_id = helpers.get_url_param_value(url, 'jk')
        date = extractors.extract_indeed_job_footer_text(page)
        sql_handler.save_indeed_job(job_id=job_id, date=date, company=company,
                                    title=title, job_meta=job_meta_header, text=desc, url=url, platform=platform)
    if platform == 'twitter':
        next_token = handle_twitter_response(page)
        while next_token:
            token_url = helpers.format_url(url, platform, add_param={'pagination_token': next_token})
            page = helpers.make_request(token_url, platform)
            next_token = handle_twitter_response(page)

    if platform == 'Volkswagen_press':
        id = platform + '_' + helpers.get_url_path_element(url, -1)
        title = extractors.extract_element_text(page, 'h1', {'class': 'page--title'})
        company = "Volkswagen"
        date = extractors.extract_element_text(page, 'div', {'class': 'meta--item'}, 0)
        date_string = extractors.extract_date_string_from_text(date, platform)
        meta_topics = extractors.extract_child_element_text(page, 'div', {'class': 'meta--item'},
                                                            'a', {'content-link': ''}, 2, 0)
        short_summary = extractors.extract_list_text_by_parent(page, 'div', {'class': 'topic-list'})
        summary = extractors.extract_child_element_text(page, 'div', {'class': 'page-item--intro'}, 'p', None, 0, 0)
        text = extractors.extract_concatinated_text_by_element(page, 'div', {'class': 'page-item--text'}, 'p')
        sql_handler.save_press_release(release_id=id, company=company, release_date=date_string,
                                       topics=meta_topics, url=url, title=title,
                                       short_summary=short_summary, summary=summary, text=text)


def handle_twitter_response(page, sql_handler):
    username = page['includes']['users'][0]['username']
    for tweet in page['data']:
        tweet_id, creation_date, text = extractors.get_tweet_data(tweet)
        sql_handler.save_tweet(tweet_id, username, creation_date, text)
        next_token = page['meta']['next_token'] if 'next_token' in page['meta'].keys() else ''
    return next_token


def handle_translation(text, time_watcher, text_handler, translator):

    # SPLIT TEXT INTO PORTIONS
    # portionize the text to translate
    # because if text is too long, google neglects it
    # splitting is done at [\n].
    portions = text_handler.portionize(text)

    # LANGUAGE DETECTION
    # is algorithm is not sure about the language
    # it has to be entered manually.
    src_lang = translator.detect_lang(text)

    #TRANSLATION
    # if the source language is english, nothing needs to be done
    # (maybe just copying the value)
    # else, we translate all portions, re-assemble them to a text
    # and store this as the english translation
    if src_lang != 'en':
        src_portions, dst_portions = [], []
        for portion in portions:
            # for testing start slowly
            time_watcher.sleep()
            try:
                _, src_portion, dst_portion = translator.translate(portion)
            except Exception as e:
                raise Exception(str(e))

            src_portions.append(src_portion)
            dst_portions.append(dst_portion)
        src_text = text_handler.assemble_portions(src_portions)
        text_en = text_handler.assemble_portions(dst_portions)
    else:
        src_text = text
        text_en = text

    # QUALITY ASSESSMENT
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
        text_en = None

    return text_en
