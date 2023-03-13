#!/bin/bash
# file: get_diff.sh

# exit when any command fails
set -e

print_readme() {
    script_dir=$(dirname "$0")
    readme_file="$script_dir"/README.txt
    echo "printing $readme_file"
    cat "$readme_file"
}

# if no arguments are passed, print the readme
if [ $# -eq 0 ]; then
  print_readme
  exit 1
fi

# parse input flags
while getopts i:o:n:r:h flag
do
    case "${flag}" in
    	i) idoverleaf=${OPTARG};;
        o) oldlabel=${OPTARG};;
        n) newlabel=${OPTARG};;
        r) rootname=${OPTARG};;
        h) print_readme; exit 0;;
    esac
done
echo "Overleaf Id: $idoverleaf";
echo "Old Version Label: $oldlabel";
echo "New Version Label: $newlabel";
echo "Root Filename: $rootname";

if [ ! -d "$idoverleaf" ] ; then
	git clone https://git.overleaf.com/"$idoverleaf"
	cd "$idoverleaf"
else
	cd "$idoverleaf"
	git pull
fi



hash1=$(git log --grep="$oldlabel" --pretty=format:'%H')
hash2=$(git log --grep="$newlabel" --pretty=format:'%H')

# check if hash is empty
if [ -z "$hash1" ]; then
    echo "label [$oldlabel] not found in git log, aborting..."
    exit 1
fi
if [ -z "$hash2" ]; then
    echo "label [$newlabel] not found in git log, aborting..."
    exit 1
fi

# checkout old label
echo "git checkout $oldlabel";
echo "hash is $hash1"
git checkout $hash1
echo "git checkout successful for label $oldlabel";

# flatten the multifile latex document into single file
latexpand "$rootname".tex > "$rootname"_v1_flat.tex

# checkout new label
echo "git checkout $newlabel";
echo "hash is $hash2"
git checkout $hash2
echo "git checkout successful for label $newlabel";

# flatten the multifile latex document into single file
latexpand "$rootname".tex > "$rootname"_v2_flat.tex

# switch back to master branch
git switch master

cd ..
# run a diff between the old label and new label branch
latexdiff "$idoverleaf"/"$rootname"_v1_flat.tex "$idoverleaf"/"$rootname"_v2_flat.tex > "$rootname"_diff.tex
echo "latexdiff finished";
