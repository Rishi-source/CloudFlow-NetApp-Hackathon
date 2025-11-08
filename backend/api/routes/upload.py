from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
import hashlib
from datetime import datetime
import random
from bson import ObjectId
from config.database import get_database
from streaming.kafka_producer import send_event
from middleware.auth_middleware import get_current_user
from utils.encryption import decrypt_credentials
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage
import tempfile
import os
import asyncio

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])

@router.post("/file")
async def upload_file(file: UploadFile = File(...), credential_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    try:
        content = await file.read()
        file_size = len(content)
        checksum = hashlib.sha256(content).hexdigest()
        if file_size > 1024 * 1024 * 1024:
            tier = "cold"
        elif file_size > 100 * 1024 * 1024:
            tier = "warm"
        else:
            tier = "hot"
        credentials_collection = get_database()["cloud_credentials"]
        is_real_upload = False
        cloud_url = ""
        location = "simulation"
        if credential_id:
            credential = credentials_collection.find_one({"_id": ObjectId(credential_id), "user_id": current_user["sub"]})
            if credential:
                decrypted = decrypt_credentials(credential["credentials_encrypted"])
                try:
                    if credential["provider"] == "aws":
                        s3 = boto3.client('s3', aws_access_key_id=decrypted["access_key_id"], aws_secret_access_key=decrypted["secret_access_key"], region_name=decrypted["region"])
                        s3_key = f"uploads/{current_user['sub']}/{datetime.utcnow().strftime('%Y%m%d')}/{file.filename}"
                        s3.put_object(Bucket=decrypted["bucket_name"], Key=s3_key, Body=content)
                        cloud_url = f"s3://{decrypted['bucket_name']}/{s3_key}"
                        location = "aws"
                        is_real_upload = True
                    elif credential["provider"] == "azure":
                        connection_string = f"DefaultEndpointsProtocol=https;AccountName={decrypted['account_name']};AccountKey={decrypted['account_key']};EndpointSuffix=core.windows.net"
                        blob_service = BlobServiceClient.from_connection_string(connection_string)
                        blob_name = f"uploads/{current_user['sub']}/{datetime.utcnow().strftime('%Y%m%d')}/{file.filename}"
                        blob_client = blob_service.get_blob_client(container=decrypted["container_name"], blob=blob_name)
                        blob_client.upload_blob(content, overwrite=True)
                        cloud_url = f"azure://{decrypted['account_name']}/{decrypted['container_name']}/{blob_name}"
                        location = "azure"
                        is_real_upload = True
                    elif credential["provider"] == "gcp":
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                            temp_file.write(decrypted["service_account_json"])
                            temp_path = temp_file.name
                        try:
                            storage_client = storage.Client.from_service_account_json(temp_path, project=decrypted["project_id"])
                            bucket = storage_client.bucket(decrypted["bucket_name"])
                            blob_name = f"uploads/{current_user['sub']}/{datetime.utcnow().strftime('%Y%m%d')}/{file.filename}"
                            blob = bucket.blob(blob_name)
                            blob.upload_from_string(content)
                            cloud_url = f"gs://{decrypted['bucket_name']}/{blob_name}"
                            location = "gcp"
                            is_real_upload = True
                        finally:
                            os.unlink(temp_path)
                except Exception as upload_error:
                    raise HTTPException(status_code=500, detail=f"Cloud upload failed: {str(upload_error)}")
        data_object = {"user_id": current_user["sub"], "name": file.filename, "size_bytes": file_size, "current_tier": tier, "current_location": location, "is_real": is_real_upload, "cloud_url": cloud_url, "credential_id": credential_id, "access_count": 0, "last_accessed": datetime.utcnow(), "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(), "metadata": {"file_type": file.filename.split('.')[-1] if '.' in file.filename else 'unknown', "owner": current_user["email"], "tags": ["real" if is_real_upload else "simulated", "uploaded"], "description": f"Uploaded by {current_user['email']}"}, "checksum": f"sha256:{checksum}", "encryption_enabled": False, "access_policy_id": None, "predicted_tier": None, "cost_per_month": 0.0}
        collection = get_database()["data_objects"]
        result = collection.insert_one(data_object)
        object_id = str(result.inserted_id)
        try:
            await send_event("file_uploaded", {"object_id": object_id, "filename": file.filename, "size_bytes": file_size, "tier": tier, "location": location, "is_real": is_real_upload, "timestamp": datetime.utcnow().isoformat()})
        except Exception as kafka_error:
            pass
        return {"status": "success", "message": f"File {file.filename} uploaded to {location}", "object_id": object_id, "is_real": is_real_upload, "cloud_url": cloud_url if is_real_upload else None, "data": {"name": file.filename, "size_bytes": file_size, "size_mb": round(file_size / (1024 * 1024), 2), "tier": tier, "location": location}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/simulate")
async def simulate_upload(filename: str, size_mb: float = 100, location: Optional[str] = None):
    try:
        size_bytes = int(size_mb * 1024 * 1024)
        
        
        if size_bytes > 100 * 1024 * 1024:
            tier = "warm" if size_bytes < 1024 * 1024 * 1024 else "cold"
        else:
            tier = "hot"
        
        locations = ["aws", "azure", "gcp", "on-premise"]
        location = location if location else random.choice(locations)
        
        
        data_object = {
            "name": filename,
            "size_bytes": size_bytes,
            "current_tier": tier,
            "current_location": location,
            "access_count": 0,
            "last_accessed": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "metadata": {
                "file_type": "simulated",
                "owner": "system",
                "tags": ["simulated", "test"],
                "description": f"Simulated upload: {filename}"
            },
            "checksum": f"sha256:simulated_{random.randint(1000, 9999)}",
            "encryption_enabled": False,
            "access_policy_id": None,
            "predicted_tier": None,
            "cost_per_month": 0.0,
            "url": ""
        }
        
        collection = get_database()["data_objects"]
        result = collection.insert_one(data_object)
        object_id = str(result.inserted_id)
        
        
        await send_event("file_uploaded", {
            "object_id": object_id,
            "filename": filename,
            "size_bytes": size_bytes,
            "tier": tier,
            "location": location,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "status": "success",
            "message": f"File {filename} uploaded successfully",
            "object_id": object_id,
            "data": {
                "name": filename,
                "size_bytes": size_bytes,
                "size_mb": round(size_bytes / (1024 * 1024), 2),
                "tier": tier,
                "location": location,
                "file_type": "simulated"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
