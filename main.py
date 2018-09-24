import json
import re
from typing import Dict, AnyStr

import requests

CONFUSABLES_URL = "http://www.unicode.org/Public/security/latest/confusables.txt"

# 064F ;	0313 ;	MA	# ( ُ → ̓ ) ARABIC DAMMA → COMBINING COMMA ABOVE	#
CONFUSABLES_RE = re.compile(r"(?P<source>.*)\s;\s(?P<target>.*)\s;\sMA\s.*")


def get_confusables(url: AnyStr = CONFUSABLES_URL):
    """Download the url to parse"""
    data = requests.get(url).text
    return data


def parse_confusables(text: str) -> Dict[AnyStr, AnyStr]:
    """convert the consumables format from the site format to a dict"""
    out = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        match = CONFUSABLES_RE.fullmatch(line)
        if not match:
            print(f"Unmatched line: {line!r}")
            continue

        match_dict = match.groupdict()
        assert match_dict["source"] not in out, f"Duplicate entry in confusables found: {match_dict['source']} -> " \
                                                f"{match_dict['target']} ({line!r})"

        source_codepoint = match_dict["source"]
        target_codepoint = match_dict["target"]
        out[source_codepoint] = target_codepoint

    return out


def convert_codepoint(codepoint: str):
    """convert codepoints (including multu byte ones) to the bytes they represent"""
    split = codepoint.split(" ")
    out = ""
    for point in split:
        out += chr(int(point, 16))

    return out


def convert_to_chars(codepoint_dict: Dict[AnyStr, AnyStr]):
    """Create a dict of real characters from a dict of codepoints"""
    out = {}
    for source, target in codepoint_dict.items():
        source_chr = convert_codepoint(source)
        target_chr = convert_codepoint(target)
        out[source_chr] = target_chr

    return out


def create_json():
    """Create json files of confusables for use in other programs"""
    confusables = get_confusables()
    codepoint_dict = parse_confusables(confusables)
    chr_dict = convert_to_chars(codepoint_dict)

    with open("codepoints.json", "w") as f:
        json.dump(codepoint_dict, f, indent=2)

    with open("chrs.json", "w") as f:
        json.dump(chr_dict, f, indent=2)


if __name__ == '__main__':
    create_json()
