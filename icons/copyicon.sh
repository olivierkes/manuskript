#!/bin/bash -  


# echo "AVR-GCC"
# elf="main.elf"
# c="main.c"
# gcc="avr-gcc"
# options=( "-mmcu=atmega128" "-Wall" -"Os" )
# command=( "$gcc" "${options[@]}" -o "$elf" "$c" )
# # execute it:
# "${command[@]}"

dirSrc=/usr/share/icons/Numix/

dirDest=$(pwd)

name=$1
echo $name
# cd $(dirname "$0")
cd $dirSrc
pwd
for i in $(find  -name $name.svg); \
                do echo $i; \
                cp --parents $i $dirDest/NumixMsk; \
done