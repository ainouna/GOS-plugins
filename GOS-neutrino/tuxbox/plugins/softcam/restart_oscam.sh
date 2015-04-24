#!/bin/sh

# Graterlia OS
# homepage: http://graterlia.xunil.pl
# e-mail: nbox@xunil.pl
#
# skrypt zarządzający działaniem OSCam z poziomu neutrino
# wersja 2015-04-16

. /etc/sysconfig/gfunctions #wczytanie funkcji wspólnych dla skryptów Graterlia
scriptname="Graterlia SoftCam" #nazwa uruchamianego czegoś
runname=/var/grun/gsoftcam #plik informujący czy uruchomiono czy nie
msginfo="start, restart, hardrestart, stop, hardstop, status, status_full" #informacja o możliwych parametrach
PATH=/sbin:/bin:/usr/sbin:/usr/bin #deklaracja ścieżek

camdir=/usr/bin
camconfig=/etc/oscam
if [ -e $camdir/oscam_debug ]; then
	actcam=oscam_debug
elif [ -e $camdir/oscam_user ]; then
	actcam=oscam_user
else
	actcam=oscam
fi

if [ -e /usr/lib/enigma2/python/Plugins/Extensions/AlternativeSoftCamManager ] && (`grep -q 'config.plugins.AltSoftcam.enabled=true' < /etc/enigma2/settings`); then
	if (`grep -q 'config.plugins.AltSoftcam.camdir=' < /etc/enigma2/settings`); then
		camdir=`grep 'config.plugins.AltSoftcam.camdir=' < /etc/enigma2/settings|cut -d '=' -f2`
	fi
	if (`grep -q 'config.plugins.AltSoftcam.camconfig=' < /etc/enigma2/settings`); then
		camconfig=`grep 'config.plugins.AltSoftcam.camconfig=' < /etc/enigma2/settings|cut -d '=' -f2`
	fi
	if (`grep -q 'config.plugins.AltSoftcam.actcam=' < /etc/enigma2/settings`); then
		actcam=`grep 'config.plugins.AltSoftcam.actcam=' < /etc/enigma2/settings|cut -d '=' -f2`
	fi
fi
echo `date`>>/tmp/softcam.log
if `pgrep $actcam`; then
	echo "stopping $actcam"
	echo "Stopping $actcam">>/tmp/softcam.log
	pkill $actcam
fi
sleep 3
echo "Starting $camdir/$actcam -c $camconfig"
echo "Starting $camdir/$actcam -c $camconfig">>/tmp/softcam.log
$camdir/$actcam -u -r 2 -d 0 -c $camconfig -t /tmp/oscam &
