#!/bin/sh
. /etc/sysconfig/gfunctions #wczytanie funkcji wspólnych dla skryptów Graterlia
GOSdebug ">>>>>>>>>> $0"

getvalue(){
value=`grep "$1" /etc/enigma2/settings | cut -d '=' -f2`
if [ -z "$value" ]; then value=0;fi
GOSdebug "E2 already started $value times"
return $value
}

PluginsPath="/usr/lib/enigma2/python/Plugins"
config="$PluginsPath/Extensions/PlugLoad/PlugLoad.cfg"

if [ ! -e "/etc/cron/moderatestandby_on/40PlugLoad" ]; then
	ln -s $PluginsPath/Extensions/PlugLoad/PlugLoad.sh /etc/cron/moderatestandby_off/40PlugLoad
fi

#if we don't have E2 configured, better is to do nothing. ;)
if [ ! -e "/etc/enigma2/settings" ]; then exit; fi

getvalue "config.misc.startCounter"
is_E2_fully_configured=$?

if [ $is_E2_fully_configured -lt 2 ]; then GOSdebug "PlugLoad starts after second E2 load" ; exit; fi

case $1 in
	py)
		# started by Delayer plugin
		for i in $( mount | grep '/usr/lib/enigma2/python/Plugins' | awk '{print $3}' ); do
			GOSdebug "Unmounting $i"
			/bin/umount -n -lf $i
		done
		GOSdebug "PlugLoad finished all actions"
		echo 1 > /proc/sys/vm/drop_caches
		;;
	"")
		#initialization, delayed plugins are mounted to empty tmpFS = will not be visible by E2 during start
		#first lets check if anything is already mounted.this speedsup the process
		#below plugins will be excluded from delayed start
		ExcludedPlugins=`cat $PluginsPath/Extensions/PlugLoad/PlugLoad.cfg | grep '^Plugin=' | tr -d '\n' | sed -e 's/,/|/g' | sed -e 's/Plugin=//g' | tr -d " "`
		SystemPlugins=`ls -l $PluginsPath/SystemPlugins |grep "^dr" |grep -v -E "$ExcludedPlugins" | awk '{print $9}'`
		ExtensionPlugins=`ls -l $PluginsPath/Extensions |grep "^dr" |grep -v -E "$ExcludedPlugins" | awk '{print $9}'`
		#lets mount systemplugins to nothing
		for plugin in $SystemPlugins
		do
			GOSdebug "PlugLoad has blocked the following system plugin: $plugin"
			if  ! `mount | grep -q "$PluginsPath/SystemPlugins/$plugin"`; then
				#GOSdebug "Mounting $PluginsPath/SystemPlugins/$plugin"
				/bin/mount -n -t tmpfs -o size=1K tmpfs "$PluginsPath/SystemPlugins/$plugin"
			fi
		done
		#lets mount Extensionplugins to nothing
		for plugin in $ExtensionPlugins
		do
			GOSdebug "PlugLoad has blocked the following extensions plugin: $plugin"
			if  ! `mount | grep -q "$PluginsPath/Extensions/$plugin"`; then
				#GOSdebug "Mounting $PluginsPath/Extensions/$plugin"
				/bin/mount -n -t tmpfs -o size=1K tmpfs "$PluginsPath/Extensions/$plugin"
			fi
		done
		GOSdebug "Blocked plugins:"
		GOSdebug `mount | grep 'tmpfs on' | grep Plugins | awk '{print $3}'`
		echo 3 > /proc/sys/vm/drop_caches
		;;
esac
