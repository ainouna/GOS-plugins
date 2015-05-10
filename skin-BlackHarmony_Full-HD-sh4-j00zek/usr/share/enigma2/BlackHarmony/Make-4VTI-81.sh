#j00zek @2015
myDir=/usr/share/enigma2/BlackHarmony

MakeChanges(){
SkinName=$1
#Global screens
sed -i 's/\(widget name="list".*\)font="[a-zA-Z_]*; [0-9]*"/\1/' $SkinName
sed -i 's/\(widget name="[a-zA-Z_]*list".*\)font="[a-zA-Z_]*; [0-9]*"/\1/' $SkinName
sed -i 's/\(render="Listbox".*\)font="[a-zA-Z_]*; [0-9]*"/\1/' $SkinName
sed -i 's/\(widget name="config".*\)font="[a-zA-Z_]*; [0-9]*"/\1/' $SkinName
#skinselector
sed -i 's/\(widget name="SkinList".*\)font="[a-zA-Z_]*; [0-9]*"/\1/' $SkinName
}

MakeChanges $myDir/skin.xml

myDirs='allScreens allFonts allColors'

for mySubDir in $myDirs; do
	for skin in `ls $myDir/$mySubDir`; do
		echo Modyfing $skin
		MakeChanges $myDir/$mySubDir/$skin
	done
done
