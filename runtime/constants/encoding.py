from __future__ import annotations


SOURCE_ENCODINGS = ("cp932", "shift_jis")

# Markers for text that still decodes as UTF-8 but is semantically mojibake.
MOJIBAKE_MARKERS = (
    "\u7e3a",
    "\u7e67",
    "\u7e5d",
    "\u7e32",
    "\u8b41",
    "\u8b4c",
    "\u8700",
    "\u8737",
    "\u86f9",
    "\u86fb",
    "\u8c41",
    "\u8b17",
    "\u8b5b",
    "\u8b5f",
    "\u8ae0",
    "\u96b1",
    "\u9695",
    "\u9081",
    "\u8373",
    "\u8389",
    "\u9015",
    "\u8822",
    "\u9666",
    "\u9a65",
    "\u9aea",
    "\u9b1f",
    "\u87c7",
    "\u8708",
    "\u87b3",
    "\ufffd",
)
