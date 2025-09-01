# steps to deploy dashboard changes to  dashboard.eoas.ubc.ca/ocgy

1. ssh into dashboard as user jovyan
0. Make sure that the ocese_trafik container defined in `~/repos/ocese_traefik` is running:
   - `traefik:v2.5` should be a running process listed by the command 
     `docker ps`
    - The `proxy_aug07` local network should be listed by the command 
    `docker network list`
    - visiting the url https://dashboard.eoas.ubc.ca/traefik should show the traefik dashboard after you provide the userid and password
   - visiting the url https://dashboard.eoas.ubc.ca/test should run https://hub.docker.com/r/traefik/whoami

2. `cd ~/repos/addon_containers`
3. git fetch and update dev25 branch
   - `git checkout dev25`
   - `git fetch origin`
   - `git rebase origin/dev25` 
4. run 
    `docker compose -f docker-compose-ocgy.yml build`
    to rebuild the image named `phaustin/ocgy25:2025`
    Your changes will not make it into the container without a rebuild
5. run
    `docker compose -f docker-compose-ocgy.yml down ocgy25`
   to bring down the old ocgy container
6. run
   `docker compose -f docker-compose-ocgy.yml up -d`  
   to bring up the modified ocgy container in detached mode

## debugging

1. If you are getting a python error about a missing dictionary key, make sure you are typing `docker compose` not `docker-compose`
2. The routing endpoint `ocgy` has to exactly match in three different places: line 12 and line 19 in `docker-compose-ocgy.yml` and
   line 39 in `ocgy-dataviewer/dashdir/app.py`
3. The line defining `requests_pathname_prefix='/ocgy/'` in `ocgy-dataviewer/dashdir/app.py` has to be uncommented

## useful docker commands

- `docker ps` lists all running containers
- `docker ps -a` lists all containers
- `docker ps -a | awk '{print $NF}'` prints the last column (container names)
- `docker rm name` deletes a container
- `docker image list` lists all images
- `docker image rmi name` removes an image
- To clear all containers, volumes, images and unused networks

      #!/bin/bash -v
      docker-compose down
      docker stop $(docker ps -aq)
      docker rm $(docker ps -a -q)
      docker volume rm $(docker volume ls -q)
      docker network prune -f
      #docker rmi $(docker images -q)`

- To start and look inside an image

      docker run -i -t phaustin/base_image:2025 /bin/bash

- To look inside a running container named ocgy25

      docker exec -it ocgy25 /bin/bash    

- To rebuild the base image

      cd ~/repos/addon_containers/base_image
      docker build -t phaustin/base_image:2025

- To push dashboard changes back to the addon_containers repo run:

      gh-scope-creds

  This will prompt you to login to your github account at https://github.com/login/device and enter an 8 digit code, which will set up an authflow to permit pushing back to github for 8 hours.  See https://github.com/jupyterhub/gh-scoped-creds
  
 



