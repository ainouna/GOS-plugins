# @j00zek 12014 dla Graterlia
#
#Plik do generowania menu
#musi znajdować się w katalogu menu i jest zawsze uruchamiany przy wyborzez ikonki
#jeśli chcemy, aby menu było statyczne, to wpisujemy w nim exit 0
#Jeśli menu ma byc dynamiczne to tutaj je sobie tworzymy przed każdym wejściem do niego
#
#struktura prosta jak budowa cepa,
#pierwsza linia zawiera nazwę menu
#MENU|<NAZWA Menu>
#
#kolejne linie zawierają poszczególne pozycje według schematu:
#ITEM|<Nazwa opcji>|Typ opcji [CONSOLE|MSG|RUN|SILENT|YESNO]|<nazwa skryptu do uruchomienia>
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
echo "MENU|OScam Menu">$myPath/_MenuItems
echo "ITEM|Info about OScam version|CONSOLE|/etc/rc.d/init.d/softcam status_full">>$myPath/_MenuItems
echo "ITEM|Start/Restart|CONSOLE|/etc/init.d/softcam restart">>$myPath/_MenuItems
echo "ITEM|Stop|CONSOLE|/etc/init.d/softcam stop">>$myPath/_MenuItems
if [ -e /var/opkg/info/oscam-webif.control ]; then
	echo "ITEM|Install OScam without WebIf|YESNO|system.sh oscamnoweb">>$myPath/_MenuItems
fi
if [ -e /var/opkg/info/oscam.control ]; then
	echo "ITEM|Install OScam with WebIf|YESNO|system.sh oscamweb">>$myPath/_MenuItems
fi
#echo "|||">$myPath/_MenuItems
