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
echo "MENU|OPKG options">$myPath/_MenuItems
if grep 'repodata/testing' </etc/opkg/opkg.conf | grep '#'; then
	echo "MENU|OPKG release branch options">$myPath/_MenuItems
else
	echo "MENU|OPKG test branch options">$myPath/_MenuItems
fi
echo "ITEM|Display complete list of changes|CONSOLE|wget -q http://openpli.xunil.pl/changes/lista_zmian.txt -O -">>$myPath/_MenuItems
echo "ITEM|List upgradeable packages|CONSOLE|opkg list-upgradable">>$myPath/_MenuItems
#echo "ITEM|||">>$myPath/_MenuItems
if grep 'graterlia.xunil.pl/iptvplayer' </etc/opkg/opkg.conf | grep -v '#' ; then
	echo 'ITEM|Disable IPTV repository|SILENT|sed -i "/src\/gz iptvplayer/d" /etc/opkg/opkg.conf'>>$myPath/_MenuItems
else
	echo 'ITEM|Enable IPTV repository|SILENT|sed -i "1 i\src/gz iptvplayer http://graterlia.xunil.pl/iptvplayer" /etc/opkg/opkg.conf'>>$myPath/_MenuItems
fi

#oscam test, tylko dla drzewa testing
if ! grep '^.*#.*src/gz[ \t]*graterlia-testing' /etc/opkg/opkg.conf; then 
	if grep 'graterlia.xunil.pl/oscams' </etc/opkg/opkg.conf | grep -v '#' ; then
		echo 'ITEM|Disable OsCam test repository|SILENT|sed -i "/src\/gz iptvplayer/d" /etc/opkg/opkg.conf'>>$myPath/_MenuItems
	else
		echo 'ITEM|Enable OsCam test repository|SILENT|sed -i "1 i\src/gz oscams http://graterlia.xunil.pl/oscams" /etc/opkg/opkg.conf'>>$myPath/_MenuItems
	fi
fi