#!/bin/bash

export ERVIZ_BASE=/home/bringout/devel/erviz/erviz-1.0.6

export PATH=$PATH:$ERVIZ_BASE/bin

erviz.sh -i pos_ubp.txt -o pos_ubp.dot

THIS_DIR=`pwd`
echo `pwd`
cd $ERVIZ_BASE

echo `pwd`
work/scripts/dot2pdf.sh $THIS_DIR/pos_ubp.dot
work/scripts/dot2png.sh $THIS_DIR/pos_ubp.dot

