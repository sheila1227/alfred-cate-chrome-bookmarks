import argparse
import sys
import codecs
import json
from workflow import Workflow, ICON_WARNING
from glob import glob
import ntpath
from os.path import expanduser, isfile

log = None

avatar_arr = [
    "avatar_generic.png",
	"avatar_generic_aqua.png",
	"avatar_generic_blue.png",
	"avatar_generic_green.png",
	"avatar_generic_orange.png",
	"avatar_generic_purple.png",
	"avatar_generic_red.png",
	"avatar_generic_yellow.png",
	"avatar_secret_agent.png",
	"avatar_superhero.png",
	"avatar_volley_ball.png",
	"avatar_businessman.png",
	"avatar_ninja.png",
	"avatar_alien.png",
	"avatar_awesome.png",
	"avatar_flower.png",
	"avatar_pizza.png",
	"avatar_soccer.png",
	"avatar_burger.png",
	"avatar_cat.png",
	"avatar_cupcake.png",
	"avatar_dog.png",
	"avatar_horse.png",
	"avatar_margarita.png",
	"avatar_note.png",
	"avatar_sun_cloud.png",
	"avatar_placeholder.png",
]

def getProfiles():
    profile_list = []
    chrome_dir = expanduser('~/Library/Application Support/Google/Chrome/')
    bookmark_files = glob(chrome_dir + '/*/Bookmarks')
    log.info('searching profiles in: %s', ', '.join(bookmark_files))
    for bookmarkFile in bookmark_files:
        profile_dir = ntpath.dirname(bookmarkFile)
        profile_info = buildProfileInfo(profile_dir)
        profile_list.append(profile_info)
    
    return profile_list

def buildProfileInfo(profile_dir):
    profile_dir_name = ntpath.basename(profile_dir)
    icon_file = profile_dir + '/Google Profile Picture.png'
    preferences_filename = profile_dir + "/Preferences"
    if isfile(preferences_filename):
        preferences_file = codecs.open(preferences_filename, encoding='utf-8')
        preferences_data = json.load(preferences_file)
        profile_name = preferences_data['profile']['name']
        if not isfile(icon_file):
            icon_file = getAvatarByIndex(preferences_data['profile']['local_avatar_index'])

    return {
        "name": profile_name,
        "dirName": profile_dir_name,
        "icon": icon_file
    }

def getAvatarByIndex(index):
    avatar_name = avatar_arr[index]
    chrome_dir = expanduser('~/Library/Application Support/Google/Chrome/')
    avatars_dir = chrome_dir + 'Avatars/'
    return avatars_dir + avatar_name

def search_key_for_profile(profile):
    elements = [profile['name'], profile['dirName']]
    return ' '.join(elements)

def main(wf):
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='?', default = None)
    args = parser.parse_args(wf.args)
    profile_list = wf.cached_data('chrome_profiles', getProfiles, max_age=300)
    query = args.query
    log.debug(query)
    
    if query:
        profile_list = wf.filter(query, profile_list, search_key_for_profile, min_score=20)
    
    if not profile_list:
        wf.add_item('No profiles found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0
    
    for profile in profile_list:
        wf.add_item(title=profile['name'],
                    subtitle=profile['dirName'],
                    arg=profile['dirName'],
                    valid=True,
                    icon=profile['icon'])
    
    wf.send_feedback()
    return 0

if __name__ == u'__main__':
    workflow = Workflow()
    log = workflow.logger
    sys.exit(workflow.run(main))
