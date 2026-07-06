# Premiere Pro Photo Import Protocol (XML)

## The "Silent Fail" Bug
When importing Final Cut Pro 7 XML files containing still images (JPEGs/PNGs), Premiere Pro 2026 will often silently fail or crash during the parsing process. This happens because Premiere has entirely undocumented, strict requirements for how a still image is structured in an XML file, diverging completely from how traditional NLEs (like FCP7 itself) handled them.

## The Solution (Native Premiere Structure)
Through reverse-engineering a native Premiere export, we discovered the exact structure required to prevent the crash and successfully import a timed photo sequence:

1. **Duration on the Master Clip, NOT the File**: 
   - Premiere demands the `<duration>` tag be placed inside the outer `<clip>` block (e.g. `<duration>86400</duration>`).
   - If you place a `<duration>` tag on the inner `<file>` block for a still image, Premiere will crash.

2. **Mandatory Timecode Block**:
   - The `<file>` block must contain a dummy `<timecode>` block (starting at `00:00:00:00`), even though stills do not inherently have timecode.

3. **Strict URL Encoding rules**:
   - For `<pathurl>`, you cannot simply URL encode the entire string.
   - Spaces must be encoded as `%20`.
   - Ampersands (`&`) **must** be XML-escaped as `&amp;` instead of URL encoded as `%26`. If you use `%26`, Premiere will fail to resolve the file path. 
   - (Example: `file://localhost/Path/To/Baby%20&amp;%20toddler/IMG_1.jpg`)

4. **Required Inner Clipitem Elements**:
   - You must include `<alphatype>none</alphatype>`, `<pixelaspectratio>square</pixelaspectratio>`, and `<anamorphic>FALSE</anamorphic>` on the `<clipitem>` referencing the photo.

By adhering to this exact schema, you can programmatically generate long, fully-timed photo montages synced to music that Premiere will import seamlessly.
