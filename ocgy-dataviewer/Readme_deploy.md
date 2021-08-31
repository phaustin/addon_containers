# steps to deploy changes to  https://dashboard.eoastest2.xyz/ocgy

1. `ssh n5jov`
2. `cd ~/repos/addon_containers`
3. git fetch and update main branch
   - `git fetch origin`
   - `git reset --hard origin/main` 
4. `docker-compose build ocgy`  -- rebuild build phaustin/ocgy:aug20
5. `docker-compose down  ocgy`   -- bring down the old ocgy container
6. `docker-compose up ocgy -d`  -- bring up the modified ocgy container
