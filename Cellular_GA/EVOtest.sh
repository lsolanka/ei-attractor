#! /bin/sh

N103="\
pcn103-01 \
pcn103-02 \
pcn103-03 \
pcn103-04 \
pcn103-05 \
pcn103-06 \
pcn103-07 \
pcn103-08 \
pcn103-09 \
pcn103-10 \
pcn103-11 \
pcn103-12 \
pcn103-13 \
pcn103-14 \
pcn103-15 \
pcn103-16 \
pcn103-17 \
pcn103-18 \
pcn103-19"

#N104="\
#pcn104-00 \
#pcn104-01 \
#pcn104-02 \
#pcn104-03 \
#pcn104-04 \
#pcn104-05 \
#pcn104-06 \
#pcn104-08 \
#pcn104-09 \
#pcn104-10 \
#pcn104-11 \
#pcn104-12 \
#pcn104-13 \
#pcn104-14 \
#pcn104-15 \
#pcn104-16 \
#pcn104-17 \
#pcn104-18 \
#pcn104-19"

N105="\
pcn105-00 \
pcn105-01 \
pcn105-02 \
pcn105-03 \
pcn105-04 \
pcn105-05 \
pcn105-06 \
pcn105-07 \
pcn105-08 \
pcn105-09 \
pcn105-10 \
pcn105-11 \
pcn105-12 \
pcn105-13 \
pcn105-14 \
pcn105-15 \
pcn105-16 \
pcn105-17 \
pcn105-18 \
pcn105-19"

#O103="\
#pco103-00 \
#pco103-01 \
#pco103-02 \
#pco103-03 \
#pco103-04 \
#pco103-05 \
#pco103-06 \
#pco103-07 \
#pco103-08 \
#pco103-09 \
#pco103-10 \
#pco103-11 \
#pco103-12 \
#pco103-13 \
#pco103-14 \
#pco103-15 \
#pco103-16 \
#pco103-17 \
#pco103-18"

#O104="\
#pco104-00 \
#pco104-01 \
#pco104-02 \
#pco104-03 \
#pco104-05 \
#pco104-06 \
#pco104-07 \
#pco104-08 \
#pco104-09 \
#pco104-10 \
#pco104-11 \
#pco104-12 \
#pco104-13 \
#pco104-14 \
#pco104-15 \
#pco104-16 \
#pco104-17 \
#pco104-18 \
#pco104-19"

N203="\
pcn203-00 \
pcn203-01 \
pcn203-02 \
pcn203-03 \
pcn203-04 \
pcn203-05 \
pcn203-06 \
pcn203-07 \
pcn203-08 \
pcn203-09 \
pcn203-10 \
pcn203-11 \
pcn203-12 \
pcn203-13 \
pcn203-14 \
pcn203-15 \
pcn203-16 \
pcn203-17 \
pcn203-18 \
pcn203-19"

N204="\
pcn204-00 \
pcn204-01 \
pcn204-02 \
pcn204-03 \
pcn204-04 \
pcn204-05 \
pcn204-06 \
pcn204-07 \
pcn204-08 \
pcn204-09 \
pcn204-10 \
pcn204-11 \
pcn204-12 \
pcn204-13 \
pcn204-14 \
pcn204-15 \
pcn204-16 \
pcn204-17 \
pcn204-18 \
pcn204-19"

N205="\
pcn205-00 \
pcn205-01 \
pcn205-02 \
pcn205-03 \
pcn205-04 \
pcn205-05 \
pcn205-06 \
pcn205-07 \
pcn205-08 \
pcn205-09 \
pcn205-10 \
pcn205-11 \
pcn205-12 \
pcn205-13 \
pcn205-14 \
pcn205-15 \
pcn205-16 \
pcn205-17 \
pcn205-18 \
pcn205-19"

M105="\
pcm105-00"

HOSTS=${HOSTS-"$N103 $N104 $N105 $O103 $O104 $N203 $N204 $N205 $M105"}
#HOSTS="pcn204-00 pcn204-01"
APP_NAME=testOneMax
ROOT="/homes/eva/xs/xsolan00/skola/arc/projekty/03/SW"

mRate=0.0001
xsize=10
ysize=10
genNum=20000
cType=1
rWalk=1

repeats=${repeats-"100"}
logdir=${logdir-"logs"}
tmp_prefix="tmp"

if [ $# -eq 1 ] ; then
    cnt=0
    for i in $HOSTS;
    do
        echo "Killing in $i"
        ssh $i killall -s 9 $APP_NAME
        let cnt=cnt+1

    done
    echo "$cnt machines available"

    exit 0
fi

if [ -z "$chrLengths" ]
then
    echo "no chrLengths set!"
    exit 1
fi


#for i in $chrLengths
#do
    touch testOneMax.cc
    CXXADD=-DCHR_LENGTH=$chrLengths make

    for m in $HOSTS
    do
        ssh $m "                    \
            cd $ROOT;               \
            ./testOneMax -g $genNum -xsize $xsize -ysize $ysize -m $mRate -r $rWalk -ct $cType 2>&1 | \
                grep \<gastat\> |tee $logdir/$tmp_prefix.$m.log" &
    
        echo "$m running"
    done

echo " Press any key to process tmp files"
read

cnt=0;
logfile=$logdir/ct$cType.chr$chrLengths.m$mRate.xs$xsize.ys$ysize.g$genNum.log
rm -f $logfile

for m in $HOSTS
do
    cat $logdir/$tmp_prefix.$m.log >> $logfile
    let cnt=$cnt+1
    rm -f $logdir/$tmp_prefix.$m.log
done

echo Number processed: $cnt
