import json, os
from typing import List


class UIDDatabaseError(Exception):
    """ Exception for UID database errors. """
    pass


class UIDService:
    """
    UIDService manages a whitelist of UIDs using a JSON file as storage.
    """

    def __init__(self, db_path: str = "database/uids.json"):
        self.db_path = db_path
        self._ensure_database()

    # ---------------------------------------------------------------------
    def _ensure_database(self) -> None:
        """ Ensure that the database file exists and has the correct structure. """
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        if not os.path.exists(self.db_path):
            self._write_database({"whitelist_uid": []})
        else:
            try:
                data = self._read_raw()
                if "whitelist_uid" not in data or not isinstance(data["whitelist_uid"], list):
                    raise UIDDatabaseError("Invalid database structure.")
            except Exception:
                self._write_database({"whitelist_uid": []})

    # ---------------------------------------------------------------------
    def _read_raw(self) -> dict:
        """ Read the JSON database without modification. """
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise UIDDatabaseError(f"Failed to read UID database: {e}")

    def _write_database(self, data: dict) -> None:
        """ Write data to the JSON database. """
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise UIDDatabaseError(f"Failed to write UID database: {e}")

    # ---------------------------------------------------------------------
    def get_all_uids(self) -> List[str]:
        """ Return the entire whitelist of UIDs. """
        return self._read_raw().get("whitelist_uid", [])

    def uid_exists(self, uid: str) -> bool:
        """ Check if a UID exists in the whitelist. """
        uid = str(uid).strip()
        return any(uid == u.strip() for u in self.get_all_uids())

    def add_uid(self, uid: str) -> bool:
        """ Add a UID if it does not exist. Returns True if added. """
        uid = str(uid)
        data = self._read_raw()
        uids = data.get("whitelist_uid", [])

        if uid not in uids:
            uids.append(uid)
            data["whitelist_uid"] = uids
            self._write_database(data)
            return True

        return False

    def remove_uid(self, uid: str) -> bool:
        """ Remove a UID from the whitelist. Returns True if removed. """
        uid = str(uid)
        data = self._read_raw()
        uids = data.get("whitelist_uid", [])

        if uid in uids:
            uids.remove(uid)
            data["whitelist_uid"] = uids
            self._write_database(data)
            return True

        return False
