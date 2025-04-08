BREF_SINGLE_PLAYER_BATTING_URL = (
    "https://www.baseball-reference.com/players/{initial}/{player_code}.shtml"
)
BREF_SINGLE_PLAYER_FIELDING_URL = (
    "https://www.baseball-reference.com/players/{initial}/{player_code}-field.shtml"
)


def _extract_table(table):
    trs = table.tbody.find_all("tr")
    row_data = {}
    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) == 0:
            continue
        for td in tds:
            data_stat = td.attrs["data-stat"]
            if data_stat not in row_data:
                row_data[data_stat] = []
            row_data[data_stat].append(td.string)
    return row_data
