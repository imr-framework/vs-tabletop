# Security Notes

## Known Vulnerabilities

### protobuf - JSON Recursion Depth Bypass

**Status**: No patch available (as of January 2026)

**Description**: The protobuf library has a known vulnerability related to JSON recursion depth bypass that affects all versions <= 6.33.4. Since version 6.33.4 is the latest available version and no patched version exists, this vulnerability cannot be currently resolved.

**Affected Version**: 4.25.8 (current)

**Mitigation**: 
- We have upgraded from version 3.19.4 to 4.25.8 to address multiple other critical DoS vulnerabilities that had available patches
- Monitor the protobuf repository for future security releases
- Consider implementing application-level input validation for protobuf JSON parsing if applicable

**Impact**: This vulnerability may allow attackers to bypass JSON recursion depth limits, potentially leading to denial of service through excessive resource consumption.

**References**: 
- GitHub Advisory Database
- All protobuf versions <= 6.33.4 are affected

## Resolved Vulnerabilities

The following vulnerabilities have been successfully resolved by upgrading dependencies:

### grpcio (1.46.3 → 1.56.2)
- Fixed: Excessive Iteration in gRPC (multiple advisories)

### opencv-python (4.6.0.66 → 4.8.1.78)
- Fixed: CVE-2023-4863 - libwebp vulnerability in bundled binaries

### Pillow (9.2.0 → 10.3.0)
- Fixed: Buffer overflow vulnerability
- Fixed: Denial of Service vulnerability  
- Fixed: Bundled libwebp vulnerability
- Fixed: DoS via SAMPLESPERPIXEL tag

### protobuf (3.19.4 → 4.25.8)
- Fixed: Multiple Denial of Service vulnerabilities in versions < 4.25.8
- Note: One unpatched vulnerability remains (see above)
