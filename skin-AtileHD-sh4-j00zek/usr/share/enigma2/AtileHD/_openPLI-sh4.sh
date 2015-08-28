# skrypt do konfiguracji/przystosowania skorki do openPLI
# j00zek dla Graterlia 2014
# u¿ywaj jak chcesz, ale nie zapomnij, kto tworzyl ten skrypt ;)

###### dostosowanie ustawien skorki do tego, co jest w openPLI
#pig w openpli nie obsluguje conditional, nie wiadomo czemu, wiec wywalamy sprawdzenie conditional
sed -i -e '/usage.use_pig/{N;d}' /usr/share/enigma2/AtileHD/skin.xml
[ -e /usr/lib/enigma2/python/Components/Renderer/ScrollLabel.py* ] && sed -i -e 's/render="VRunningText"/render="ScrollLabel"/g' /usr/share/enigma2/AtileHD/skin.xml

#do wywalenia
#render="Cover"
#type="MovieBarInfo"

for f in /usr/share/enigma2/AtileHD/allScreens/skin_*.xml
do
  echo "Processing $f file..."
  # take action on each file. $f store current file name
  sed -i -e '/usage.use_pig/{N;d}' $f
  [ -e /usr/lib/enigma2/python/Components/Renderer/ScrollLabel.py* ] && sed -i -e 's/render="VRunningText"/render="ScrollLabel"/g' $f
#rc_vu_1.png

done
