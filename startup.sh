#!/bin/sh

mypass=`pwgen -1`

echo "Password is $mypass"

/usr/bin/expect <<EOF
log_user 0
spawn /usr/bin/vncpasswd
expect "Password:"
send "$mypass\r"
expect "Verify:"
send "$mypass\r"
expect "Would you like to enter a view-only password"
send "n\r"
expect eof
exit
EOF

export USER=root
vncserver -geometry 1600x900

export DISPLAY=:1

export SELENIUM_BROWSER=chrome
make test

export SELENIUM_BROWSER=firefox
make test

