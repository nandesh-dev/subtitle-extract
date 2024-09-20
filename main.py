import os
import subprocess
import re

import ass
import srt
from ass_tag_parser import (parse_ass, AssText)

top_left = "╭"
top = "─"
top_right = "╮"
right = "│"
bottom_right = "╯"
bottom = "─"
bottom_left = "╰"
left = "│"
vertical = "│"
horizontal = "─"
cross = "┼"


def display_file_selector():
    terminal_size = os.get_terminal_size()

    print(top_left + " Files " + (top * (terminal_size.columns - 9)) + top_right)

    files = []
    for file in os.listdir():
        if os.path.isfile(file):
            files.append(file)
            print(
                left
                + " "
                + "[{}] ".format(len(files))
                + file
                + (" " * (terminal_size.columns - len(file + str(len(files))) - 6))
                + right
            )

    print(bottom_left + (bottom * (terminal_size.columns - 2)) + bottom_right)

    selected_file_index = int(input(">>> "))

    return files[selected_file_index - 1]


def display_stream_selector(streams):
    terminal_size = os.get_terminal_size()

    print(top_left + " Streams " + (top * (terminal_size.columns - 11)) + top_right)

    column_widths = (terminal_size.columns - 3) // 2

    for index, stream in enumerate(streams):
        start_line = "[{}] ".format(index + 1) + stream["start_line"]
        start_line_sections = [
            start_line[i : i + column_widths - 2]
            for i in range(0, len(start_line), column_widths - 2)
        ]

        metadata_lines = stream["metadata_lines"]

        if len(start_line_sections) > len(metadata_lines):
            metadata_lines += [""] * (len(start_line_sections) - len(metadata_lines))
        else:
            start_line_sections += [" " * (column_widths - 2)] * (
                len(metadata_lines) - len(start_line_sections)
            )

        for m in range(len(stream["metadata_lines"])):
            print(
                left
                + " "
                + start_line_sections[m].ljust(column_widths - 2)
                + " "
                + vertical
                + " "
                + (stream["metadata_lines"][m] or "").ljust(column_widths - 2)[
                    : (column_widths - 2)
                ]
                + (" " * ((terminal_size.columns - 3) % (column_widths * 2) + 1))
                + right
            )

        if index + 1 != len(streams):
            print(
                left
                + horizontal * (column_widths)
                + cross
                + horizontal * (terminal_size.columns - column_widths - 3)
                + right
            )

    print(bottom_left + (bottom * (terminal_size.columns - 2)) + bottom_right)

    selected_stream_index = int(input(">>> ")) - 1

    return streams[selected_stream_index]


def display_convert_to_srt():
    terminal_size = os.get_terminal_size()
    print(top_left + (top * (terminal_size.columns - 2)) + top_right)
    print(
        left
        + " Do you want to convert the ass format to srt? [Y/N]".ljust(
            terminal_size.columns - 3
        )
        + right
    )
    print(bottom_left + (bottom * (terminal_size.columns - 2)) + bottom_right)

    answer = input(">>> ")

    match answer:
        case "Y":
            return True
        case "y":
            return True
        case _:
            return False

def display_auto_parsing_failed(original_text, semi_parsed_text):
    terminal_size = os.get_terminal_size()
    print(top_left + " Auto parsing failed " + (top * (terminal_size.columns - 23)) + top_right)

    divider_line = horizontal * (terminal_size.columns - 2)

    lines = [ 
             " " + original_text[i : i + terminal_size.columns - 3] for i in range(0, len(original_text), terminal_size.columns - 3) 
             ] + [
            divider_line
            ] + [
    " Enter to accept"
            ] +[ 
             divider_line 
             ]+ [ " " + semi_parsed_text[i : i + terminal_size.columns - 3] for i in range(0, len(semi_parsed_text), terminal_size.columns - 3) 
             ] + [ divider_line ] + [ " Or manually type subtitle" ]

    for line in lines:
        print(
            left 
            + line.ljust(
                terminal_size.columns - 2
            )
            + right
        )
    print(bottom_left + (bottom * (terminal_size.columns - 2)) + bottom_right)

    answer = input(">>> ")

    if answer == "":
        return semi_parsed_text
    return answer



stream_start_list_pattern = re.compile(r"Stream #(\d+:\d+)\(\w*\): (\w*): (\w*)")


def extract_streams(filepath):
    output = subprocess.run(["ffprobe", filepath], capture_output=True, text=True)
    streams_string = output.stdout or output.stderr

    stream_detail_started = False
    metadata_detail_started = False

    streams = []

    current_stream = {
        "stream": "",
        "format": "",
        "start_line": "",
        "metadata_lines": [],
    }
    for line in streams_string.splitlines():
        if line.startswith("  Stream"):
            metadata_detail_started = False
            if stream_detail_started:
                streams.append(current_stream)
                current_stream = {
                    "stream": "",
                    "format": "",
                    "start_line": "",
                    "metadata_lines": [],
                }

            matches = re.findall(stream_start_list_pattern, line)

            if len(matches) > 0 and matches[0][1] == "Subtitle":
                stream_detail_started = True

                current_stream["stream"] = matches[0][0]
                current_stream["start_line"] = line.strip()
                current_stream["format"] = matches[0][2]
            else:
                stream_detail_started = False

        if metadata_detail_started:
            current_stream["metadata_lines"].append(line.strip())

        if stream_detail_started and line.startswith("    Metadata"):
            metadata_detail_started = True

    if stream_detail_started:
        streams.append(current_stream)

    return streams


def extract_subtitle(filepath, stream, format):
    match format:
        case "ass":
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    filepath,
                    "-map",
                    stream,
                    "temp.ass",
                ],
                capture_output=True,
            )
        case _:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    filepath,
                    "-map",
                    stream,
                    "temp.srt",
                ],
                capture_output=True,
            )


def convert_ass_to_srt(filepath):
    with open("temp.ass", encoding="utf_8_sig") as file:
        doc = ass.parse(file)

        subtitles = []
        for index, event in enumerate(doc.events):
            try:
                text = ""
                for tag in parse_ass(event.text):
                    if type(tag) == AssText:
                        text += tag.text

                subtitle = srt.Subtitle(
                    index, event.start, event.end, text.replace("\\N", "\n")
                )
                subtitles.append(subtitle)
            except:
                error_text = ""
                bracket_open = False
                for char in event.text:
                    if char == "{":
                        bracket_open = True

                    if bracket_open == False:
                        error_text += char

                    if char == "}":
                        bracket_open = False

                text = display_auto_parsing_failed(event.text, error_text)
                subtitle = srt.Subtitle(
                    index, event.start, event.end, text.replace("\\N", "\n")
                )
                subtitles.append(subtitle)

        with open(filepath, "w") as file:
            file.write(srt.compose(subtitles))


def main():
    selected_file = display_file_selector()

    streams = extract_streams(selected_file)

    streams.reverse()
    selected_stream = display_stream_selector(streams)

    extract_subtitle(
        selected_file, selected_stream["stream"], selected_stream["format"]
    )

    if selected_stream["format"] == "ass":
        should_convert_to_srt = display_convert_to_srt()

        if should_convert_to_srt:
            convert_ass_to_srt(
                os.path.splitext(os.path.basename(selected_file))[0] + ".srt"
            )
            os.remove("temp.ass")
        else:
            os.rename(
                "temp.ass",
                os.path.splitext(os.path.basename(selected_file))[0] + ".ass",
            )
    else:
        os.rename(
            "temp.srt",
            os.path.splitext(os.path.basename(selected_file))[0] + ".srt",
        )


if __name__ == "__main__":
    main()
