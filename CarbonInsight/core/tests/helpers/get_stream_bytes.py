from io import BytesIO


def get_stream_bytes(response) -> bytes:
    """
    Helper to read the streaming content of a response into bytes.
    """
    buffer = BytesIO()
    for chunk in response.streaming_content:
        buffer.write(chunk)
    return buffer.getvalue()