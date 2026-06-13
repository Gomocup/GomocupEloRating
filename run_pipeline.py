import sys
import os
import json
import subprocess


def run_command(args, stdin=None):
    print "Running: %s" % " ".join(args)
    if stdin:
        with open(stdin, 'r') as f:
            subprocess.check_call(args, stdin=f)
    else:
        subprocess.check_call(args)


def main():
    try:
        with open('rules.json', 'r') as f:
            rules_data = json.load(f)
    except Exception as e:
        print "Error reading rules.json:", e
        sys.exit(1)

    sections = rules_data.get('sections', [])
    
    # 1. Collect all rules
    rules = []
    for section in sections:
        for rule in section.get('rules', []):
            rules.append(rule)

    # 2. Run for each active rule
    for rule in rules:
        rule_id = str(rule['id'])
        min_games = rule['min_games']
        print "\n=== Processing rule: %s ===" % rule_id
        
        # Step A: merge
        run_command(["py", "-2", "merge.py", rule_id])
        
        # Step B: txt2pgn
        run_command(["txt2pgn.exe"])
        
        # Step C: bayeselo
        run_command(["bayeselo.exe"], stdin="input.txt")
        
        # Step D: merge_version for all versions
        run_command(["py", "-2", "merge_version.py", rule_id, str(min_games), "1"])
        
        # Step E: merge_version for best versions only
        run_command(["py", "-2", "merge_version.py", rule_id, str(min_games), "0"])

    # 3. Run for global reference baseline
    print "\n=== Processing global reference baseline ==="
    run_command(["py", "-2", "merge.py", "global_reference"])
    run_command(["txt2pgn.exe"])
    run_command(["bayeselo.exe"], stdin="input.txt")
    run_command(["py", "-2", "merge_version.py", "global_reference", "100", "1"])
    run_command(["py", "-2", "merge_version.py", "global_reference", "100", "0"])

    # 4. Calibrate bias using get_bias.py
    print "\n=== Calibrating ELO bias ==="
    ref_html = "ratings_merge_global_reference_100_1.html"
    for rule in rules:
        rule_id = str(rule['id'])
        min_games = rule['min_games']
        base_bias = rule.get('base_bias', 0)
        
        html_1 = "ratings_merge_%s_%d_1.html" % (rule_id, min_games)
        html_0 = "ratings_merge_%s_%d_0.html" % (rule_id, min_games)
        
        cmd = ["py", "-2", "get_bias.py", html_1, html_0, ref_html]
        if base_bias != 0:
            cmd.append(str(base_bias))
        
        run_command(cmd)

    # 5. Merge all files into final output.html
    print "\n=== Consolidating HTML results ==="
    run_command(["py", "-2", "merge_all.py"])
    print "\n=== Pipeline completed successfully! ==="


if __name__ == '__main__':
    main()
