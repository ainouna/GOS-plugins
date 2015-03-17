Those are initial, starting templates for some skins, to show the magic.
They are copied to allScreens/allFonts/allColors/preview directories located in skin folder.
Put your modifications to appropriate subfolders for your skin.

The schema is:
=>allScreens: screen(s) definition (<screen name=>...</screen>), can contain multiple screens. Other sections will be omitted
			type: skin, with same schema normal skin.xml file uses
			name: colors_<skinName>_<any info without spaces>.xml

=>allFonts: contains fonts definition (<fonts>...</fonts>)
			type: xml, with same schema normal skin.xml file uses
			name: font_<skinName>_<any info without spaces>.xml
			
=>allColors: contains colors and windowstyle definitions
			type: xml, with same schema normal skin.xml file uses
			name: colors_<skinName>_<any info without spaces>.xml
			
=>preview:	contains screenshots showing modified screen/skin,
			type: png
			name: preview_<skinName>_<any info without spaces>.png
			resolution 400x244x8bit
			
NOTE: <SkinName> sections are not needed, when file is directly put into skin subfolder.(e.g. by author of the skin)