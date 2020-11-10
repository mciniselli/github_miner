import requests

from datetime import datetime, timezone
import time

import json

import os

from utils.inputoutput import *

output_dir = "output_files"


class Commit(object):
    def __init__(self, hash, repository, message, author, api_url, created_at):
        self.hash = hash
        self.repository = repository
        self.message = message
        self.author = author
        self.api_url = api_url
        self.created_at = created_at


class Repository:
    def __init__(self, repo_full_name):
        self.repo_name = repo_full_name
        if not os.path.isdir('temp'):
            os.makedirs('temp')
        self.repo_dir = os.path.join(os.getcwd(), 'temp', self.repo_name.replace('/', '_'))

    def is_commit_ok(self, data):

        parents = data["parents"]

        modifications = ""

        if len(parents) > 1:
            return False, modifications

        num_java_files = 0

        for file in data['files']:
            filename = file["filename"]

            if filename.endswith(".java"):

                num_java_files += 1

                if file["status"] != "modified":
                    return False, modifications
                if file["additions"] > 4:
                    return False, modifications
                else:
                    modifications += str(file["additions"]) + " "
                if file["deletions"] > 4:
                    return False, modifications
                else:
                    modifications += str(file["additions"])

        if num_java_files != 1:
            return False, modifications

        return True, modifications

    def wait_if_requests_finished(self, response_header):

        # print(response_header["X-RateLimit-Remaining"])

        if int(response_header["X-RateLimit-Remaining"]) != 0:
            return

        ts = int(response_header["X-RateLimit-Reset"])

        date_end = datetime.utcfromtimestamp(ts)

        date_now = datetime.now(timezone.utc)

        date_now_notz = date_now.replace(tzinfo=None)
        date_end_notz = date_end.replace(tzinfo=None)

        num_sec_to_wait = (date_end_notz - date_now_notz).total_seconds()

        settings.logger.info(
            "SEC TO WAIT {} REMAINING REQUESTS {}".format(num_sec_to_wait, response_header["X-RateLimit-Remaining"]))

        time.sleep(num_sec_to_wait + 10)

    def store_before_after_file(self, id_commit, repo, date_commit, tot_processed, URL, after_api, before_api, message,
                                file_path, id_internal, modifications):

        data = {}
        data["id_internal"] = id_internal
        data["tot_processed"] = tot_processed
        data["id_commit"] = id_commit
        data["repo"] = repo
        data["date_commit"] = date_commit
        data["before_api"] = before_api
        data["after_api"] = after_api
        data["URL"] = URL
        data["message"] = message
        data["file_path"] = file_path
        data["modifications"] = modifications

        with open(settings.result_name, 'a+') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')

    def miner(self, fix_commit, repository, tot_processed, gh_name, id_internal, id_row):

        api_token = "your api token"  # local

        headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'Authorization': 'token %s' % api_token
        }

        # # OK COMMIT
        # commit_id = "bebd9d9517377c76dfc16b185bf639f35e7c8b57"
        # URL = "https://api.github.com/repos/mciniselli/test/commits/{}".format(commit_id)

        commit_id = fix_commit.hash
        URL = "https://api.github.com/repos/{}/commits/{}".format(repository, commit_id)

        # KO COMMIT
        # commit_id = "d4be82b0f71405bfd8e17e6fd4b0f2c05010a3ff"
        # URL = "https://api.github.com/repos/dragonGR/frameworks_base/commits/{}".format(commit_id)

        # # KO COMMIT
        # commit_id = "6a462d25b435496bbdd834e604e22dfbe57b25a3"
        # URL = "https://api.github.com/repos/mciniselli/test/commits/{}".format(commit_id)
        #
        # # KO COMMIT
        # commit_id = "2bcb7749d3ca42ab28d368f4f2e4ef0eeaa45bfd"
        # URL = "https://api.github.com/repos/mciniselli/test/commits/{}".format(commit_id)

        response = requests.get(url=URL, headers=headers)

        # extracting data in json format
        data = response.json()

        response_header = response.headers

        self.wait_if_requests_finished(response_header)

        if response.status_code != 200:
            settings.logger.error("ERRROR {}".format(response))
            return

        is_ok, modifications = self.is_commit_ok(data)

        if is_ok == False:  # only one java file modified with less than 4 additions and insertions
            return

        java_files = list()
        java_files_url = list()
        java_parent = list()

        for file in data['files']:
            filename = file["filename"]
            if filename.endswith(".java"):
                parents = data["parents"]

                sha_previous = parents[0]["sha"]

                java_files.append(file)
                java_files_url.append(file["raw_url"])
                java_parent.append(file["raw_url"].replace(commit_id, sha_previous))

        after = requests.get(java_files_url[0])
        before = requests.get(java_parent[0])

        if before.status_code != 200 or after.status_code != 200:
            settings.logger.error("ERROR")
            return

        code_before = (before.content).decode("utf-8")
        code_after = (after.content).decode("utf-8")

        self.store_before_after_file(commit_id, repository, str(fix_commit.created_at)[:19], tot_processed, URL,
                                     java_files_url[0], java_parent[0], fix_commit.message, gh_name, id_internal,
                                     modifications)

        WriteFile("{}/{}_before.txt".format(output_dir, id_internal), [code_before])
        WriteFile("{}/{}_after.txt".format(output_dir, id_internal), [code_after])
