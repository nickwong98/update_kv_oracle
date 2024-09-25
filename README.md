# update_kv_oracle
This Python script update Oracle 11g username/password and corresponding Azure Key Vault secrets


## Pre-requsites
- Python 3.9
- Python packages: azure-keyvault-secrets azure-identity jaydebeapi JPype1 python-dotenv
- Java Runtime Environment (JRE) 11
- az login with Key Vault Administrator role
- Database login with "ALTER USER" privilege
- ojdbc6.jar

## How to use
- Update credentials.txt for username/password pairs
- Update .env for Azure Key Vault and Oracle 11g database information
- Set JAVA_HOME environment variable
- az login
- Run update_orapwd.py
