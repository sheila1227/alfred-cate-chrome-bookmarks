import argparse
import sys
import codecs
import json
import ntpath
from workflow import Workflow, ICON_WARNING
from workflow.notify import notify
from os.path import expanduser, isfile
from profiles import buildProfileInfo
from utils.search import *

log = None

def getFlattenedBookmarks(bookmarkObj, parent, results):
    log.debug('*************************')
    log.debug(bookmarkObj)
    if bookmarkObj['type'] == 'url':
        results.append({
            "url": bookmarkObj['url'],
            "folder": parent['name'],
            "name": bookmarkObj['name']
        })
    elif bookmarkObj['type'] == 'folder':
        for child in bookmarkObj['children']:
            getFlattenedBookmarks(child, bookmarkObj, results)

def getBookmarksArr(roots):
    flattened_bookmarks = []
    for key in roots:
        if 'type' in roots[key]:
            getFlattenedBookmarks(roots[key], {}, flattened_bookmarks)

    
    log.debug(flattened_bookmarks)
    return flattened_bookmarks

def getBookmarksData(profileDir):
    bookmarks_file_name = profileDir + "/Bookmarks"
    if isfile(bookmarks_file_name):
        log.info('Bookmark file: %s', bookmarks_file_name)
        bookmarks_file = codecs.open(bookmarks_file_name)
        bookmarks_data = json.load(bookmarks_file)
        roots = bookmarks_data['roots']
        return getBookmarksArr(roots)

    return []

def search_key_for_bookmark(bookmark):
    elements = [bookmark['name'], bookmark['url']]
    return u' '.join(elements)

def search_key_for_bookmark_cate(bookmark):
    elements = [bookmark['folder'], bookmark['name'], bookmark['url']]
    return u' '.join(elements)

def getFilteredBookmarks(bookMarkSearchKey, folderSearchKey, rawData):
    log.debug('bookMarkSearchKey: %s', bookMarkSearchKey)
    log.debug('folderSearchKey: %s', folderSearchKey)
    def bookmarkFilter(bookmark):
        folder = bookmark['folder']
        name = bookmark['name']
        url = bookmark['url']
        nameOrUrlMatched = strContainedInTarget(bookMarkSearchKey, name) or strContainedInTarget(bookMarkSearchKey, url)
        log.debug('nameOrUrlMatched: %s', nameOrUrlMatched)
        if folderSearchKey:
            return charsContainedInTarget(folderSearchKey, folder) and nameOrUrlMatched
        else:
            return nameOrUrlMatched

    return filter(bookmarkFilter, rawData)


def main(wf):
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)
    query = args.query
    log.debug(query)
    selected_profile_dir = wf.settings['selected_chrome_profile']
    profile_dir = expanduser("~/Library/Application Support/Google/Chrome/%s" % selected_profile_dir)
    bookmarks_data = getBookmarksData(profile_dir)
    folderSearchKey = None
    bookMarkSearchKey = None
    params = []
    if query:
        params = query.split(':')
        # folder param passed in
        if len(params) == 2:
            folderSearchKey = params[0]
            bookMarkSearchKey= params[1]
        else:
            bookMarkSearchKey = params[0]
        
        bookmarks_data = getFilteredBookmarks(bookMarkSearchKey, folderSearchKey, bookmarks_data)

    if not len(bookmarks_data):
        wf.add_item('No bookmarks found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    profile_info = buildProfileInfo(profile_dir)
    icon = profile_info['icon']

    for bookmark in bookmarks_data:
        wf.add_item(title=bookmark['name'],
                    subtitle=bookmark['folder'] + ': ' + bookmark['url'],
                    arg=bookmark['url'],
                    valid=True,
                    icon=icon)
        
    wf.send_feedback()
    return 0

if __name__ == u'__main__':
    workflow = Workflow()
    log = workflow.logger
    sys.exit(workflow.run(main))