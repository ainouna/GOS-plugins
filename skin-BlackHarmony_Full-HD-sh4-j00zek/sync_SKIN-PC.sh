# skrypt do konfiguracji/przystosowania skorki do openPLI
# j00zek dla Graterlia 2015
# uzywaj jak chcesz, ale nie zapomnij, kto tworzyl ten skrypt ;)

myPath=`dirname $0`

addons='ftp://blackharmony.pl:55535/FTP/addons/'
skinurl='ftp://blackharmony.pl:55535/FTP/BlackHarmony.tar.gz'
tarName=`basename $skinurl`

[ -f /tmp/$tarName ] && rm -rf /tmp/$tarName
curl -s --ftp-pasv $skinurl -o /tmp/$tarName
if [ $? -gt 0 ]; then
  echo "_(Archive downloaded improperly)"
  exit 0
fi

echo "_(Checking archive consistency)..."
tar -tzf /tmp/$tarName >/dev/null
if [ $? -gt 0 ]; then
  echo "_(Archive is broken)"
  exit 0
fi

echo "_(Unpacking new version)..."

cd $myPath

tar -zxf /tmp/$tarName 2>/dev/null
if [ $? -gt 0 ]; then
  echo "Archive unpacked improperly"
  exit 0sed -i -e 's/render="VRunningText"/render="ScrollLabel"/g' $myPath/skin.xml
fi
rm -rf /tmp/$tarName

##### ADDONS

DownloadableAddons=`curl -s --ftp-pasv $addons -o -|awk '{print $9}'|egrep -v '^plugin_|^VFD_'|sort`

for addon in $DownloadableAddons
do
  echo "Downloading $addon..."
  curl -s --ftp-pasv $addons$addon -o /tmp/$addon
  if [ $? -gt 0 ]; then
    echo "_(Archive downloaded improperly)"
  else
    #echo "_(Checking archive consistency)..."

    tar -tzf /tmp/$addon >/dev/null
    if [ $? -gt 0 ]; then
      echo "Archive is broken"
    else
      #echo "_(Unpacking )$addon..."
      cd $myPath
      tar -zxf /tmp/$addon 2>/dev/null
      if [ $? -gt 0 ]; then
        echo "Archive unpacked improperly"
      fi
    fi
  rm -rf /tmp/$addon
  fi

done

mv -f $myPath/usr/share/enigma2/BlackHarmony/fonts/* $myPath/usr/share/fonts/
rm -rf $myPath/usr/share/enigma2/BlackHarmony/fonts
rm -rf $myPath/usr/lib/enigma2/python/Plugins

sed -i -e 's;filename="/usr/share/enigma2/BlackHarmony/fonts/;filename=";g' $myPath/usr/share/enigma2/BlackHarmony/skin.xml