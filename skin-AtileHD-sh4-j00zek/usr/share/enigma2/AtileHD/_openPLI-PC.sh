# skrypt do konfiguracji/przystosowania skorki do openPLI
# j00zek dla Graterlia 2014
# u¿ywaj jak chcesz, ale nie zapomnij, kto tworzyl ten skrypt ;)

###### dostosowanie ustawien skorki do tego, co jest w openPLI
#pig w openpli nie obsluguje conditional, nie wiadomo czemu, wiec wywalamy sprawdzenie conditional
myPath=`dirname $0`

sed -i -e '/usage.use_pig/{N;d}' $myPath/skin.xml
sed -i -e 's/render="VRunningText"/render="ScrollLabel"/g' $myPath/skin.xml

#do wywalenia
#render="Cover"
#type="MovieBarInfo"

for f in $myPath/allScreens/skin_*.xml
do
  echo "Processing $f file..."
  # take action on each file. $f store current file name
  sed -i -e '/usage.use_pig/{N;d}' $f
  sed -i -e 's/render="VRunningText"/render="ScrollLabel"/g' $f
#rc_vu_1.png
done

ToDelete='skin_Atmolight skin_LCD4Linux skin_Vfd_Clock_only_blink skin_Vfd_Clock_only'
for f in $ToDelete
do
  echo "Deleting $f file..."
  rm -f $myPath/allScreens/$f.xml
  rm -f $myPath/allPreviews/preview_$f.png
done
