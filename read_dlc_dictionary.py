import io
import os
import struct
import sys
import zlib

def main():
    try:
        files = sys.argv[1:]
    except Exception as e:
        files = []

    if not files:
        print("Usage: python3 read_dlc_dictionary.py <input_file_1.pc> [<input_file_2>, ...]")

    else:
        for filepath in files:
            if os.path.isfile(filepath):
                try:
                    with open(filepath, "rb") as f:
                        print(f"Processing file {filepath}")
                        parse_dictionary_file(f, filepath)

                except Exception as e:
                    raise e

            else:
                print(f"Invalid file path: {filepath}")

def parse_dictionary_file(stream, filepath):
    """Step 1

    Decompress.
    """
    compressed   = stream.read()
    decompressed = zlib.decompress(compressed[400:])

    stream = io.BytesIO(decompressed)


    """Step 2

    Find size of dictionary data. Always one of two values at the same offsets.
    """
    stream.seek(0x08)
    size_1 = struct.unpack("<I", stream.read(4))[0]

    stream.seek(0x58)
    size_2 = struct.unpack("<I", stream.read(4))[0]

    dict_size = size_1 if size_1 > size_2 else size_2


    """Step 3

    Find "STAB" - always aligned to 4 bytes and seems to mark the beginning of the dictionary.
    """
    sig = None

    try:
        while sig != 0x53544142:
            sig = struct.unpack(">I", stream.read(4))[0]

    except Exception as e:
        print("Unable to find beginning of PC file data; skipping")
        return


    """Step 4

    Find the dictionary size again, as the phrase count is always 20 bytes after it.
    """
    temp_size = None

    try:
        while temp_size != dict_size:
            temp_size = struct.unpack("<I", stream.read(4))[0]

    except Exception as e:
        print("Unable to find size/phrase count; skipping")
        return

    # Offset values that appear later are relative to the beginning of the previous 16 byte row
    begin_offset = stream.tell() - 0x10

    # Move 20 bytes to find the count
    stream.seek(0x14, 1)

    count = struct.unpack("<I", stream.read(4))[0]


    """Step 5

    Group phrase offsets and sizes.
    """
    stream.seek(24 * 2, 1)
    groups = get_phrase_sizes(stream, count)


    """Step 6

    Extract phrases using the data gathered in step 4.
    """
    replace_pairs = (
        ("\x19", "'"),
        ("\x1C", "\u201C"), # opening double quote
        ("\x1D", "\u201D"), # closing double quote
    )

    output = [
        "------------------------------------------",
        "Group Name -> Phrase",
        "------------------------------------------",
    ]

    for x in range(len(groups)):
        group = groups[x]

        begin = begin_offset + group[0]

        try:
            end = begin_offset + groups[x + 1][0]
        except Exception as e:
            end = 0

        stream.seek(begin)

        phrase_size = group[1] * 2 + 2 # x2 for UTF-16 encoding + 2 null bytes

        phrase = stream.read(phrase_size).decode("utf-16").strip("\x00 ")

        if end > 0:
            group_name = stream.read(end - stream.tell()).decode("latin-1").strip("\x00 ")
        else:
            group_name = get_unsized_text(stream)

        for find, replace in replace_pairs:
            phrase     = phrase.replace(find, replace)
            group_name = group_name.replace(find, replace)

        output.append(f"{group_name} -> {phrase}")

    output_name = os.path.splitext(filepath)[0]

    with open(f"{output_name}_phrases.txt", "w", encoding = "utf-8") as output_file:
        output_file.write("\n".join(output))

def get_phrase_sizes(stream, count):
    groups = []
    total  = count - 1

    for x in range(total):
        start = struct.unpack("<I", stream.read(4))[0]
        size  = struct.unpack("<I", stream.read(4))[0]
        end   = struct.unpack("<I", stream.read(4))[0]

        stream.seek(4, 1) # ID?

        if x != total - 1:
            stream.seek(8, 1)

        else:
            stream.seek(4, 1)

        group = [
            start,
            size,
            end,
            end - start
        ]

        groups.append(group)

    return groups

def get_unsized_text(stream):
    text = ""
    char = struct.unpack("c", stream.read(1))[0].decode()

    while char != "\x00":
        text += char
        char = struct.unpack("c", stream.read(1))[0].decode()

    return text

if __name__ == "__main__":
    main()