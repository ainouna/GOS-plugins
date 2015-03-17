#!/bin/sh
LOG(){
echo "$1"
echo "$1" >>/tmp/dba.log
}

GOTERROR(){
echo "$1"
echo "$1" >>/tmp/dba.log
touch /tmp/dba.error
[ -f /tmp/dba.ok ] && rm -rf /tmp/dba.ok
echo
echo ">>>> ERROR!!! Press OK to close"
exit 1
} 

dbaPATH="/DuckBA/bin"
[ -f /tmp/dba.ok ] && rm -rf /tmp/dba.ok
[ -f /tmp/dba.error ] && rm -rf /tmp/dba.error
[ -f /tmp/dba.log ] && rm -rf /tmp/dba.log

if `cat /proc/stb/info/model | grep -q spark7162`; then
	LOG "spark7162 detected :)" 
    
	bootargs_spark='console=ttyAS1,115200 rw ramdisk_size=6144 init=/linuxrc root=/dev/ram0 nwhwconf=device:eth0,hwaddr:00:80:E1:12:40:69 ip=192.168.0.69:192.168.3.119:192.168.3.1:255.255.0.0:Spark:eth0:off stmmaceth=msglvl:0,phyaddr:1,watchdog:5000 bigphysarea=7000'
	userfs_base_spark="0x01400000"
	userfs_len_spark="0x16c00000"
	kernel_base_spark="0x00100000"
	bootcmd_spark="nboot.i 0x80000000 0  0x00100000 ;bootm 0x80000000"
	
	if [ -e /lib/modules/i2s.ko ]; then
		insmod /lib/modules/i2s.ko
	elif [ -e /lib/modules/2.6.32.61_stm24_0215/extra/i2c_spi/i2s.ko ]; then
		insmod /lib/modules/2.6.32.61_stm24_0215/extra/i2c_spi/i2s.ko
	elif [ -e /lib/modules/2.6.32.61_stm24_0216/extra/i2c_spi/i2s.ko ]; then
		insmod /lib/modules/2.6.32.61_stm24_0216/extra/i2c_spi/i2s.ko
	elif [ -e /lib/modules/2.6.32.61_stm24_02*/extra/i2c_spi/i2s.ko ]; then
		insmod /lib/modules/2.6.32.61_stm24_02*/extra/i2c_spi/i2s.ko
	fi 
	[ $? -gt 0 ] && GOTERROR "error inserting i2s module"
elif `cat /proc/stb/info/model | grep -q spark`; then
	LOG "spark detected :)" 
	
	bootargs_spark='console=ttyAS1,115200 rw ramdisk_size=6144 init=/linuxrc root=/dev/ram0 nwhwconf=device:eth0,hwaddr:00:80:E1:12:40:69 ip=192.168.0.69:192.168.3.119:192.168.3.1:255.255.0.0:lh:eth0:off stmmaceth=msglvl:0,phyaddr:1,watchdog:5000 bigphysarea=4000'
	userfs_base_spark="800000"
	userfs_len_spark="17800000"
	kernel_base_spark="0x00080000"
	bootcmd_spark="bootm  0xa0080000"
	
else
	[ $? -gt 0 ] && GOTERROR "Unknown box :("
	exit 1
fi

echo "Writing bootargs..."
#bootargs
$dbaPATH/fw_setenv bootargs "$bootargs_spark"
[ $? -gt 0 ] && GOTERROR "error writing bootargs" || LOG "bootargs configured" 
#bootcmd
$dbaPATH/fw_setenv bootcmd "$bootcmd_spark"
[ $? -gt 0 ] && GOTERROR "error writing bootcmd" || LOG "bootcmd configured" 
#userfs_base_spark
$dbaPATH/fw_setenv userfs_base "$userfs_base_spark"
[ $? -gt 0 ] && GOTERROR "error writing userfs_base" || LOG "userfs_base configured" 
#userfs_len_spark
$dbaPATH/fw_setenv userfs_len "$userfs_len_spark"
[ $? -gt 0 ] && GOTERROR "error writing userfs_len" || LOG "userfs_len configured" 
#kernel_base_spark
$dbaPATH/fw_setenv kernel_base "$kernel_base_spark" 
[ $? -gt 0 ] && GOTERROR "error writing kernel_base" || LOG "kernel_base configured" 
#taki sam dla obu sparkow
$dbaPATH/fw_setenv kernel_name "spark/mImage"
[ $? -gt 0 ] && GOTERROR "error writing kernel_name" || LOG "kernel_name configured" 
#taki sam dla obu sparkow
$dbaPATH/fw_setenv userfs_name "spark/userfsub.img"
[ $? -gt 0 ] && GOTERROR "error writing userfs_name" || LOG "userfs_name configured" 
#taki sam dla obu sparkow
$dbaPATH/fw_setenv tftp_kernel_name "mImage"
[ $? -gt 0 ] && GOTERROR "error writing tftp_kernel_name" || LOG "tftp_kernel_name configured" 
#taki sam dla obu sparkow
$dbaPATH/fw_setenv tftp_userfs_name "userfsub.img" 
[ $? -gt 0 ] && GOTERROR "error writing tftp_userfs_name" || LOG "tftp_userfs_name configured" 
#taki sam dla obu sparkow
$dbaPATH/fw_setenv boot_system "spark"
[ $? -gt 0 ] && GOTERROR "error writing boot_system" || LOG "boot_system configured" 

#rmmod i2s.ko 2>/dev/null
touch /tmp/dba.ok
fw_printenv >/tmp/spark.env
echo
echo ">>>> Press OK to reboot to SPARK"
