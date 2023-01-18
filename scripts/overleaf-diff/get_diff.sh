while getopts i:o:n:r: flag
do
    case "${flag}" in
    	i) idoverleaf=${OPTARG};;
        o) oldlabel=${OPTARG};;
        n) newlabel=${OPTARG};;
        r) rootname=${OPTARG};;
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

git checkout $hash1
latexpand "$rootname".tex > "$rootname"_v1_flat.tex

git checkout $hash2
latexpand "$rootname".tex > "$rootname"_v2_flat.tex

git switch master

cd ..
latexdiff "$idoverleaf"/"$rootname"_v1_flat.tex "$idoverleaf"/"$rootname"_v2_flat.tex > "$rootname"_diff.tex
