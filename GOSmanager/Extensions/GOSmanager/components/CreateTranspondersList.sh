#!/bin/sh
# 2015 @j00zek for Graterlia
# Script creates list of transponders being in use by PL providers
# j00zeBouquets will filter data based on it
#
ping -c 1 www.lyngsat.com >/dev/null
if [ $? -gt 0 ]; then
	echo "_(No internet connection. Exiting)"
	exit 0
fi
myPath=`dirname $0`
echo "_(Downloading from lyngsat...)"
wget -q http://www.lyngsat.com/packages/NC-.html -O - |egrep ' [HV]<'|sed 's/^.*<b>\([0-9]*\) [HV].*/\1/' >>$myPath/PLtrans.tmp
wget -q http://www.lyngsat.com/packages/Cyfrowy-Polsat.html -O - |egrep ' [HV]<'|sed 's/^.*<b>\([0-9]*\) [HV].*/\1/' >>$myPath/PLtrans.tmp
echo "_(Downloading from kingofsat...)"
wget -q http://pl.kingofsat.net/pack-ncplus.php -O -|grep -e 'class="bld">1[0-9]*'|sed 's/^.*bld">\(1[0-9]*\).*/\1/' >>$myPath/PLtrans.tmp
wget -q http://pl.kingofsat.net/pack-polsat.php -O -|grep -e 'class="bld">1[0-9]*'|sed 's/^.*bld">\(1[0-9]*\).*/\1/' >>$myPath/PLtrans.tmp
grep '^.....$' < $myPath/PLtrans.tmp > $myPath/PLtrans.temp
rm -f $myPath/PLtrans.tmp
sort -u <$myPath/PLtrans.temp >$myPath/transponders.PL
rm -f $myPath/PLtrans.temp
echo "_(List of transponders being in use by PL providers has been updated)"
exit 0
