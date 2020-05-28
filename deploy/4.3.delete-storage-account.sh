#!/bin/bash

source azure.conf

# Delete storage account
echo "Deleting storage account..."
az storage account delete \
  --name $m_api_storage \
  --resource-group $m_group \
  --yes