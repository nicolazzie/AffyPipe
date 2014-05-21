#!/bin/sh
### This small bash creates a CEL list file from the current folder, extracting the whole path from pwd.
### Coded originally by Ezequiel L. Nicolazzi (Fondazione Parco Tecnologico Padano).
### March 2014
### For comments and bug report: ezequiel.nicolazzi@tecnoparco.org
### All rights... naaaaaaaahhh. Just use it and modify at will!

echo;echo "Creating .CEL files list, needed as input file for AffyPipe pipeline"

# Output file
outf=mycellistfile.txt
# Current working directory
here=`pwd`
# Find cel files
celfiles=`find . -maxdepth 1 -type f -name "*.CEL" 2>/dev/null | cut -b3-`

if [[ -z "$celfiles" ]];then
    echo;echo "ERROR: No .CEL file was found in this directory."
    echo "       Please place this program in the .CEL file folder and run again!";exit
else
    dim=`ls *.CEL| wc -l | awk '{print $1}'`
fi

echo "A total of $dim .CEL files found and added to $outf"

# Create the output file
echo "cel_files" > $outf
for file in $celfiles;
do
    echo $here/$file >> $outf
done

echo;echo;echo "Bazinga! It's done!"
echo "Please check file $outf"
echo "Have a nice day...:)";echo


