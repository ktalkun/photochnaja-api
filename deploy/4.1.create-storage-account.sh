#!/bin/bash

source azure.conf

# Create storage account
echo -e "\n-----Creating storage account:"
az storage account create \
  --name $m_api_storage \
  --resource-group $m_group \
  --location $m_location \
  --kind $m_api_storage_kind \
  --sku $m_api_storage_sku \
  --access-tier $m_api_storage_tier