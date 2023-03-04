#!/bin/bash
for FORM in $(find manuskript/ | grep "\.ui$"); do
	echo "FORMS += ../$FORM"
done
for SOURCE in $(find manuskript/ | grep "\.py$"); do
	echo "SOURCES += ../$SOURCE"
done
for TRANSLATION in $(find i18n/ | grep "\.ts$"); do
	echo "TRANSLATIONS += $(basename $TRANSLATION)"
done
