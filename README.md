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
  - For upload: `./install.sh && dev_appserver --admin_port 8085 --port 8086 upload.yaml`
  - For apiv2: `pip install -r requirements.txt && python manage.py runserver`

4) Run ETL script:
  - `./run_etl.sh`

