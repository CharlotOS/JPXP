# prerequirements: pillow and pillow-avif-plugin (and python ofc)
# commands: 
# pip install Pillow
# pip install pillow-avif-plugin
#
# to use: replace input.png with path to any jpeg jpg or png image on your system
# then run "python path/to/Encoder-Decoder.py" or "py path/to/Encoder-Decoder.py" without the brackets (if on windows replace "/" with "\")
#
import struct
import json
from PIL import Image
import io
import pillow_avif  # just importing registers AVIF support since pyavif is hard to install

MAGIC = b'JPX+'
VERSION = 1

class JPXPFile:
    def __init__(self, width=0, height=0, compression='AVIF', alpha=False, hdr=False, image_bytes=b''):
        self.width = width
        self.height = height
        self.compression = compression
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

def compress_image_to_avif(image_path: str) -> tuple:
    img = Image.open(image_path).convert('RGBA')
    has_alpha = img.mode == 'RGBA'

    buf = io.BytesIO()
    img.save(buf, format='AVIF')
    return buf.getvalue(), img.width, img.height, has_alpha

def decompress_avif_to_image(avif_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(avif_bytes))

if __name__ == '__main__':
    input_image_path = 'input.png' # change input.png with path to any png/jpeg/jpg image on your system
    output_jpxp_path = 'output.jpxp' # change output.jpxp with the desired filename .jpxp
    output_decoded_path = 'decoded.png' # change decoded.png with the desired filename .png

    avif_data, width, height, has_alpha = compress_image_to_avif(input_image_path)
    jpxp_file = JPXPFile(width, height, 'AVIF', has_alpha, False, avif_data)

    with open(output_jpxp_path, 'wb') as f:
        f.write(jpxp_file.encode())
    print(f"Saved JPXP file to {output_jpxp_path}")

    with open(output_jpxp_path, 'rb') as f:
        decoded = JPXPFile.decode(f.read())

    img = decompress_avif_to_image(decoded.image_bytes)
    img.save(output_decoded_path)
    print(f"Decoded image saved to {output_decoded_path}")

