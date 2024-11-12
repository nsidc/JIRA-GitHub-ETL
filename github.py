from dataclasses import dataclass
from typing import List
import stages
import json
import requests
import time

@dataclass
class Comment:
    author:str
    created:str
    text:str

@dataclass
class Ticket:
    id:str
    title:str
    description:str
    reporter:str
    projects:List[str]
    milestone:str
    comments:List[Comment]
    subscribable:str
    labels:List[str]
    assignees:List[str]

class AbstractGitHubQuery(stages.SinkStage):

    def __init__(self, org_or_user:str, repository:str, token:str):
        super().__init__()
        self.org_or_user = org_or_user
        self.repository = repository
        self.token = token

    def make_get_request(self, url, title:str):
        headers = {
            'Authorization': 'token ' + self.token
        }
        r = None
        try:
            r = requests.get(url, headers=headers, timeout=5)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error {title}")
            print(errh.args[0])
            return None
        except requests.exceptions.ReadTimeout as errrt:
            print(f"Time out {title}")
            print(errrt.args[0])
            return None
        except requests.exceptions.ConnectionError as conerr:
            print(f"Connection error  {title}")
            print(conerr.args[0])
            return None
        except requests.exceptions.RequestException as errex:
            print(f"Exception request {title}")
            print(errex.args[0])
            return None
        return r

    def make_post_request(self, url, data, title:str):
        headers = {
            'Authorization': 'token ' + self.token
        }
        r = None
        try:
            r = requests.post(url, data=json.dumps(data), headers=headers, timeout=5)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error {title}")
            print(errh.args[0])
            return None
        except requests.exceptions.ReadTimeout as errrt:
            print(f"Time out {title}")
            print(errrt.args[0])
            return None
        except requests.exceptions.ConnectionError as conerr:
            print(f"Connection error  {title}")
            print(conerr.args[0])
            return None
        except requests.exceptions.RequestException as errex:
            print(f"Exception request {title}")
            print(errex.args[0])
            return None
        return r

class IdFinder(AbstractGitHubQuery):

    def __init__(self, org_or_user: str, repository: str, token: str):
        super().__init__(org_or_user, repository, token)
        self.output_port = stages.OutputPort()
        self.title_id_map = {}
        self.fetch_tickets()

    def fetch_tickets(self):
        complete = False
        page_number = 1
        while(not complete):
            url = f'https://api.github.com/repos/{self.org_or_user}/{self.repository}/issues?per_page=100&page={page_number}'

            r = self.make_get_request(url=url, title="github")

            if r is None:
                return None

            if r.ok:
                if (len(r.json()) < 100):
                    complete = True

                print(f"Read github tickets {(page_number-1)*100+len(r.json())}")
                page_number+=1
                for e in r.json():
                    self.title_id_map[e['title']]=e['number']
            else:
                print(f"Failed to retrieve tickets {page_number}")
                exit(1)

    def execute(self, ticket:Ticket):
        ticket.id = self.title_id_map.get(ticket.title, None)
        if ticket.id is None:
            print(f"Error {ticket.title} is missing from the map")
        else:
            self.output_port.send(ticket)

class CommentWriter(AbstractGitHubQuery):

    def create_comment_data(self, comment: Comment):
        data = {
            'body':f"author {comment.author} -- {comment.created}\n{comment.text}"
        }
        return data

    def create_comment(self, comment, ticket:Ticket):
        url = f'https://api.github.com/repos/{self.org_or_user}/{self.repository}/issues/{ticket.id}/comments'

        # Issue link to be returned for easy human access
        issue_link = None

        # Load the data of the issue
        data = self.create_comment_data(comment)

        success = False
        count = 0
        while(not success):
            r = self.make_post_request(url, data, ticket.title)
            if r is None:
                count = count + 1
                print(f"Error on comment for {ticket.title} sleeping {count*30} sec")
                time.sleep(count*30)
            else:
                success=True
            if (count == 10):
                print(f"Error on comment for {ticket.title} cannot complete transfer")
                exit(1)

        if r.ok:
            issue_link = r.json()
            print(f"Successfully created comment {issue_link['id']} for {ticket.title}")

        return issue_link

    def execute(self, ticket:Ticket):
        print()
        for comment in ticket.comments:
            result = self.create_comment(comment=comment, ticket=ticket)

class Writer(AbstractGitHubQuery):

    def create_issue_data(self, ticket:Ticket):
        data = {
                'title': ticket.title,
                'body': ticket.description,
                'labels': ticket.labels,
                'assignees': ticket.assignees,
                'owner': ticket.reporter
            }

        return data

    # This function uploads an issue's data to github at the provided repo name, owner, and PAT. (The GitHub PAT user needs to have edit access on the repository.)
    # It will return the new issue's link and number as a tuple: (link, number). If the issue could not be created, then (None, None) is returned instead
    def create_issue(self, ticket:Ticket):
        print()
        url = f'https://api.github.com/repos/{self.org_or_user}/{self.repository}/issues'

        # Issue link to be returned for easy human access
        issue_link = None

        # Issue number to be returned for possible updates to an issue
        issue_number = None

        # Load the data of the issue
        data = self.create_issue_data(ticket)

        success = False
        count = 0
        while(not success):
            r = self.make_post_request(url, data, ticket.title)
            if r is None:
                count = count + 1
                print(f"Error on {ticket.title} sleeping {count*30} sec")
                time.sleep(count*30)
            else:
                success=True
            if (count == 10):
                print(f"Error on {ticket.title} cannot complete transfer")
                exit(1)

        if r.ok:
            issue_link = r.json()["url"]
            issue_number = r.json()["number"]
            print(f"Successfully Created Issue {issue_number}")

        return (issue_link, issue_number)


    def execute(self, ticket:Ticket):
        result = self.create_issue(ticket=ticket)
        print(f"ID: {result[1]}  Link {result[0]}  Title {ticket.title}  sleep 5 sec\n")
