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
echo "MENU|Information about...">$myPath/_MenuItems
echo "ITEM|uptime|CONSOLE|uptime">>$myPath/_MenuItems
echo "ITEM|Memory usage|CONSOLE|free">>$myPath/_MenuItems
echo "ITEM|Started from...|CONSOLE|sed 's/^.*root=\(.* \)rw.*$/\1/' </proc/cmdline">>$myPath/_MenuItems
echo "ITEM|Mounted devices|CONSOLE|mount">>$myPath/_MenuItems
echo "ITEM|Space on partitions|CONSOLE|df -h">>$myPath/_MenuItems
echo "ITEM|System processes|CONSOLE|ps">>$myPath/_MenuItems
echo "ITEM|Network card(s)|CONSOLE|ifconfig">>$myPath/_MenuItems
echo "ITEM|Network state|CONSOLE|netstat -an">>$myPath/_MenuItems
echo "ITEM|Test network connection|CONSOLE|system.sh testnet">>$myPath/_MenuItems
#echo "ITEM|Historia systemu|CONSOLE|cat /etc/upd_info">>$myPath/_MenuItems
#echo "ITEM|MSG test|MSG|echo 'aqq'">>$myPath/_MenuItems
#echo "|||">$myPath/_MenuItems
