import httpx


async def upload_to_aem(
    aem_host: str,
    aem_token: str,
    folder_path: str,
    file_name: str,
    image_bytes: bytes,
    mime_type: str = "image/png",
) -> None:
    """Upload binary to AEM Assets via Direct Binary Upload protocol.

    The 3-step protocol:
    1. Initiate - AEM returns CDN-accelerated upload URIs
    2. PUT binary - Upload raw bytes to CDN edge
    3. Complete - AEM ingests the binary and kicks off processing
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Step 1: Initiate upload
        initiate_url = f"{aem_host}/content/dam/{folder_path}.initiateUpload.json"
        initiate_resp = await client.post(
            initiate_url,
            headers={"Authorization": f"Bearer {aem_token}"},
            data={
                "fileName": file_name,
                "fileSize": str(len(image_bytes)),
            },
        )
        initiate_resp.raise_for_status()
        initiate_data = initiate_resp.json()

        # uploadURIs[0] works for files under the maxPartSize threshold (~10MB).
        # For larger files, iterate over uploadURIs and upload chunks sequentially.
        upload_uri = initiate_data["files"][0]["uploadURIs"][0]
        complete_uri = initiate_data["completeURI"]
        upload_token = initiate_data["files"][0]["uploadToken"]

        # Step 2: PUT binary to CDN
        put_resp = await client.put(
            upload_uri,
            content=image_bytes,
            headers={
                "Content-Type": mime_type,
                "Content-Length": str(len(image_bytes)),
            },
        )
        put_resp.raise_for_status()

        # Step 3: Complete upload
        complete_resp = await client.post(
            f"{aem_host}{complete_uri}",
            headers={"Authorization": f"Bearer {aem_token}"},
            data={
                "fileName": file_name,
                "mimeType": mime_type,
                "uploadToken": upload_token,
            },
        )
        complete_resp.raise_for_status()
