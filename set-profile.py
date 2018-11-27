import argparse
import sys
from workflow import Workflow
from workflow.notify import notify

log = None

def main(wf):
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)
    query = args.query
    log.debug(query)

    if not query:
        notify('Warning', 'No profile selected')
        return 1

    wf.settings['selected_chrome_profile'] = query
    notify('Success', query + ' selected')

if __name__ == u'__main__':
    workflow = Workflow()
    log = workflow.logger
    sys.exit(workflow.run(main))