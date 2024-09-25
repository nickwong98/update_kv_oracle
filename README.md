# update_kv_oracle
This Python script update Oracle 11g username/password and corresponding Azure Key Vault secrets


## Pre-requisites
- Python 3.9
- Python packages: azure-keyvault-secrets azure-identity jaydebeapi JPype1 python-dotenv
- Java Runtime Environment (JRE) 11
- az login with Key Vault Administrator role
- Database login with "ALTER USER" privilege
- ojdbc6.jar

## How to use
1. Update credentials.txt for username/password pairs
2. Update .env for Azure Key Vault and Oracle 11g database information
3. Set JAVA_HOME environment variable
4. az login
5. Run update_orapwd.py

## Notes
- Azure Key Vault secret names can only contain alphanumeric characters and dashes, so database logins with characters other than that are ***not supported***.
