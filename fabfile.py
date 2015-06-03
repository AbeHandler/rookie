'''
Fabric API for management tasks
'''

from fabric.api import local


def scripts():
    '''/scripts/'''

    local('git add rookie/static/js/search.js')


def datamanagement():
    '''/scripts/'''
    local('git add rookie/datamanagement/lensloader.py')
