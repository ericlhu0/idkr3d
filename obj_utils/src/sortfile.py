import argparse


def sort_file(input_file, output_file, reverse=False, ignore_case=False):
    """
    Sort lines in a file and write to output file.

    Args:
        input_file (str): Path to input file
        output_file (str): Path to output file
        reverse (bool): Sort in descending order if True
        ignore_case (bool): Ignore case when sorting if True
    """
    try:
        # Read all lines from input file
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Remove trailing whitespace and filter empty lines
        lines = [line.strip() for line in lines if line.strip()]

        # Sort the lines
        if ignore_case:
            lines.sort(key=str.lower, reverse=reverse)
        else:
            lines.sort(reverse=reverse)

        # Write sorted lines to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')

        print(f"Successfully sorted {len(lines)} lines from '{input_file}' to '{output_file}'")

    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort lines in a text file")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("-r", "--reverse", action="store_true", help="Sort in descending order")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Ignore case when sorting")

    args = parser.parse_args()
    sort_file(args.input, args.output, args.reverse, args.ignore_case)