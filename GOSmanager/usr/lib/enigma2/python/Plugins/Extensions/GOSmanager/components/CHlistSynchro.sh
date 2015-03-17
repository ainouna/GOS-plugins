#!/bin/sh
# Graterlia OS
# homepage: http://graterlia.xunil.pl
# e-mail: nbox@xunil.pl
#
# skrypt synchronizujacy liste kanalow pomiedzy tunerami
# @j00zek
# wersja 2014-12-18

. /etc/sysconfig/gfunctions #wczytanie funkcji wspólnych dla skryptów Graterlia
GOSdebug ">>>>>>>>>> $0"

##### FUNKCJE #####
getCONFIG(){
value=`grep "config.plugins.$1=" /etc/enigma2/settings | cut -d '=' -f2` 
if [ -z $value ]; then
	case $1 in #ustawienia standardowe
		"GOS.chlistServerHidden") value='192.168.1.5';;
		"GOS.chlistServerLogin") value='root';;
		"GOS.chlistServerPass") value='root';;
		"GOS.chlistServerHidden") value='false';;
	esac
fi
echo "$value"
}

##### INICJALIZACJA #####
ChannelsListPath='/tmp/myCHlist'
[ -z $1 ] && IPaddr=$( getCONFIG "GOS.chlistServerHidden" ) || IPaddr=$1
[ -z $2 ] && login=$( getCONFIG "GOS.chlistServerLogin" )   || login=$2
[ -z $3 ] && password=$( getCONFIG "GOS.chlistServerPass" ) || password=$3

GOSdebug "Synchronizing from $IPaddr login:$login password:$password"

[ -e ChannelsListPath ] && rm -rf $ChannelsListPath/* || mkdir $ChannelsListPath # czyszczenie katalogu

if ! opkg list-installed | grep -lq wget;then
	opkg update; opkg install wget
fi

##### FUNKCJE c.d. #####
getFILE(){
wget --user=$login --password=$password -x ftp://$IPaddr/$1 -P $ChannelsListPath -q
if [ $? -eq 0 ]; then
	GOSdebug "$1 downloaded"
else
	GOSdebug "ERROR downloading $1, end!!!"
	exit 0
fi
}

getDIR(){
wget --user=$login --password=$password -r ftp://$IPaddr/$1 -P $ChannelsListPath -q
if [ $? -eq 0 ]; then
	GOSdebug "DIR $1 downloaded"
else
	GOSdebug "ERROR downloading $1 DIR, end!!!"
	exit 0
fi
}
##### POBIERANIE KATALOGOW i PODSTAWOWE PORZADKI #####
getDIR /etc/enigma2
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/playlist 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/profile 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/blacklist 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/whitelist 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/settings 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/timers.xml 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/*.cache 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/*.pem 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/*.conf 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/enigma2/*.e2pls 2>/dev/null

getDIR /etc/tuxbox
rm -rf $ChannelsListPath/$IPaddr/etc/tuxbox/scart.conf 2>/dev/null
rm -rf $ChannelsListPath/$IPaddr/etc/tuxbox/timezone.xml 2>/dev/null
##### PRZYGOTOWANIE LISTY #####
GOSdebug "Preparing channels list..."
mkdir $ChannelsListPath/etc
mv -f $ChannelsListPath/$IPaddr/etc/tuxbox $ChannelsListPath/etc/
mkdir $ChannelsListPath/etc/enigma2
mv -f $ChannelsListPath/$IPaddr/etc/enigma2/lamedb $ChannelsListPath/etc/enigma2/ 2>/dev/null
mv -f $ChannelsListPath/$IPaddr/etc/enigma2/satellites.xml $ChannelsListPath/etc/enigma2/ 2>/dev/null
mv -f $ChannelsListPath/$IPaddr/etc/enigma2/bouquets.radio $ChannelsListPath/etc/enigma2/ 2>/dev/null
mv -f $ChannelsListPath/$IPaddr/etc/enigma2/bouquets.tv $ChannelsListPath/etc/enigma2/
##### KOPIOWANIE TYLKO TEGO CO POTRZEBNE #####
while read bukiet; do
	myFile=`echo $bukiet | awk '{print $4}' | tr -d '"'`
	#echo "'$myFile'"
	if [ -f $ChannelsListPath/$IPaddr/etc/enigma2/$myFile ]; then
		mv -f $ChannelsListPath/$IPaddr/etc/enigma2/$myFile $ChannelsListPath/etc/enigma2/
	fi
done <$ChannelsListPath/etc/enigma2/bouquets.radio
while read bukiet; do
	myFile=`echo $bukiet | awk '{print $4}' | tr -d '"'`
	#echo "'$myFile'"
	if [ -f $ChannelsListPath/$IPaddr/etc/enigma2/$myFile ]; then
		mv -f $ChannelsListPath/$IPaddr/etc/enigma2/$myFile $ChannelsListPath/etc/enigma2/
	fi
done <$ChannelsListPath/etc/enigma2/bouquets.tv
##### OSTATECZNA SYNCHRONIZACJA #####
GOSdebug "Syncing channels list..."
rm -rf /etc/enigma2/userbouquet*

mv -f $ChannelsListPath/etc/tuxbox/* /etc/tuxbox/
mv -f $ChannelsListPath/etc/enigma2/* /etc/enigma2/
##### Jesli openPLI dzia³¹ to Prze³adowanie listy #####
if ps | grep -lq enigma2; then 
	wget -q -O - http://127.0.0.1/web/servicelistreload?mode=0  | grep e2statetext | cut -d ">" -f2 | cut -d "<" -f1 
fi
##### Sprzatanie #####
rm -rf $ChannelsListPath

exit 0
