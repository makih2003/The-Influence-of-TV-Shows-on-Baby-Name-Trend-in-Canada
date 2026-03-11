import os
import pandas as pd
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def get_popular_shows():
    """
    Filter IMDb data to only include English TV shows with ≥ 5,000 votes, rating > 8.2, and release years 1983-2021.
    Saves the results to 'popular_shows.csv' and returns a DataFrame with the following columns:
        - tconst: Unique IMDb ID of the show
        - primaryTitle: Name of the show
        - startYear: Release year of the show's first episode
    """
    df = pd.read_csv(os.path.join(RAW_DATA_DIR, "IMDB.csv"))
    # Include shows released between 1990 and 2021 because the baby names dataset ranges from 1987 to 2024.
    # We need baby name data for ±3 years around each show's release year for the analysis.
    popular_shows = df[
        (df['titleType'] == 'tvSeries') &
        (df['language'] == 'en') &
        (df['numVotes'] >= 5000) &
        (df['averageRating'] >= 8.0) &
        (df['startYear'] >= 1990) & (df['startYear'] <= 2021)
    ]

    # Sort by average rating and number of votes
    popular_shows = popular_shows.sort_values(
        by=['averageRating', 'numVotes'],
        ascending=False
    )

    popular_shows = popular_shows[['tconst', 'primaryTitle', 'startYear']]

    filename = "popular_shows.csv"
    popular_shows.to_csv(os.path.join(PROCESSED_DATA_DIR, filename), index=False)
    print(f"{filename} with {popular_shows.shape[0]} rows has been saved in {PROCESSED_DATA_DIR}")
    return popular_shows


def get_main_characters_names(popular_shows):
    """
    Use the popular_shows dataframe and 'title.principals.tsv' to get the top 3 main character full names per show.
    Returns the resulting DataFrame with the following columns:
        - tconst: Unique IMDb ID of the show
        - characters: Name of the character
        - primaryTitle: Name of the show
        - startYear: Release year of the show's first episode
    Note: Character names may include prefixes (e.g., 'Dr.', 'Detective') or contain noise like "Narrator" or "Voices".
    """
    top_tconsts = popular_shows['tconst']

    # principals has [tconst, ordering, nconst, category, job, characters]
    principals = pd.read_csv(os.path.join(RAW_DATA_DIR, 'title.principals.tsv'), sep='\t', dtype=str)

    # Filter for main actors/actresses from popular shows
    filtered = principals[
        (principals['tconst'].isin(top_tconsts)) &
        (principals['category'].isin(['actor', 'actress']))
    ].copy()

    filtered['ordering'] = filtered['ordering'].astype(int)

    # Keep max 3 characters per show
    top_characters = filtered.sort_values(by=['tconst', 'ordering']).groupby('tconst').head(3)

    #main_characters = top_characters[['tconst', 'characters', 'category', 'ordering']]
    main_characters = top_characters[['tconst', 'characters']]

    # Keep every row in main_characters and match corresponding show info from popular_shows
    main_characters = main_characters.merge(
        popular_shows[['tconst', 'primaryTitle', 'startYear']],
        on='tconst',
        how='left'
    )

    filename = "main_characters.csv"
    main_characters.to_csv(os.path.join(PROCESSED_DATA_DIR, filename), index=False)
    print(f"{filename} with {main_characters.shape[0]} rows has been saved in {PROCESSED_DATA_DIR}")
    return main_characters


def get_clean_firstname(main_characters):
    """
    Clean the main_characters DataFrame to get characters' first names.
    Removes prefixes (e.g., Miss, Dr, Queen) and filters out invalid or generic names  (e.g., "Narrator", "Self").
    Saves the result to 'main_characters.csv' with the following columns:
        - firstName: Cleaned first name of the character
        - releaseYear: Release year of the show's first episode
        - title: Name of the show
    """
    df_with_first_name = main_characters.rename(columns={'characters': 'name'}).copy()

    # Convert to lowercase and remove brackets, quotes, punctuation
    df_with_first_name['name_cleaned'] = (
        df_with_first_name['name']
        .str.lower()
        .str.replace(r"[\[\]\"'()]", "", regex=True)
        .str.replace(r"[^\w\s]", "", regex=True)
    )

    # Drop rows where the full name includes invalid keywords
    invalid_keywords = [
        "Audience", "Various", "Narrator", "Self", "Voice", "Over",
        "Additional", "Regular", "Host", "Girlfriend", "Boyfriend"
    ]
    drop_pattern = r'\b(?:' + '|'.join(invalid_keywords) + r')\b'
    df_with_first_name = df_with_first_name[~df_with_first_name['name'].str.contains(drop_pattern, case=False, na=False)].copy()

    # Remove known prefixes
    prefixes = [
        'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'lord', 'sir', 'ambassador', 
        'special agent', 'the', 'ds', 'detective', 'lieutenant', 'general', 'captain', 'commander', 'major general',
        'sergeant', 'president', 'father', 'mother', 'major', 'officer', 'di', 'dci', 'dc', 'sgt',
        'queen', 'king', 'prince', 'princess', 'lt', 'young', 'old', 'inspector',
        'dad', 'mum', 'audience', 'robot', 'kids', 'samurai', 'superman', 'godmother', 'girlfriend', 'boyfriend'
    ]
    pattern_prefix = r'^\s*(?:' + '|'.join(prefixes) + r')\b\s*'
    df_with_first_name['name_cleaned'] = df_with_first_name['name_cleaned'].str.replace(pattern_prefix, '', regex=True)

    # Extract first word as first name and capitalize them
    df_with_first_name['firstName'] = df_with_first_name['name_cleaned'].str.extract(r'^\s*(\w+)')
    df_with_first_name['firstName'] = df_with_first_name['firstName'].str.strip().str.capitalize()

    # Drop rows with missing first_name and duplicates. i.e., same show and same first name
    df_with_first_name = df_with_first_name.dropna(subset=['firstName'])
    df_with_first_name = df_with_first_name.drop_duplicates(subset=['tconst', 'firstName'], keep='first').copy()

    df_with_first_name = df_with_first_name[['firstName', 'startYear', 'primaryTitle']]
    df_with_first_name.rename(columns={'startYear': 'releaseYear', 'primaryTitle': 'title'}, inplace=True)

    filename = "clean_main_characters.csv"
    df_with_first_name.to_csv(os.path.join(PROCESSED_DATA_DIR, filename), index=False)
    print(f"{filename} with {df_with_first_name.shape[0]} rows has been saved in {PROCESSED_DATA_DIR}")
    return df_with_first_name

def get_name_trends(characters):
    """
    Combine Canadian baby name data with main character names.
    Calculates the number of babies given a character's name in each year from 3 years before to 3 years after the show's release.
    i.e., a 7-year window centered on the release year.
    Filters for name-title pairs where total name count is at least 30 across ±3 years from the show's release year. 
    The final dataset is saved as 'name_trends.csv' which includes the following columns:
        - firstName: Cleaned first name of the character
        - releaseYear: Release year of the show's first episode
        - title: Name of the show
        - count: Number of babies given the character's name in the show's release year
    """
    baby_names = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'baby_names_by_year.csv'))  # name, year, count
    baby_names = baby_names.rename(columns={'name': 'firstName'})
 
    characters['firstName'] = characters['firstName'].str.capitalize()
    baby_names['firstName'] = baby_names['firstName'].str.capitalize()

    merged = pd.merge(characters, baby_names, on='firstName', how='left')
    merged['years_from_release'] = merged['year'] - merged['releaseYear']
    merged = merged[(merged['years_from_release'] >= -3) & (merged['years_from_release'] <= 3)]

    grouped = merged.groupby(['firstName', 'title', 'years_from_release'], as_index=False)['count'].sum()

    unique_names_titles = characters[['firstName', 'title']].drop_duplicates()
    full_years = pd.DataFrame({'years_from_release': range(-3, 4)})
    full_grid = unique_names_titles.merge(full_years, how='cross')

    final = full_grid.merge(grouped, on=['firstName', 'title', 'years_from_release'], how='left')
    final['count'] = final['count'].fillna(0).astype(int)

    # Remove name-title pairs with total count < 30 across all 7 years
    total_counts = final.groupby(['firstName', 'title'])['count'].sum().reset_index()
    valid_pairs = total_counts[total_counts['count'] >= 30][['firstName', 'title']]
    final = final.merge(valid_pairs, on=['firstName', 'title'])
    
    filename = "name_trends.csv"
    final.to_csv(os.path.join(PROCESSED_DATA_DIR, filename), index=False)
    print(f"{filename} with {final.shape[0]} rows has been saved in {PROCESSED_DATA_DIR}")


def main():
    popular_shows = get_popular_shows() # tconst, primaryTitle, startYear
    main_characters = get_main_characters_names(popular_shows) # tconst, characters, primaryTitle, startYear
    df_with_first_name = get_clean_firstname(main_characters) # firstName, releaseYear, title
    get_name_trends(df_with_first_name)  # firstName, releaseYear, title, count


if __name__ == '__main__':
    main()