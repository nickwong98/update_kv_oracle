import os
from dotenv import dotenv_values
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import jaydebeapi

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

# Update secrets in Azure Key Vault
def update_key_vault_secrets(vault_url, credentials):
    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    for username, password in credentials.items():
        secret_name = f"{username}"
        client.set_secret(secret_name, password)
        print(f"Updated secret for {username} in Key Vault.")

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
            cursor.execute(f"ALTER USER {username} IDENTIFIED BY {new_password}")
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

    # Update Azure Key Vault secrets
    update_key_vault_secrets(vault_url, credentials)

    # Update Oracle database passwords
    update_oracle_passwords(credentials, jdbc_url, driver_class, jar_file_path, db_user, db_password)

if __name__ == '__main__':
    main()