python merge.py 1234hta
txt2pgn.exe
bayeselo.exe
python merge_version.py 1234hta 50 1
python merge_version.py 1234hta 50 0
python merge.py f
txt2pgn.exe
bayeselo.exe
python merge_version.py f 100 1
python merge_version.py f 100 0
python merge.py s
txt2pgn.exe
bayeselo.exe
python merge_version.py s 20 1
python merge_version.py s 20 0
python merge.py 1234htafs
txt2pgn.exe
bayeselo.exe
python merge_version.py 1234htafs 100 1
python merge_version.py 1234htafs 100 0
python get_bias.py ratings_merge_1234hta_50_1.html ratings_merge_1234hta_50_0.html ratings_merge_1234htafs_100_1.html
python get_bias.py ratings_merge_f_100_1.html ratings_merge_f_100_0.html ratings_merge_1234htafs_100_1.html
python get_bias.py ratings_merge_s_20_1.html ratings_merge_s_20_0.html ratings_merge_1234htafs_100_1.html
python merge_all.py ratings_merge_1234htafs_100_0.html ratings_merge_1234hta_50_0.html ratings_merge_f_100_0.html ratings_merge_s_20_0.html ratings_merge_1234htafs_100_1.html ratings_merge_1234hta_50_1.html ratings_merge_f_100_1.html ratings_merge_s_20_1.html
