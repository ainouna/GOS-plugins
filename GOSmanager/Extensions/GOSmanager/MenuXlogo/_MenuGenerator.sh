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
#PIC| - wyświetla zdjecie u dołu
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

cronPath='/etc/cron/daily'
currConfig=`ls $cronPath | grep bootlogo`
currService=''
if [ -z $1 ]; then
  myPath=`dirname $0`
else
  myPath=$1
fi
echo "MENU|Automatic bootlogo downloader">$myPath/_MenuItems
echo "PIC|/boot/userlogo.jpg">>$myPath/_MenuItems

if `echo $currConfig | grep -q bing_bootlogo`; then
	echo "ITEM|Disable download from Bing|SILENT|$myPath/bootlogo.sh unset bing_bootlogo">>$myPath/_MenuItems
	currService='from Bing'
else
	echo "ITEM|Download from Bing|SILENT|$myPath/bootlogo.sh set bing_bootlogo $myPath">>$myPath/_MenuItems
fi
if `echo $currConfig | grep -q natgeo_bootlogo`; then
	echo "ITEM|Disable download from National Geographic|SILENT|$myPath/bootlogo.sh unset natgeo_bootlogo">>$myPath/_MenuItems
	currService='from National Geographic'
else
	echo "ITEM|Download from National Geographic|SILENT|$myPath/bootlogo.sh set natgeo_bootlogo $myPath">>$myPath/_MenuItems
fi
if `echo $currConfig | grep -q user_bootlogo`; then
	echo "ITEM|Disable using /hdd/picture/ folder|SILENT|$myPath/bootlogo.sh unset user_bootlogo">>$myPath/_MenuItems
	currService='from /hdd/picture'
else
	echo "ITEM|Use /hdd/picture/ folder|SILENT|$myPath/bootlogo.sh set user_bootlogo $myPath">>$myPath/_MenuItems
fi
if `echo $currConfig | grep -q random_bootlogo`; then
	echo "ITEM|Disable donwload from random source|SILENT|$myPath/bootlogo.sh unset random_bootlogo">>$myPath/_MenuItems
	currService='randomly'
else
	echo "ITEM|Download from random source|SILENT|$myPath/bootlogo.sh set random_bootlogo $myPath">>$myPath/_MenuItems
fi

[ -z $currConfig ] || echo "ITEM|Download now $currService|SILENT|`ls /etc/cron/daily/*_bootlogo | grep -m 1 bootlogo`">>$myPath/_MenuItems
