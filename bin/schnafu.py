#!/opt/splunk/bin/python
# Copyright (C) 2021 MuS
# http://answers.splunk.com/users/2122/mus

# enable / disable logger debug output
myDebug = 'no'

# Changelog

# import some Python moduls
import splunk
import sys
import os
import splunk.Intersplunk
import re
import logging
import collections
import splunk.rest as rest
from optparse import OptionParser


# get SPLUNK_HOME form OS
SPLUNK_HOME = os.environ['SPLUNK_HOME']

# get myScript name and path
myScript = os.path.basename(__file__)
myPath = os.path.dirname(os.path.realpath(__file__))

# define the logger to write into log file
def setup_logging(n):
    logger = logging.getLogger(n)
    if myDebug == 'yes':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(
        SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = '%s.log' % myScript
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
    LOGGING_FORMAT = '%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s'
    splunk_log_handler = logging.handlers.RotatingFileHandler(
        os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a')
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE,
                             LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger

# print message to log and Splunk
def print_msg(str):
    # setting up empty output list
    myList = []
    endpointresult = {}  # set empty result dict
    endpointresult['Action'] = str  # set result endpoint
    od = collections.OrderedDict(sorted(endpointresult.items()))  # sort the list
    myList.append(od)  # append the ordered results to the list
    logger.info('%s' % str)
    splunk.Intersplunk.outputResults(myList)  # output the result to splunk

# start the logger only if needed
logger = setup_logging('logger started ...')

# starting the main
logger.info('starting the main task ...')

# getting the sessionKey, owner, namespace
results, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
results = []  # we don't care about incoming results
logger.info('setting: %s ' % settings)
sessionKey = settings.get('sessionKey', None)  # getting session key but will not log!
owner = settings.get('owner', None)  # getting user / owner
logger.info('using owner: %s ' % owner)
namespace = settings.get('namespace', None)  # getting namespace
logger.info('using namespace: %s ' % namespace)

# get key value pairs from user search
if len(sys.argv) == 1:
    logger.info('argv len: %s ...' % len(sys.argv))
    print_msg('Nothing to see here! Move along ...')
    sys.exit()

# check what function is called
if sys.argv[1].lower() == 'dc':
    logger.info('argv is dc ...')
    logger.info('argv len: %s ...' % len(sys.argv))
    if len(sys.argv) == 2:
        print_msg('Needs more arguments, check the command ...')
        sys.exit()
    host = sys.argv[2]
    print_msg('adding host %s as deployment client ...' % host)
    os.system('/opt/splunk/bin/splunk set deploy-poll 172.18.0.9:8089 -uri https://%s:8089 -auth admin:hello1234 >/dev/null 2>&1' % host)
    sys.exit()

# check what function is called
if sys.argv[1].lower() == 'fwd':
    logger.info('argv is fwd ...')
    logger.info('argv len: %s ...' % len(sys.argv))
    if len(sys.argv) == 2:
        print_msg('Needs more arguments, check the command ...')
        sys.exit()
    host = sys.argv[2]
    print_msg('adding host %s as fwd client ...' % host)
    os.system('/opt/splunk/bin/splunk add forward-server "STLIDX01:9997" -uri https://%s:8089 -auth admin:hello1234 >/dev/null 2>&1' % host)
    os.system('/opt/splunk/bin/splunk add forward-server "STLIDX02:9997" -uri https://%s:8089 -auth admin:hello1234 >/dev/null 2>&1' % host)
    os.system('/opt/splunk/bin/splunk add forward-server "STLIDX03:9997" -uri https://%s:8089 -auth admin:hello1234 >/dev/null 2>&1' % host)
    sys.exit()

# reload deployment server
elif sys.argv[1].lower() == 'ds':
    logger.info('argv is ds ...')
    logger.info('argv len: %s ...' % len(sys.argv))
    if len(sys.argv) == 2:
        print_msg('Needs more arguments, check the command ...')
        sys.exit()
    if sys.argv[2].lower() == 'reload':
        print_msg('reloading deployment server ...')
        target = '/servicesNS/-/-/admin/deploymentserver/_reload'
        logger.info('reloading the %s endpoints now ...' % target)
        # get rest response and content
        response, content = rest.simpleRequest(target, sessionKey=sessionKey, method='POST')
        logger.info('reloading response :  %s ...' % response)
        sys.exit()
    else:
        print_msg('not implementated yet ...')
        sys.exit()

# do indexer stuff
elif sys.argv[1].lower() == 'idx':
    logger.info('argv is idx ...')
    logger.info('argv len: %s ...' % len(sys.argv))
    if len(sys.argv) == 2:
        print_msg('Needs more arguments, check the command ...')
        sys.exit()
    if sys.argv[2].lower() == 'restart':
        print_msg('restarting HWF cluster ...')
        os.system('/opt/splunk/bin/splunk rolling-restart cluster-peers -site-order site1 -auth admin:hello1234 >/dev/null 2>&1')
        sys.exit()
    elif sys.argv[2].lower() == 'add':
        if len(sys.argv) == 3:
            print_msg('Needs more arguments, check the command ...')
            sys.exit()
        print_msg('adding index ...')
        os.system('/opt/splunk/bin/splunk add index %s -auth admin:hello1234 >/dev/null 2>&1' % sys.argv[3])
        sys.exit()
    elif sys.argv[2].lower() == 'apply':
        print_msg('apply cluster bundle ...')
        target = '/services/cluster/master/control/default/apply'
        logger.info('reloading the %s endpoints now ...' % target)
        # get rest response and content
        response, content = rest.simpleRequest(target, sessionKey=sessionKey, method='POST')
        logger.info('reloading response :  %s ...' % response)
        sys.exit()
    else:
        print_msg('not implementated yet ...')
        sys.exit()

# unknown argument provided
else:
    print_msg('doing nothing unknown argument provided ...')
    sys.exit()
# end message
logger.info('done with the work ...')
