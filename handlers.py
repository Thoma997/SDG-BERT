import extractors
import helpers
import models
sql_handler = models.SQLHandler()


def handle_listing(page, platform, url):
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


def handle_twitter_response(page):
    username = page['includes']['users'][0]['username']
    for tweet in page['data']:
        tweet_id, creation_date, text = extractors.get_tweet_data(tweet)
        sql_handler.save_tweet(tweet_id, username, creation_date, text)
        next_token = page['meta']['next_token'] if 'next_token' in page['meta'].keys() else ''
    return next_token