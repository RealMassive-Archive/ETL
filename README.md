# ETL
Currently supported:
 - Building asset, Space asset, Space leases, Attachments (except videos), Users, Contacts, Team Members, Teams


## Instructions
1) Build this environment (virtual environment recommended):
  - `pip install -r requirements.txt`

2) Clone `upload` and `apiv2` repositories:
  - git@github.com:RealMassive/upload.git@development
  - git@github.com:RealMassive/apiv2.git@staging

3) Build and run `upload` and `apiv2` servers (virtual environments recommended):
  - `./deploy_local.sh  # For upload`
  - `pip install -r requirements.txt && python manage.py runserver  # For apiv2`

4) Run ETL script:
  - `./run_etl.sh`

