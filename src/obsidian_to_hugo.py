"""
Utilities to process obsidian notes and convert them to hugo ready content files.
"""

import os
import shutil
from distutils.dir_util import copy_tree
from wiki_links_processor import replace_wiki_links
from hugo_bundle_processor import transfer_image_to_bundle


class ObsidianToHugo:
    """Process the obsidian vault and convert it to hugo ready content."""

    def __init__(
        self,
        obsidian_vault_dir: str,
        vault_content_dir: str,
        hugo_content_dir: str,
    ) -> None:
        self.obsidian_vault_dir = obsidian_vault_dir
        self.obsidian_content_dir = vault_content_dir
        self.hugo_content_dir = hugo_content_dir

    def process(self) -> None:
        """
        Process the obsidian vault and convert it to hugo ready content.

        Delete the hugo content directory and copy the obsidian vault to the
        hugo content directory, then process the content so that the wiki links
        are replaced with the hugo links.
        """
        print("Clearing hugo content directory...")
        self.clear_hugo_content_dir()
        print("Copying obsidian vault to hugo content directory...")
        # self.copy_obsidian_vault_to_hugo_content_dir()
        self.copy_obsidian_note_to_hugo_page_bundle()
        print("Processing content...")
        self.process_hugo_page_bundle()

    def clear_hugo_content_dir(self) -> None:
        """
        Delete the whole content directory.

        NOTE: The folder itself gets deleted and recreated.
        """
        shutil.rmtree(self.hugo_content_dir)
        os.mkdir(self.hugo_content_dir)

    # def copy_obsidian_vault_to_hugo_content_dir(self) -> None:
    #     """
    #     Copy all files and directories from the obsidian vault to the hugo content directory.
    #     """
    #     copy_tree(self.obsidian_vault_dir, self.hugo_content_dir)
    #     # We don't want to have the .obsidian folder in the hugo content directory.
    #     if os.path.isdir(os.path.join(self.hugo_content_dir, ".obsidian")):
    #         shutil.rmtree(os.path.join(self.hugo_content_dir, ".obsidian"))

    def copy_obsidian_note_to_hugo_page_bundle(self) -> None:
        """
        Copy all files and directories from the obsidian vault to the hugo content directory.
        """
        for root, dirs, files in os.walk(os.path.join(self.obsidian_vault_dir, self.obsidian_content_dir)):
            for file in files:
                if file.endswith(".md"):
                    print(f"Creating Hugo Bundle: {file}")
                    # Create the page bundle directory.
                    page_bundle_dir = os.path.join(
                        self.hugo_content_dir,
                        # os.path.relpath(root, self.obsidian_vault_dir),
                        os.path.basename(file).split('.')[0]
                    )
                    os.makedirs(page_bundle_dir, exist_ok=True)
                    # Copy the markdown file.
                    shutil.copy(
                        os.path.join(root, file),
                        os.path.join(page_bundle_dir, "index.md"),
                    )
                    # Copy the assets.
                    assets_dir = os.path.join(root, "assets")
                    if os.path.isdir(assets_dir):
                        copy_tree(assets_dir, os.path.join(page_bundle_dir, "assets"))
                    ##
                    ## https://github.com/klalle/ObsidianToHtmlConverter/blob/main/exportMdFileToHtml.py
                    ##

        # We don't want to have the .obsidian folder in the hugo content directory.
        if os.path.isdir(os.path.join(self.hugo_content_dir, ".obsidian")):
            shutil.rmtree(os.path.join(self.hugo_content_dir, ".obsidian"))

    def process_hugo_page_bundle(self) -> None:
        """
        Looping through all files in the hugo content directory and replace the
        wiki links of each matching file.
        """
        for hugo_bundle_path, dirs, files in os.walk(self.hugo_content_dir):
            for file in files:
               
                if file.endswith(".md"):
                    bundle_file = os.path.join(hugo_bundle_path, file)
                    print(f"Processing Bundle: {hugo_bundle_path}")
                    with open(bundle_file, "r", encoding="utf-8") as f:
                        text = f.read()
                    text = transfer_image_to_bundle(text, file, self.obsidian_vault_dir, hugo_bundle_path)
                    # text = replace_wiki_links(text)
                    with open(os.path.join(hugo_bundle_path, file), "w", encoding = "utf-8") as f:
                        f.write(text)
