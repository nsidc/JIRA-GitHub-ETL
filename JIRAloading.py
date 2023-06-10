import bs4
import requests
import re

with open('../testJIRA.xml', 'r') as f:
    file = f.read()

soup = bs4.BeautifulSoup(file, 'xml')

# Getting all of the items, which are individual JIRA issues
issues = soup.rss.channel.find_all('item')
# print(type(issues))
# print(len(issues))
# print(issues[0])

def issue_titles(issues):
    titles = list()
    for item in issues:
        titles.append(item.title.text)
    return titles

titles = issue_titles(issues)
# print(type(titles))
# print(len(titles))
# print(titles[3])

# Getting the links to the original JIRA issues
def issue_links(issues):
    links = list()
    for issue in issues:
        links.append(issue.link.text)
    return links

links = issue_links(issues)
# print(type(links))
# print(len(links))
# print(links[3])

def issue_description(issues):
    descriptions = list()
    for issue in issues:
        descriptions.append(issue.description.text)
    return descriptions

# use the .contents to loop through and print content tags inside the description
description = issue_description(issues)
print(type(description))
print(len(description))
print(description[3])
