Uninstall or disable android apps by list via ADB.

Example for Xiaomi Redmi Note 8 Pro:
apps_clean_list_Xiaomi.txt
This file contains a list of preinstalled apps that can be uninstalled.

App marked as [UNINST] will be uninstalled permanently!
Not marked apps will be disabled.
You can enable it later with the command:
pm enable <app name>


You can make a list for your smartphone using the commands:
adb shell
pm list packages

ATTENTION!
Check carefully if it is safe to uninstall an app before adding it to the list!
