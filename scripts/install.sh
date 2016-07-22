#!/bin/bash
#
# Create group for sudo.
# Modify sudoers file to allow group to run phoenixToolkit.
# Create symlink in /sbin/ to make script globaly available
#
GROUPNAME="phoenix_toolkit"
BINLINK="/sbin/phoenixToolkit"

# $1 exit code of process
# $2 Error message
# $3 Success message
function printMessageOrError {
    #echo "printMessageOrError - $1 - $2 - $3"
    if [ $1 -eq 0 ]; then
        echo "  $3"
    else
        echo
        echo "  $2"
        echo
        exit 1
    fi
}
# check user
[ $UID -eq 0 ]
printMessageOrError $?  "Script needs to be executed as root. Abort." "Run script as root"

# check if we have a proper base dir
#[ -f "phoenixToolkit.py" ]
#printMessageOrError $? "Script needs to be executed from within phoenix folder. Abort." "Base dir $(pwd) is ok."

# check if phoenixToolkit group exists
egrep -i "^$GROUPNAME" /etc/group &> /dev/null
if [ $? -ne 0 ]; then
    addgroup $GROUPNAME
    printMessageOrError $? "Failed to add group $GROUPNAME. Abort." "Add group phoenixToolkit"
else
    echo "  Group $GROUPNAME already exists. Skip this step."
fi
# add group to sudoers list
SUDOERSTR="%$GROUPNAME ALL=NOPASSWD: $BINLINK"
egrep -i "$GROUPNAME" /etc/sudoers &> /dev/null
if [ $? -ne 0 ]; then
    echo "$SUDOERSTR" >> /etc/sudoers
    printMessageOrError $? "adding $GROUPNAME to /etc/sudoers failed. Abort." "Add group to sudoer list. Allow execute $BINLINK"
else
    echo "  Group entry in sudoers list already exists. Skip this step."
fi

# check if there is a link in /sbin/phoenixToolkit
if [ -L $BINLINK ]; then
    echo "  Link $BINLINK already exists."
else
    echo "  Create $BINLINK symbolic link."
    phoenixRunable="$( pwd )/phoenixToolkit.py"
    ln -s "$phoenixRunable" $BINLINK
    chmod a+x $phoenixRunable
    printMessageOrError $? "Creating $BINLINK failed. Abort." "Symlink $BINLINK has been created"
fi
