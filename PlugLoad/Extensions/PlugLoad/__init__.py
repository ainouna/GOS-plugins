from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
from os import symlink, system

try:
	#j00zek:initial setup of the script
	if fileExists("/etc/cron/moderatestandby_on/40PlugLoad"):
		pass
	else:
		symlink(resolveFilename(SCOPE_PLUGINS, "Extensions/PlugLoad/PlugLoad.sh"), "/etc/cron/moderatestandby_on/40PlugLoad")
		#system("chmod 775 %s" % resolveFilename(SCOPE_PLUGINS, "Extensions/PlugLoad/PlugLoad.sh"))
except OSError:
	pass

