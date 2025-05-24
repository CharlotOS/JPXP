import struct
import json
from PIL import Image
import io
import avif  # pyavif library

MAGIC = b'JPX+'
VERSION = 1

class JPXPFile:
    def __init__(self, width=0, height=0, compression='AVIF', alpha=False, hdr=False, image_bytes=b''):
        self.width = width
        self.height = height
        self.compression = compression  # 'AVIF' or 'JPEGXL'
        self.alpha = alpha
        self.hdr = hdr
        self.image_bytes = image_bytes

    def encode(self) -> bytes:
        flags = 0
        if self.alpha:
            flags |= 1 << 0
        if self.hdr:
            flags |= 1 << 1
        if self.compression.upper() == 'JPEGXL':
            flags |= 1 << 3

        header = struct.pack('<4sBB10s', MAGIC, VERSION, flags, b'\x00' * 10)

        metadata = {
            "width": self.width,
            "height": self.height,
            "compression": self.compression,
            "alpha": self.alpha,
            "hdr": self.hdr
        }
        meta_json = json.dumps(metadata).encode('utf-8')
        meta_len = struct.pack('<I', len(meta_json))

        image_len = struct.pack('<I', len(self.image_bytes))

        return header + meta_len + meta_json + image_len + self.image_bytes

    @staticmethod
    def decode(data: bytes) -> 'JPXPFile':
        magic, version, flags, _ = struct.unpack('<4sBB10s', data[:16])
        if magic != MAGIC:
            raise ValueError("Invalid JPXP file magic bytes")

        alpha = bool(flags & (1 << 0))
        hdr = bool(flags & (1 << 1))
        compression = 'JPEGXL' if (flags & (1 << 3)) else 'AVIF'

        meta_len = struct.unpack('<I', data[16:20])[0]
        meta_json = data[20:20 + meta_len].decode('utf-8')
        metadata = json.loads(meta_json)

        image_start = 20 + meta_len
        image_len = struct.unpack('<I', data[image_start:image_start + 4])[0]
        image_bytes = data[image_start + 4:image_start + 4 + image_len]

        return JPXPFile(
            width=metadata.get("width", 0),
            height=metadata.get("height", 0),
            compression=metadata.get("compression", compression),
            alpha=metadata.get("alpha", alpha),
            hdr=metadata.get("hdr", hdr),
            image_bytes=image_bytes
        )

def compress_image_to_avif(image_path: str) -> bytes:
    # Load image with Pillow
    img = Image.open(image_path).convert('RGBA')  # keep alpha if any

    # Encode to AVIF bytes using pyavif
    avif_bytes = avif.encode(img)

    return avif_bytes, img.width, img.height, img.mode == 'RGBA'

def decompress_avif_to_image(avif_bytes: bytes) -> Image.Image:
    # Decode AVIF bytes to Pillow image
    img = avif.decode(avif_bytes)
    return img

if __name__ == '__main__':
    input_image_path = 'input.png'  # Replace with your input image file path
    output_jpxp_path = 'output.jpxp'
    output_decoded_path = 'decoded.png'

    # Compress image to AVIF
    avif_data, width, height, has_alpha = compress_image_to_avif(input_image_path)
    print(f"Compressed {input_image_path} to AVIF ({len(avif_data)} bytes)")

    # Create JPXP file bytes
    jpxp_file = JPXPFile(width=width, height=height, compression='AVIF', alpha=has_alpha, hdr=False, image_bytes=avif_data)
    encoded_bytes = jpxp_file.encode()

    # Save JPXP file
    with open(output_jpxp_path, 'wb') as f:
        f.write(encoded_bytes)
    print(f"Saved JPXP file to {output_jpxp_path}")

    # Read JPXP file and decode
    with open(output_jpxp_path, 'rb') as f:
        read_bytes = f.read()

    decoded_jpxp = JPXPFile.decode(read_bytes)
    print(f"Decoded JPXP file metadata: width={decoded_jpxp.width}, height={decoded_jpxp.height}, alpha={decoded_jpxp.alpha}")

    # Decompress AVIF back to image
    decoded_img = decompress_avif_to_image(decoded_jpxp.image_bytes)
    decoded_img.save(output_decoded_path)
    print(f"Saved decoded image to {output_decoded_path}")
