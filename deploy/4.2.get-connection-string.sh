#!/bin/bash

source azure.conf

# Get connection string for storage account
echo -e "\n-----Getting connection string:"
az storage account show-connection-string \
  --name $m_api_storage \
  --resource-group $m_group