import mysql.connector
import settings
import helpers
import requests
import cld3
import re


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

    def connect_table(self, t):
        """
        Connects the cursor to a table in the master_thesis database.

        Args:
        t -- name of table to connect to (string)
        """
        q = "SELECT * FROM {}".format(t)
        self.cur.execute(q)

    def return_row(self):
        """
        Returns a single row of the database.
        LIFO principle.
        By calling the mysql fetchone() function.
        """
        return self.cur.fetchone()

    def fetch_random_not_english_indeed_row(self):
        q = ("SELECT * FROM job_postings "
             "WHERE src_lang <> 'en' AND text_en IS NULL "
             "ORDER BY RAND() "
             "LIMIT 1;")
        self.cur.execute(q)
        try:
            return self.cur.fetchone()
        except Exception as e:
            print("CONGRATS all DB entries are translated into english!")
            print("Spread the news to your friends! (And find out if thats actually correct :))")
            return None

    def close_connection(self):
        """
        Closes the connection to the connected database.
        """
        self.cnx.close()

    def update_translation_info(self, table, id, src_lang, text_en):
        s = ("UPDATE {} "
             "SET "
             "src_lang = %(src_lang)s, "
             "text_en = %(text_en)s "
             "WHERE "
             "id = %(id)s;").format(table)

        data = {"id": id,
                "src_lang": src_lang,
                "text_en": text_en}

        with self.cnx.cursor() as cursor:
            cursor.execute(s, data)
            self.cnx.commit()

        helpers.log(("UPDATE DB: table: {}, id: {}\n "
                     "NEW: src_lang: {}\n"
                     "NEW: text_en[:80]: {}").format(table, id, src_lang, text_en[:80]))


    def update_column(self, table, id, col, data):

        assert col in ['src_lang', 'text_en'], 'Col: {} not supported.'.format(str(col))

        s_col = ("UPDATE {} "
                 "SET "
                 "{} = %(data)s "
                 "WHERE "
                 "id = %(id)s;").format(table, col)

        data_col = {"id": id,
                    "data": data}

        with self.cnx.cursor() as cursor:
            cursor.execute(s_col, data_col)
            self.cnx.commit()

        helpers.log("UPDATE DB: table: {}, id: {}, column: {}\nNEW: data[:80]: {}\n".format(table, id, col, data[:80]))


class Translator(object):
    """
    This class enables language detection and translation of text from any detectable language
    to the engligh language.
    """

    def __init__(self):
        self.base_url = "https://translate.googleapis.com/translate_a/single?"
        self.portion_size = 1000
        self.portion_keys = []

    def make_request(self, q):
        """
        Calling the Google Translate API
        Parameters are preset:
        client = gtx,
        sl = auto -- to detect the source language (sl)
        tl = en -- translation language is set to english
        dt = t
        q  = arg(q) -- the query is set to the argument passed

        Raises an Exception if the status code is not 200.

        Args:
        q -- query to be translated

        Return:
        obj -- the parsed JSON object returned by the API
        """
        url_extention = "client=gtx&sl=auto&tl=en&dt=t&q={}".format(q)
        url = self.base_url + url_extention
        r = requests.get(url)
        if r.status_code == 200:
            obj = helpers.format_json(r.text)
            return obj
        else:
            print("Returned status code: {}\nExit with error message:\n{}".format(r.status_code, r.text))
            raise Exception

    def prepare_query(self, q):
        """
        Preparation of the query so that Google Translate API
        does not complain.

        Steps include:
        - replacement of special characters.
        TODO: To Be Completed

        Args:
        q -- query to be translated

        Return:
        q -- prepared query on which the above mentioned steps were applied
        """
        replace_signs = {"&": "and"}
        for f, t in replace_signs.items():
            q = q.replace(f, t)
        return q

    def translate(self, q):
        """
        Orchestrates the helper functions and returns the translation results.
        Orchestration contains:
        - cleansing of query
        - performing the API call
        - return the source language, source text and destination text as tuple

        Agrs:
        q -- query to be translated

        Returns:
        3-Tuple containing the following:
            -- country code of the original language of the query
            -- query in the original language, the translation is based upon
            -- translation of the query in english language
        """
        q = self.prepare_query(q)
        r = self.make_request(q)
        text_src = "".join([obj[1] for obj in r[0]])
        text_dst = "".join([obj[0] for obj in r[0]])
        return str(r[8][0][0]), text_src, text_dst

    def detect_lang(self, text):
        src_lang, _, is_reliable, _ = cld3.get_language(text)
        return src_lang, is_reliable


class TextHandler(object):

    def __init__(self):
        self.limit = settings.char_limit_translator

    @staticmethod
    def split_missing_linebreaks(text):
        char_list = list(text)
        for i in reversed(range(1, len(text)-1)):
            z = text[i-1]
            a = text[i]
            b = text[i+1]
            if (b != " " and b.islower()) and (a.isupper()) and (z not in [".", " "] and z.islower()):
                char_list.insert(i, ". ")
        return "".join(char_list)

    @staticmethod
    def split_paragraphs(text):
        paragraphs = text.split('\n')
        return [p + '\n' for p in paragraphs]

    @staticmethod
    def split_sentences(text):
        sentences = [frag + ". " for frag in re.split(r'\.\s|!\s|\?\s', text)]
        return sentences[:-1]

    @staticmethod
    def assemble_portions(portions):
        """
        Re-assembles the portionized text fragments.

        Args:
        portions -- list of text fragments

        Return:
        String of combined text fragments
        """
        return " ".join(portions)

    def exceeds_limit(self, text):
        return len(text) >= self.limit

    def split_text(self, text):
        """
        Divides the text agrument (string) into a list of fragments
        not exceeding the query limit self.limit

        Args:
        text -- string

        Return:
        fragments -- list of text fragments which give -text- when combined.
        """
        fragments = []
        for paragraph in self.split_paragraphs(text):
            if self.exceeds_limit(paragraph):
                sentences = self.split_sentences(paragraph)
                checksum = sum(1 for sentence in sentences if self.exceeds_limit(sentence))
                if checksum != 0:
                    print("Paragraph Exceed Limit:\n{}".format(sentences))
                    new_paragraph = self.split_missing_linebreaks(paragraph)
                    sentences = self.split_sentences(new_paragraph)
                    checksum = sum(1 for sentence in sentences if self.exceeds_limit(sentence))
                    if checksum != 0:
                        print("Manually split into sentences:\n\n{}".format(paragraph))
                        flag = True
                        while flag:
                            manual_sentence = input("Enter Sentence, Press Enter until done, than enter DONE:") + " "
                            if manual_sentence == "DONE":
                                flag = False
                            else:
                                fragments.append(manual_sentence)
                    else:
                        fragments += sentences
                        print("Split paragraph into sentences:\n{}".format(sentences))
                else:
                    fragments += sentences
            else:
                fragments.append(paragraph)
        return fragments

    def portionize(self, text):
        """
        Divides the text agrument (string) into a list of fragments
        not exceeding the query limit self.portion_size

        Args:
        text -- string

        Return:
        portions -- list of text fragments which give -text- when combined.
        """
        fragments = self.split_text(text)
        portions = []
        tmp_s = ""
        for fragment in fragments:
            if len(tmp_s + fragment) >= self.limit:
                portions.append(tmp_s)
                tmp_s = fragment
            else:
                tmp_s += fragment
        portions.append(tmp_s)
        return portions




