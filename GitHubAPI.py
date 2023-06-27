import requests
import bs4
import json
import JIRAloading as JL


def make_request(URL, data, headers):
# ****************************************************
# Use of try and exception handeling provided by GeeksForGeeks at https://www.geeksforgeeks.org/exception-handling-of-python-requests-module/
    r = None
    try:
        r = requests.post(URL, data=json.dumps(data), headers=headers, timeout=5)
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])
        return None
    except requests.exceptions.ReadTimeout as errrt:
        print("Time out")
        return None
    except requests.exceptions.ConnectionError as conerr:
        print("Connection error")
        return None
    except requests.exceptions.RequestException as errex:
        print("Exception request")
        print(errex.args[0])
        return None
    return r



def load_issue_data(issue, USERNAMES):
    body = None
    data = None
    # Getting correct form of username, depending on what data is avilable
    if issue[5] not in list(USERNAMES.keys()):
        reporter = issue[5] + ' (JIRA username)'
    else:
        reporter = USERNAMES[issue[5]]

    # Adding a checklist if there is one
    if issue[4] is not None:
        body = "JIRA Issue: " + issue[1] + "\nOriginal Reporter: " + reporter + "\n *** \n" + issue[2]
        body += "\n## Checklist:" + issue[4]
    else:
        body = "JIRA Issue: " + issue[1] + "\nOriginal Reporter: " + reporter + "\n *** \n" + issue[2]

    # Add comments if there are any
    if issue[7] is not None:
        body += "\n## JIRA Comments:\n" 
        for i, comment in enumerate(issue[7]):
            author_username = ''
            if comment[0] in list(USERNAMES.keys()):
                author_username = USERNAMES[comment[0]]
            else:
                print(f"{comment[0]} is not in JGUsernames.json")
                author_username = comment[0] + " (JIRA username)"

            # Checking for final line to properly print without left over whitespace
            if i == (len(issue[7]) - 1):
                body += f" ### {author_username} added a comment on {comment[1][:-6]}\n {comment[2]}"
            else:
                body += f" ### {author_username} added a comment on {comment[1][:-6]}\n {comment[2]}\n\n"


    # Testing for assignee and assigning one if possible
    if issue[6] == "-1":
        # No assignee
        data = {
            'title': issue[0],
            'body': body,
            'labels': issue[3]
        }
    elif issue[6] not in USERNAMES.keys():
        print('*****Notice*****')
        print(f"Assignee with JIRA username {issue[6]} was not found in JGUsernames.json. There will be no assignee on this GitHub issue.")
        data = {
            'title': issue[0],
            'body': body,
            'labels': issue[3]
        }
    else:
        data = {
            'title': issue[0],
            'body': body,
            'labels': issue[3],
            'assignees': [USERNAMES[issue[6]]]
        }

    return data



# This function uploads an issue's data to github at the provided repo name, owner, and PAT. (The GitHub PAT user needs to have edit access on the repository.) 
# It will return the new issue's link and number as a tuple: (link, number). If the issue could not be created, then (None, None) is returned instead
def create_issue(issue, REPO_NAME, REPO_OWNER, PAT, USERNAMES):
    URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'

    headers = {
        'Authorization': 'token ' + PAT
    }

    # Issue link to be returned for easy human access
    issue_link = None

    # Issue number to be returned for possible updates to an issue
    issue_number = None 

    # Load the data of the issue
    data = load_issue_data(issue, USERNAMES)

    r = make_request(URL, data, headers)

    if r is None:
        return (None, None)

    if r.ok:
        issue_link = r.json()["url"]
        issue_number = r.json()["number"]
        print(f"Successfully Created Issue {issue_number}\n")

    return (issue_link, issue_number)



# This function updates a GitHub issue to the provided issue data at the provided repo name, repo owner, issue number, and PAT. (The GitHub PAT user needs to have edit access on the repository.) 
# It will return the issue's link. If the issue could not be updated, then None is returned instead.
def update_issue(issue, REPO_NAME, REPO_OWNER, PAT, USERNAMES, ISSUE_NUMBER):
    URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{ISSUE_NUMBER}'

    headers = {
        'Authorization': 'token ' + PAT
    }

    # Issue link to be returned for easy human access
    issue_link = None

    # Load the data of the issue
    data = load_issue_data(issue, USERNAMES)

    r = make_request(URL, data, headers)

    if r is None:
        return None

    if r.ok:
        print(f"Successfully Updated Issue {ISSUE_NUMBER}")
        issue_link = r.json()["url"]

    return issue_link



# This is a text-based, user interface to use both the JIRAloader.py and GitHubAPI.py function calls. The user needs to have the location of the JIRA file, the repo owner's name or the organization the repo is in, the name of the repo, and a working PAT key. More information about GitHub PATs can be found here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
def run():
    file_name = input('Enter the path to the JIRA .xml file: ')
    issues = JL.JIRALoader(file_name)

    # Getting the issues loaded into the JIRALoader object
    issues.get_issue_data()

    # Load usernames
    USERNAMES = issues.load_usernames()

    # Below is an example repository link:
    # https://github.com/<repo owner username or organization>/<repo name>
    REPO_OWNER = input("Enter the repository owner's GitHub username or the organization's GitHub name: ")

    REPO_NAME = input("Enter the name of the repository: ")

    # GitHub PAT tokens are how this tool authenticates with the GitHub REST API. Please note that if you are creating an issue, the PAT owner will be the creator of the issue. To create a PAT for GitHub please visit: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
    PAT = input("Enter your PAT token: ")

    create_or_update = True
    while(create_or_update):
        print('------------------------Menu--------------------------')
        print('\t- "c" to create an issue from the loaded issues')
        print('\t- A number to update that issue in the repository')
        print('\t- "s" to stop updating and creating')
        print()
        choice = input('Enter an option from the above menu: ')

        # User wants to create an issue
        if choice == 'c':
            print_input = input('Would you like to print all of the currently lodaded issues\' titles? ("y" for yes, anything else for no): ')

            if print_input == "y":
                print("These are the titles of all loaded issues: ")
                issues.print_issue_titles()

            flag = True
            while(flag):
                question = input('Enter the issue number to be created. (This issue\'s data will be the data used to create the new issue.) Enter "s" to stop the creation: ')
                if question == "s":
                    print("\nCancelling issue creation.\n")
                    flag = False
                elif question.isdigit():
                    # Create the issue
                    link, number = create_issue(issues.issues_data[int(question) - 1], REPO_NAME, REPO_OWNER, PAT, USERNAMES)

                    if link is None:
                        print("\nIssue could not be updated\n")
                    else:
                        print(f"\nLink to new issue: {link}\n")

                    flag = False
                else:
                    print('Please enter a number or "n" to cancel')

        elif choice.isdigit():
            ISSUE_NUMBER = int(choice)

            print_input = input('Would you like to print all of the currently lodaded issues\' titles? ("y" for yes, anything else for no): ')

            if print_input == "y":
                print("These are the titles of all loaded issues: ")
                issues.print_issue_titles()

            flag = True
            while(flag):
                question = input('Enter the issue number with the correct issue information. (This issue\'s data will be the replacement data for the provided issue number.) Enter "s" to stop the update: ')

                if question == "s":
                    print(f"Cancelling update on issue {issue_num}\n")
                    flag = False
                elif question.isdigit():
                    # Update the issue
                    link = update_issue(issues.issues_data[int(question) - 1], REPO_NAME, REPO_OWNER, PAT, USERNAMES, ISSUE_NUMBER)

                    if link is None:
                        print("\nIssue could not be updated\n")
                    else:
                        print(f"\nLink to updated issue: {link}\n")

                    flag = False
                else:
                    print('Please enter a number or "n" to cancel')

        elif choice == "s":
            print("Stopping Program")
            create_or_update = False
        else:
            print('Please enter "c", a number, or "s"')

run()
