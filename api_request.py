import requests
import settings
import datetime
import helpers


# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'


def auth():
    return settings.twitter_credentials['bearer_token']
    #return os.environ.get("BEARER_TOKEN")


def create_url(company_id, next_token=None):
    path = "{}/tweets".format(company_id)
    tweet_fields = "tweet.fields=author_id,created_at"
    exclude = "exclude=replies"
    max_results = "max_results=100"

    if next_token:
        next_token = 'pagination_token={}'.format(next_token)
        url = "https://api.twitter.com/2/users/{}?{}&{}&{}&{}".format(
            path, tweet_fields, exclude, max_results, next_token
        )
    else:
        url = "https://api.twitter.com/2/users/{}?{}&{}&{}".format(
            path, tweet_fields, exclude, max_results
        )

    return url



def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def get_tweet_data(tweet):
    tweet_id = tweet['id']
    creation_date = datetime.datetime.strptime(tweet['created_at'][:10], '%Y-%m-%d').date()
    text = helpers.clean_text(tweet['text'])
    return tweet_id, creation_date, text


def main():
    sql_handler = helpers.sql_handler
    bearer_token = auth()
    headers = create_headers(bearer_token)
    next_token = ''
    for company, company_dict in settings.twitter['companies'].items():
        helpers.log("\n\n----------\nCRAWL {}\n----------\n\n".format(company))
        for username, company_id in company_dict.items():
            helpers.log("\n\n----------\nCRAWL {}\n----------\n\n".format(username))
            next_token = 'init'
            while next_token:
                if next_token == 'init':
                    url = create_url(company_id)
                else:
                    url = create_url(company_id, next_token)
                json_response = helpers.make_request(url, 'twitter', headers=headers, return_format='json')
                for tweet in json_response['data']:
                    tweet_id, creation_date, text = get_tweet_data(tweet)
                    sql_handler.save_tweet(tweet_id, username, creation_date, text)
                next_token = json_response['meta']['next_token'] if 'next_token' in json_response['meta'].keys() else ''


#def main():
#    bearer_token = auth()
#    headers = create_headers(bearer_token)
#    url = return_test_url()
#    json_response = connect_to_endpoint(url, headers)
#    print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
