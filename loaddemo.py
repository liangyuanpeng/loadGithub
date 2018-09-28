import requests, json
from sgqlc.endpoint.http import HTTPEndpoint
import sys

url = 'https://api.github.com/graphql'
headers = {'Authorization': 'bearer df2d58564d98fa3b24e82fb8a54a71d8edb4f874'}

query = 'query { viewer { following(first:10){' \
          'edges {' \
            'follower:node {' \
              'login' \
            '}' \
          '}' \
        '}' \
        'repositories(first:10){' \
          'edges{' \
            'node{' \
              'id' \
            '}' \
          '}' \
        '}' \
        'starredRepositories(first:10){' \
          'edges{' \
            'node{' \
              'id' \
            '}' \
          '}' \
        '}' \
        'followers(first:10){' \
            'edges{' \
            'follower:node{' \
              'login' \
            '}' \
          '}' \
        '}' \
        '}}'

variables = {'varName': 'value'}

endpoint = HTTPEndpoint(url, headers)
data = endpoint(query, variables)
# print(data)
# jsondata = json.loads(data)
# print(jsondata.get("data"))
# json.dump(data, sys.stdout, sort_keys=True, indent=2, default=str)
datastr = json.dumps(data, sort_keys=True, indent=2, default=str)
# print(datastr)
jsondata = json.loads(datastr)
print(jsondata.get("data").get("viewer"))
# print(data.data)

header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.79 Safari/537.36',
        'authorization': 'token df2d58564d98fa3b24e82fb8a54a71d8edb4f874',
        'query': 'query { viewer { login }}'
    }

query = 'query { viewer { following(first:10){' \
          'edges {' \
            'follower:node {' \
              'login' \
            '}' \
          '}' \
        '}' \
        'repositories(first:10){' \
          'edges{' \
            'node{' \
              'id' \
            '}' \
          '}' \
        '}' \
        'starredRepositories(first:10){' \
          'edges{' \
            'node{' \
              'id' \
            '}' \
          '}' \
        '}' \
        'followers(first:10){' \
            'edges{' \
            'follower:node{' \
              'login' \
            '}' \
          '}' \
        '}' \
        '}}'

user = 'query { user(login:"ujjboy") { following(first:10){' \
          'edges {' \
            'follower:node {' \
              'login' \
            '}' \
          '}' \
        '}' \
        'repositories(first:10){' \
          'edges{' \
            'node{' \
              'id' \
            '}' \
          '}' \
        '}' \
        'starredRepositories(first:10){' \
          'edges{' \
            'node{' \
              'id' \
            '}' \
          '}' \
        '}' \
        'followers(first:10){' \
            'edges{' \
            'follower:node{' \
              'login' \
            '}' \
          '}' \
        '}' \
        '}}'

# url = "https://api.github.com/graphql"
# response = requests.post(url, json.dumps({"query": user}),headers=header)
# print(response.json())