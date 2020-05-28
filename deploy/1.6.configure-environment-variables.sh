#!/bin/bash

source azure.conf

# Set DATABASE_USER variable
echo -e "\n-----Setting DATABASE_USER variable:"
az webapp config appsettings set \
  --name $m_api \
  --resource-group $m_group \
  --settings DATABASE_USER=$m_api_db_login

# Set DATABASE_PASSWORD variable
echo -e "\n-----Setting DATABASE_PASSWORD variable:"
az webapp config appsettings set \
  --name $m_api \
  --resource-group $m_group \
  --settings DATABASE_PASSWORD=$m_api_db_password

# Set DATABASE_HOST variable
echo -e "\n-----Setting DATABASE_HOST variable:"
az webapp config appsettings set \
  --name $m_api \
  --resource-group $m_group \
  --settings DATABASE_HOST="$m_api_db_server.database.windows.net"

# Set DATABASE_PORT variable
echo -e "\n-----Setting DATABASE_PORT variable:"
az webapp config appsettings set \
  --name $m_api \
  --resource-group $m_group \
  --settings DATABASE_PORT="1433"

# Set DATABASE_NAME variable
echo -e "\n-----Setting DATABASE_NAME variable:"
az webapp config appsettings set \
  --name $m_api \
  --resource-group $m_group \
  --settings DATABASE_NAME=$m_api_database

# Set DATABASE_DRIVER variable
echo -e "\n-----Setting DATABASE_DRIVER variable:"
az webapp config appsettings set \
  --name $m_api \
  --resource-group $m_group \
  --settings DATABASE_DRIVER="ODBC+Driver+17+for+SQL+Server"

# Set STORAGE_CONNECTION_STRING variable
echo -e "\n-----Setting STORAGE_CONNECTION_STRING variable:"
az webapp config appsettings set \
  --name $m_api \
  --resource-group $m_group \
  --settings STORAGE_CONNECTION_STRING=$m_api_storage_conn_string
