# steps to deploy on eoastest5.xyz:8000

1. `ssh n3jov`
2. `cd ~/repos/ocgy-dataviewr`
3. git fetch and update raw branch __(be sure about using either `origin` or `upstream`)__
   - `git reset --hard upstream/raw` if you don’t care about the jovyan code, or
   - `git rebase upstream/raw` if there’s a change on jovyan you want to keep.
   - Use `git diff --name-only upstream/raw` or `git diff upstream/raw` to check difference between current and "fetched" branch.
4. `docker-compose build ocgy_dash`
5. `docker-compose down`
6. `docker-compose up -d`
