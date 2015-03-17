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
echo "MENU|System management">$myPath/_MenuItems
#echo "ITEM|GUI restart|APPLET|applet_restartgui">>$myPath/_MenuItems
echo "ITEM|Settings backup|CONSOLE|system.sh settingsbackup">>$myPath/_MenuItems
#echo "ITEM|Close system|SILENT|system.sh shutdown &">>$myPath/_MenuItems
#echo "ITEM|Restart system|SILENT|system.sh restart &">>$myPath/_MenuItems
if [ -e /etc/sysconfig/autoupdateh ]; then
	echo "ITEM|Disable automatic info about updates|CONSOLE|system.sh setautoupdate">>$myPath/_MenuItems
else
	echo "ITEM|Enable automatic info about updates|CONSOLE|system.sh setautoupdate">>$myPath/_MenuItems
fi
echo "ITEM|||">>$myPath/_MenuItems
echo "ITEM|Channel list backup|YESNO|system.sh listbackup">>$myPath/_MenuItems
echo "ITEM|Channel list restore|YESNO|system.sh listrestore">>$myPath/_MenuItems
echo "ITEM|||">>$myPath/_MenuItems
echo "ITEM|System cleanup|CONSOLE|$myPath/clean_system.sh">>$myPath/_MenuItems
echo "ITEM|||">>$myPath/_MenuItems
echo "ITEM|Network restart|CONSOLE|/etc/init.d/network restart">>$myPath/_MenuItems
echo "ITEM|sshd/telnet restart|CONSOLE|/etc/init.d/sshd restart">>$myPath/_MenuItems
if ls /dev/dvb/adapter0/demux* | grep -q disabled; then
	echo "ITEM|Configure to work with sat|CONSOLE|$myPath/nosatconfig.sh">>$myPath/_MenuItems
else
	echo "ITEM|Configure to work without sat|CONSOLE|$myPath/nosatconfig.sh standalone">>$myPath/_MenuItems
fi