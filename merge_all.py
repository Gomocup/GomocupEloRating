# -*- coding: utf-8 -*-
import sys
import json
import re

try:
    with open('rules.json', 'r') as f:
        rules_data = json.load(f)
except Exception as e:
    print 'Error reading rules.json:', e
    sys.exit(1)

fout = open('output.html', 'w')

# Write minimal toggle script
fout.write('''<script>
function toggleVersions(btn, classId) {
    var rows = document.getElementsByClassName('child-' + classId);
    if (rows.length === 0) return;
    var isHidden = rows[0].style.display === 'none';
    for (var i = 0; i < rows.length; i++) {
        rows[i].style.display = isHidden ? '' : 'none';
    }
    btn.innerHTML = isHidden ? '▼' : '▶';
}
</script>
''')

# 1. Introduction Text
# Construct list of conditions dynamically based on active rules
intro_parts = []
for section in rules_data.get('sections', []):
    for rule in section.get('rules', []):
        disp_name = rule['display_name']
        if disp_name.startswith("The "):
            disp_name = disp_name[4:]
        if disp_name.endswith(" Rating"):
            disp_name = disp_name[:-7]
        intro_parts.append("%d %s" % (rule['min_games'], disp_name.lower()))

if len(intro_parts) > 1:
    intro_games_str = "There exist at least " + ", or ".join(intro_parts[:-1]) + ", or " + intro_parts[-1] + " games."
elif len(intro_parts) == 1:
    intro_games_str = "There exist at least " + intro_parts[0] + " games."
else:
    intro_games_str = "There exist games."

fout.write('<p>Here we compute the Elo ratings of all the gomoku AIs which have ever taken part in gomocup, based on the historical competition results (2000 - present).</p><p>An AI would appear in the best rating list only if it satisfies the following conditions at the same time:</p><ul><li>' + intro_games_str + '</li><li>It has been active in Gomocup in the last five years, or none of its versions has been active in Gomocup during this time period.</li></ul>')
fout.write('\n')

# 2. Generate Navigation Links
base_anchor = 1
for section in rules_data.get('sections', []):
    fout.write('<p><strong>%s:</strong></p>\n' % section['name'])
    fout.write('<ul>\n')
    idx = base_anchor
    for rule in section.get('rules', []):
        fout.write('<li><a href="#elo_%d">%s</a></li>\n' % (idx, rule['display_name']))
        idx += 1
    fout.write('</ul>\n\n')
    
    base_anchor += len(section.get('rules', []))

# 3. Write Table Contents
base_anchor = 1
for section in rules_data.get('sections', []):
    rules = section.get('rules', [])
    M = len(rules)
    
    for i, rule in enumerate(rules):
        anchor_idx = base_anchor + i
        rule_id = str(rule['id'])
        min_games = rule['min_games']
        disp_name = rule['display_name']
        
        fout.write('<p><a name="elo_%d"></a>%s:</p>\n' % (anchor_idx, disp_name))
        
        filename = "ratings_merge_%s_%d_1.html" % (rule_id, min_games)
        try:
            with open(filename, 'r') as fin:
                html_content = fin.read()
        except Exception as e:
            print "Error reading %s: %s" % (filename, e)
            continue
            
        # Parse table rows using regex
        all_trs = re.findall(r'<tr[^>]*>(.*?)</tr>', html_content, re.IGNORECASE | re.DOTALL)
        data_rows = []
        for tr in all_trs:
            if '<td' in tr.lower():
                cells = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.IGNORECASE | re.DOTALL)
                if len(cells) == 11:
                    data_rows.append(cells)
                    
        # Group engines by their family name (first token of name)
        families_order = []
        parents = {}
        children = {}
        for cells in data_rows:
            rank = cells[0].strip()
            name = cells[1].strip()
            family = name.split(' ')[0]
            if rank != "":
                families_order.append(family)
                parents[family] = cells
                children[family] = []
            else:
                if family not in children:
                    children[family] = []
                children[family].append(cells)
                
        # Write the new consolidated collapsible table
        fout.write('<table border=1>\n')
        fout.write('<tbody>\n')
        fout.write('<tr><th>Rank</th><th>Name</th><th>Elo</th><th>+</th><th>-</th><th>games</th><th>score</th><th>oppo.</th><th>draws</th><th>Author</th><th>Place</th></tr>\n')
        
        counter = 0
        for family in families_order:
            cells_parent = parents[family]
            list_children = children[family]
            has_children = len(list_children) > 0
            family_id = "%s_%d" % (rule_id, counter)
            counter += 1
            
            parent_rank = cells_parent[0]
            parent_name = cells_parent[1]
            
            fout.write('<tr>\n')
            if has_children:
                fout.write('  <td>%s <span style="cursor:pointer;background:transparent;background-color:transparent;border:none;outline:none;display:inline-block;" onclick="toggleVersions(this, \'%s\')">▶</span></td>\n' % (parent_rank, family_id))
            else:
                fout.write('  <td>%s</td>\n' % parent_rank)
            fout.write('  <td>%s</td>\n' % parent_name)
                
            for j in range(2, 11):
                fout.write('  <td>%s</td>\n' % cells_parent[j])
            fout.write('</tr>\n')
            
            for cells_child in list_children:
                child_name = cells_child[1]
                fout.write('<tr class="child-%s" style="display: none;">\n' % family_id)
                fout.write('  <td></td>\n')
                fout.write('  <td>&nbsp;&nbsp;&nbsp;&nbsp;%s</td>\n' % child_name)
                for j in range(2, 11):
                    fout.write('  <td>%s</td>\n' % cells_child[j])
                fout.write('</tr>\n')
                
        fout.write('</tbody>\n')
        fout.write('</table>\n\n')
        
    base_anchor += M

# 4. Write Footer
sec_names = []
for section in rules_data.get('sections', []):
    name = section['name']
    if name.startswith("The "):
        name = name[4:]
    if name.endswith(" Rating"):
        name = name[:-7]
    sec_names.append(name)

if len(sec_names) > 1:
    joined_names = ", ".join(sec_names[:-1]) + ", and " + sec_names[-1]
elif len(sec_names) == 1:
    joined_names = sec_names[0]
else:
    joined_names = ""

fout.write('<p>All ratings are calculated using <a href="http://www.remi-coulom.fr/Bayesian-Elo/">Bayesian Elo</a> with eloAdvantage = 0, eloDraw = 0.01, and default prior.</p>\n')
fout.write('<p>The Elo ratings for %s rules are from different rating systems, and should not be compared directly.</p>\n' % joined_names)
fout.close()