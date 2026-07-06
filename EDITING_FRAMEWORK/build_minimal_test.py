import os
import xml.etree.ElementTree as ET

PROJECT_ROOT = "/Volumes/Extreme SSD/JOSH"
TEMPLATE_XML = "/Volumes/Extreme SSD/Parker Hannifin/XML_Exports/Parker_Hannifin_v47_20260618_210923.xml"
OUT_XML = os.path.join(PROJECT_ROOT, "Premiere", "XML", "Josh_Memorial_v17_MINIMAL.xml")

def build_minimal():
    tree = ET.parse(TEMPLATE_XML)
    root = tree.getroot()
    
    main_bin_children = root.find("bin").find("children")
    
    # 1. Keep only Footage bin and Rough Edit sequence
    footage_bin = None
    seq = None
    
    for child in main_bin_children.findall("*"):
        if child.tag == "bin" and child.find("name").text == "Footage":
            footage_bin = child
        elif child.tag == "sequence" and child.find("name").text == "Rough Edit v47":
            seq = child
        else:
            main_bin_children.remove(child)
            
    # 2. Keep only C0003.MP4 in footage bin
    footage_children = footage_bin.find("children")
    for child in footage_children.findall("*"):
        if child.find("name").text != "C0003.MP4":
            footage_children.remove(child)
            
    # 3. Strip the sequence to just a few clips
    # Actually, we don't even need to strip it. C0003.MP4 is the only file available, 
    # the rest will just be offline media. That is a valid state for Premiere.
    
    # Write output
    os.makedirs(os.path.dirname(OUT_XML), exist_ok=True)
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str += ET.tostring(root, encoding="unicode")
    
    with open(OUT_XML, "w", encoding="utf-8") as f:
        f.write(xml_str)
        
    print(f"Success! Built Minimal XML: {OUT_XML}")

if __name__ == "__main__":
    build_minimal()
