#! /bin/bash
#
#    gcalcron v0.1 Installer Script
#
#    Copyright Patrick Spear 2008
#    patrick@pfspear.net
#    www.pfspear.net
#
#    Please note: this is dumb script that will probably
#    work/meet the needs of 90% of people, but if any part
#    fails, you will have to install manually.  It will 
#    also probably only work on Debian-based systems,
#
#    Please see gcalcron.py, README, or COPYING for
#    more information.


# Make sure we are root
EXECUTER=`whoami`
if [ ! "$EXECUTER" == "root" ]; then
  echo "Run this script as root."
  exit 0
fi

# Ensure python is up to date
if [ $1 == "install" ]; then

  # Get parameters
  echo "Google account username: "
  read USER

  echo "Password for that account: "
  read -s PW

  echo "Confirm password: "
  read -s PW2

  if [ $PW != $PW2 ]; then
    echo "Passwords do not match- aborting."
    exit 0
  fi

  echo "ID for your automation calendar: "
  read CALID

  apt-get install python

  # Install Google API
  wget http://gdata-python-client.googlecode.com/files/gdata.py-1.2.1.tar.gz
  tar -xvf gdata.py-1.2.1.tar.gz
  cd gdata.py-1.2.1
  python setup.py install
  cd ..
  rm -rf gdata.py-1.2.1 gdata.py-1.2.1.tar.gz

  # Install script
  cp -fv gcalcron.py /usr/bin
  chmod +x gcalcron.py

  # Set up cron job
  echo "# This cron job lets gcalcron check Google Calendars every so often to do its thing." > /etc/cron.d/gcalcron
  echo "# SHELL /usr/bin/python" > /etc/cron.d/gcalcron
  echo "*/30 * * * * root gcalcron.py -u $USER -p $PW -c $CALID" >> /etc/cron.d/gcalcron

  echo "gcalcron v0.1 installed."
  exit 0
fi

echo "Usage: setup.sh install
See README for more information."

exit 0
