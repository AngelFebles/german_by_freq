from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup


def split_txt_file(input_file):

    with open(input_file, "r", encoding="utf-8") as file:
        arr_of_words = [line.strip().split(" ; ") for line in file]
        # arr_of_words = [line.strip().split("	 ") for line in file]

    # print(arr_of_words)

    # Create a dataframe from the list of words
    words_df = pd.DataFrame(arr_of_words, columns=["German", "English"])

    # print(words_df)

    raw_pd = words_df.copy()

    # Remove empty rows
    words_df = words_df.dropna()

    # Delete articles and remove special characters from german words column (except for umlauts)
    # Not converting to lower case, I want to keep the original words for Anki
    # exportation
    words_df["German"] = (
        words_df["German"]
        .str.replace(r"(der|die|das) |[^a-zA-Zäöüß\s]", "", regex=True)
        .str.lower()
    )

    print(words_df)

    return words_df, raw_pd


def scrape_frequencity_df():
    """
    This function scrapes the frequency table from the following websites:

    https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/German_subtitles_1000
    https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/German_subtitles_1001-2000

    They contain the 2000 most common words in the German language by frequency.
    """

    link1 = "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/German_subtitles_1000"
    link2 = "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/German_subtitles_1001-2000"

    table1__pd = scrape_table(link1)
    table2__pd = scrape_table(link2)
    # Merge the two tables
    full_table = pd.concat([table1__pd, table2__pd], ignore_index=True)

    # Remove duplicates based on the 'word' column
    full_table = full_table.drop_duplicates(subset="word")

    full_table.to_csv(
        "src/data/freq_guide_df.txt",
        sep=";",
        index=False,
        header=False,
        encoding="utf-8",
    )

    return full_table


def scrape_table(link_to_table):

    soup = BeautifulSoup(requests.get(link_to_table).content, "html.parser")
    table = soup.find("table", class_="wikitable")
    result = pd.read_html(StringIO(str(table)))[0].dropna()

    # This is to only get the first two columns of the table
    result = result.iloc[:, :2]

    result["rank"] = result["rank"].astype(int)
    result["word"] = result["word"].str.lower()

    return result


def sort_by_frequencity(freq_guide_df, words_df):

    # Merge the two dataframes
    merged_df = words_df.merge(freq_guide_df, left_on="German", right_on="word")

    # Sort the dataframe by rank
    sorted_df = merged_df.sort_values(by="rank")

    # After sort is over, we can drop the extra columns from merge
    sorted_df = sorted_df.drop(columns=["word", "rank"])

    # restore_capitalization(sorted_df, words_df)

    return sorted_df


def restore_capitalization(sorted_df, raw_pd):
    # Rename the columns to avoid confusion in merge
    raw_pd = raw_pd.rename(columns={"German": "German_raw"})
    sorted_df = sorted_df.rename(columns={"German": "German_sorted"})

    reordered_df = sorted_df.merge(raw_pd, on="English", how="left")

    # Make column 3 be column 1, then drop column 3
    reordered_df["German_sorted"] = reordered_df["German_raw"]
    reordered_df = reordered_df.drop(columns=["German_raw"])

    # print(reordered_df)

    return reordered_df


def sort(word_file):

    freq_guide_df = scrape_frequencity_df()

    words_df, raw_pd = split_txt_file(word_file)

    sorted_df = sort_by_frequencity(freq_guide_df, words_df)

    final_df = restore_capitalization(sorted_df, raw_pd)

    print(final_df)

    final_df.to_csv(
        "src/data/sorted_words.txt",
        sep=";",
        index=False,
        header=False,
        encoding="utf-8",
    )
