import os

home = os.path.expanduser("~") + '/'
current_dir = home + 'Desktop/codebase_thesis/'

replacements = {'ł': 'l', 'ć': 'c', 'ø': 'o', 'ö': 'oe', 'é': 'e', 'ü': 'ue', 'ä': 'ae', 'à': 'a',
               '¡': 'i', 'Ü': 'Ue', 'Ö': 'Oe', 'Ä': 'Ae', 'í': 'i', 'á': 'a', 'ê': 'e',
               'ñ': 'n', 'ç': 'c', '“': '"', '”': '"', '–': '-', "‘": "'", 'ó': 'o', 'ã': 'a',
               '…': '.', 'ë': 'e', 'è': 'e', 'ô': 'o', 'î': 'i', 'œ': 'oe', '«': '"', '»': '"', 'â': 'a',
               'É': 'E', 'À': 'A', 'û': 'u', 'å': 'a', 'æ': 'ae', '₂': '2', '\n': ' ', 'ß': 'ss', '„': '"',
               '—': ' ', 'õ': 'o', 'Š': 'S', 'Ó': 'O', '²': '2', 'Ø': 'O', 'ù': 'u', 'Ê': 'E', 'Ú': 'U', 'ú': 'u',
               'Á': 'A'}
allowed_charset = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!"§$%&/()=?+#*\'<>-_.:,; []@’€£')
replacements_dict = {
    'ł': 'l',
    '￼': '',
    '₂': '2',
    '‐': ' ',
    '❌': '',
    '\uf0fc': '',
    '✶': '',
    '✦': '',
    '\uf0a7': '',
    '\uf0b7': '',
    '✔': '',
    '\uf0d7': '',
    '\ufeff': '',
    '✓': '',
    '🥋':' ',
    '✩': ' ',
    '️': '',
    '✅ ': '',
    '\u200d': ''
}


# author_ids
#   found these on twitter
#   some are the accounts of the groups e.g. BMW group
#   and others are of the brands
#   I assume that the contents are different for the groups
#   and the brands e.g. may the fashion brand accounts be more
#   concerned about marketing the cloths and the group accounts about
#   following more sustainable goals.
#   We only used verified accounts. If a brand did not have a verified account,
#   we did not include it because it is not verified that the person behind the account is
#   really posting in the name of the brand.
#   Bestseller did not have an official account. Thus, we used the accounts of their subbrands
#   e.g. jack & jones.
#   IDs can be backlinked with name and username again using the user lookup endpoint


platforms = {
    'twitter':
        {
            'credentials':
                {
                    'API_key': 'gwRI7UBYQu35glQPrBzz8V2pE',
                    'API_secret_key': '1KhwBWySoqiBQm500PhLfrUolzBT6kHrzxnk45WcDEzjjIRbAv',
                    'bearer_token': 'AAAAAAAAAAAAAAAAAAAAAK9yKwEAAAAArvnQ1Ih8Om6Tj%2F2wTUtU5CFYmxw%3Dw6202st2XT4rPKomzsbvdeLhDYOn0Seh0ed1AhLAgpb5qfkzrq'
                },
            'requires_auth': True,
            'protocol': ['explore', 'exploit'],
            'returns_json': True,
            'allowed_hosts': ['api.twitter.com'],
            'allowed_params': ['tweet.fields', 'exclude', 'max_results', 'pagination_token'],
            'companies':
                {
                    'H&M': {'hm': '14399483'},
                    'Zara': {'ZARA': '346742249'},
                    'Primark': {'Primark': '1630182978'},
                    'Puma': {'PUMA': '50883209', 'PUMAGroup': '98153853'},
                    'Adidas': {'adidas': '300114634'},
                    'Pandora-Jewelry': {'PANDORA_Corp': '983301177948430337', 'Pandora_UK': '271383486'},
                    'JD-Sports-Fashion-PLC': {'JDOfficial': '26239843', 'JDSports': '2805156282'},
                    'Gucci': {'gucci': '16913418'},
                    'Louis-Vuitton': {'LouisVuitton': '44084633', 'LVMH': '558606074'},
                    'Bestseller': {'JackandJonesTM': '62924046', 'VEROMODA': '19061982'},
                    'BMW': {'BMW': '1545994664', 'BMWGroup': '107122128'},
                    'Daimler-Ag': {'Daimler': '12637732'},
                    'Volvo': {'VolvoGroup': '18238328'},
                    'Volkswagen': {'VWGroup': '3021235211'},
                    'Porsche-Ag': {'Porsche': '57016932'},
                    'Peugeot': {'Peugeot': '100186027'},
                    'Seat': {'SEATofficial': '833562217'},
                    'Renault': {'Groupe_Renault': '16144151'},
                    'Audi': {'AudiOfficial': '29679737'},
                    'Skoda': {'SKODAUK': '120985729'},
                    'Orsted': {'Orsted': '2656316095'},
                    'Enel': {'EnelGroup': '364784007'},
                    'Edf': {'edfenergy': '123065047', 'EDFofficiel': '268267143'},
                    'National-Grid': {'nationalgriduk': '109525104'},
                    'Engie': {'ENGIEgroup': '88697269'},
                    'Endesa': {'Endesa': '482014260'},
                    'E.on': {'EON_SE_en': '2474086476'},
                    'Fortum': {'Fortum': '404127128'},
                    'Rwe': {'RWE_AG': '158347171'},
                    'Sse-PLC': {'SSE': '67342845'}
                }
        },
    'indeed':
        {
            'credentials': None,
            'requires_auth': False,
            'protocol': ['explore', 'sanitize', 'exploit'],
            'returns_json': False,
            'allowed_hosts': ['dk.indeed.com', 'de.indeed.com', 'www.indeed.co.uk',
                               'no.indeed.com', 'se.indeed.com', 'es.indeed.com',
                               'fr.indeed.com', 'ch.indeed.com', 'nl.indeed.com',
                               'be.indeed.com'],
            'allowed_params': ['q', 'sort', 'limit', 'start', 'jk']
        },
    'Volkswagen_press':
        {
            'credentials': None,
            'requires_auth': False,
            'protocol': ['explore', 'sanitize', 'exploit'],
            'returns_json': False,
            'allowed_hosts': ['www.volkswagen-newsroom.com', 'www.volkswagen-newsroom.com:443'],
            'allowed_params': [],
            'search_listings':
                {
                    'search_by': 'class',
                    'search_query': 'meta--item',
                    'element_positions': [-1, -2, -3, -4],
                    'date_format': '%m/%d/%y',
                    'reference_date': '2019-01-01',
                    'show_more_xpath': '//button[contains(text(),"Show more Press Releases")]',

                },
            'exploit_listings':
                {
                    'date_format': '%m/%d/%y'
                }
        }

}

# Database
database = 'master_thesis'
host = os.environ.get('MYSQL_HOST_THESIS')
user = os.environ.get('MYSQL_USER_THESIS')
password = os.environ.get('MYSQL_PW_THESIS')


# companies
backlog_companies = ['H&M', 'Zara', 'Primark', 'Puma', 'Adidas', 'Pandora-Jewelry', 'JD-Sports-Fashion-PLC', 'Gucci', 'Louis-Vuitton', 'Bestseller',
             'BMW', 'Daimler-Ag', 'Volvo', 'Volkswagen', 'Porsche-Ag', 'Peugeot', 'Seat', 'Renault', 'Audi', 'Skoda',
             'Orsted', 'Enel', 'Edf', 'National-Grid', 'Engie', 'Endesa', 'E.on', 'Fortum', 'Rwe', 'Sse-PLC']

companies = ['H&M', 'Zara', 'Primark', 'Puma', 'Pandora-Jewelry', 'JD-Sports-Fashion-PLC', 'Gucci', 'Louis-Vuitton', 'Bestseller',
             'Daimler-Ag', 'Volkswagen', 'Porsche-Ag', 'Peugeot', 'Seat', 'Renault', 'Audi', 'Skoda',
             'Orsted', 'Enel', 'Edf', 'National-Grid', 'Endesa', 'E.on', 'Fortum', 'Rwe']

# file storage
files = {'listing_files': {'indeed': current_dir + 'listing_files/indeed.txt',
                           'Volkswagen_press': current_dir + 'listing_files/Volkswagen_press.txt',
                           'BMW_press': current_dir + 'listing_files/BMW_press.txt'},
         'start_files': {'indeed': current_dir + 'start_files/indeed.txt',
                         'twitter': current_dir + 'start_files/twitter.txt',
                         'Volkswagen_press': current_dir + 'start_files/Volkswagen_press.txt',
                         'BMW_press': current_dir + 'start_files/BMW_press.txt'},
         'failed_extraction_files': {'indeed': current_dir + 'failed_extraction_files/indeed.txt'}
         }

char_limit_translator = 1000

# logging
log_stdout = True