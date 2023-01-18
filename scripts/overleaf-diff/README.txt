Bash script for creating diff .tex files from Overleaf documents with different *labeled* versions.
(Robert needed this because a grant collaborator doesn't know how to use latex or overleaf, but wanted to see diffs)

Usage:

bash get_diff.sh -i <overleaf_project_id> -o <exact old version label> -n <exact new version label> -r <name of root file without .tex>

You will get a <name of root>_diff.tex file in the same folder in which you ran the script. You can then upload this file to the overleaf project and compile it to obtain a pdf with highlighted differences.

Example:

bash get_diff.sh -i 63bbe166341302e3d3346f38 -o "Jan 16 at 0-16am" -n "17 Jan Version for Julia" -r root

Notes:

Keep in mind that overleaf urls are in the format https://www.overleaf.com/project/<overleaf_project_id> .

You need to create version labels in Overleaf for this to work.
