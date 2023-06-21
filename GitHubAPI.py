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
def upload_issue(issue, REPO_NAME, REPO_OWNER, PAT):
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


# Testing
issues = JL.JIRALoader('../testJIRA.xml')

# Getting the issues loaded into the JIRALoader object
issues.get_issue_data()

REPO_OWNER = 'iansincolorado'
REPO_NAME = 'pythonapis'

# Only way of authenticating at the current moment is with GitHub PAT tokens, which are deleted from your GitHub account if it is found in a public repository
PAT = ''

ISSUE_NUMBER = '45'
print(len(issues.issues_data))
test_issue = issues.issues_data[4] 
# link = upload_issue(test_issue, REPO_NAME, REPO_OWNER, PAT)
link = update_issue(test_issue, REPO_NAME, REPO_OWNER, PAT, ISSUE_NUMBER)
# print(link)
