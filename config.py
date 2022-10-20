import logging
import json
from pathlib import Path, PurePath

import messages
import util
import util.file

DEFAULT_PROFILES = {
    "Hades": {
        "default_target": ["Scripts/RoomManager.lua"],
    },
    "Pyre": {
        "default_target": ["Scripts/Campaign.lua", "Scripts/MPScripts.lua"],
    },
    "Transistor": {
        "default_target": ["Scripts/AllCampaignScripts.txt"],
    },
    "Bastion": {},
}


class SggmiConfiguration:
    def __init__(self, **kwargs):
        self.this_file = Path(kwargs.pop("thisfile")).resolve()

        self.config_file = "config.json"
        self.mod_file = "modfile.txt"
        self.edited_suffix = ".hash"

        self.hashes = ["md5"]

        self.echo = True
        self.log = True
        self.input = True

        self.uninstall = False
        self.modify_config = False
        self.overwrite_config = False

        self.logs_prefix = "sggmi_"
        self.logs_suffix = ".log"

        self.scope_rel_path = "Content"

        self.base_cache_rel_dir = "Base Cache"
        self.deploy_rel_dir = "Deploy"  # Must be accessible to game scope
        self.edit_cache_rel_dir = "Edit Cache"
        self.logs_rel_dir = "Logs"
        self.mods_rel_dir = "Mods"

        self.chosen_profile = None

        self.profile = {
            "default_target": None,
            "game_dir_path": None,
            "folder_deployed": None,
            "folder_mods": None,
            "folder_basecache": None,
            "folder_editcache": None,
        }

        self.use_special_profile = False
        self.special_profile = False

        for key, value in kwargs:
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def scope_dir(self):
        game_dir = self.this_file.parent.parent
        return PurePath.joinpath(game_dir, self.scope_rel_path)

    @property
    def base_cache_dir(self):
        if not getattr(self, "_base_cache_dir", None):
            self._base_cache_dir = Path.joinpath(
                self.scope_dir, self.base_cache_rel_dir
            ).resolve()
        return self._base_cache_dir

    @property
    def deploy_dir(self):
        if not getattr(self, "_deploy_dir", None):
            self._deploy_dir = Path.joinpath(
                self.scope_dir, self.deploy_rel_dir
            ).resolve()
        return self._deploy_dir

    @property
    def edit_cache_dir(self):
        if not getattr(self, "_edit_cache_dir", None):
            self._edit_cache_dir = Path.joinpath(
                self.scope_dir, self.edit_cache_rel_dir
            ).resolve()
        return self._edit_cache_dir

    @property
    def logs_dir(self):
        if not getattr(self, "_logs_dir", None):
            self._logs_dir = Path.joinpath(
                self.scope_dir, self.logs_rel_dir
            ).resolve()
        return self._logs_dir

    @property
    def mods_dir(self):
        if not getattr(self, "_mods_dir", None):
            self._mods_dir = Path.joinpath(
                self.scope_dir, self.mods_rel_dir
            ).resolve()
        return self._mods_dir

    @classmethod
    def load_from_file(cls, config_file):
        with open(config_file, "r") as config_in:
            return cls(**(json.load(config_in)))

    def dump_to_file(self):
        if self.overwrite_config:
            config_out_path = Path(self.config_file).resolve()
        else:
            config_out_path = Path(self.config_file + util.timestamp()).resolve()

            with open(config_out_path, "w") as config_out:
                json.dump(self.to_dict(), config_out, indent=2)

    def apply_command_line_arguments(self, parsed_args):
        for arg, value in vars(parsed_args).items():
            if arg == "special_profile" and value:
                self.special_profile = json.loads(value)

            if arg == "hashes" and value:
                self.hashes = value.split(" ")

    def detect_profile(self):
        game_name = self.this_file.parent.parent.name
        self.profile = DEFAULT_PROFILES.get(game_name, None)
        if self.profile:
            self.chosen_profile = game_name

    def set_profile(self, special_profile=None):

        if special_profile:
            self.folder_profile = util.merge_dict(self.folder_profile, special_profile)
            return

        self.chosen_profile = input(
            "Type the name of a profile, or leave empty to cancel:\n\t> ", config=config
        )
        self.profile = util.get_attribute(self.all_profiles, self.chosen_profile, None)

        if not profile:
            logging.warning(messages.missing_folder_profile(self.config_file))
            exit(1)
        else:
            self.folder_profile = util.merge_dict(self.folder_profile, DEFAULT_PROFILES[self.chosen_profile])

        if profile is None:
            logging.warning(messages.missing_folder_profile(self.config_file))
            profile = {}

config = SggmiConfiguration()