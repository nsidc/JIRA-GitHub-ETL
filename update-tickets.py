import jira
import argparse as arg
import github as gh
import converter
import stages

class SkipUntilStage(stages.ConsumerStage):

    def __init__(self, key):
        super().__init__()
        self.skip = True
        self.key = key

    def execute(self, ticket):
        if self.skip:
            if ticket.key == self.key:
                print("")
                self.skip = False
                self.output_port.send(ticket)
        else:
            self.output_port.send(ticket)

#
# parameter parsing
#
def arguments():
    print("JIRA to GitHub migrator")
    parser = arg.ArgumentParser("JIRA to GitHub migrator - comment added")
    parser.add_argument('-i', dest='input',  type=str, required=True, help="Input xml file")
    parser.add_argument('-u', dest='user_org_name', type=str, required=True, help="Name of the user or organization on GitHub")
    parser.add_argument('-r', dest='repository', type=str, required=True, help="Name of GitHub repository")
    parser.add_argument('-t', dest='token', type=str, required=True, help="GitHub Token")
    parser.add_argument('-k', dest='key', type=str, required=False, help="JIRA Token used as skip mark")

    return parser.parse_args()

#
# pipeline setup
#
def pipeline_setup(args):
    jira_reader = jira.JiraReader(args.input)
    skip_ticket = None
    if args.key is not None:
        skip_ticket = SkipUntilStage(args.key)
    convert_ticket = converter.ConvertTicket()
    github_id_finder = gh.IdFinder(args.user_org_name, args.repository, args.token)
    github_comment_writer = gh.CommentWriter(args.user_org_name, args.repository, args.token)

    if skip_ticket is None:
        jira_reader.output_port.receiver = convert_ticket
    else:
        jira_reader.output_port.receiver = skip_ticket
        skip_ticket.output_port.receiver = convert_ticket

    convert_ticket.output_port.receiver = github_id_finder
    github_id_finder.output_port.receiver = github_comment_writer

    return jira_reader

def main():
    args = arguments()
    reader = pipeline_setup(args)

    reader.execute()
    reader.on_terminate()

if __name__ == "__main__":
    main()
