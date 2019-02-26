# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import argparse
import json
import sys
import getpass
import textwrap

import requests

from collections import OrderedDict


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', dest='project', default="LQSAM", help='Project key to check for version')
    parser.add_argument('-v', '--version', dest='version', default="0.8.0", help='Version to check')
    return parser.parse_args()


class JiraSearch(object):
    __base_url = None
    __headers = None

    def __init__(self):
        self.__base_url = 'https://healthq.atlassian.net/rest/api/latest/'
        self.__headers = {
            "Accept": "application/json",
            "Authorization": "Basic d3luYW5kQGhlYWx0aHF0ZWNoLmNvbTp4MHVFaTRxSEdBWFRZeDQwOHRrRkM4NUM=",
            "Content-Type": "application/json"
        }
        self.fields = ','.join(['key', 'summary', 'status', 'issuetype', 'issuelinks', 'subtasks', 'fixVersions'])

    def get(self, uri, params={}):
        url = self.__base_url + uri

        response = requests.request(
            "GET",
            url,
            params=params,
            headers=self.__headers
        )
        response.raise_for_status()
        return response.json()

    def get_issue(self, key):
        # we need to expand subtasks and links since that's what we care about here.
        return self.get('/issue/%s' % key, params={'fields': self.fields})


def main(args):
    jira = JiraSearch()

    jql = 'project = %s and fixVersion in (%s)' % (args.project, args.version)

    response = jira.get("search", params={'jql': jql})

    issues = response["issues"]

    print 'Version %s in %s' % (args.version, args.project)

    for issue in issues:
        # print issue["key"]
        response = jira.get_issue(issue["key"])
        if 'issuelinks' in response["fields"]:
            for other_link in response["fields"]['issuelinks']:
                if 'outwardIssue' in other_link:
                    print "%s" % (other_link["type"]["outward"])
                    other_issue = jira.get_issue(other_link["outwardIssue"]["key"])
                    print "versions"
                    for version in other_issue["fields"]["fixVersions"]:
                        full_version = jira.get('version/%s' % version["id"])
                        other_project = jira.get('project/%s' % full_version["projectId"])
                        print "%s in project %s" % (version["name"], other_project["key"])
                elif 'inwardIssue' in other_link:
                    print "%s" % (other_link["type"]["inward"])
                    other_issue = jira.get_issue(other_link["inwardIssue"]["key"])
                    print "versions"
                    for version in other_issue["fields"]["fixVersions"]:
                        full_version = jira.get('version/%s' % version["id"])
                        other_project = jira.get('project/%s' % full_version["projectId"])
                        print "%s in project %s" % (version["name"], other_project["key"])


if __name__ == '__main__':
    options = parse_args()
    main(options)
