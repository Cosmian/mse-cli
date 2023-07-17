#!/bin/bash

# This scripts builds the PDF for a single document
# Usage: ./scripts/single_doc_build.sh [DOCUMENT ROOT]

if [ -z "$1" ]; then
    echo Please specify the root folder containing the mkdocs.yml file
    exit 1
fi

working_folder=$1

set -e

# Pre-requisites:
    # sudo dpkg -i pandoc-3.1.5-1-amd64.deb
    # sudo apt-get install fonts-noto-mono fonts-noto pandoc-citeproc librsvg2-bin
    # pip install pydoc-markdown git+https://github.com/twardoch/mkdocs-combine.git mkdocs-kroki-plugin mkdocs-material pandoc-latex-admonition install markdown-katex git+https://gitlab.com/myriacore/pandoc-kroki-filter.git

branch_tag="${CI_COMMIT_REF_NAME:-main}"
echo "Building documentation for branch/tag: ${branch_tag}"

# eisvogel_template=$(realpath pandoc/eisvogel.tex)
working_dir=$(pwd)
eisvogel_template="${working_dir}/pandoc/eisvogel.tex"

rm -fr doc_build

common_sed()
{
    args=$1
    file=$2
    os_version=$(uname)
    if [[ "Linux" == *"$os_version"* ]]; then
        # echo "Linux"
        sed -i "${args}" "$file"
    else
        # echo "Not Linux"
        sed -i '' "${args}" "$file"
    fi
}

 # Set root folder and working folder
doc=$(basename "$working_folder")
root=$(dirname "$working_folder")
output="doc"

# Merge .md files
# command added to build site directory to fix images displaying issue
pushd "${root}/${doc}"
if [[ -f "mkdocs.yml" ]]
then
    echo "mkdocs.yml exists in folder ${doc}"

    # create site directory
    mkdocs build

    # merge .md files into one .pd file
    mkdocscombine -o "${output}.pd"

    # Remove css classes added by mkdocscombine
    common_sed "s/{: .page-title}/ /g" "${output}.pd"

    # Replace $`...`$ by $...$
    #common_sed "s/$\`/$/g" "${output}.pd"
    #common_sed "s/\`\\$/$/g" "${output}.pd"

    # Replace ```math ... ```by $$...$$
    perl -i  -0pe "s/(\`\`\`math)(.+?)(\`\`\`)/\\$\\$\2\\$\\$/smg" "${output}.pd"

    # Replace ```toml ... ```
    perl -i  -0pe "s/(    \`\`\`toml)(.+?)(    \`\`\`)/\n\`\`\`toml\2\`\`\`/smg" "${output}.pd"

    # Replace **...** by \textbf{}
    perl -i  -0pe "s/(\*\*)([^*]+?)(\*\*)/\\\\underline{\2}/smg" "${output}.pd"

    # Replace !!! warning ... by \begin{warning}...\end{warning}
    perl -i  -0pe "s/(!!! warning \"[^\"\n]+\"\n\n)(.+?)\n/\\\begin{warning}\2\\\end{warning}\n/smg" "${output}.pd"

    # Replace !!! danger ... by \begin{danger}...\end{danger}
    perl -i  -0pe "s/(!!! danger \"[^\"\n]+\"\n\n)(.+?)\n/\\\begin{dang}\2\\\end{dang}\n/smg" "${output}.pd"

    # Replace !!! info ... by \begin{note}...\end{note}
    perl -i  -0pe "s/(!!! info \"[^\"\n]+\"\n\n)(.+?)\n/\\\begin{note}\2\\\end{note}\n/smg" "${output}.pd"

    # Replace !!! example ... by \begin{example}...\end{example}
    perl -i  -0pe "s/(!!! Examples \"[^\"\n]+\"\n\n)(.+?)\n/\\\begin{ex}\2\\\end{ex}\n/smg" "${output}.pd"

    # Replace markdown tab syntax for Pandoc
    grep -n '=== "' "${output}.pd" | cut -f1 -d: | while read -r source ; do
        #echo - "$source"
        common_sed "${source}s/===//g" "${output}.pd"
        common_sed "${source}s/\"//g" "${output}.pd"
    done

    # generate PDF
    pdf_title="${output}"
    pandoc --citeproc --from markdown --include-before-body=pandoc/macros.tex --template="${eisvogel_template}" includes.yml "${output}.pd" -s  -o "${pdf_title}.pdf" --listings --pdf-engine=xelatex --filter pandoc-kroki --number-sections -M reference-section-title=References 

    rm -r site/
fi