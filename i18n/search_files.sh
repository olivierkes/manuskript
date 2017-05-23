while read line; do
  echo $line
  grep -c $line manuskript.pro
done < list.txt
