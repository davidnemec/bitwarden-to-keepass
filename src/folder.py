import collections
import re
from collections.abc import Callable
from typing import Optional

from pykeepass import PyKeePass
from pykeepass.group import Group as KPGroup


class Folder:
    id: str | None
    name: str | None
    children: list["Folder"]
    parent: Optional["Folder"]
    keepass_group: KPGroup | None

    def __init__(self, id: str | None) -> None:
        self.id = id
        self.name = None
        self.children = []
        self.parent = None
        self.keepass_group = None

    def add_child(self, child: "Folder") -> None:
        self.children.append(child)
        child.parent = self


# logic was lifted directly from https://github.com/bitwarden/jslib/blob/ecdd08624f61ccff8128b7cb3241f39e664e1c7f/common/src/misc/serviceUtils.ts#L7
def nested_traverse_insert(
    root: Folder,
    name_parts: list[str],
    new_folder: Folder,
    delimiter: str,
) -> None:
    if len(name_parts) == 0:
        return

    end: bool = len(name_parts) == 1
    part_name: str = name_parts[0]

    for child in root.children:
        if child.name != part_name:
            continue

        if end and child.id != new_folder.id:
            # Another node with the same name.
            new_folder.name = part_name
            root.add_child(new_folder)
            return
        nested_traverse_insert(child, name_parts[1:], new_folder, delimiter)
        return

    if end:
        new_folder.name = part_name
        root.add_child(new_folder)
        return
    new_part_name: str = part_name + delimiter + name_parts[1]
    new_name_parts: list[str] = [new_part_name]
    new_name_parts.extend(name_parts[2:])
    nested_traverse_insert(root, new_name_parts, new_folder, delimiter)


def bfs_traverse_execute(
    kp: PyKeePass,
    root: Folder,
    callback: Callable[[PyKeePass, Folder], None],
) -> None:
    queue: collections.deque[Folder] = collections.deque()
    queue.extend(root.children)
    while queue:
        child: Folder = queue.popleft()
        queue.extend(child.children)
        callback(kp, child)


def load_folders(kp: PyKeePass, folders: list[dict]) -> dict[str, KPGroup]:
    # sort folders so that in the case of nested folders
    # the parents would be guaranteed to show up before the children
    folders.sort(key=lambda x: x["name"])

    # dict to store mapping of Bitwarden folder id to keepass group
    groups_by_id: dict[str | None, KPGroup] = {}

    # build up folder tree
    folder_root: Folder = Folder(None)
    folder_root.keepass_group = kp.root_group
    groups_by_id[None] = kp.root_group

    for folder in folders:
        if folder["id"] is not None:
            new_folder: Folder = Folder(folder["id"])
            # regex lifted from https://github.com/bitwarden/jslib/blob/ecdd08624f61ccff8128b7cb3241f39e664e1c7f/common/src/services/folder.service.ts#L108
            folder_name_parts: list[str] = re.sub(
                r"^\/+|\/+$",
                "",
                folder["name"],
            ).split("/")
            nested_traverse_insert(
                folder_root,
                folder_name_parts,
                new_folder,
                "/",
            )

    # create keepass groups based off folder tree
    def add_keepass_group(kp: PyKeePass, folder: Folder) -> None:
        parent_group: KPGroup = folder.parent.keepass_group
        new_group: KPGroup = kp.add_group(parent_group, folder.name)
        folder.keepass_group = new_group
        groups_by_id[folder.id] = new_group

    bfs_traverse_execute(kp, folder_root, add_keepass_group)

    return groups_by_id
