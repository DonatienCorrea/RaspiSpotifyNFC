import argparse
from dataclasses import dataclass
from typing import Optional

try:
    import MFRC522
except ImportError:  # pragma: no cover - hardware-specific library not installed in dev
    MFRC522 = None  # type: ignore


@dataclass
class NFCEvent:
    uid: str
    payload: str
    source: str = "nfc"


class ReaderBase:
    def read_once(self) -> Optional[NFCEvent]:
        raise NotImplementedError

    def write_tag(self, uid: str, payload: str) -> bool:
        raise NotImplementedError


class SimulatedReader(ReaderBase):
    def __init__(self, payload_map: Optional[dict] = None):
        self.payload_map = payload_map or {}

    def read_once(self) -> Optional[NFCEvent]:
        if not self.payload_map:
            return None
        uid, payload = next(iter(self.payload_map.items()))
        return NFCEvent(uid=uid, payload=payload, source="simulated")

    def write_tag(self, uid: str, payload: str) -> bool:
        self.payload_map[uid] = payload
        return True


class RC522Reader(ReaderBase):
    def __init__(self):
        if MFRC522 is None:
            raise RuntimeError("MFRC522 library not available; use SimulatedReader for local development.")
        self.reader = MFRC522.MFRC522()

    def read_once(self) -> Optional[NFCEvent]:
        status, tag_type = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
        if status != self.reader.MI_OK:
            return None

        status, uid = self.reader.MFRC522_Anticoll()
        if status != self.reader.MI_OK:
            return None

        uid_hex = "".join(f"{byte:02X}" for byte in uid)
        from .db import get_tag_by_uid

        tag = get_tag_by_uid(uid_hex)
        payload = tag["value"] if tag else uid_hex
        return NFCEvent(uid=uid_hex, payload=payload, source="nfc")

    def write_tag(self, uid: str, payload: str) -> bool:
        raise NotImplementedError("RC522 tag writing is not implemented in v1 scaffold; use simulated mode for now.")


def parse_tag_value(value: str) -> str:
    if value.startswith("spotify:") or value.startswith("action:"):
        return value
    return value.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate an NFC tag scan")
    parser.add_argument("--uid", required=True)
    parser.add_argument("--payload", required=True)
    args = parser.parse_args()

    reader = SimulatedReader({args.uid: parse_tag_value(args.payload)})
    event = reader.read_once()
    if event is None:
        raise SystemExit("No simulated event produced.")
    print(f"uid={event.uid} payload={event.payload} source={event.source}")


if __name__ == "__main__":
    main()
