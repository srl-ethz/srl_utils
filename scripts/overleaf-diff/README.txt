Bash script for creating "tracked changes" outputs in Overleaf

You need installed on you machine:
* latexpand -- https://ctan.org/pkg/latexpand
* latexdiff -- https://ctan.org/pkg/latexdiff

###
For Mac users:
0) open Terminal app
1) install Homebrew https://brew.sh
	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2) install TexLive
	brew install texlive
3) install latexpand
	brew install latexpand
4) install latexdiff
	brew install latexdiff
###

Find your Overleaf Project ID by going to your overleaf document and inspecting its URL	https://www.overleaf.com/project/<overleaf_project_id>

Open the "History" of your Overleaf project and assign a label to the versions you want to track the changes using the "Label this version" button.

Identify the root or main .tex file of your Overleaf project.

Change your Terminals path to where the shell script is currently located at.
###
For Mac users, type "cd " and drag&drop the shell script (get_diff.sh) into the Terminal window. Delete "get_diff.sh" and press enter.
###

Copy this line into the Terminal, adapting the "<...>" sections with the information specific to your Overleaf project.

bash get_diff.sh -i <overleaf_project_id> -o <exact old version label> -n <exact new version label> -r <name of root file without .tex>

The script will be executed in your Terminal resulting in a "<name of root>_diff.tex" file that you can upload and compile on your Overleaf Project to obtain a pdf with highlighted differences.

Example:

bash get_diff.sh -i 614c49f383c9092a37543117 -o "18:50" -n "current" -r Main
