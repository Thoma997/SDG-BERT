import settings
import handlers
import sys
import models
import helpers


def main(platform, mode='all'):

    if mode == 'all':
        protocol = settings.platforms[platform]['protocol']
    else:
        protocol = [mode]

    for element in protocol:
        if element == 'explore':
            generate_listing_urls(platform)
        elif element == 'sanitize':
            sanitize_listing_urls(platform)
        elif element == 'exploit':
            exploit_listings_urls(platform)


def generate_listing_urls(platform):
    with open(settings.files['start_files'][platform], "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip blank and commented out lines

            host = helpers.get_url_host(line)

            if host in settings.platforms[platform]['allowed_hosts']:
                helpers.queue_listings(line, platform)


def sanitize_listing_urls(platform):
    print('\n---\n\nStart sanitizing listing files\n\n---\n')

    listing_file = settings.files['listing_files'][platform]

    # load sql_ids that are already stored in database
    sql_handler = models.SQLHandler()
    sql_ids = sql_handler.get_ids(platform)

    # load query ids found on indeed
    # and filter for unknown ids
    unknown_ids = []
    with open(listing_file, 'r') as f:
        for l in f:
            if platform == 'indeed':
                l_id = helpers.get_url_param_value(l.strip(), 'jk')
            if platform == 'Volkswagen_press':
                l_id = platform + '_' + helpers.get_url_path_element(l.strip(), -1)
            if l_id not in sql_ids:
                unknown_ids.append(l.strip())

    # remove duplicates
    unknown_ids = list(set(unknown_ids))

    # store unknown ids in listing_files
    with open(listing_file, 'w') as f:
        for l in unknown_ids:
            f.write(l + '\n')

    # print the stats
    helpers.log('Filtered {} unknown listings for exoloit'.format(len(unknown_ids)))


def exploit_listings_urls(platform):
    print('\n---\n\nStart exploitation\n\n---\n')
    # go through start urls
    flag = True

    while flag:
        url = helpers.dequeue_url('listing_files', platform)
        if url:
            page = helpers.make_request(url, platform)
            if not page:
                continue
            try:
                handlers.handle_listing(page, platform, url)
            except Exception as e:
                helpers.queue_url(url, 'listing_files', platform)
                raise Exception('Exception: {}'.format(e))
        else:
            flag = False


if __name__ == '__main__':
    args = sys.argv
    keys = settings.platforms.keys()
    assert len(args) >= 2, 'crawler.py takes min 2 arguments but {} given'.format(len(args))
    assert args[1] in keys, '{} not in {}'.format(args[1], keys)
    if len(args) == 2:
        main(args[1])
    elif len(args) == 3:
        main(args[1], args[2])
    else:
        raise ValueError('')
