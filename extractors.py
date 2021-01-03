import re
import helpers
import settings
from datetime import datetime, timedelta


def extract_indeed_job_count(s, url):
    pattern = '.*\w+ \d+ \w+ (\d+) .*'
    match = re.match(pattern, s)
    if match:
        return int(match.group(1))
    else:
        helpers.log("No job count detected in {}".format(url))
        return None

def extract_indeed_job_id(s):
    pattern = '.*,(.+),.*'
    return get_single_group_regex(pattern, s)

def get_single_group_regex(pattern, s, n=1):
    match = re.match(pattern, s)
    if match:
        return match.group(n).strip()
    else:
        helpers.log("Regex pattern: {} failed single group extraction in: {}".format(pattern, s))
        return None

def has_datatnentityid_attr(tag):
    if tag:
        return tag.has_attr('data-tn-entityid')
    else:
        return

def find_element(page, element, attr, pos):
    tags = page.find_all(element, attr)
    if len(tags) != 0:
        return tags[pos]
    else:
        return None


def find_child_element(page, parent_element, parent_attr, child_element, child_attr, parent_pos, child_pos):
    tags = page.find_all(parent_element, parent_attr)
    if tags:
        tag = tags[parent_pos]
        children = tag.findChildren(child_element, child_attr)
        if children:
            return children[child_pos]
        else:
            return None
    else:
        return None


def extract_text_from_element(element):
    return element.text.strip()


def extract_element_text(page, element, attr, pos=0):
    element = find_element(page, element, attr, pos)
    return extract_text_from_element(element)


def extract_child_element_text(page, parent_element, parent_attr, child_element, child_attr, parent_pos=0, child_pos=0):
    element = find_child_element(page, parent_element, parent_attr, child_element, child_attr, parent_pos, child_pos)
    if element:
        return element.text.strip()
    else:
        return None
def extract_date_string_from_text(date, platform):
    date_format = settings.platforms[platform]['exploit_listings']['date_format']
    date_string = str(datetime.strptime(date, date_format).date())
    return date_string


def extract_list_text_by_parent(page, parent_element, parent_attr, parent_pos=0):
    ul = find_child_element(page, parent_element, parent_attr, 'ul', None, parent_pos, 0)
    list_text = ''
    if ul:
        for li in ul.findAll('li'):
            list_text += li.text.strip() + '\n'
        return list_text
    else:
        return None


def extract_concatinated_text_by_element(page, element, attr, iterative_element, pos=0):
    element = find_element(page, element, attr, pos)
    cum_text = ''
    for tag in element.findAll(iterative_element):
        cum_text += tag.text.strip() + '/n'
    return cum_text


def extract_element_attr_value(page, element, search_attr, target_attr):
    tag = find_element(page, element, search_attr)
    return tag.get(str(target_attr)).strip()


def extract_child_element_attr_value_list(page, element, search_attr, child_element, target_attr):
    tags = page.find_all(element, search_attr)
    values = []
    if len(tags) != 0:
        for tag in tags:
            child = tag.findChild(child_element)
            if child:
                values.append(child.get(str(target_attr)).strip())
            else:
                return None
        return values
    else:
        raise ValueError('Parent element not found')


def extract_grandchild_element_attr_value_list(page, element, attr, child_element, child_attr,
                                               grandchild_element, target_attr):
    tag = find_element(page, element, attr, 0)
    children = tag.findChildren(child_element, child_attr)
    values = []
    if len(children) != 0:
        for child in children:
            grandchild = child.findChild(grandchild_element)
            if grandchild:
                values.append(grandchild.get(str(target_attr)).strip())
            else:
                return None
        return values
    else:
        raise ValueError('Parent element not found')


def extract_indeed_job_footer_text(page):
    tags = page.find_all('div', {'class': 'jobsearch-JobMetadataFooter'})

    try:
        children = tags[0].contents
    except AttributeError or IndexError:
        return None

    s = ''
    if len(children) != 0:
        for child in children:
            try:
                s += child.text
            except AttributeError:
                continue
        return s.strip()
    else:
        return None

def get_date_from_indeed_footer(s):
    pattern = '.+\s?-?(\s\w*)?\s(\d\d?)\+?\s.*-?.+'
    pattern_today = '.*-\s(\w+(\s\w+)?)\s-.*'
    today_synonymes = ['dagen geleden', 'gerade geschaltet', 'vandaag', "aujourd\'hui", 'heute']
    days_back = get_single_group_regex(pattern, s, 2)
    if not days_back:
        today = get_single_group_regex(pattern_today, s, 1)
        helpers.log(today)
        if today:
            days_back = 0
        else:
            for phrase in today_synonymes:
                if phrase in s.lower():
                    helpers.log('found gerade geschaltet in {}'.format(s))
                    days_back = 0


    if days_back:
        date = datetime.now().date() - timedelta(days=int(days_back))
        #date_string = datetime.strftime(date, '%Y-%m-%d')
        return date
    else:
        return None


def get_tweet_data(tweet):
    tweet_id = tweet['id']
    creation_date = datetime.datetime.strptime(tweet['created_at'][:10], '%Y-%m-%d').date()
    text = tweet['text']
    return tweet_id, creation_date, text


def extract_twitter_response(page):
    username = page['includes']['users'][0]['username']
    for tweet in page['data']:
        tweet_id, creation_date, text = get_tweet_data(tweet)
        helpers.sql_handler.save_tweet(tweet_id, username, creation_date, text)
        next_token = page['meta']['next_token'] if 'next_token' in page['meta'].keys() else ''

    return next_token


