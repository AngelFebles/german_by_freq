# from german_by_freq import my_function
import argparse

from german_by_freq.sort import sort


def main(word_file):
    """
    This function is called when the script is run from the command line.
    It takes the path to a file with german words and calls the split_txt_file function from the sort.py file.

    It is assumed that the file has the following format:
    word1 ; translation1
    word2 ; translation2
    ...
    wordn ; translationn

    Args:
        word_file (str): path to file with german words

    Returns:
        None
    """

    # print("Running as a script")
    sort(word_file)
    # sort


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Path to file with german words")
    parser.add_argument("word_file", help="Path to file with german words")
    args = parser.parse_args()

    main(args.word_file)
