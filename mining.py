from utils.settings import *
import os
from dateutil.parser import isoparse
import traceback
import json
from model import Repository, Commit

from utils.settings import init_global
import utils.settings as settings
from utils.progress import get_progress_value, read_progress_file, update_progress_bar

data_path = 'raw_data'

fix_words = ['fix', 'solve']
bug_words = ['bug', 'issue', 'problem', 'error']

# (“fix” or “solve”) and (“bug” or “issue” or “problem” or “error”)
def is_bugfix_commit(message):
    return ('Merge' not in message) and any(w in message for w in fix_words) and any(w in message for w in bug_words)

def extract_data(fix_commit, num_processed, file_name, id_internal, id_row):
    try:
        repo = Repository(fix_commit.repository)
        repo.miner(fix_commit, fix_commit.repository, num_processed, file_name, id_internal, id_row)

    except Exception as e:
        settings.logger.error(f'exception: {type(e).__name__} {e.args}')
        settings.logger.error(traceback.format_exc())

def main(file_names):
    settings.logger.info('files count:'.format(len(file_names)))

    if os.path.exists("result") == False:
        os.makedirs("result")

    tot_processed = 0
    tot = len(file_names)
    for i, file_name in enumerate(file_names):
        settings.logger.info(f'{file_name} # {str(i + 1)} of {tot}')
        try:
            with open(os.path.join(data_path, file_name)) as f:

                index_start = get_progress_value(file_name)
                settings.logger.info("INDEX START: {}".format(index_start))

                for i, line in enumerate(f):

                    if i <= index_start:
                        continue

                    data = json.loads(line)

                    tot_processed += 1

                    settings.logger.info("Processing repo {} {}".format(data["repo"], tot_processed))

                    extract_data(Commit(
                        hash=data['sha'],
                        repository=data['repo'],
                        message=data['message'],
                        author=data['author'],
                        api_url=data['api'],
                        created_at=isoparse(data['created_at'])
                    ), i + 1, data['filename'], data['id'], i)

                    # update progress bar
                    update_progress_bar(file_name, i)

                settings.logger.info(f'total processed commits: {tot_processed}')
        except Exception as file_error:
            settings.logger.error(f'file exception: {type(file_error).__name__} {file_error.args}')
            print(traceback.format_exc())

    print('+++ DONE +++')

if __name__ == "__main__":
    init_global()

    file_names = [f for f in os.listdir(data_path) if f.endswith('.txt')]

    settings.file_list = file_names

    read_progress_file()
    main(file_names)
