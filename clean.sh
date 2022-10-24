git filter-branch --tree-filter "rm -rf notebooks" --prune-empty HEAD
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d
echo notebooks/ >> .gitignore
git add .gitignore
git commit -m 'Removing notebooks from git history'
git gc
git push origin furui --force