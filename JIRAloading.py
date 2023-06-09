import bs4
import requests
import re

with open('../testJIRA.xml', 'r') as f:
    file = f.read()

soup = bs4.BeautifulSoup(file, 'xml')

# print(soup.rss.channel.find_all('item')[0].title.text)

# Getting all of the items, which are individual JIRA issues
issues = soup.rss.channel.find_all('item')

# print(type(issues))
# print(len(issues))

# Making a list of all of the titles
titles = list()
for issue in issues:
    titles.append(issue.title)

# print(len(titles))

# for title in titles[:5]:
#     print(title)

# Functions for getting the list of data for each field of an issue
def load_titles(issues):
    titles = list()
    for issue in issues:
        titles.append(issue.title)
    return titles

# Testing load_titles() with issues
# test = load_titles(issues)
# assert test == titles
# print(len(test))
# for title in test[:10]:
#     print(title.text)

# Getting the links to the original JIRA issues
def load_original_links(issues):
    links = list()
    for issue in issues:
        links.append(issue.link)
    return links

print(load_original_links(issues)[1].text)

def load_description_tags(issues):
    descriptions = list()
    for issue in issues:
        descriptions.append(issue.description)
    return descriptions

def load_description_text(descriptions):
    descriptions = list()
    for issue in issues:
        descriptions.append(re.sub(r'(<[/,\s,\w, ]*>)|(<a[\s,\w,/]*>)|(<a[\s,\w,/]*\n)', '', issue.description.text))
    return descriptions

def has_list(descriptions):
    list_bool = list()
    for desc in descriptions:
        if re.search('(<ol>)|(<li>)', desc.text) is not None:
            list_bool.append(1) 
        else:
            list_bool.append(0)
    return list_bool

# Testing 
test = load_description_tags(issues)
print(len(test))
test_lists = has_list(test)
    
print(has_list(test)[1])
# list_removal_test = test[1].text
# print(list_removal_test)

def remove_list(lists):
    removed_list = lists.copy()  
    for i,list in enumerate(lists):
        search_1 = re.search(r'(<ol>)|(<ul>)', list.text)
        search_2 = re.search(r'(</ol>)|(/<ul>)', list.text)
        if (search_1 is None or search_2 is None):
            continue

        start_1, end_1 = search_1.span()
        start_2, end_2 = search_2.span()
        list_removed = list_removal_test[:start_1] + list_removal_test[end_2:]
        removed_list[i] = list_removed

    return removed_list

# removed_lists = remove_list(test)
# print(removed_lists[1])

# Extracting the list (with tags) from descriptions
def find_lists_in_descriptions(descriptions):
    found_lists = descriptions.copy()  
    for i,list in enumerate(descriptions):
        search_1 = re.search(r'(<ol>)|(<ul>)', list.text)
        search_2 = re.search(r'(</ol>)|(/<ul>)', list.text)
        if (search_1 is None or search_2 is None):
            found_lists[i] = None
            continue

        start_1, end_1 = search_1.span()
        start_2, end_2 = search_2.span()
        list_removed = list_removal_test[start_1:end_2]
        found_lists[i] = list_removed

    return found_lists

# found_lists = find_lists_in_descriptions(test)
# print(found_lists[1])

# Returns a list with the number of lists for each issue description
def multiple_lists(descriptions):
    mult_lists = list()
    for i,desc in enumerate(descriptions):
        search_1 = re.findall(r'(<ol>)|(<ul>)', desc.text)
        mult_lists.append(len(search_1))

    return mult_lists

# for desc in multiple_lists(test):
#     print(desc)
