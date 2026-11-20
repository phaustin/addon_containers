# Deploy the Bamfield CTD archive dashboard to dashboard.eoas.ubc.ca/bamfield-ctd

The app is developed and its data built in the EOSC 473 course folder
(`473_2026/Past_CTD_data/ctd_dashboard/`). This folder holds only what runs on the server.

## Update the copy here (on the laptop)

1. In `ctd_dashboard/`, rebuild the data if anything changed: `build_dashboard_data.py`
   (`notebook` env).
2. Run `ctd_dashboard/publish_to_addon_containers.sh`. It copies `app.py`, `plotting.py`,
   `upload.py`, `shared.py`, `instructions.md`, `attributions.md`, `assets/` and the five data
   files the app reads into `bamfield-ctd/dashdir/`.
3. Commit on `dev25` and push.

## On the server (ssh as jovyan)

1. Check the traefik proxy is running (see `ocgy-dataviewer-class/Readme_deploy.md`, step 0).
2. `cd ~/repos/addon_containers`, then `git checkout dev25`, `git fetch origin`,
   `git rebase origin/dev25`.
3. `docker compose -f docker-compose-bamfield-ctd.yml build`
4. `docker compose -f docker-compose-bamfield-ctd.yml down bamfield-ctd` (skip the first time)
5. `docker compose -f docker-compose-bamfield-ctd.yml up -d`
6. Open https://dashboard.eoas.ubc.ca/bamfield-ctd/

## Notes

- The proxy path `bamfield-ctd` appears in three places in `docker-compose-bamfield-ctd.yml`:
  the router rule, the stripprefix and `DASH_REQUESTS_PATHNAME_PREFIX`. They must match.
  `app.py` is not edited for deployment.
- Uploaded casts stay in the viewer's browser (`dcc.Store`); nothing is written on the server.
- Tested locally under gunicorn with the `/bamfield-ctd/` prefix (20 Nov 2026). The Docker
  image itself has not been built off the server.
