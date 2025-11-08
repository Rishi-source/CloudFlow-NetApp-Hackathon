from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from typing import List
from bson import ObjectId
from config.database import get_database
from models.cloud_credential import (
    AWSCredentialCreate, AzureCredentialCreate, GCPCredentialCreate,
    CloudCredentialResponse, CredentialTestResult
)
from utils.encryption import encrypt_credentials, decrypt_credentials
from middleware.auth_middleware import get_current_user
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage
import json
import tempfile
import os

router = APIRouter(prefix="/api/v1/credentials", tags=["cloud-credentials"])

@router.post("/aws", response_model=CloudCredentialResponse, status_code=status.HTTP_201_CREATED)
async def add_aws_credentials(creds: AWSCredentialCreate, current_user: dict = Depends(get_current_user)):
    credentials_collection = get_database()["cloud_credentials"]
    credentials_dict = {"access_key_id": creds.access_key_id, "secret_access_key": creds.secret_access_key, "region": creds.region, "bucket_name": creds.bucket_name}
    encrypted = encrypt_credentials(credentials_dict)
    credential_doc = {"user_id": current_user["sub"], "provider": "aws", "display_name": creds.display_name, "credentials_encrypted": encrypted, "is_active": True, "is_verified": False, "last_verified": None, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
    result = credentials_collection.insert_one(credential_doc)
    cred_id = str(result.inserted_id)
    return CloudCredentialResponse(id=cred_id, provider="aws", display_name=creds.display_name, is_active=True, is_verified=False, last_verified=None, created_at=credential_doc["created_at"])

@router.post("/azure", response_model=CloudCredentialResponse, status_code=status.HTTP_201_CREATED)
async def add_azure_credentials(creds: AzureCredentialCreate, current_user: dict = Depends(get_current_user)):
    credentials_collection = get_database()["cloud_credentials"]
    credentials_dict = {"account_name": creds.account_name, "account_key": creds.account_key, "container_name": creds.container_name}
    encrypted = encrypt_credentials(credentials_dict)
    credential_doc = {"user_id": current_user["sub"], "provider": "azure", "display_name": creds.display_name, "credentials_encrypted": encrypted, "is_active": True, "is_verified": False, "last_verified": None, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
    result = credentials_collection.insert_one(credential_doc)
    cred_id = str(result.inserted_id)
    return CloudCredentialResponse(id=cred_id, provider="azure", display_name=creds.display_name, is_active=True, is_verified=False, last_verified=None, created_at=credential_doc["created_at"])

@router.post("/gcp", response_model=CloudCredentialResponse, status_code=status.HTTP_201_CREATED)
async def add_gcp_credentials(creds: GCPCredentialCreate, current_user: dict = Depends(get_current_user)):
    credentials_collection = get_database()["cloud_credentials"]
    credentials_dict = {"project_id": creds.project_id, "bucket_name": creds.bucket_name, "service_account_json": creds.service_account_json}
    encrypted = encrypt_credentials(credentials_dict)
    credential_doc = {"user_id": current_user["sub"], "provider": "gcp", "display_name": creds.display_name, "credentials_encrypted": encrypted, "is_active": True, "is_verified": False, "last_verified": None, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
    result = credentials_collection.insert_one(credential_doc)
    cred_id = str(result.inserted_id)
    return CloudCredentialResponse(id=cred_id, provider="gcp", display_name=creds.display_name, is_active=True, is_verified=False, last_verified=None, created_at=credential_doc["created_at"])

@router.get("/", response_model=List[CloudCredentialResponse])
async def list_credentials(current_user: dict = Depends(get_current_user)):
    credentials_collection = get_database()["cloud_credentials"]
    credentials = list(credentials_collection.find({"user_id": current_user["sub"]}))
    return [CloudCredentialResponse(id=str(cred["_id"]), provider=cred["provider"], display_name=cred["display_name"], is_active=cred["is_active"], is_verified=cred["is_verified"], last_verified=cred.get("last_verified"), created_at=cred["created_at"]) for cred in credentials]

@router.post("/{credential_id}/test", response_model=CredentialTestResult)
async def test_credential(credential_id: str, current_user: dict = Depends(get_current_user)):
    credentials_collection = get_database()["cloud_credentials"]
    credential = credentials_collection.find_one({"_id": ObjectId(credential_id), "user_id": current_user["sub"]})
    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    decrypted = decrypt_credentials(credential["credentials_encrypted"])
    try:
        if credential["provider"] == "aws":
            s3 = boto3.client('s3', aws_access_key_id=decrypted["access_key_id"], aws_secret_access_key=decrypted["secret_access_key"], region_name=decrypted["region"])
            s3.head_bucket(Bucket=decrypted["bucket_name"])
            credentials_collection.update_one({"_id": ObjectId(credential_id)}, {"$set": {"is_verified": True, "last_verified": datetime.utcnow()}})
            return CredentialTestResult(success=True, message=f"Successfully connected to AWS S3 bucket: {decrypted['bucket_name']}", details={"region": decrypted["region"], "bucket": decrypted["bucket_name"]})
        elif credential["provider"] == "azure":
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={decrypted['account_name']};AccountKey={decrypted['account_key']};EndpointSuffix=core.windows.net"
            blob_service = BlobServiceClient.from_connection_string(connection_string)
            container_client = blob_service.get_container_client(decrypted["container_name"])
            container_client.get_container_properties()
            credentials_collection.update_one({"_id": ObjectId(credential_id)}, {"$set": {"is_verified": True, "last_verified": datetime.utcnow()}})
            return CredentialTestResult(success=True, message=f"Successfully connected to Azure container: {decrypted['container_name']}", details={"account": decrypted["account_name"], "container": decrypted["container_name"]})
        elif credential["provider"] == "gcp":
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_file.write(decrypted["service_account_json"])
                temp_path = temp_file.name
            try:
                storage_client = storage.Client.from_service_account_json(temp_path, project=decrypted["project_id"])
                bucket = storage_client.bucket(decrypted["bucket_name"])
                bucket.reload()
                credentials_collection.update_one({"_id": ObjectId(credential_id)}, {"$set": {"is_verified": True, "last_verified": datetime.utcnow()}})
                return CredentialTestResult(success=True, message=f"Successfully connected to GCP bucket: {decrypted['bucket_name']}", details={"project": decrypted["project_id"], "bucket": decrypted["bucket_name"]})
            finally:
                os.unlink(temp_path)
    except Exception as e:
        return CredentialTestResult(success=False, message=f"Connection failed: {str(e)}")

@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(credential_id: str, current_user: dict = Depends(get_current_user)):
    credentials_collection = get_database()["cloud_credentials"]
    result = credentials_collection.delete_one({"_id": ObjectId(credential_id), "user_id": current_user["sub"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    return None
