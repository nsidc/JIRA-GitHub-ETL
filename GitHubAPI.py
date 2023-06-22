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


# This function uploads an issue's data to github at the provided repo name, owner, and PAT. (The GitHub PAT user needs to have edit access on the repository.) 
# It will return the new issue's link and number as a tuple: (link, number). If the issue could not be created, then (None, None) is returned instead
def create_issue(issue, REPO_NAME, REPO_OWNER, PAT):
    URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
    headers = {
        'Authorization': 'token ' + PAT
    }

    # Issue link to be returned for easy human access
    issue_link = None

    # Issue number to be returned for possible updates to an issue
    issue_number = None 

    if issue[4] is not None:
        data = {
            'title': issue[0],
            'body': "JIRA Issue: " + issue[1] + "\n\n" + issue[2] + "\nChecklist:\n" + issue[4],
            'labels': issue[3]
        }
    else:
        data = {
            'title': issue[0],
            'body': "JIRA Issue: " + issue[1] + "\n\n" + issue[2], 
            'labels': issue[3]
        }

    r = make_request(URL, data, headers)

    if r is None:
        return (None, None)

    if r.ok:
        issue_link = r.json()["url"]
        issue_number = r.json()["number"]
        print(f"Successfully Created Issue {issue_number}")

    return (issue_link, issue_number)

# This function updates a GitHub issue to the provided issue data at the provided repo name, repo owner, issue number, and PAT. (The GitHub PAT user needs to have edit access on the repository.) 
# It will return the issue's link. If the issue could not be updated, then None is returned instead.
def update_issue(issue, REPO_NAME, REPO_OWNER, PAT, ISSUE_NUMBER):
    URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{ISSUE_NUMBER}'
    headers = {
        'Authorization': 'token ' + PAT
    }

    # Issue link to be returned for easy human access
    issue_link = None

    if issue[4] is not None:
        data = {
            'title': issue[0],
            'body': "JIRA Issue: " + issue[1] + "\n\n" + issue[2] + "\nChecklist:\n" + issue[4],
            'labels': issue[3]
        }
    else:
        data = {
            'title': issue[0],
            'body': "JIRA Issue: " + issue[1] + "\n\n" + issue[2], 
            'labels': issue[3]
        }

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

    # Below is an example repository link:
    # https://github.com/<repo owner username or organization>/<repo name>
    REPO_OWNER = input("Enter the repository owner's GitHub username or the organization's GitHub name: ")

    REPO_NAME = input("Enter the name of the repository: ")

    # GitHub PAT tokens are how this tool authenticates with the GitHub REST API. Please note that if you are creating an issue, the PAT owner will be the creator of the issue. To create a PAT for GitHub please visit: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
    PAT = input("Enter your PAT token: ")

    create_or_update = True
    while(create_or_update):
        print('Enter one of the following choices: ')
        print('\t- "c" to create an issue from the loaded issues')
        print('\t- A number to update that issue in the repository')
        print('\t- "s" to stop updating and creating')
        choice = input('Enter "c" to create an issue, the issue number in the repository to update an issue, or "s" to stop: ')

        # User wants to create an issue
        if choice == 'c':
            print_input = input('Would you like to print all of the currently lodaded issues\' titles? ("y" for yes, anything else for no):')

            if print_input == "y":
                print("These are the titles of all loaded issues:")
                issues.print_issue_titles()

            flag = True
            while(flag):
                question = input('Enter the issue number to be created. (This issue\'s data will be the data used to create the new issue.) Enter "s" to stop the creation: ')
                if question == "s":
                    print("Cancelling issue creation.")
                    flag = False
                elif question.isdigit():
                    # Create the issue
                    link, number = create_issue(issues.issues_data[int(question) - 1], REPO_NAME, REPO_OWNER, PAT)

                    if link is None:
                        print("Issue could not be updated")
                    else:
                        print(f"Link to updated issue: {link}")

                    flag = False
                else:
                    print('Please enter a number or "n" to cancel')

        elif choice.isdigit():
            ISSUE_NUMBER = int(choice)

            print_input = input('Would you like to print all of the currently lodaded issues\' titles? ("y" for yes, anything else for no):')

            if print_input == "y":
                print("These are the titles of all loaded issues:")
                issues.print_issue_titles()

            flag = True
            while(flag):
                question = input('Enter the issue number with the correct issue information. (This issue\'s data will be the replacement data for the provided issue number) Enter "s" to stop the update:')

                if question == "s":
                    print(f"Cancelling update on issue {issue_num}")
                    flag = False
                elif question.isdigit():
                    # Update the issue
                    link = update_issue(issues.issues_data[int(question) - 1], REPO_NAME, REPO_OWNER, PAT, ISSUE_NUMBER)

                    if link is None:
                        print("\nIssue could not be updated")
                    else:
                        print(f"\nLink to updated issue: {link}")

                    flag = False
                else:
                    print('Please enter a number or "n" to cancel')

        elif choice == "s":
            print("Stopping requests")
            create_or_update = False
        else:
            print('Please enter "c", a number, or "s"')

run()
