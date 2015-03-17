# @j00zek 2015 dla Graterlia
#
#skrypt ma być w katalogu odpowiedniego Menu

myPath="/dev.static/dvb/adapter0"
myPath2="/dev/dvb/adapter0"
case $1 in
	nosat|standalone|ip)echo "Configuring tuner to work without sat"
	for mydevice in demux1 demux2 demux3
	do
		[ -e $myPath/$mydevice ] && mv -f $myPath/$mydevice $myPath/$mydevice.disabled
		[ -e $myPath2/$mydevice ] && mv -f $myPath2/$mydevice $myPath2/$mydevice.disabled
	done
	;;
	*)echo "Configuring tuner to use sat"
	for mydevice in demux1 demux2 demux3
	do
		[ -e $myPath/$mydevice.disabled ] && mv -f $myPath/$mydevice.disabled $myPath/$mydevice
		[ -e $myPath2/$mydevice.disabled ] && mv -f $myPath2/$mydevice.disabled $myPath2/$mydevice
	done
	;;
esac

echo
echo "Restart tuner to activate changes!!!"