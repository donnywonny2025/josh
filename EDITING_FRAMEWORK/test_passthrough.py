import xml.etree.ElementTree as ET

TEMPLATE_XML = "/Volumes/Extreme SSD/Parker Hannifin/XML_Exports/Parker_Hannifin_v47_20260618_210923.xml"
OUT_XML = "/Volumes/Extreme SSD/JOSH/EDITING_FRAMEWORK/test_passthrough.xml"

tree = ET.parse(TEMPLATE_XML)
root = tree.getroot()

xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml_str += ET.tostring(root, encoding="unicode")

with open(OUT_XML, "w", encoding="utf-8") as f:
    f.write(xml_str)
