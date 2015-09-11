# skrypt do konfiguracji/przystosowania skorki do openPLI
# j00zek dla Graterlia 2014
# u¿ywaj jak chcesz, ale nie zapomnij, kto tworzyl ten skrypt ;)

###### dostosowanie ustawien skorki do tego, co jest w openPLI
#pig w openpli nie obsluguje conditional, nie wiadomo czemu, wiec wywalamy sprawdzenie conditional
myPath=`dirname $0`

sed -i -e '/usage.use_pig/{N;d}' $myPath/skin.xml
sed -i -e 's/render="VRunningText"/render="ScrollLabel"/g' $myPath/skin.xml
sed -i -e 's;filename="/usr/share/enigma2/.*/fonts/;filename=";g' $myPath/skin.xml
#wywalamy widgety na pewno nie dzialajace i niepotrzebne
xmlstarlet ed --inplace -d "/skin/screen/widget[@source='HbbtvApplication']" $myPath/skin.xml #na sh4 nie dziala
xmlstarlet ed --inplace -d "/skin/screen/widget[@render='VtiEmuInfo']" $myPath/skin.xml #niepotrzebne info o wersji oscama
xmlstarlet ed --inplace -d "/skin/screen/widget[@render='AudioIcon']" $myPath/skin.xml #niepotrzebne info o wersji oscama
xmlstarlet ed --inplace -d "/skin/screen/widget/convert[@type='VAudioInfo']" $myPath/skin.xml #niepotrzebne info o wersji oscama

#do wywalenia
#render="Cover"
#type="MovieBarInfo"

for f in $myPath/allScreens/skin_*.xml
do
  echo "Processing $f file..."
  # take action on each file. $f store current file name
  sed -i -e '/usage.use_pig/{N;d}' $f
  sed -i -e 's/render="VRunningText"/render="ScrollLabel"/g' $f
  xmlstarlet ed --inplace -d "/skin/screen/widget[@source='HbbtvApplication']" $f
  xmlstarlet ed --inplace -d "/skin/screen/widget[@render='VtiEmuInfo']" $f
  xmlstarlet ed --inplace -d "/skin/screen/widget[@render='AudioIcon']" $f
  xmlstarlet ed --inplace -d "/skin/screen/widget/convert[@type='VAudioInfo']" $f
#rc_vu_1.png
done

ToDelete='skin_Atmolight skin_LCD4Linux skin_Vfd_Clock_only_blink skin_Vfd_Clock_only'
for f in $ToDelete
do
  echo "Deleting $f file..."
  rm -f $myPath/allScreens/$f.xml
  rm -f $myPath/allPreviews/preview_$f.png
done
