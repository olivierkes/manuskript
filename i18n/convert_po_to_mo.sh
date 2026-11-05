#!/bin/sh
LOCALE_DIR=../locale
for f in $(ls *_*.po); do
  NAME=$(echo $f | cut -f1 -d '.');
  DOMAIN=$(echo $NAME | tr '_' ' ' | awk '{print $1}')
  LANG=$(echo $NAME | tr '_' ' ' | awk '{$1="";print}' | cut -c 2- | tr ' ' '_')
  DIR=$LOCALE_DIR/$LANG/LC_MESSAGES
  mkdir -p $DIR
  msgfmt -o $DIR/$DOMAIN.mo $f
done
