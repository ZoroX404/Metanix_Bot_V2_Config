import os
import json
import asyncio
import logging
from urllib.parse import urlparse
import aiohttp
import tempfile

logger = logging.getLogger(__name__)

class Utilities:
    @staticmethod
    async def get_media_info(file_link):
        """
        Extract media information from a file without downloading the entire content.
        Uses ffprobe to analyze only the necessary parts of the file.
        
        Args:
            file_link (str): URL to the media file or local file path
            
        Returns:
            bytes: JSON formatted media information as bytes
        """
        is_url = urlparse(file_link).scheme in ('http', 'https')
        
        if is_url:
            # For remote files, download to a temporary file first
            # but we'll only download the minimum required data
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Use range requests to limit data transfer
                headers = {'Range': 'bytes=0-4194304'}  # Get first 4MB for initial headers
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(file_link, headers=headers) as response:
                        with open(temp_path, 'wb') as f:
                            # Write the partial file data
                            f.write(await response.content.read())
                
                file_path = temp_path
            except Exception as e:
                logger.error(f"Error downloading file header: {e}")
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
        else:
            # Local file
            file_path = file_link
            
        try:
            # Use ffprobe to extract media info - it's designed to work efficiently
            # even with partial files, as it primarily needs the headers
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                '-show_chapters',
                '-show_programs',
                file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                # If ffprobe failed with the partial file, we might need more data
                # This could happen with some file formats that store important metadata elsewhere
                if is_url and "Invalid data found when processing input" in stderr.decode():
                    logger.info("Initial probe failed, trying with more data...")
                    
                    # Clean up the temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    
                    # Use mediainfo as a fallback - it can often extract data even when ffprobe fails
                    mediainfo_cmd = [
                        'mediainfo',
                        '--Output=JSON',
                        file_link
                    ]
                    
                    mi_process = await asyncio.create_subprocess_exec(
                        *mediainfo_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    mi_stdout, mi_stderr = await mi_process.communicate()
                    
                    if mi_process.returncode == 0:
                        return mi_stdout
                    else:
                        logger.error(f"MediaInfo also failed: {mi_stderr.decode()}")
                        raise Exception(f"Failed to extract media info: {mi_stderr.decode()}")
                else:
                    logger.error(f"FFprobe error: {stderr.decode()}")
                    raise Exception(f"Failed to extract media info: {stderr.decode()}")
            
            # Process ffprobe output
            try:
                # Validate the JSON output
                media_info = json.loads(stdout)
                
                # Add some additional metadata about the extraction
                media_info["_extraction_method"] = "ffprobe"
                media_info["_extraction_timestamp"] = str(datetime.datetime.now())
                
                # Convert back to bytes for returning
                return json.dumps(media_info, indent=2).encode('utf-8')
            except json.JSONDecodeError:
                logger.error("Failed to parse ffprobe output as JSON")
                raise Exception("Failed to parse media info output")
            
        finally:
            # Clean up the temporary file if it exists
            if is_url and os.path.exists(temp_path):
                os.unlink(temp_path)
                
    @staticmethod
    async def get_media_info_direct(file_link):
        """
        Alternative method that uses mediainfo directly on the URL
        (mediainfo has direct URL support for many protocols)
        
        Args:
            file_link (str): URL to the media file
            
        Returns:
            bytes: JSON formatted media information as bytes
        """
        cmd = [
            'mediainfo',
            '--Output=JSON',
            file_link
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"MediaInfo error: {stderr.decode()}")
            raise Exception(f"Failed to extract media info: {stderr.decode()}")
        
        return stdout
