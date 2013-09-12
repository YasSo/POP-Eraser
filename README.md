POP-Eraser
==========

Delete only old emails in the spool file of the POP3 server.

Usage: poperaser.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --host=HOST           POP3 server's hostname or IP address (default:
                        localhost)
  --port=PORT           POP3 server's port number (default: None)
  -s, --ssl             use SSL connection
  -u USER, --user=USER  POP3 user name (default: miyoshi)
  -p PASSWORD, --pass=PASSWORD
                        user's POP3 password (if not specified, prompt you for
                        the password)
  -d DAYS, --days=DAYS  set how many days to save the emails which arrived by
                        (default: 14)
  -f, --force           this option deletes forcibly email that received time
                        is unknown
  -n, --noexec          this option is for test, and prevents actually
                        deleting email
  -v, --verbose         set verbose mode
