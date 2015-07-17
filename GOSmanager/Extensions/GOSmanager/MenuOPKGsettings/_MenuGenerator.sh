# @j00zek 2015 dla Graterlia
#
#Plik do generowania menu
#musi znajdować się w katalogu menu i jest zawsze uruchamiany przy wyborzez ikonki
#jeśli chcemy, aby menu było statyczne, to na początku wpisujemy exit 0
#Jeśli menu ma byc dynamiczne to tutaj je sobie tworzymy przed każdym wejściem do niego
#
#struktura prosta jak budowa cepa,
#pierwsza linia zawiera nazwę menu
#MENU|<NAZWA Menu>
#
#kolejne linie zawierają poszczególne pozycje według schematu:
#ITEM|<Nazwa opcji>|Typ opcji [CONSOLE|MSG|RUN|SILENT|YESNO|APPLET]|<nazwa skryptu do uruchomienia>
#
#CONSOLE wyświetla okno konsoli i wszystko co się w nim dzieje
#MSG uruchamia w tle skrypt i wyświetla wiadomość zawierającą to co zwróci skrypt
#RUN uruchamia skrypt w tle i potwierdza jego wykonanie
#SILENT uruchamia skrypt w tle
#YESNO pyta sie czy uruchomic skrypt
#
#skrypt ma być w katalogu odpowiedniego Menu
if [ -z $1 ]; then
  myPath=`dirname $0`
else
  myPath=$1
fi

#porzadki
sed -i "/iptvplayer/d" /etc/opkg/opkg.conf
sed -i "/oscams/d" /etc/opkg/opkg.conf
sed -i "/graterlia-ready/d" /etc/opkg/opkg.conf
sed -i "/graterlia-testing/d" /etc/opkg/opkg.conf
sed -i "/graterlia-src/d" /etc/opkg/opkg.conf

echo "MENU|OPKG options">$myPath/_MenuItems
if grep 'repodata/testing' </etc/opkg/opkg.conf | grep '#'; then
	echo "MENU|OPKG release branch options">$myPath/_MenuItems
else
	echo "MENU|OPKG test branch options">$myPath/_MenuItems
fi
echo "ITEM|Display complete list of changes|CONSOLE|wget -q http://openpli.xunil.pl/changes/lista_zmian.txt -O -">>$myPath/_MenuItems
echo "ITEM|List upgradeable packages|CONSOLE|opkg list-upgradable">>$myPath/_MenuItems
#echo "ITEM|||">>$myPath/_MenuItems

#oscam test
[ -e /etc/opkg/oscam.conf ] && mv -f /etc/opkg/oscam.conf /etc/opkg/xopkg-oscam.conf

if [ -e /etc/opkg/xopkg-oscam.conf ]; then
	echo 'ITEM|Disable OsCam test repository|SILENT|rm -rf /etc/opkg/*oscam.conf'>>$myPath/_MenuItems
else
	echo 'ITEM|Enable OsCam test repository|SILENT|echo "src/gz oscams http://graterlia.xunil.pl/oscams" >/etc/opkg/xopkg-oscam.conf'>>$myPath/_MenuItems
fi
#zrodla
tunerarch=`cat /etc/opkg/opkg.conf |grep '^arch'|grep -v sh4|awk '{print $2}'`
echo "src/gz graterlia-src http://graterlia.xunil.pl/repodata/release-src/sh4">$myPath/xopkg-sources.conf
echo "src/gz graterlia-ready-src http://graterlia.xunil.pl/repodata/ready-src/sh4">>$myPath/xopkg-sources.conf
echo "src/gz graterlia-testing-src http://graterlia.xunil.pl/repodata/testing-src/sh4">>$myPath/xopkg-sources.conf
echo "src/gz $tunerarch-src http://graterlia.xunil.pl/repodata/release-src/$tunerarch">>$myPath/xopkg-sources.conf
echo "src/gz $tunerarch-ready-src http://graterlia.xunil.pl/repodata/ready-src/$tunerarch">>$myPath/xopkg-sources.conf
echo "src/gz $tunerarch-testing-src http://graterlia.xunil.pl/repodata/testing-src/$tunerarch">>$myPath/xopkg-sources.conf

if [ -e /etc/opkg/xopkg-sources.conf ]; then
        echo 'ITEM|Disable Sources repository|SILENT|rm -rf /etc/opkg/xopkg-sources.conf'>>$myPath/_MenuItems
else
        echo 'ITEM|Enable Sources repository|SILENT|cp -rf $myPath/xopkg-sources.conf /etc/opkg/xopkg-sources.conf'>>$myPath/_MenuItems
fi
i