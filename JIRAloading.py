import bs4
import requests
import re

with open('../testJIRA.xml', 'r') as f:
    file = f.read()

soup = bs4.BeautifulSoup(file, 'xml')

# print(soup.rss.channel.find_all('item')[0].title.text)

# Getting all of the items, which are individual JIRA issues
issues = soup.rss.channel.find_all('item')

# print(type(issues))
# print(len(issues))

# Making a list of all of the titles
titles = list()
for issue in issues:
    titles.append(issue.title)

print(len(titles))

# for title in titles[:5]:
#     print(title)

def load_titles(issues):
    titles = list()
    for issue in issues:
        titles.append(issue.title)
    return titles

# Testing load_titles() with issues
# test = load_titles(issues)
# assert test == titles
# print(len(test))
for title in test[:10]:
    print(title.text)
