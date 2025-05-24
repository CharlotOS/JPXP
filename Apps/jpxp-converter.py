# run with "python jpxp-converter.py my-image.jpg"
# ensure to have ran "pip install pillow pillow-avif-plugin" before and ensure you have python installed
import sys
import struct
import json
import io
from datetime import datetime
from PIL import Image
import os

def encode_jpxp(input_path, output_path):
    # Load image and convert to RGBA
    image = Image.open(input_path).convert("RGBA")
    
    # Save to AVIF in memory
    avif_buffer = io.BytesIO()
    image.save(avif_buffer, format="AVIF", quality=80)
    avif_bytes = avif_buffer.getvalue()

    # Metadata
    metadata = {
        "original_filename": os.path.basename(input_path),
        "format": "AVIF",
        "width": image.width,
        "height": image.height,
        "has_alpha": True,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    metadata_json = json.dumps(metadata).encode("utf-8")

    # JPXP header
    header = b"JPX+"                              # Magic
    header += struct.pack("B", 1)                # Version
    flags = 0b00000001 if image.mode == "RGBA" else 0
    header += struct.pack("B", flags)            # Flags
    header += b"\x00\x00\x00\x00"                # Reserved
    header += struct.pack("<I", len(metadata_json))  # Metadata length
    header += metadata_json                      # Metadata
    header += struct.pack("<I", len(avif_bytes)) # Image length
    header += avif_bytes                         # AVIF data

    # Save to output
    with open(output_path, "wb") as f:
        f.write(header)

    print(f"✔ Saved: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_to_jpxp.py input_image [output.jpxp]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(input_path)[0] + ".jpxp"
    encode_jpxp(input_path, output_path)
