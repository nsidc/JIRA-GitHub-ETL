import stages
import jira
import github as gh
import json
import re

class ConvertTicket(stages.ConsumerStage):

    def __init__(self):
        super().__init__()

        f = open('comment-replacement.json')
        self.comment_name_map = json.load(f)
        f.close

        f = open("j2gh-map.json")
        self.jira_github_map = json.load(f)
        f.close()

        f = open('jira-ids.json')
        self.jira_ids = json.load(f)
        f.close(    )

    def lookup_github_user(self, name):
        return self.jira_github_map.get(name, None)

    def convert_username(self, id):
        jira_name = self.jira_ids.get(id)
        if jira_name is None:
            return f"{id} unknown Jira user"
        github = self.lookup_github_user(jira_name)
        if github is None:
            return f"{jira_name}"
        else:
            return github

    def replace_names(self, text):
        for key in self.comment_name_map.keys():
            text = text.replace(f"@{key}", self.comment_name_map[key])
        text = re.sub(r"@(\w*)",r"\1",text)
        return text

    def format_checklist(self, checklist):
        result = ''
        for item in checklist:
            result = result + f"Entry {item}\n"
        return result

    def execute(self, ticket:jira.Ticket):
        # Adding a checklist if there is one
        description = f"JIRA Issue: {ticket.title}\nOriginal Reporter: {ticket.reporter}\n *** \n{ticket.description}"

        if ticket.checklist is not None:
            if len(ticket.checklist) > 0:
                description += f"\n## Checklist: {self.format_checklist(ticket.checklist)}"

        description = self.replace_names(description)

        comments = []
        if len(ticket.comments) > 0:
            for i, comment in enumerate(ticket.comments):
                comments.append(gh.Comment(author=self.convert_username(comment.author),created=comment.created, text=self.replace_names(comment.text)))

        labels=ticket.labels
        if (ticket.status == "Done"):
            labels.append("Donex")

        assignees=[]
        assignee=self.lookup_github_user(ticket.assignee)
        if assignee is not None:
            assignees.append(assignee)

        gh_ticket = gh.Ticket(title=ticket.title, description=description, assignees=assignees, id=None,
                        reporter=self.lookup_github_user(ticket.reporter), projects=[], milestone="", comments=comments, subscribable="",
                        labels=labels)

        self.output_port.send(gh_ticket)
