# Helper function to get indent (original idea by lorcan17)
def get_indent(line):
    stripped_line = line.strip()
    if not stripped_line:
        return None
    else:
        return len(line) - len(stripped_line)