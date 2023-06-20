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

 
# This class takes a text file and does all of the beautiful soup logic in a black box so it can just be extracted and put into github.
class JIRALoader:
    def __init__(self, filepath):
        self.titles = None
        self.links = None
        self.descriptions = None
        self.labels = None
        self.issues_data = None
        self.checklists = None

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
    def issue_descriptions(self):
        descriptions = list()
        for i, issue in enumerate(self.issues):
            description = issue.find_all('description')
            tags = list()
            for desc in description:
                d = ''
                for content in desc.contents:
                    # Need to split the content and re add it because this is a navigable string rather than a regular string
                    split_content = content.split('\n')

                    for tag in split_content:
                        d += tag + '\n'

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



    # This function gets the checklists and puts it in the correct form for GitHub checklists
    def issue_checklists(self):
        checklists = list()
        for issue in issues:
            all_issue_checklists = issue.find_all('checklist')
            issue_checklist = all_issue_checklists[0]

            checklist_soup = bs4.BeautifulSoup(issue_checklist.text, 'html.parser')

            # Title is kept in a span with this class
            title = checklist_soup.select_one('.aui-lozenge')

            checklist = ''
            if title.text != "Empty":
                all_divs = checklist_soup.find_all('div')

                # Need to do this weird thing with range to ignore the first 5 divs (both <div> and </div>) and only every other div from then on because the nested divs are all listed out
                for i in range(5, len(all_divs), 2):
                    full_box = all_divs[i].text.strip('\n')

                    # Removing whitespace, leaving only text
                    text = full_box[56:-24]
                    check_box = '- [ ] ' + text
                    checklist += check_box
            else:
                checklist = None

            checklists.append(checklist)

        self.checklists = checklists
        return checklists



    # This function compiles the data from the titles, links, descriptions, labels, and checklists into a zipped array of tuples, where each tuple is all of the data for one issue.
    def get_issue_data(self):
        self.issue_titles()
        self.issue_links()
        self.issue_descriptions()
        self.issue_labels()
        self.issue_checklists()

        issues_data = list()
        for zipped in zip(self.titles, self.links, self.descriptions, self.labels, self.checklists):
            issues_data.append(zipped)

        self.issues_data = issues_data
        return issues_data



# Testing
test = JIRALoader('../testJIRA.xml')
issues_data = test.get_issue_data()
# for issue in issues_data:
    # print(issue[1])

