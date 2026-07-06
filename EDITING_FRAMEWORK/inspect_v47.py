import xml.etree.ElementTree as ET

tree = ET.parse('/Volumes/Extreme SSD/Parker Hannifin/XML_Exports/Parker_Hannifin_v47_20260618_210923.xml')
root = tree.getroot()

print("Root:", root.tag)
for child in root:
    print("  Child:", child.tag, child.find('name').text if child.find('name') is not None else '')
    for subchild in child:
        print("    Subchild:", subchild.tag, subchild.find('name').text if subchild.find('name') is not None else '')
        if subchild.tag == 'children':
            for gchild in subchild:
                print("      GChild:", gchild.tag, gchild.find('name').text if gchild.find('name') is not None else '')
