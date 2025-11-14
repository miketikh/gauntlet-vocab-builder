#!/usr/bin/env python3
"""
Configure S3 Bucket CORS for Vocab Builder

This script configures CORS (Cross-Origin Resource Sharing) on the S3 bucket
to allow direct browser uploads from the frontend application.

Run this script ONCE after creating the S3 bucket:
    python configure_s3_cors.py

The script uses AWS credentials from your .env file.
"""
import os
import sys
import json
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def configure_cors():
    """Apply CORS configuration to S3 bucket"""

    # Get configuration from environment
    bucket_name = os.getenv('AWS_S3_BUCKET')
    region = os.getenv('AWS_REGION', 'us-east-2')
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Validate environment variables
    if not bucket_name:
        print("❌ ERROR: AWS_S3_BUCKET not set in .env file")
        sys.exit(1)

    if not access_key or not secret_key:
        print("❌ ERROR: AWS credentials not set in .env file")
        print("   Required: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        sys.exit(1)

    print(f"📦 Configuring CORS for bucket: {bucket_name}")
    print(f"🌍 Region: {region}")

    # Initialize S3 client
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    except Exception as e:
        print(f"❌ Error creating S3 client: {e}")
        sys.exit(1)

    # CORS configuration
    # This allows the frontend (running on localhost:3000) to upload/download
    # files directly to/from S3 using presigned URLs
    cors_configuration = {
        'CORSRules': [
            {
                # Origins that are allowed to access the bucket
                # For production, add your production domain here
                'AllowedOrigins': [
                    'http://localhost:3000',  # Next.js dev server (default port)
                    'http://localhost:3001',  # Alternative dev port
                    # Add production domain when deploying:
                    # 'https://your-production-domain.com',
                ],

                # HTTP methods allowed for CORS requests
                'AllowedMethods': [
                    'GET',   # For downloading files
                    'PUT',   # For uploading files (presigned URLs use PUT)
                    'POST',  # For alternative upload methods
                    'HEAD',  # For checking file existence
                ],

                # Request headers that can be used
                'AllowedHeaders': [
                    '*',  # Allow all headers (Content-Type, etc.)
                ],

                # Response headers that browser can access
                'ExposeHeaders': [
                    'ETag',                          # File integrity check
                    'x-amz-server-side-encryption',  # Encryption status
                    'x-amz-request-id',              # Request tracking
                    'x-amz-id-2',                    # Extended request ID
                ],

                # How long browser can cache preflight response (1 hour)
                'MaxAgeSeconds': 3600
            }
        ]
    }

    try:
        # Apply CORS configuration to bucket
        print(f"⏳ Applying CORS configuration...")
        s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
        print(f"✅ CORS configuration applied successfully!")

        # Verify configuration
        print(f"⏳ Verifying CORS configuration...")
        response = s3_client.get_bucket_cors(Bucket=bucket_name)
        num_rules = len(response.get('CORSRules', []))
        print(f"✅ Verified: {num_rules} CORS rule(s) configured")

        # Display configured origins
        if response.get('CORSRules'):
            print(f"\n📋 Configured allowed origins:")
            for origin in response['CORSRules'][0].get('AllowedOrigins', []):
                print(f"   • {origin}")

        print(f"\n🎉 CORS configuration complete!")
        print(f"\nYou can now upload documents from the frontend.")
        print(f"\n💡 Remember to add your production domain to AllowedOrigins before deploying!")

    except s3_client.exceptions.NoSuchBucket:
        print(f"❌ Error: Bucket '{bucket_name}' does not exist")
        print(f"   Please create the bucket first or check the bucket name in .env")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error configuring CORS: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Check AWS credentials have S3 permissions (s3:PutBucketCORS)")
        print(f"2. Verify bucket name is correct: {bucket_name}")
        print(f"3. Ensure bucket is in region: {region}")
        sys.exit(1)


def check_cors():
    """Check current CORS configuration"""

    bucket_name = os.getenv('AWS_S3_BUCKET')
    region = os.getenv('AWS_REGION', 'us-east-2')

    if not bucket_name:
        print("❌ ERROR: AWS_S3_BUCKET not set in .env file")
        sys.exit(1)

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=region
    )

    try:
        response = s3_client.get_bucket_cors(Bucket=bucket_name)
        print(f"📋 Current CORS configuration for {bucket_name}:")
        print(json.dumps(response['CORSRules'], indent=2))
    except s3_client.exceptions.NoSuchCORSConfiguration:
        print(f"⚠️  No CORS configuration found for bucket: {bucket_name}")
    except Exception as e:
        print(f"❌ Error checking CORS: {e}")
        sys.exit(1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Configure S3 bucket CORS for Vocab Builder'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check current CORS configuration without making changes'
    )

    args = parser.parse_args()

    if args.check:
        check_cors()
    else:
        configure_cors()
