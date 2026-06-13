# -*- coding: utf-8 -*-
import sys
import os
import re
import json

try:
    import urllib2 as urllib
except ImportError:
    import urllib.request as urllib

# Base Gomocup URL
BASE_URL = "https://gomocup.org"


def fetch_url(url):
    req = urllib.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    response = urllib.urlopen(req)
    return response.read()


def load_nickmap():
    nickmap = {}
    if os.path.exists('nickname.txt'):
        with open('nickname.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = re.split(r'\s+', line)
                if len(rec) >= 3:
                    nickmap[rec[0].upper()] = (rec[1], rec[2])
                elif len(rec) == 2:
                    nickmap[rec[0].upper()] = (rec[1], None)
    return nickmap


def load_displayname():
    display_names = set()
    if os.path.exists('displayname.txt'):
        with open('displayname.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('\t')
                if parts:
                    display_names.add(parts[0].strip().upper())
    return display_names


def get_existing_base_names(year_str):
    existing = set()
    records_dir = 'records'
    if not os.path.exists(records_dir):
        return existing
    for filename in os.listdir(records_dir):
        # Exclude non-record files and the current target year records
        if not filename.endswith('.txt') or filename == 'add_title.py' or filename.startswith(year_str + '_'):
            continue
        filepath = os.path.join(records_dir, filename)
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                match = re.match(r'^\s*(.+?)\s+-\s+(.+?)\s*:', line)
                if match:
                    for name in (match.group(1), match.group(2)):
                        base_match = re.match(r'^([A-Za-z_\-\.]+)', name)
                        if base_match:
                            existing.add(base_match.group(1).upper())
    return existing


def map_key_to_suffix(group_key, rules):
    rule_map = {r["id"]: r["suffixes"] for r in rules}
    
    # Identify rule_id based on key characteristics
    rule_id = None
    group_num = 1
    
    if group_key.startswith("f15_"):
        rule_id = "freestyle15"
        try:
            group_num = int(group_key.split("_")[1])
        except ValueError:
            pass
    elif group_key.startswith("f20_"):
        rule_id = "freestyle20"
        try:
            group_num = int(group_key.split("_")[1])
        except ValueError:
            pass
    elif re.match(r'^f\d+$', group_key):
        rule_id = "freestyle20"
        group_num = int(group_key[1:])
    elif group_key == 'f':
        rule_id = "fastgame"
        group_num = 1
    elif re.match(r'^s\d+$', group_key):
        rule_id = "standard"
        group_num = int(group_key[1:])
    elif re.match(r'^r\d+$', group_key):
        rule_id = "renju"
        group_num = int(group_key[1:])
    elif group_key == 'r':
        rule_id = "renju"
        group_num = 1
    elif re.match(r'^c\d+$', group_key):
        rule_id = "caro"
        group_num = int(group_key[1:])
    elif group_key == 'c':
        rule_id = "caro"
        group_num = 1
        
    if rule_id and rule_id in rule_map:
        suffixes = rule_map[rule_id]
        idx = group_num - 1
        if 0 <= idx < len(suffixes):
            return suffixes[idx]
            
    return None


def main():
    if len(sys.argv) < 2:
        print "Usage: py -2 scrape_results.py <results_page_url>"
        print "Example: py -2 scrape_results.py https://gomocup.org/results/gomocup-result-2023/"
        sys.exit(1)
        
    main_url = sys.argv[1].strip()
    
    # Extract year from URL, e.g. gomocup-result-2023/ -> 2023
    match_year = re.search(r'result-(\d+)', main_url)
    if not match_year:
        match_year = re.search(r'/(\d{4})/', main_url)
    if not match_year:
        match_year = re.search(r'/(\d{4})$', main_url)
    if not match_year:
        print "Error: Cannot extract year from URL: %s" % main_url
        print "The URL must contain a 4-digit year (e.g. 'gomocup-result-2023' or '2024')."
        sys.exit(1)
        
    year_str = match_year.group(1)
    print "Starting Gomocup %s results scraper and parser..." % year_str
    
    # 1. Load configuration and dictionaries
    nickmap = load_nickmap()
    display_names = load_displayname()
    existing_bases = get_existing_base_names(year_str)
    
    # Load rules.json
    rules = []
    if os.path.exists('rules.json'):
        try:
            with open('rules.json', 'r') as f:
                rules_data = json.load(f)
                for section in rules_data.get('sections', []):
                    for rule in section.get('rules', []):
                        rules.append(rule)
        except Exception as e:
            print "Warning: Error reading rules.json: %s" % e
            
    # 2. Fetch main results page
    print "Fetching main results page: %s" % main_url
    try:
        main_html = fetch_url(main_url)
    except Exception as e:
        print "Error fetching main page:", e
        sys.exit(1)
        
    # Find all table iframes matching the extracted year
    iframe_pattern = r'tables/' + year_str + r'_([a-z0-9_]+)\.html'
    iframe_matches = re.findall(iframe_pattern, main_html)
    if not iframe_matches:
        print "No tournament tables found in main page HTML for year %s!" % year_str
        sys.exit(1)
        
    print "Found %d tournament tables to parse." % len(iframe_matches)
    
    new_nicknames = []
    new_displaynames = []
    
    records_dir = 'records'
    if not os.path.exists(records_dir):
        os.makedirs(records_dir)
        
    for group_key in iframe_matches:
        suffix = map_key_to_suffix(group_key, rules)
        if not suffix:
            print "Warning: Unknown group key '%s', skipping." % group_key
            continue
            
        table_url = BASE_URL + "/static/tournaments/tables/" + year_str + "_" + group_key + ".html"
        print "\nParsing table URL: %s (Suffix: _%s)" % (table_url, suffix)
        
        try:
            table_html = fetch_url(table_url)
        except Exception as e:
            print "Error fetching table URL %s:" % table_url, e
            continue
            
        # Parse names in order
        names = re.findall(r'<TR><TD><NUM>\d+</NUM></TD><TD><NAME>([^<]+)</NAME></TD>', table_html)
        if not names:
            print "No engine names found in table, skipping."
            continue
            
        print "Engines in this group: %s" % ", ".join(names)
        
        # Parse scores for each row
        rows = re.findall(r'<TR>(.*?)</TR>', table_html, re.DOTALL)
        
        new_lines = []
        
        # Parse matches
        for i, row in enumerate(rows):
            # Check if it is an engine data row
            if "<TD><NUM>" not in row:
                continue
                
            cells = re.findall(r'<TD[^>]*>(.*?)</TD>', row)
            if len(cells) < 5:
                continue
                
            row_engine = re.search(r'<NAME>([^<]+)</NAME>', cells[1]).group(1)
            try:
                row_idx = names.index(row_engine)
            except ValueError:
                continue
                
            match_results = cells[4:]
            for col_idx in range(len(match_results)):
                # Skip duplicate pairs and diagonal cells
                if row_idx >= col_idx or col_idx >= len(names):
                    continue
                    
                cell_val = match_results[col_idx].strip()
                if cell_val == '-' or 'dash' in cell_val:
                    continue
                
                # Parse score A:B
                score_match = re.search(r'(\d+)\s*:\s*(\d+)', cell_val)
                if score_match:
                    score_a = int(score_match.group(1))
                    score_b = int(score_match.group(2))
                    new_lines.append("%s - %s: %d : %d" % (names[row_idx], names[col_idx], score_a, score_b))
                    
        # Write to records
        dest_file = os.path.join(records_dir, "%s_%s.txt" % (year_str, suffix))
        with open(dest_file, 'w') as f:
            f.write("\n".join(new_lines) + "\n")
        print "Saved %d match results to %s" % (len(new_lines), dest_file)
        
        # 3. Detect new engines and versions
        for name in names:
            name_upper = name.upper()
            
            # Resolve name base and year
            base = name_upper
            year = None
            
            # Check for trailing digits indicating year
            base_match = re.match(r'^([A-Z_\-\.]+)([0-9]+)$', name_upper)
            if base_match:
                base = base_match.group(1)
                year_suffix = base_match.group(2)
                if len(year_suffix) == 2 and year_suffix[0] in ('0', '1', '2'):
                    year = '20' + year_suffix
                else:
                    year = year_suffix
            else:
                if name_upper in nickmap:
                    mapped = nickmap[name_upper]
                    base = mapped[0]
                    if mapped[1] and mapped[1].isdigit() and len(mapped[1]) == 4:
                        year = mapped[1]
                else:
                    clean_match = re.match(r'^([A-Z_\-\.]+)', name_upper)
                    if clean_match:
                        base = clean_match.group(1)
            
            is_new = False
            if year is None:
                if base not in existing_bases:
                    print "New engine family detected: %s! Mapping to %s." % (base, year_str)
                    year = year_str
                    is_new = True
                    existing_bases.add(base)
                    
            resolved_name = base + " " + (year if year else year_str)
            
            # If it's a new engine family, add nickname map entry
            if is_new:
                nickname_entry = "%s\t%s\t%s" % (base, base, year_str)
                new_nicknames.append(nickname_entry)
                nickmap[base] = (base, year_str)
                
            # If resolved_name is not in display_names, add display name mapping
            if resolved_name.upper() not in display_names:
                display_entry = "%s\t%s" % (resolved_name, resolved_name)
                new_displaynames.append(display_entry)
                display_names.add(resolved_name.upper())
                
    # 4. Save updates to nickname.txt and displayname.txt
    if new_nicknames:
        print "\nAppending %d new engines to nickname.txt..." % len(new_nicknames)
        with open('nickname.txt', 'a') as f:
            for entry in new_nicknames:
                f.write(entry + '\n')
                print "  Added nickname: %s" % entry
                
    if new_displaynames:
        print "\nAppending %d new display names to displayname.txt..." % len(new_displaynames)
        with open('displayname.txt', 'a') as f:
            for entry in new_displaynames:
                f.write(entry + '\n')
                print "  Added displayname: %s" % entry
                
    print "\nAll Gomocup %s results successfully scraped, parsed, and recorded!" % year_str


if __name__ == '__main__':
    main()
