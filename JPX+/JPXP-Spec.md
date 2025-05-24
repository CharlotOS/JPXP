
# 📄 JPXP File Format Specification  
**Version:** 1.0  
**Extension:** `.jpxp`  
**Magic Bytes:** `0x4A 50 58 2B` (`"JPX+"`)  

---

## 📌 Overview

**JPXP (JPEG Plus eXtended Portable)** is a next-generation image format designed to replace traditional JPEG with modern features such as:

- Advanced lossy/lossless compression (AVIF or JPEG XL)
- Full alpha transparency support
- HDR and wide color gamut
- Extensible metadata
- Stream-friendly progressive loading
- Optional integrity checks and encryption

---

## 🧱 File Structure

```
[Header]                // 16 bytes  
[Metadata Block]        // Variable (JSON)  
[Color Profile Block]   // Optional (ICC or NCLX)  
[Alpha Channel Block]   // Optional (compressed alpha)  
[Image Data Block]      // Compressed pixel data (e.g., AVIF)  
[Integrity Block]       // Optional SHA-256 or CRC32  
```

---

## 🧩 Detailed Structure

### 🔷 1. Header (16 bytes)

| Field        | Size | Type     | Description                             |
|--------------|------|----------|-----------------------------------------|
| Magic Bytes  | 4    | Bytes    | Always `0x4A 50 58 2B` (`"JPX+"`)        |
| Version      | 1    | Byte     | Format version (currently `0x01`)       |
| Flags        | 1    | Bitfield | Alpha, HDR, compression type, etc.      |
| Reserved     | 10   | Bytes    | Future use (set to zero)                |

---

### 🔷 2. Metadata Block

- Format: UTF-8 encoded JSON string  
- Prefixed with a 4-byte little-endian length  
- Example:

```json
{
  "width": 1920,
  "height": 1080,
  "bit_depth": 10,
  "color_space": "BT.2020",
  "compression": "AVIF",
  "alpha": true,
  "hdr": true
}
```

---

### 🔷 3. Color Profile Block

- Contains ICC profile or NCLX color info  
- Prefixed with a 4-byte length  
- Identifies how to interpret pixel color values

---

### 🔷 4. Alpha Channel Block

- Contains the alpha mask (grayscale image)  
- Compressed using Brotli, Zstd, or same codec as image  
- Prefixed with 4-byte length

---

### 🔷 5. Image Data Block

- Raw compressed image (AVIF or JPEG XL)  
- No extra markers; read until EOF or next block

---

### 🔷 6. Integrity Block

- 1-byte type ID (e.g. `0x01` = SHA-256)  
- Followed by fixed-size checksum or hash  
- Used to validate metadata + image

---

## 🧪 Flag Bits (1 byte)

| Bit | Purpose         | Description                             |
|-----|------------------|-----------------------------------------|
| 0   | Alpha channel    | If set, image has transparency          |
| 1   | HDR              | If set, uses 10+ bit and HDR metadata   |
| 2   | Reserved         | Future use                              |
| 3   | Compression Type | 0 = AVIF, 1 = JPEG XL                   |
| 4-7 | Reserved         | Future use                              |

---

## 🖼 Compression Codecs

### AVIF (default)

- Efficient lossy/lossless codec  
- Excellent for photographic images  
- Supported via AV1 video technology

### JPEG XL

- High compression efficiency  
- Advanced progressive loading  
- Better lossless support than PNG or JPEG

---

## 🔐 Future Features (Planned)

- Steganographic watermark embedding  
- Metadata encryption  
- Native support for streaming chunks  

---
