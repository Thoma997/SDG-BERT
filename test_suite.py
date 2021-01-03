import sys
import requests

def main(url):
    response = requests.request("GET", url)
    print(response.status_code)
    print(response.text[:1000])

if __name__ == '__main__':
    args = sys.argv
    main(args[1])