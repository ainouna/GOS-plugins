#!/bin/bash
. /etc/sysconfig/gfunctions #wczytanie funkcji wspólnych dla skryptów Graterlia

if ! opkg list-installed | grep -q 'ffmpeg ';then
	opkg update; opkg install ffmpeg
fi
 
OUTPUT=/tmp/userlogo.jpg
[ -f $OUTPUT ] && rm -f $OUTPUT
[ -f /tmp/userlogo.mpg ] && rm -f /tmp/userlogo.mpg
[ -f /tmp/standbylogo.jpg ] && rm -f /tmp/standbylogo.jpg

bing() {
# get the bing.com page, and separate the background image (DONT touch this)
GOSdebug "Getting bing wallpaper url"
IMG=`wget -q "http://www.bing.com" -O- | sed -r "s/[\]//g;s/.*g_img=\{url:'([^']+)'.*/\1/gp;d"`
if `echo IMG | grep -q "\.jpg"`; then
	GOSdebug "Error, no url found, exiting"
	exit 1
fi
GOSdebug "Downloading bing wallpaper"
# get the background image to the output (DONT touch this)
wget -q "http://www.bing.com$IMG" -O $OUTPUT
# error handle
if [ $? -gt 0 ]; then
    GOSdebug "there is a problem with downloading.."
	exit 1
fi
}

natgeo() {
#Based on code of APOD, you can really find everywhere on the web.
#Downloading html of the Picture-Of-The-Day
GOSdebug "Getting NatGeo wallpaper url"
wget -q http://photography.nationalgeographic.com/photography/photo-of-the-day/ -O /tmp/ngpod.html
#Getting the URL of the image
img_location="http:`egrep -o "//images.nationalgeographic.com/[^<]*[^>]*\.jpg" /tmp/ngpod.html|head -n 1|tail -n 1`"
rm /tmp/ngpod.html

#Download image
GOSdebug "Downloading NatGeo wallpaper"
wget $img_location -O  $OUTPUT
if [ $? -gt 0 ]; then
    GOSdebug "there is a problem with downloading.."
    exit 1
fi
}

user() {
myLOGO=`find /hdd/picture/ -type f -regex ".*/.*\.\(jpg\|JPG\)" -size +1k -print | awk 'BEGIN{srand()} {x[NR] = $0} END{print x[1 + int(rand() * NR)]}'`
#echo "|$myLOGO|"
cp -f "$myLOGO" $OUTPUT
}

random() {
	bing
	[ -f $OUTPUT ] && mv -f $OUTPUT /tmp/userlogo1.random
	natgeo
	[ -f $OUTPUT ] && mv -f $OUTPUT /tmp/userlogo2.random
	user
	[ -f $OUTPUT ] && mv -f $OUTPUT /tmp/userlogo3.random
	autoLOGO=`ls /tmp/*.random | awk 'BEGIN{srand()} {x[NR] = $0} END{print x[1 + int(rand() * NR)]}'`
	echo $autoLOGO
	mv -f $autoLOGO $OUTPUT
	rm -rf /tmp/*.random
}

ffmpegConvert() {
if [ -f $OUTPUT ]; then
	#nice -n 19 ffmpeg -y -i $OUTPUT -s 634:341 -qscale 1 /tmp/standbylogo.jpg &>/dev/null
	nice -n 19 ffmpeg -y -i $OUTPUT -vf scale="'if(gt(a,4/3),634,-1)':'if(gt(a,4/3),-1,341)'" -qscale 1 /tmp/standbylogo.jpg &>/dev/null
	if [ $? -gt 0 ]; then
		echo "error converting standbylogo.."
	else
		echo "standbylogo converted"
	fi
	nice -n 19 ffmpeg -y -i $OUTPUT -r 25 -b:v 1800 /tmp/userlogo.mpg &>/dev/null
	if [ $? -gt 0 ]; then
		echo "error converting userlogo.jpg, trying with standbylogo.jpg.."
		nice -n 19 ffmpeg -y -i /tmp/standbylogo.jpg -r 25 -b:v 1800 /tmp/userlogo.mpg &>/dev/null
		if [ $? -gt 0 ]; then
			echo "error converting userlogo.jpg and standbylogo.jpg :("
			exit 1
		fi
	else
		echo "bootlogo converted"
	fi
else
	exit 1
fi
[ ! -f /tmp/userlogo.mpg ] && exit 1
SIZE=`wc -c /tmp/userlogo.mpg | awk '{print $1}'`
if [ $SIZE -gt 20000 ]; then
	mv -f /tmp/userlogo.mpg /boot/logo_.mvi
	mv -f $OUTPUT /boot/userlogo.jpg
	[ -f /tmp/standbylogo.jpg ] && mv -f /tmp/standbylogo.jpg /boot/standbylogo.jpg
fi
}

case $1 in
	"set") 	rm -rf /etc/cron/daily/*_bootlogo
			if [ $2 == bing_bootlogo ]; then
				echo -e "#!/bin/bash\n$3/bootlogo.sh bing\n" >/etc/cron/daily/bing_bootlogo
			elif [ $2 == natgeo_bootlogo ]; then
				echo -e "#!/bin/bash\n$3/bootlogo.sh natgeo\n" >/etc/cron/daily/natgeo_bootlogo
			elif [ $2 == user_bootlogo ]; then
				echo -e "#!/bin/bash\n$3/bootlogo.sh user\n" >/etc/cron/daily/user_bootlogo
			elif [ $2 == random_bootlogo ]; then
				echo -e "#!/bin/bash\n$3/bootlogo.sh random\n" >/etc/cron/daily/random_bootlogo
			fi
			chmod 755 /etc/cron/daily/*_bootlogo
	;;
	"unset") rm -rf /etc/cron/daily/$2
	;;
	"bing")bing; ffmpegConvert
	;;
	"natgeo")natgeo; ffmpegConvert
	;;
	"user")user; ffmpegConvert
	;;
	"random")random; ffmpegConvert
	;;
	*) GOSdebug "wrong option"
	exit 0
	;;
esac
