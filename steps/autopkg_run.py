#!/usr/bin/python

import os
import plistlib
import shutil
import subprocess
import sys

from tempfile import mkdtemp

# temp dirs
tmp_cache, tmp_munki_repo = mkdtemp(), mkdtemp()

# Git
if 'GIT' in os.environ.keys():
    git_path = os.environ['GIT']
else:
    git_path = '/usr/bin/git'

checkout_dir = 'autopkg-recipes'

# the Jenkins job will have already written out this job's recipe to this file
recipe_list_file = os.path.join(os.environ['WORKSPACE'], 'recipe.txt')
if not os.path.exists(recipe_list_file):
    sys.exit("Missing expected recipe list file at %s" % recipe_list_file)

# this string is used by the Description Setter plugin to set a description of
# the build which we're repurposing to contain the version number
version_out_string = "PARSED_VERSION"

def get_version(report_plist):
    for new_list in ['new_imports', 'new_packages']:
        if report_plist[new_list]:
            for item in report_plist[new_list]:
                if 'version' in item.keys():
                    return item['version']
    return None

def main():

    # check out recipes
    if os.path.exists(checkout_dir):
        shutil.rmtree(checkout_dir)
    subprocess.call([git_path, 'clone', 'https://github.com/autopkg/recipes', checkout_dir])

    # run autopkg
    autopkg_cmd = [
    'Code/autopkg',
    'run',
    '--report-plist',
    '--search-dir', checkout_dir,
    '-k', 'CACHE_DIR=%s' % tmp_cache,
    '-k', 'MUNKI_REPO=%s' % tmp_munki_repo,
    '--recipe-list', recipe_list_file
    ]

    p = subprocess.Popen(autopkg_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env={'LANG': 'en_US.UTF-8'})
    out, err = p.communicate()
    try:
        report_plist = plistlib.readPlistFromString(out)
    except:
        print >> sys.stderr, out
        sys.exit("Couldn't parse a valid report plist!")

    # print out our version info
    version = get_version(report_plist)
    if not version:
        version = 'N/A'
    print "%s %s" % (version_out_string, version)

    # clean up
    for stuff in [tmp_cache, tmp_munki_repo, checkout_dir]:
        shutil.rmtree(stuff)

if __name__ == '__main__':
    main()

