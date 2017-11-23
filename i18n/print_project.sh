
# Adds forms
for i in $(find .. -iname *.ui)
do
  echo "FORMS += " $i;
done

# Adds file containing .tr(
for i in $(grep -ril "\.tr(" ../manuskript)
do
  echo "SOURCES += " $i;
done

# Adds file containing .translate
for i in $(grep -ril "\.translate(" ../manuskript)
do
  echo "SOURCES += " $i;
done

# Adds translations
cat languages.txt
