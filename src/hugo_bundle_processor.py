"""
Create Hugo page bundle from a markdown file.
"""

import os
from shutil import copyfile, copyfileobj
import shutil
from pathlib import Path
import pathlib
import sys
import re
import html
from urllib.parse import unquote
import urllib.request
from random import seed,random,randint
from typing import TypedDict
from wiki_links_processor import wiki_link_to_hugo_link, update_link_to_hugo_bundle, get_hashtags


resourceLink = TypedDict("ResourceLink", {"source": str, "link": str, "text": str})

seed(1)


def get_note_images(text: str) -> list[resourceLink]:
    """Find all image links in the given text and return a list of them."""
    image_links = []

    # Find all image links in the text
    # Wiki link: [[image.png]] or [[image.png|text]]
    image_link_regex = r"!\[\[(.*?)\]\]"  
    for match in re.finditer(image_link_regex, text):
        out = {
            "source": match.group(),
        }

        if "|" in match.group(1):
            out["link"], out["text"] = match.group(1).split("|")
        else:
            out["link"] = match.group(1)
            out["text"] = match.group(1)

        image_links.append(out)

    # Markdown Link: ![image.png](image.png)
    image_link_regex = r"!\[(.*)\]\((.*)\)"  # HTML Image Link
    for match in re.finditer(image_link_regex, text):
        out = {
            "source": match.group(),
        }

        out["link"] = match.group(2)
        out["text"] = match.group(1)

        image_links.append(out)

    return image_links


def findImages(line, currentFile):
    antalAssets = 0
    pattern = re.compile(r"!\[\[([^\]]*)\]\]")
    for (asset) in re.findall(pattern, line):
        antalAssets += 1
        img = str(copyFileToExport(asset.split("|")[0], currentFile))
        if(exportToHtml):
            style = 'border-radius: 4px;"'
            if('|' in asset):
                style = style + 'width:' + asset.split('|')[1] + 'px; border-radius: 3px;'
            line = line.replace("![[" + asset + "]]", '<img src="./' + img + '" alt="' + img.replace("\\","/").split("/")[-1] + '" style="' + style + '" >')
    
    pattern = re.compile(r"!\[(.*)\]\((.*)\)")
    for size,imglink in re.findall(pattern,line):
        antalAssets += 1
        if(exportToHtml):
            if("http" not in imglink):
                originallink = imglink
                imglink = str(copyFileToExport(unquote(imglink.replace("\\","/").split("/")[-1]), currentFile))
                
                style = 'border-radius: 4px;"'
                if('|' in imglink):
                    style = style + 'width:' + imglink.split('|')[1] + 'px; border-radius: 3px;'
                line = line.replace("![" + size + "](" + originallink + ")", '<img src="./' + imglink + '" alt="' + imglink.replace("\\","/").split("/")[-1] + '" style="' + style + '" >')
            elif downloadImages:
                imgname = 'utl_download_' + str(randint(0,10000)) + imglink.split("/")[-1]
                destFile = os.path.join(exportDir,"downloaded_images",imgname)
                with urllib.request.urlopen(imglink) as responese:
                    with open(destFile,'wb') as fdest:
                        copyfileobj(responese, fdest)
                
                style = 'border-radius: 4px;"'
                line = line.replace("![" + size + "](" + imglink + ")", '<img src="../downloaded_images/' + imgname + '" style="' + style + '" >')
            else:
                style = 'border-radius: 4px;"'
                line = line.replace("![" + size + "](" + imglink + ")", '<img src="' + imglink + '" style="' + style + '" >')
    
    
    return (line, antalAssets)


def transfer_image_to_bundle(text: str, file: str, obsidian: str, bundle: str) -> str:
    """Identify all the image links, copy the images and update with hugo links."""
    links = get_note_images(text)
    hashtags = get_hashtags(text)
    for link in links:
        image_source_path = os.path.join(obsidian, link["link"])
        print(f"  Copying image {image_source_path} to {bundle}")
        shutil.copy(image_source_path, os.path.join(bundle))
        hugo_link = update_link_to_hugo_bundle(link)

        # hugo_link = wiki_link_to_hugo_link(link)
        wiki_link = link["source"]
        text = text.replace(wiki_link, hugo_link)

    return text
