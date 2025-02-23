# -*- coding: utf-8 -*-

import os
from utils import decode_bytes_with_fallback


def parse_cue(cue_file):
    general = {}
    tracks = []

    with open(cue_file, "rb") as f:
        content_bytes = f.read()

    content_text = decode_bytes_with_fallback(content_bytes)

    if content_text is None:
        return 1, general, tracks

    d = content_text.splitlines()

    for line in d:
        if line.startswith("REM GENRE "):
            general["genre"] = " ".join(line.split(" ")[2:]).replace('"', "")
        if line.startswith("REM DATE "):
            general["date"] = " ".join(line.split(" ")[2:])
        if line.startswith("PERFORMER "):
            general["artist"] = " ".join(line.split(" ")[1:]).replace('"', "")
        if line.startswith("TITLE "):
            general["album"] = " ".join(line.split(" ")[1:]).replace('"', "")
        if line.startswith("FILE "):
            general["file"] = " ".join(line.split(" ")[1:-1]).replace('"', "")
            general["file_type"] = line.split(" ")[-1]

        if "file_type" in general and general["file_type"] not in ["BINARY"]:
            if line.startswith("  TRACK "):
                track = general.copy()
                track["track"] = int(line.strip().split(" ")[1], 10)

                tracks.append(track)

            if line.startswith("    TITLE "):
                tracks[-1]["title"] = " ".join(line.strip().split(" ")[1:]).replace(
                    '"', ""
                )
            if line.startswith("    PERFORMER "):
                tracks[-1]["artist"] = " ".join(line.strip().split(" ")[1:]).replace(
                    '"', ""
                )
            if line.startswith("    INDEX 01 "):
                t = [
                    int(a)
                    for a in " ".join(line.strip().split(" ")[2:])
                    .replace('"', "")
                    .split(":")
                ]
                tracks[-1]["start"] = 60 * t[0] + t[1] + t[2] / 100.0

    for i in range(len(tracks)):
        if i != len(tracks) - 1:
            tracks[i]["duration"] = tracks[i + 1]["start"] - tracks[i]["start"]

    return 0, general, tracks
