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

# Getting a list of titles from the issues
def issue_titles(issues):
    titles = list()
    for item in issues:
        titles.append(item.title.text)
    return titles

# titles = issue_titles(issues)
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

# Getting the descriptions
def issue_description(issues):
    descriptions = list()
    for i, issue in enumerate(issues):
        description = issue.find_all('description')
        no_tags = list()
        for desc in description:
            for content in desc.contents:
                # The description is all in one line, but the tags are separated by newline characters
                split_into_tags = content.text.split('\n')

                # Turn each tag into just text
                for tag in split_into_tags:
                    no_tag = re.sub('<[/\w\s".:-]*>', '', tag)
                    no_tags.append(no_tag)

                # Use the list of tags to make one description string
                d = ''
                for tag in no_tags:
                    d += tag + '\n'

        descriptions.append(d)
    return descriptions

descriptions = issue_description(issues)
print(len(descriptions))
print(type(descriptions))
for desc in descriptions:
    print(desc)

# Function for printing number of tags
def print_issues(issues):
    for issue in issues[:5]:
        content = issue.contents
        for con in content[:10]:
            print(con.text)

# print_issues(issues)
