import os


def process_onefile(file_in, ffmpeg_path, dir_out):
    filename = os.path.basename(file_in)
    name, ext = os.path.splitext(filename)

    name = safe_name(name)

    cmd = '%s -i "%s"' % (ffmpeg_path, file_in)
    cmd += ' "%s.flac"' % os.path.join(dir_out, name)

    return cmd


def safe_name(string):
    r = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for s in r:
        string = string.replace(s, '_')
    return string


def make_split_cmd(tracks, ffmpeg_path, current_file, dir_out, verbose=False, overwrite=False):
    cmds = []

    for track in tracks:
        metadata = {
            "artist": track["artist"],
            "title": track["title"],
            "album": track["album"],
            "track": str(track["track"]) + "/" + str(len(tracks)),
        }

        if "genre" in track:
            metadata["genre"] = track["genre"]
        if "date" in track:
            metadata["date"] = track["date"]

        cmd = ffmpeg_path
        if not verbose:
            cmd += " -nostats"
        cmd += ' -i "%s"' % current_file
        cmd += " -ss %.2d:%.2d:%.2d" % (
            int(track["start"]) / 60 / 60,
            int(track["start"]) / 60 % 60,
            int(track["start"]) % 60,
        )

        if "duration" in track:
            cmd += " -t %.2d:%.2d:%.2d" % (
                int(track["duration"]) / 60 / 60,
                int(track["duration"]) / 60 % 60,
                int(track["duration"]) % 60,
            )
        # cmd += ' ' + ' '.join('-metadata %s="%s"' % (k, v) for (k, v) in metadata.items())
        # cmd += ' -ab %s' % 128
        cmd += " " + " ".join(
            '-metadata %s="%s"' % (k, v) for (k, v) in metadata.items()
        )
        filename = "%.2d - %s.flac" % (
            int(track["track"]),
            # track['artist'].replace(":", "-"),
            track["title"].replace(":", "-"),
        )

        filename = safe_name(filename)

        cmd += ' "%s"' % os.path.join(dir_out, filename)

        if not overwrite:
            cmd += ' -n'

        cmds.append(cmd)

    return cmds


