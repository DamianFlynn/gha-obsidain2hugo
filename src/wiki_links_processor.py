"""
Utilities to extract wiki links from text and turn them into hugo links.
"""

from typing import TypedDict
import re
import os


WikiLink = TypedDict("WikiLink", {"wiki_link": str, "link": str, "text": str})


def get_wiki_links(text: str) -> list[WikiLink]:
    """
    Get all wiki links from the given text and return a list of them.
    
    Each list item is a dictionary with the following keys:
    - wiki_link: the exact match
    - link: the extracted link
    - text: the possible extracted text
    """
    wiki_links = []
    wiki_link_regex = r"\[\[(.*?)\]\]"
    for match in re.finditer(wiki_link_regex, text):
        out = {
            "wiki_link": match.group(),
        }

        if "|" in match.group(1):
            out["link"], out["text"] = match.group(1).split("|")
        else:
            out["link"] = match.group(1)
            out["text"] = match.group(1)

        # if the link ends with `_index` remove it
        if out["link"].endswith("_index"):
            out["link"] = out["link"][:-6]

        wiki_links.append(out)
    return wiki_links


def update_link_to_hugo_bundle(link: WikiLink) -> str:
    """Convert the wiki link into a hugo bundle link."""
    link["link"] = os.path.basename(link["link"])
    hugo_link = f'![{link["text"]}]({link["link"]})'
    return hugo_link


def wiki_link_to_hugo_link(wiki_link: WikiLink) -> str:
    """Convert the wiki link into a hugo link."""
    # if the links contains a link to a heading, convert the heading part to
    # lower case and replace spaces by minus
    link_seperated = wiki_link["link"].split("#", 1)
    if len(link_seperated) > 1:
        link_combined = "#".join(
            [link_seperated[0], link_seperated[1].lower().replace(" ", "-")]
        )
    else:
        link_combined = wiki_link["link"]
    hugo_link = f'[{wiki_link["text"]}]({{{{< ref "{link_combined}" >}}}})'
    return hugo_link


def replace_wiki_links(text: str) -> str:
    """
    Replace all wiki links in the given text with hugo links.
    """
    links = get_wiki_links(text)
    for link in links:
        hugo_link = wiki_link_to_hugo_link(link)
        text = text.replace(link["wiki_link"], hugo_link)
    return text


# function to print all the hashtags in a text

def get_hashtags(text: str) -> list[str]:
    """Get all hashtags from the given text and return a list of them."""
    hashtag_regex = r"#(\w+)"

    hashtag_list = re.findall(hashtag_regex, text)

    for hashtag in hashtag_list:
        print(hashtag)
    return hashtag_list
