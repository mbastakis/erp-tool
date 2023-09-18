byte_string = b'\xcc.\xcc'

# Attempt to decode using 'ISO-8859-7'
try:
    decoded_string_iso = byte_string.decode('ISO-8859-7')
    print(f"Decoded using ISO-8859-7: {decoded_string_iso}")
except UnicodeDecodeError:
    print("Failed to decode using ISO-8859-7")

# Attempt to decode using 'windows-1253'
try:
    decoded_string_windows = byte_string.decode('windows-1253')
    print(f"Decoded using windows-1253: {decoded_string_windows}")
except UnicodeDecodeError:
    print("Failed to decode using windows-1253")
