py -2 merge.py 1234hta
txt2pgn.exe
cat input.txt | bayeselo.exe
py -2 merge_version.py 1234hta 50 1
py -2 merge_version.py 1234hta 50 0
py -2 merge.py f
txt2pgn.exe
cat input.txt | bayeselo.exe
py -2 merge_version.py f 100 1
py -2 merge_version.py f 100 0
py -2 merge.py s
txt2pgn.exe
cat input.txt | bayeselo.exe
py -2 merge_version.py s 20 1
py -2 merge_version.py s 20 0
py -2 merge.py r
txt2pgn.exe
cat input.txt | bayeselo.exe
py -2 merge_version.py r 20 1
py -2 merge_version.py r 20 0
py -2 merge.py 1234htafs
txt2pgn.exe
cat input.txt | bayeselo.exe
py -2 merge_version.py 1234htafs 100 1
py -2 merge_version.py 1234htafs 100 0
py -2 get_bias.py ratings_merge_1234hta_50_1.html ratings_merge_1234hta_50_0.html ratings_merge_1234htafs_100_1.html
py -2 get_bias.py ratings_merge_f_100_1.html ratings_merge_f_100_0.html ratings_merge_1234htafs_100_1.html
py -2 get_bias.py ratings_merge_s_20_1.html ratings_merge_s_20_0.html ratings_merge_1234htafs_100_1.html
py -2 get_bias.py ratings_merge_r_20_1.html ratings_merge_r_20_0.html ratings_merge_1234htafs_100_1.html 384
py -2 merge_all.py ratings_merge_1234hta_50_0.html ratings_merge_f_100_0.html ratings_merge_s_20_0.html ratings_merge_1234htafs_100_0.html ratings_merge_1234hta_50_1.html ratings_merge_f_100_1.html ratings_merge_s_20_1.html ratings_merge_1234htafs_100_1.html ratings_merge_r_20_0.html ratings_merge_r_20_1.html
