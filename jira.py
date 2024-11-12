import bs4
import requests
import re
import json
import stages
from dataclasses import dataclass
from typing import List

@dataclass
class Ticket:
    title:str
    key:str
    link:str
    description:str
    labels:List[str]
    status:str
    checklist:str
    reporter:str
    assignee:str
    comments:List[tuple]

@dataclass
class Comment:
    author:str
    created:str
    text:str

# This class takes a text file and does all of the beautiful soup logic in a black box so the JIRA issues can just be extracted and put into GitHub.
class JiraReader(stages.ProducerStage):

    def __init__(self, filepath):
        super().__init__()

        self.filepath = filepath

    def issue_id(self, issue):
        return issue.key.text

    # Getting the titles of each issue
    def issue_titles(self, issue):
        return issue.title.text

    # Getting the links to the original JIRA issues
    def issue_links(self, issue):
        return issue.link.text

    # This function takes in a list of issues and returns the raw description of each issue, as a list of tags
    def issue_descriptions(self, issue):
        description = issue.find_all('description')
        tags = list()
        result = ''
        for desc in description:
            d = ''
            for content in desc.contents:
                # Need to split the content and re add it because this is a navigable string rather than a regular string
                split_content = content.split('\n')

                for tag in split_content:
                    d += tag + '\n'

            result = result + d

        return result

    def issue_status(self, issue):
        return issue.find('status').text

    # This functions returns a list of labels, where the status is the first label in every list, then the actual labels follow; the return is a list of list of strings
    def issue_labels(self, issue):
        issue_labels = list()

        xml_labels = issue.find_all('label')

        for label in xml_labels:
            issue_labels.append(label.text.replace(",",""))

        return issue_labels



    # This function gets the checklists and puts it in the correct form for GitHub checklists
    def issue_checklists(self, issue):
            all_issue_checklists = issue.find_all('checklist')
            checklist = ''
            if len(all_issue_checklists) > 0:
                issue_checklist = all_issue_checklists[0]

                checklist_soup = bs4.BeautifulSoup(issue_checklist.text, 'html.parser')

                # Title is kept in a span with this class
                title = checklist_soup.select_one('.aui-lozenge')

                if title.text != "Empty":
                    checklist += '\n'
                    all_divs = checklist_soup.find_all('div')

                    # Need to do this weird thing with range to ignore the first 5 divs (both <div> and </div>) and only every other div from then on because the nested divs are all listed out
                    for i in range(5, len(all_divs), 2):
                        full_box = all_divs[i].text.strip('\n')

                        # Removing whitespace, leaving only text
                        text = full_box[56:-24]
                        check_box = ' - [ ] ' + text
                        checklist += check_box
                else:
                    checklist = None

            return checklist

    # This function extracts the reporter's username from each JIRA issue
    def issue_reporters(self, issue):
        reporter_tag:bs4.element.Tag = issue.find('reporter')
        username = str(reporter_tag.contents[0])

        return username

    # This function extracts the assignee's username from each JIRA issue, whcih will be '-1' if there is no assignee
    def issue_assignees(self, issue):
        assignee_tag = issue.find('assignee')
        username = str(assignee_tag.contents[0])

        return username

    def issue_comments(self, issue):
        comments_tag = issue.find('comments')

        if comments_tag is not None:
            # Have each comment be a tuple of the author, date created, and the contents; tuples are useful because they are ordered, so it makes for easy data access
            comments = list()

            comment_tags = comments_tag.find_all('comment')
            for comment_tag in comment_tags:
                author = comment_tag['author']
                created = comment_tag['created']
                comment = Comment(author, created, comment_tag.text)
                comments.append(comment)

            return comments
        else:
            return []

    def execute(self):
        with open(self.filepath, 'r') as f:
            file = f.read()

        self.soup = bs4.BeautifulSoup(file, 'xml')

        # Getting all of the items, which are individual JIRA issues
        issues = self.soup.rss.channel.find_all('item')

        count = 0
        number_of_issues = len(issues)
        for issue in issues:
            id=self.issue_id(issue)
            title=self.issue_titles(issue)
            link=self.issue_links(issue)
            description=self.issue_descriptions(issue)
            labels=self.issue_labels(issue)
            checklist=self.issue_checklists(issue)
            reporter=self.issue_reporters(issue)
            assignee=self.issue_assignees(issue)
            comments=self.issue_comments(issue)
            status=self.issue_status(issue)

            count=count+1
            print(f"Progress {count} of {number_of_issues} {count/number_of_issues*100:.2f}\r", end="")

            self.output_port.send(Ticket(key=id, title=title, link=link, description=description, labels=labels, status=status,
                                             checklist=checklist, reporter=reporter, assignee=assignee, comments=comments))


