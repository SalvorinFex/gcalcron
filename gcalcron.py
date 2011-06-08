#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    gcalcron v0.1
#
#    Copyright Patrick Spear 2008
#    patrick@pfspear.net
#    www.pfspear.net
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    For additional information, please see the README file distributed
#    with this script or visit www.pfspear.net/projects/gcalcron.


__author__ = 'Patrick Spear  |  patrick@pfspear.net  |  www.pfspear.net'


try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import getopt
import sys
import string
import time
import datetime
import os


class CronCal:

  def __init__(self, user, pw, verbose):

    self.cal_client = gdata.calendar.service.CalendarService()
    self.cal_client.email = user
    self.cal_client.password = pw
    self.cal_client.source = 'gcalCron Interpreter 0.1'
    if verbose: print 'Logging in user %s' % user
    self.cal_client.ProgrammaticLogin()
    if verbose: print 'User logged in successfully'


  def Run(self, calId, delimter='---', path='', execute=True, verbose=False, override=''):

    start_date = datetime.datetime.now()
    end_date = start_date + datetime.timedelta(1);


    # Query the automation calendar.
    if verbose: print 'Setting up query: %s to %s' % (start_date, end_date,)
    query = gdata.calendar.service.CalendarEventQuery(calId, 'private', 'full')
    query.start_min = start_date.isoformat()
    query.start_max = end_date.isoformat()
    if verbose: print 'Submitting query'
    feed = self.cal_client.CalendarQuery(query)
    if verbose: print 'Query results received'


    # Iterate through events to find those that begin or end at current time.
    
    if (override == ''):
      hr = start_date.hour
      if (hr < 10): hr = '0%s' % (start_date.hour)
      mn = start_date.minute
      if (mn == 0): mn = '00'
      current_time = '%s:%s' % (hr, mn)
    else:
      current_time = override

    if verbose: print 'Looking for events matching current time %s' % current_time
    commands = []

    for i, event in zip(xrange(len(feed.entry)), feed.entry):
      for when in event.when:
	#Split event description into commands at start and end of event.
	command_text = event.content.text.partition("---\n")
	
	# If event ends now, add event end commands to list of commands to be executed. 
	if (when.end_time[11:16] == current_time):
	  if verbose: print 'Event: %s- Endtime match' % event.title.text
	  commands.extend(command_text[2].splitlines())

	# If event starts now, add event start commands to list of commands to be executed.
	if (when.start_time[11:16] == current_time):
	  if verbose: print 'Event: %s- Starttime match' % event.title.text
	  commands.extend(command_text[0].splitlines())

    # Execute the commands parsed.
    for command in commands:
      if verbose: print 'Excuting: %s' % (path + command)
      if execute: os.system(path + command)
 


def usage():
  print """
gcalcron : use Google Calendar as a frontend for cron-like functionality

  gcalcron.py [-h] -u <username> -p <password> -c <automation cal ID> [-d <delimiter>] [-t path] [-v] [-s] [o <time string>]

 -h                  help (print this message)
 
 -u <username>       Google account username 
 -p <password>       Google account password
 -c <cal ID>         Calendar ID for automation calendar
 -d <delimiter>      override characters to delimit start & end commands
 -t <path>           path prefix for commands
 -v 	             verbose
 -s                  safe mode: do not execute commands
 -o <time string>    override system time (for testing purposes)

"""

 
def main():

  print sys.argv[1:]

  try:
    o, a = getopt.getopt(sys.argv[1:], 'hu:p:c:d:t:vso:')
  except getopt.error, msg:
    print 'gcalcron.py [-h] -u <username> -p <password> -c <automation cal ID> [-d <delimiter>] [-t path] [-v] [-s]'
    sys.exit(2)

  user = ''
  pw = ''
  calId = ''
  delimiter = '---'
  path = ''
  verbose = False
  execute = True
  override = ''

  # Process options
  opts = {}
  for k, v in o:
    opts[k] = v
  
  if opts.has_key('-h'): usage(); sys.exit(0)
  if opts.has_key('-u'): user      = opts['-u']
  if opts.has_key('-p'): pw        = opts['-p']
  if opts.has_key('-c'): calId     = opts['-c']
  if opts.has_key('-d'): delimiter = opts['-d']
  if opts.has_key('-t'): path      = opts['-t']
  if opts.has_key('-v'): verbose   = True
  if opts.has_key('-s'): execute   = False  
  if opts.has_key('-o'): override  = opts['-o'] 

  if user == '' or pw == '' or calId == '':
    print 'gcalcron.py -u <username> -p <password> -c <automation cal ID> [-d <delimiter>] [-v] [-s]'
    sys.exit(2)

  # Create automation object and run it.
  automation = CronCal(user, pw, verbose)
  automation.Run(calId, delimiter, path, execute, verbose, override)

if __name__ == '__main__':
  main()
