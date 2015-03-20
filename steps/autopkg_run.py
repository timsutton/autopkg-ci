#!/usr/bin/python

import os
import plistlib
import shutil
import subprocess
import sys

from pprint import pprint
from tempfile import mkdtemp, mkstemp


def get_version(report_plist):
    for new_list in ['munki_importer_summary_result', 'pkg_creator_summary_result']:
        if report_plist['summary_results'].get(new_list):
            for item in report_plist['summary_results'][new_list]['data_rows']:
                if 'version' in item.keys():
                    return item['version']
    return None


def main():
    workspace = os.environ['WORKSPACE']
    # Git
    if 'GIT' in os.environ.keys():
        git_path = os.environ['GIT']
    else:
        git_path = '/usr/bin/git'

    checkout_dir = os.path.join(workspace, 'autopkg-recipes')

    # the Jenkins job will have already written out this job's recipe to this file
    recipe_list_file = os.path.join(workspace, 'recipe.txt')
    if not os.path.exists(recipe_list_file):
        sys.exit("Missing expected recipe list file at %s" % recipe_list_file)

    # this string is used by the Description Setter plugin to set a description of
    # the build which we're repurposing to contain the version number
    version_out_string = "PARSED_VERSION"

    # check out recipes
    if os.path.exists(checkout_dir):
        shutil.rmtree(checkout_dir)
    subprocess.call([git_path, 'clone', 'https://github.com/autopkg/recipes', checkout_dir])

    # make temp report plist
    report_file = mkstemp()[1]

    # make fake Munki repo
    munki_repo_path = '/private/tmp/autopkg-ci-munki-repo'
    if not os.path.isdir(munki_repo_path):
        os.mkdir(munki_repo_path)

    # run autopkg
    autopkg_cmd = [
    os.path.join(workspace, 'Code/autopkg'),
    'run',
    '--report-plist', report_file,
    '--search-dir', checkout_dir,
    '-k', 'MUNKI_REPO=%s' % munki_repo_path,
    '--recipe-list', recipe_list_file
    ]

    p = subprocess.Popen(autopkg_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env={'LANG': 'en_US.UTF-8'})
    out, err = p.communicate()
    if err:
        print >> sys.stderr, err

    try:
        report_plist = plistlib.readPlist(report_file)
    except:
        sys.exit("Couldn't parse a valid report plist!")
    pprint(report_plist['summary_results'])

    # print out our version info for the Build Description Setter
    version = get_version(report_plist)
    if not version:
        version = 'N/A'
    print "%s %s" % (version_out_string, version)

    # clean up
    for stuff in [checkout_dir]:
        shutil.rmtree(stuff)
    os.remove(report_file)

    # output our failure data
    if report_plist['failures']:
        for fail in report_plist['failures']:
            print >> sys.stderr, "Failure for recipe %s:" % fail['recipe']
            print >> sys.stderr, fail['message']
        sys.exit(1)


if __name__ == '__main__':
    main()
