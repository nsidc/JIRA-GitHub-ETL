import requests
import bs4
import json
import JIRAloading as JL

issues = JL.JIRALoader('../testJIRA.xml')
issues.issue_titles()
issues.issue_links()
issues.issue_description()

# print(len(issues.titles))
# print(len(issues.links))
# print(len(issues.descriptions))

issues_data = list()
for i, title in enumerate(issues.issue_titles()):
    issues_data.append((title, issues.links[i], issues.descriptions[i]))

# print(issues_data[0])
# print(type(issues_data[0]))
# description = issues.issue_description[0]

REPO_OWNER = 'iansincolorado'
REPO_NAME = 'pythonapis'

# Only way of authenticating at the current moment is with GitHub PAT tokens, which are deleted from your GitHub account if it is found in a public repository
PAT = ''

URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'

headers = {
    'Authorization': 'token ' + PAT
    # 'accept': 'application/vnd.github+json'
}

# data = {
    # 'title': title in the form of a sting
    # 'milestone' : milestone number
    # 'labels': list of labels
    # 'body': contents of the issue
    # 'assignees' : GH usernames to assign to this issue
# }

data = {
    'title': issues.titles[0],
    # 'milestone' : milestone number
    # 'labels': list of labels
    'body': issues.descriptions[0]
    # 'assignees' : GH usernames to assign to this issue
}
'''
# ****************************************************
# Use of try and exception handeling provided by GeeksForGeeks at https://www.geeksforgeeks.org/exception-handling-of-python-requests-module/
try:
    r = requests.post(URL, data=json.dumps(data), headers=headers, timeout=1)
    r.raise_for_status()
except requests.exceptions.HTTPError as errh:
    print("HTTP Error")
    print(errh.args[0])
except requests.exceptions.ReadTimeout as errrt:
    print("Time out")
except requests.exceptions.ConnectionError as conerr:
    print("Connection error")
except requests.exceptions.RequestException as errex:
    print("Exception request")
print("Post Success")
# ****************************************************
# print(r.headers)
print(r.status_code)
print(r.reason)

# print(r.json())
print()
print()

# Getting the new issue url; always after the /issues/
print(r.json()['url'])
'''

def upload_issue(issue, REPO_NAME, REPO_OWNER, PAT):
    URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
    headers = {
        'Authorization': 'token ' + PAT
        # 'accept': 'application/vnd.github+json'
    }

    issue_link = ''

    data = {
        'title': issue[0],
        'body': "JIRA Issue: " + issue[1] + "\n\n" + issue[2]
    }

# ****************************************************
# Use of try and exception handeling provided by GeeksForGeeks at https://www.geeksforgeeks.org/exception-handling-of-python-requests-module/
    try:
        r = requests.post(URL, data=json.dumps(data), headers=headers, timeout=1)
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])
    except requests.exceptions.ReadTimeout as errrt:
        print("Time out")
    except requests.exceptions.ConnectionError as conerr:
        print("Connection error")
    except requests.exceptions.RequestException as errex:
        print("Exception request")
    print("Upload Success")
# ****************************************************

    if r.ok:
        issue_link = r.json()["url"]
    else:
        issue_link = None

    return issue_link

for issue in issues_data[:5]:
    print(issue[0])
    print(issue[1])
    print()
#     print(upload_issue(issue, REPO_NAME, REPO_OWNER, PAT))
