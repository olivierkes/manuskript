#!/bin/sh
for f in $(ls *.ts); do
  ts2po $f "$(echo $f | cut -f1 -d '.').po";
done
