#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
A tool for synchronizing a master google calendar to several
user calendars. 
"""

__author__ = 'Markus Koskinen (markus.koskinen@futurice.com)'
__copyright__ = 'Copyright (c) 2013 Futurice Oy'
__license__ = 'Apache License 2.0'

import os
import sys

import CES_db
import CES_calendar
import CES_serviceaccount_googleservice
import CES_group

from CES_util import *
from local_settings import *
from optparse import OptionParser

global CMD_OPTIONS
parser = OptionParser(usage="Usage: %prog [options]")
parser.add_option("-s", "--simulate",
                  action="store_true",
                  dest="simulate_only",
                  default=False,
                  help="Simulate only. Do not do any writes or updates.")
    
CMD_OPTIONS, _ = parser.parse_args()

def main(argv):
    init_logging()

    if CMD_OPTIONS.simulate_only:
        logging.info("Simulate switch is enabled. Will not do writes.")

    CES_db.init_db()
    logging.info("Creating admin google services ...")
    calendar_service = CES_serviceaccount_googleservice.createCalendarService() 
    directory_service = CES_serviceaccount_googleservice.createDirectoryService()

    logging.info("Populating list of all groups ...")
    CES_group.init_groups(directory_service)

    logging.info("Done. Sizeof all groups: %s" % len(CES_group.ALL_GROUPS))
    logging.debug("All groups: %s" % CES_group.ALL_GROUPS)

    logging.info("Fetching all master events ...")
    master_events = CES_calendar.get_master_events(calendar_service)
    logging.info("Done. Sizeof all master events: %d" % len(master_events))

    logging.debug("Master events:\n%s" % pp.pformat(master_events))

    logging.info("Creating CES events ...")
    tmplist = master_events
    mevent_list = [mevent for mevent in tmplist if not "recurringEventId" in mevent]
    logging.info("* Cropped %d recurring events from list." % (len(tmplist) - len(mevent_list)))
    tmplist = mevent_list
    mevent_list = [mevent for mevent in mevent_list if "description" in mevent]
    logging.info("* Cropped %d descriptionless events from list." % (len(tmplist) - len(mevent_list)))

    ces_events = [CES_calendar.cesEvent(mevent) for mevent in mevent_list]
    logging.info("Done. Sizeof CES events: %d" % len(ces_events))

    logging.info("Applying CES events to calendars ...")
    for ces_event in ces_events:
        ces_event.apply_to_calendars(calendar_service, directory_service)

    logging.info("All done.")

if __name__ == '__main__':
  main(sys.argv)
