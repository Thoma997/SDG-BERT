from urllib.parse import urlparse
import requests
import os
import time

from bs4 import BeautifulSoup
from datetime import datetime
import random

import extractors
import settings
import selenium_utils
from models import SQLHandler
sql_handler = SQLHandler()
t_prev = time.time()
SLEEP_TIME = 9

def sleep():
    # global request building and response handling
    global t_prev
    # one request per 3 sconds (being gentle)
    t_diff = time.time() - t_prev
    t_sleep = (SLEEP_TIME - t_diff) + SLEEP_TIME * random.random()
    if t_sleep > 0:
        time.sleep(t_sleep)
    t_prev = time.time()


def make_request(url, platform):

    return_format = 'soup'
    if settings.platforms[platform]['returns_json']:
        return_format = 'json'

    headers = None
    if settings.platforms[platform]['requires_auth']:
        headers = create_headers(platform)

    url = format_url(url, platform)
    log('Request page: {}'.format(url))

    sleep()

    try:
        r = requests.get(url, headers=headers)
    except requests.RequestException as e:
        log("WARNING: Request for {} failed, trying again.".format(url))
        return make_request(url, platform)  # try request again, recursively

    if r.status_code != 200:
        os.system('say "Got non-200 Response"')
        log("WARNING: Got a {} status code for URL: {}\n{}".format(r.status_code, url, r.text))
        queue_url(url, 'listing_files', platform)
        return None

    captcha_texts = ['<title>hCaptcha solve page</title>', '<title>reCAPTCHA solve page</title>']

    for t in captcha_texts:
        if t in r.text:
            os.system('say "Encountered Re-Captcha Page"')
            log("WARNING: Got a re-captcha for URL: {}".format(url))
            log('Lets make a 30 min break.')
            time.sleep(1800)
            queue_url(url, 'failed_extraction_files', platform)
            return None

    if return_format == 'soup':
        return BeautifulSoup(r.text, features='html.parser')
    elif return_format == 'json':
        return r.json()
    else:
        return r


def format_url(url, platform, change_path=None, change_param={}, add_param=None):
    # make sure URLs aren't relative, and strip unnecssary query args
    u = urlparse(url)

    scheme = u.scheme or "https"
    # here one can use the host as a key to retrieve relevant settings
    host = u.netloc if u.netloc in settings.platforms[platform]['allowed_hosts'] else None
    path = u.path if not change_path else change_path

    # changing query
    if not u.query:
        query = ""
    else:
        query = "?"
        for piece in u.query.split("&"):
            k, v = piece.split("=")
            if k in settings.platforms[platform]['allowed_params']:
                if k in change_param.keys():
                    query += "{}={}&".format(k, change_param[k])
                else:
                    query += "{k}={v}&".format(**locals())
        query = query[:-1]

    # adding to query
    if (len(query) > 0) & (add_param is not None):
        for key, val in add_param.items():
            if key not in [k for piece in query.split('&') for k, v in piece.split('=')]:
                query += '&{}={}'.format(key, val)
    if (len(query) == 0) & (add_param is not None):
        query = "?"
        for key, val in add_param.items():
            query += '{}={}&'.format(key, val)
        query = query[:-1]

    return "{scheme}://{host}{path}{query}".format(**locals())


def get_url_host(url):
    u = urlparse(url)
    return u.netloc


def get_url_param_value(url, param):
    u = urlparse(url)
    for piece in u.query.split('&'):
        if param == piece.split('=')[0]:
            return piece.split('=')[1]
    return None

def get_url_path_element(url, pos=0):
    u = urlparse(url)
    return u.path.split('/')[pos]

def log(msg):
    # global logging function
    if settings.log_stdout:
        try:
            print("{}: {}".format(datetime.now(), msg))
        except UnicodeEncodeError:
            pass  # squash logging errors in case of non-ascii text


def queue_url(other, location, platform):
    with open(settings.files[location][platform], 'a') as file:
        file.write(other + '\n')


def dequeue_url(location, platform):
    with open(settings.files[location][platform], 'r') as file:
        lines = file.readlines()
        try:
            url = lines[-1][:-1].strip()
            lines = lines[:-1]
        except IndexError:
            return None

    with open(settings.files[location][platform], 'w') as file:
        for line in lines:
            file.write(line)

    return url


def clean_text(text):

    for to_replace, replace_with in settings.replacements_dict.items():
        text = text.replace(to_replace, replace_with)

    clean = []
    bin = []
    for letter in text:
        if letter in settings.allowed_charset:
            clean.append(letter)
        else:
            bin.append(letter)

    if len(bin) > 0:
        log('Removed chars: {}'.format(','.join(bin)))

    return ''.join(clean)


def queue_listings(url, platform):

    if 'indeed' in url:
        for company in settings.companies:
            url_expansion = '{}/jobs'.format(company)
            extended_url = url + url_expansion
            page, html = make_request(extended_url, platform)

            jobs = page.find_all(extractors.has_datatnentityid_attr)
            log('Found {} jobs.'.format(len(jobs)))
            if len(jobs) > 0:  # check if there are any jobs for a company
                for job in jobs:
                    job_id_raw = job.get('data-tn-entityid')
                    job_id = extractors.extract_indeed_job_id(job_id_raw)
                    job_url = format_url(extended_url, platform, change_path='/viewjob', add_param={'jk': job_id})
                    queue_url(job_url, 'listing_files', platform)

    if platform == 'twitter':
        queue_url(url, 'listing_files', platform)

    if platform == 'Volkswagen_press':
        driver = selenium_utils.get_driver_with_options()
        driver.get(url)
        selenium_utils.scroll_down_till_limit(driver, platform)
        html = driver.page_source
        page = BeautifulSoup(html, features='html.parser')
        links = extractors.extract_child_element_attr_value_list(page, 'div', {'class': 'page-preview--read-on'},
                                                                 'a', 'href')
        for link in list(set(links)):
            queue_url(link, 'listing_files', platform)

    if platform == 'BMW_press':
        driver = selenium_utils.get_driver_with_options()
        driver.get(url)
        selenium_utils.scroll_down_till_limit(driver, platform)
        html = driver.page_source
        page = BeautifulSoup(html, features='html.parser')
        links = extractors.extract_grandchild_element_attr_value_list(page, 'div', {'class': 'content'},
                                                                      'h3', None, 'a', 'href')
        for link in list(set(links)):
            queue_url(link, 'listing_files', platform)


def auth():
    return settings.platforms['twitter']['credentials']['bearer_token']
    #return os.environ.get("BEARER_TOKEN")


def create_headers(platform):
    if platform == 'twitter':
        bearer_token = auth()
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def handle_listing(page, platform, url):
    if platform == 'indeed':
        title = extractors.extract_element_text(page, 'h1', {'class': 'jobsearch-JobInfoHeader-title'})
        company = extractors.extract_element_text(page, 'div', {'class': 'jobsearch-CompanyReview--heading'})
        if not company:
            company = extractors.extract_element_text(page, 'div', {'class': 'icl-u-lg-mr--sm icl-u-xs-mr--xs'})
        job_meta_header = extractors.extract_element_text(page, 'span', {'class': 'jobsearch-JobMetadataHeader-item'})
        desc = extractors.extract_element_text(page, 'div', {'id': 'jobDescriptionText'})
        url = extractors.extract_element_attr_value(page, 'meta', {'id': 'indeed-share-url'}, 'content')
        job_id = get_url_param_value(url, 'jk')
        footer = extractors.extract_indeed_job_footer_text(page)
        date = extractors.get_date_from_indeed_footer(footer)
        sql_handler.save_indeed_job(job_id=job_id, date=date, company=company,
                                    title=title, job_meta=job_meta_header, text=desc, url=url, platform=platform)
    if platform == 'twitter':
        next_token = extractors.extract_twitter_response(page)
        while next_token:
            token_url = format_url(url, platform, add_param={'pagination_token': next_token})
            page = make_request(token_url, platform)
            next_token = extractors.extract_twitter_response(page)

    if platform == 'Volkswagen_press':
        id = platform + '_' + get_url_path_element(url, -1)
        title = extractors.extract_element_text(page, 'h1', {'class': 'page--title'})
        company = "Volkswagen"
        date = extractors.extract_element_text(page, 'div', {'class': 'meta--item'}, 0)
        date_string = extractors.extract_date_string_from_text(date, platform)
        meta_topics = extractors.extract_child_element_text(page, 'div', {'class': 'meta--item'},
                                                            'a', {'content-link': ''}, 2, 0)
        short_summary = extractors.extract_list_text_by_parent(page, 'div', {'class': 'topic-list'})
        summary = extractors.extract_child_element_text(page, 'div', {'class': 'page-item--intro'}, 'p', None, 0, 0)
        text = extractors.extract_concatinated_text_by_element(page, 'div', {'class': 'page-item--text'}, 'p')
        sql_handler.save_press_release(release_id=id, company=company, release_date=date_string, topics=meta_topics, url=url,
                                       title=title, short_summary=short_summary, summary=summary, text=text)




#        next_token = ''
#        for company, company_dict in settings.platforms['companies'].items():
#            log("\n\n----------\nCRAWL {}\n----------\n\n".format(company))
#            for username, company_id in company_dict.items():
#                log("\n\n----------\nCRAWL {}\n----------\n\n".format(username))
#                next_token = 'init'
#                while next_token:
#                    if next_token == 'init':
#                        url = create_url(company_id)
#                    else:
#                        url = create_url(company_id, next_token)
#                    json_response = helpers.make_request(url, 'twitter', headers=headers, return_format='json')
#                    for tweet in json_response['data']:
#                        tweet_id, creation_date, text = get_tweet_data(tweet)
#                        sql_handler.save_tweet(tweet_id, username, creation_date, text)
#                    next_token = json_response['meta']['next_token'] if 'next_token' in json_response[
#                        'meta'].keys() else ''


