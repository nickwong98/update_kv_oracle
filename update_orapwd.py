import os
import time
from dotenv import dotenv_values
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import jaydebeapi

### !!! Please read the following before execution !!!

### run get_key_vault_secrets/access_oracle for access confirmation before
### running update_key_vault_secrets/update_oracle_passwords

### if get_key_vault_secrets/access_oracle fail, read the following

### check azure access, e.g. az account list

### SET JAVA_HOME before running this script
### e.g. $env:JAVA_HOME="C:\Users\lmwn\Downloads\sqldeveloper\jdk"

### Make user ojdbc is accessible, e.g. "./ojdbc6.jar"

### this script takes 7 sec to finish in OLT staging environment


# oracledb does not support 11g
#import oracledb

# cx_Oracle requires instant client
#import cx_Oracle

# Load username, password pairs from a text file
def load_credentials(file_path):
    credentials = {}
    with open(file_path, 'r') as file:
        for line in file:
            username, password = line.strip().split(',')
            credentials[username] = password
    return credentials

# Get secrets in Azure Key Vault
def get_key_vault_secrets(vault_url, credentials):
    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    for username, password in credentials.items():
        secret_name = f"{username}"
        retrieved_secret = client.get_secret(secret_name)
        print(f"{username} {retrieved_secret.value}")
        #print(f"Retrieved secret for {username} in Key Vault.")

# Access Oracle database
def access_oracle(credentials,jdbc_url, driver_class, jar_file_path, db_user, db_password):
    try:
        # Establish the database connection
        connection = jaydebeapi.connect(
            driver_class,
            jdbc_url,
            [db_user, db_password],
            jar_file_path
        )
        cursor = connection.cursor()
        
        # Iterate over the users dictionary and update passwords
        for username, new_password in credentials.items():
            cursor.execute(f"SET ROLE ALL")
            print(f"Access succeeded for {username} in Oracle database.")
        
        # Commit the changes
        connection.commit()
        
    except jaydebeapi.DatabaseError as e:
        print(f"Error updating Oracle database: {e}")
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Update secrets in Azure Key Vault
def update_key_vault_secrets(vault_url, credentials):
    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    for username, password in credentials.items():
        secret_name = f"{username}"
        client.set_secret(secret_name, password)
        print(f"Updated secret for {username} in Key Vault.")

# Backup secrets in Azure Key Vault
def backup_key_vault_secrets(vault_url, credentials):
    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    for username, password in credentials.items():
        secret_name = f"{username}"
        secret_backup = client.backup_secret(secret_name)
        backupfilename = f"kv_backup_{secret_name}.txt"
        with open(backupfilename, "wb") as backupfile:
            backupfile.write(secret_backup)
            backupfile.close()
        print(f"Backed up secret for {username} in Key Vault.")

# Delete and purge secrets in Azure Key Vault
def delete_key_vault_secrets(vault_url, credentials):
    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    for username, password in credentials.items():
        secret_name = f"{username}"

        print("\n.. Deleting secret...")
        delete_operation = client.begin_delete_secret(secret_name)
        deleted_secret = delete_operation.result()
        assert deleted_secret.name
        print(f"Deleted secret with name '{deleted_secret.name}'")

        # Wait for the deletion to complete before purging the secret.
        delete_operation.wait()
        print("\n.. Purge the secret")
        client.purge_deleted_secret(secret_name)
        print(f"Purged secret with name '{secret_name}'")


# Restore secrets in Azure Key Vault, the Key Vault must be the original one
def restore_key_vault_secrets(vault_url, credentials):
    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    for username, password in credentials.items():
        secret_name = f"{username}"

        backupfilename = f"kv_backup_{secret_name}.txt"
        with open(backupfilename, "rb") as backupfile:
            print("\n.. Restore the secret using the backed up secret bytes")
            secret_properties = client.restore_secret_backup(backupfile.read())
            print(f"Restored secret with name '{secret_properties.name}'")
            backupfile.close()

# Update Oracle database passwords
def update_oracle_passwords(credentials,jdbc_url, driver_class, jar_file_path, db_user, db_password):
    try:
        # Establish the database connection
        connection = jaydebeapi.connect(
            driver_class,
            jdbc_url,
            [db_user, db_password],
            jar_file_path
        )
        cursor = connection.cursor()
        
        # Iterate over the users dictionary and update passwords
        for username, new_password in credentials.items():
            cursor.execute(f"SET ROLE ALL")
            cursor.execute(f"ALTER USER {username} IDENTIFIED BY \"{new_password}\"")
            #print(f"Trying to update password for {username} in Oracle database.")
            #cursor.execute(f"select count(9) from dba_users where username='{username}'")
            print(f"Updated password for {username} in Oracle database.")
        
        # Commit the changes
        connection.commit()
        
    except jaydebeapi.DatabaseError as e:
        print(f"Error updating Oracle database: {e}")
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Main function
def main():
    # Define file path, vault URL, and Oracle connection details
    config = dotenv_values(".env")

    credentials_file = 'credentials.txt'
    vault_url = config.get('vault_url')

    # Define the JDBC connection parameters
    jdbc_url = config.get('jdbc_url')
    driver_class = "oracle.jdbc.driver.OracleDriver"
    jar_file_path = config.get('jar_file_path')
    db_user = config.get('db_user')
    db_password = config.get('db_password')

    # Load credentials
    credentials = load_credentials(credentials_file)

    # Get Azure Key Vault secrets
    #get_key_vault_secrets(vault_url, credentials)

    # Back up Azure Key Vault secrets
    #backup_key_vault_secrets(vault_url, credentials)

    # Restore Azure Key Vault secrets, delete original secret beforehand to avoid secret name conflict
    # The purge will take some time, so wait before restoring the backup to avoid a conflict.
    #delete_key_vault_secrets(vault_url, credentials)
    #time.sleep(60)
    #restore_key_vault_secrets(vault_url, credentials)

    # Access Oracle database passwords
    # access_oracle(credentials, jdbc_url, driver_class, jar_file_path, db_user, db_password)

    # Update Azure Key Vault secrets
    #backup_key_vault_secrets(vault_url, credentials)
    #update_key_vault_secrets(vault_url, credentials)

    # Update Oracle database passwords
    #update_oracle_passwords(credentials, jdbc_url, driver_class, jar_file_path, db_user, db_password)

if __name__ == '__main__':
    main()
