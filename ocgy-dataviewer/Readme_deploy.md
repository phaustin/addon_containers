# steps to deploy changes to  dashboard.eoas.ubc.ca/ocgy

1. `ssh dashjov`
2. `cd ~/repos/addon_containers`
3. git fetch and update main branch
   - git checkout dev24
   - `git fetch origin`
   - `git reset --hard origin/dev25` 
4. `docker compose build ocgy`  -- rebuild build phaustin/ocgy:aug20
5. `docker-compose down  ocgy`   -- bring down the old ocgy container
6. `docker-compose up ocgy -d`  -- bring up the modified ocgy container
