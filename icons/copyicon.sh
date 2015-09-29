#!/bin/bash -  


# echo "AVR-GCC"
# elf="main.elf"
# c="main.c"
# gcc="avr-gcc"
# options=( "-mmcu=atmega128" "-Wall" -"Os" )
# command=( "$gcc" "${options[@]}" -o "$elf" "$c" )
# # execute it:
# "${command[@]}"

name=$1
echo $name
cd $(dirname "$0")
cd Numix
pwd
for i in $(find  -name $name.svg); \
                do echo $i; \
                cp --parents $i ../NumixMsk; \
done