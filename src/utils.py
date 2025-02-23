import os
import chardet
import magic


def decode_bytes_with_fallback(content_bytes):
    """
    Attempts to decode a bytes object into a string using guessed encodings.

    This function first uses the 'magic' library to guess the encoding, and then
    employs 'chardet' to detect the encoding along with a confidence score.
    It will:
      - Try chardet's encoding first if its confidence is above 0.8.
      - Otherwise, attempt decoding with magic's encoding.
      - If that fails, try chardet's encoding a second time.
      - Finally, as a fallback, decode using UTF-8 with error replacement.

    Args:
        content_bytes (bytes): The byte sequence to decode.

    Returns:
        str or None: The decoded string if decoding was successful; otherwise, None.
    """
    m = magic.Magic(mime_encoding=True)
    encoding_m = m.from_buffer(content_bytes)

    detected = chardet.detect(content_bytes)
    encoding_d = detected.get("encoding")
    confidence_d = detected.get("confidence", 0)

    # If chardet is highly confident, try its encoding first
    if encoding_d and confidence_d > 0.8:
        try:
            return content_bytes.decode(encoding_d)
        except Exception:
            pass

    # Next, try the encoding from magic
    if encoding_m:
        try:
            return content_bytes.decode(encoding_m)
        except Exception:
            pass

    # If magic failed, try chardet's encoding again
    if encoding_d:
        try:
            return content_bytes.decode(encoding_d)
        except Exception:
            pass

    # As a last resort, use utf-8 with error replacement
    try:
        return content_bytes.decode('utf-8', errors='replace')
    except Exception:
        return None


def ensure_directory_exists(dir_out):
    """
    Creates a directory if it does not already exist.

    Args:
        dir_out (str): The path of the directory to create.
    """
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)


def write_text_to_file(text, out_file):
    """
    Saves a text string to a file in UTF-8 encoding.

    The text is encoded in UTF-8 and written in binary mode.

    Args:
        text (str): The text content to save.
        out_file (str): The file path where the text should be written.
    """
    with open(out_file, mode="wb") as f:
        f.write(text.encode('utf-8'))
