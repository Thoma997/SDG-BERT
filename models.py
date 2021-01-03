import mysql.connector
import settings
import helpers


class SQLHandler(object):
    """
    # TODO
    """
    counter = 0

    def __init__(self):
        self.cnx = mysql.connector.connect(user=settings.user,
                                           password=settings.password,
                                           host=settings.host,
                                           database=settings.database)
        self.cur = self.cnx.cursor(buffered=True)

    @staticmethod
    def update_replacement_dict(replace, replacement):
        settings.replacements_dict.update({replace: replacement})

    def get_ids(self, platform):
        if platform == 'indeed':
            s = "SELECT id FROM job_postings"
        if platform == 'Volkswagen_press':
            s = ("SELECT id FROM press_releases " 
                 "WHERE company = 'Volkswagen'")

        self.cur.execute(s)
        ids = self.cur.fetchall()
        return [el[0] for el in ids]


    def save_press_release(self, release_id, company, release_date, topics, url, title, short_summary, summary, text):
        global counter
        counter = 0

        s = ("INSERT INTO press_releases "
             "(id, company, date, meta_topics, title, short_summary, summary, text, url) "
             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
             "ON DUPLICATE KEY UPDATE id=id")

        data = (release_id, company, release_date, topics, title, short_summary, summary, text, url)

        self.save(s, data, url, company)

    def save_tweet(self, tweet_id, username, creation_date, text):
        global counter
        counter = 0

        s = ("INSERT INTO tweets "
             "(id, post_date, username, text) "
             "VALUES (%s, %s, %s, %s) "
             "ON DUPLICATE KEY UPDATE id=id")

        data = (tweet_id, creation_date, username, text)

        url = 'twitter, tweet_id: {}'.format(tweet_id)

        self.save(s, data, url, 'twitter')

    def save_indeed_job(self, job_id, date, company, title, job_meta, text, url, platform):
        global counter
        counter = 0
        if len(title) > 120:
            title = title[:120]
        if len(company) > 30:
            company = company[:30]

        s = ("INSERT INTO job_postings "
             "(id, post_date, company, title, job_meta, text) "
             "VALUES (%s, %s, %s, %s, %s, %s) "
             "ON DUPLICATE KEY UPDATE id=id")

        data = (job_id, date, company, title, job_meta, text)

        self.save(s, data, url, platform)

    def save(self, s, data, url, platform):
        try:
            self.cur.execute(s, data)
        except mysql.connector.errors.IntegrityError as e:
            helpers.queue_url(url, 'failed_extraction_files', platform)
            helpers.log('Failed extraction of URL: {}\nRequeued URL in failed_extraction_files\n{}'.format(url, e))
        except mysql.connector.errors.DatabaseError as e:
            global counter
            counter += 1
            if counter > 3:
                print(e)
                raise mysql.connector.DatabaseError

            # If text includes encoding issues, reformat to UTF-8 string and try again.
            helpers.log('SQL ERROR: ' + e)
            d = list(data)
            for i in [-1, 2]:  # company and text
                # if data in bytes, decode to string
                if type(d[i]) == bytes:
                    d[i] = d[i].decode('UTF-8', 'ignore')

                # if data in string, replace the usual problem characters with known solutions
                # if the known solutions do not help, manually input new solutions
                if type(d[i]) == str:
                    if counter > 1:
                        replace = input('Which character to replace?')
                        replacement = input('Which character to replace the character with?')
                        SQLHandler.update_replacement_dict(replace, replacement)
                        print('Thanks for inserting! Dont forget to add this keypair to the settings file')
                    for to_replace, replace_with in settings.replacements_dict.items():
                        d[i] = d[i].replace(to_replace, replace_with)

            data = tuple(d)
            helpers.log(data)
            self.save(s, data, url, platform)

        try:
            self.cnx.commit()
        except mysql.connector.errors.OperationalError as e:
            msg = 'SQL Error: {0}'.format(e)
            if 'Lost connection' in msg:
                global cnx, cur
                self.cnx = mysql.connector.connect(user=settings.user,
                                              password=settings.password,
                                              host=settings.host,
                                              database=settings.database)
                self.cur = self.cnx.cursor(buffered=True)
                self.save(s, data, url, platform)
            else:
                raise mysql.connector.errors.OperationalError(msg)
