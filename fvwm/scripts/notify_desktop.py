#!/usr/bin/python3

"""
Notify or show a message box on the desktop. Can be extended via its library, has much functionality.
This tool only uses the defaults. It's a work in progress.
"""

import sys
import gi

gi.require_version('Notify', '0.7')
from gi.repository import Notify

title = sys.argv[1]
message = ''
try:
  message = sys.argv[2]
except:
  pass

if not message:
  message = title

Notify.init("DesktopNotification")
notification = Notify.Notification.new(title, message, "dialog-information")
notification.show()
