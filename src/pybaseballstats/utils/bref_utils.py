BREF_SINGLE_PLAYER_URL = (
    "https://www.baseball-reference.com/players/{initial}/{player_code}.shtml"
)
BREF_SINGLE_PLAYER_SABERMETRIC_FIELDING_URL = (
    "https://www.baseball-reference.com/players/{initial}/{player_code}-field.shtml"
)


def _extract_table(table):
    trs = table.tbody.find_all("tr")
    row_data = {}
    for tr in trs:
        if tr.has_attr("class") and "thead" in tr["class"]:
            continue
        tds = tr.find_all("td")
        if len(tds) == 0:
            continue
        for td in tds:
            data_stat = td.attrs["data-stat"]
            if data_stat not in row_data:
                row_data[data_stat] = []
            if td.find("a"):
                row_data[data_stat].append(td.find("a").string)
            elif td.find("span"):
                row_data[data_stat].append(td.find("span").string)
            elif td.find("strong"):
                row_data[data_stat].append(td.find("strong").string)
            else:
                row_data[data_stat].append(td.string)
    return row_data


BREF_DRAFT_URL = "https://www.baseball-reference.com/draft/index.fcgi?year_ID={draft_year}&draft_round={draft_round}&draft_type=junreg&query_type=year_round&from_type_hs=0&from_type_jc=0&from_type_4y=0&from_type_unk=0"


MANAGERS_URL = "https://www.baseball-reference.com/leagues/majors/{year}-managers.shtml#manager_record"

MANAGER_TENDENCY_URL = "https://www.baseball-reference.com/leagues/majors/{year}-managers.shtml#manager_tendencies"
