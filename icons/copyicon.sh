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

cd $dirDest

# Clean strange folders
echo "Cleaning strange folders"
echo "------------------------"
for i in 16 22 24 32 48 64;
do

    if [ -d "NumixMsk/$i/" ]; then
        echo "NumixMsk/$i/"
        cp -r "NumixMsk/$i/*" "NumixMsk/$(echo $i)x$(echo $i)/"
        rm -R "NumixMsk/$i/"
    fi

done

# echo $dirDest
# # Move 256 to scalable
# if [ -d "NumixMsk/256x256/" ]; then
#
#     echo "Move 256x256 to scalable"
#     echo "------------------------"
#     cp -r NumixMsk/256x256/* "NumixMsk/scalable/"
#     rm -R "NumixMsk/256x256/"
# fi
