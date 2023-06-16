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

# This function takes in a list of issues and returns the raw description of each issue, as a list of tags
def issue_description_raw(issues):
    descriptions = list()
    for i, issue in enumerate(issues):
        description = issue.find_all('description')
        tags = list()
        for desc in description:
            for content in desc.contents:
                # The description is all in one line, but the tags are separated by newline characters
                split_into_tags = content.text.split('\n')

                # one descrtiption string

                # add each line to the description to make one description string
                for tag in split_into_tags:
                    tags.append(tag)

        descriptions.append(tags)

    return descriptions

# raw_descriptions = issue_description_raw(issues)
# for description in raw_descriptions:
    # for tag in description:
        # print(desc)

# This function takes input a list of issues. It returns the a list of a tags for each issue; an empty list for each issue that has no a tags in is's description
def a_tags_descriptions_raw(issues):
    raw_descriptions = issue_description_raw(issues)
    issue_a_tags = list()
    for description in raw_descriptions:
        a_tags = list()
        for tag in description:
            a_search = re.search('<a.*?>', tag) 
            if a_search is not None:
                a_tags.append(a_search)
        issue_a_tags.append(a_tags)

    return issue_a_tags


# This function takes input a list of issues and returns the description of each issue as a single string, with proper spacing and indenting. It will return a list containing all of theses string descriptions
def issue_description(issues):
    descriptions = list()
    for i, issue in enumerate(issues):
        description = issue.find_all('description')
        no_tag_desc = list()
        for desc in description:
            for content in desc.contents:
                # The description is all in one line, but the tags are separated by newline characters (except for a-tags, which will be extracted later)
                split_into_tags = content.text.split('\n')

# ************************************ (Start)
# This block of code adds the proper list starter for html ordered and unordered lists
                # 0 = no list / end of list; 1 = ordered list started; 2 = unordered list started
                start_flag = 0

                # flag to tell whether a tag has already been added
                # 0 = not added to d yet; 1 = added
                added_flag = 0

                # for ordered list counting
                counter = 1

                d = ''
                for tag in split_into_tags:
                    # Logic to add correct starts to list items
                    if re.search('<ol>', tag) is not None:
                        start_flag = 1

                    if re.search('<ul>', tag) is not None:
                        start_flag = 2 

                    if re.search('<(/ol)|(/ul)>', tag) is not None:
                        start_flag = 0
                        counter = 1
        
                    if re.search('<((li)|(/li))>', tag) is not None:
                        # Strips tabs, html tags, and in-line a tags from the tag
                        no_tabs = re.sub('\t', '', tag)
                        raw_str = re.sub('<[/\w\s".:-]*>', '', no_tabs)
                        no_a_tags = re.sub('<a.*?>', '', raw_str)

                        # add the correct start (numbered or GitHub bullet points)
                        # ordred list, so add numbers based on counter
                        if start_flag == 1:
                            num_tag = f'\t{counter}) ' + str(no_a_tags)
                            # print(num_tag)
                            counter += 1
                            d += num_tag + '\n'
                            added_flag = 1
        
                        # unordered list, so make bullet points
                        if start_flag == 2:
                            bullet_tag = '\t- ' + str(no_a_tags)
                            # print(bullet_tag)
                            d += bullet_tag + '\n'
                            added_flag = 1

# ************************************ (End)

                    # add the regular description text if it is not a list tag
                    if added_flag == 0:
                        no_tag = re.sub('<[/\w\s".:-]*>', '', tag)
                        no_a_tag = re.sub('<a.*?>', '', no_tag)
                        d += no_a_tag + '\n'
                        # d += no_tag + '/n'
                    
                    # reset added flag
                    added_flag = 0


                # d will be the complete description
                descriptions.append(d)
                d = ''

    return descriptions

# descriptions = issue_description(issues)
# print(len(descriptions))
# print(type(descriptions))
# for desc in descriptions[:2]:
    # print(desc)

# Function for printing number of tags
def print_issues(issues):
    for issue in issues[:5]:
        content = issue.contents
        for con in content[:10]:
            print(con.text)

# print_issues(issues)


# This class takes a text file and does all of the beautiful soup logic in a black bock so it can just be extracted and put into github.
class JIRALoader:
    def __init__(self, filepath):
        self.titles = None
        self.links = None
        self.descriptions = None
        self.labels = None

        with open(filepath, 'r') as f:
            file = f.read()

        self.soup = bs4.BeautifulSoup(file, 'xml')

        # Getting all of the items, which are individual JIRA issues
        self.issues = soup.rss.channel.find_all('item')


    # Getting the titles of each issue
    def issue_titles(self):
        titles = list()
        for item in self.issues:
            titles.append(item.title.text)

        self.titles = titles
        return titles



    # Getting the links to the original JIRA issues
    def issue_links(self):
        links = list()
        for issue in self.issues:
            links.append(issue.link.text)

        self.links = links
        return links



    # This function takes in a list of issues and returns the raw description of each issue, as a list of tags
    def issue_description_raw(self):
        descriptions = list()
        for i, issue in enumerate(self.issues):
            description = issue.find_all('description')
            tags = list()
            for desc in description:
                for content in desc.contents:
                    # The description is all in one line, but the tags are separated by newline characters
                    split_into_tags = content.text.split('\n')

                    # one descrtiption string

                    # add each line to the description to make one description string
                    for tag in split_into_tags:
                        tags.append(tag)

            descriptions.append(tags)
        self.descriptions = descriptions
        return descriptions



    # This function takes input a list of issues. It returns the a list of a tags for each issue; an empty list for each issue that has no a tags in is's description
    def a_tags_descriptions_raw(self):
        raw_descriptions = issue_description_raw(self.issues)
        issue_a_tags = list()
        for description in raw_descriptions:
            a_tags = list()
            for tag in description:
                a_search = re.search('<a.*?>', tag) 
                if a_search is not None:
                    a_tags.append(a_search)
            issue_a_tags.append(a_tags)
        
        return issue_a_tags


    # This function takes input a list of issues and returns the description of each issue as a single string, with proper spacing and indenting. It will return a list containing all of theses string descriptions
    def issue_description(self):
        descriptions = list()
        for i, issue in enumerate(self.issues):
            description = issue.find_all('description')
            no_tag_desc = list()
            d = ''
            for desc in description:
                for content in desc.contents:
                    # The description is all in one line, but the tags are separated by newline characters (except for a-tags, which will be extracted later)
                    split_into_tags = content.text.split('\n')

    # ************************************ (Start)
    # This block of code adds the proper list starter for html ordered and unordered lists; needed to use regex and not beautiful soup because the tags were not written in xml format. (&lt; and &gt; are used instead of <>)
                    # 0 = no list / end of list; 1 = ordered list started; 2 = unordered list started
                    start_flag = 0

                    # flag to tell whether a tag has already been added
                    # 0 = not added to d yet; 1 = added
                    added_flag = 0

                    # for ordered list counting
                    counter = 1

                    for tag in split_into_tags:
                        # Logic to add correct starts to list items
                        if re.search('<ol>', tag) is not None:
                            start_flag = 1

                        if re.search('<ul>', tag) is not None:
                            start_flag = 2 

                        if re.search('<(/ol)|(/ul)>', tag) is not None:
                            start_flag = 0
                            counter = 1
            
                        if re.search('<((li)|(/li))>', tag) is not None:
                            # Strips tabs, html tags, and in-line a tags from the tag
                            no_tabs = re.sub('\t', '', tag)
                            raw_str = re.sub('<[/\w\s".:-]*>', '', no_tabs)
                            no_a_tags = re.sub('<a.*?>', '', raw_str)

                            # add the correct start (numbered or GitHub bullet points)
                            # ordred list, so add numbers based on counter
                            if start_flag == 1:
                                num_tag = f'\t{counter}) ' + str(no_a_tags)
                                # print(num_tag)
                                counter += 1
                                d += num_tag + '\n'
                                added_flag = 1
            
                            # unordered list, so make bullet points
                            if start_flag == 2:
                                bullet_tag = '\t- ' + str(no_a_tags)
                                # print(bullet_tag)
                                d += bullet_tag + '\n'
                                added_flag = 1

    # ************************************ (End)

                        # add the regular description text if it is not a list tag
                        if added_flag == 0:
                            no_tag = re.sub('<[/\w\s".:-]*>', '', tag)
                            no_a_tag = re.sub('<a.*?>', '', no_tag)
                            d += no_a_tag + '\n'
                            # d += no_tag + '/n'
                        
                        # reset added flag
                        added_flag = 0


                    # d will be the complete description
            descriptions.append(d)

        self.descriptions = descriptions
        return descriptions

    # This functions returns a list of labels, where the status is the first label in every list, then the actual labels follow; the return is a list of list of strings
    def issue_labels(self):
        labels = list()
        for issue in issues:
            issue_labels = list()

            # add the status to the labels list first
            status = issue.find('status').text
            issue_labels.append(status)

            xml_labels = issue.find_all('label')

            for label in xml_labels:
                issue_labels.append(label.text)

            labels.append(issue_labels)
        
        self.labels = labels
        return labels


# test = JIRALoader('../testJIRA.xml')
# for link in test.issue_links():
    # print(link)

labels = list()
for issue in issues:
    issue_labels = list()

    # add the status to the labels list first
    status = issue.find('status').text
    issue_labels.append(status)

    xml_labels = issue.find_all('label')

    for label in xml_labels:
        issue_labels.append(label.text)

    labels.append(issue_labels)

for label in labels:
    for l in label:
        print(l)
