cd /home/user/Tofo/mestres
for k in n2_durer13 n4_girl n4_mother n1_paganini n2_more n4_holbein_lady n3_ideal n3_yeats g_schiele g_vangogh n4_schiele_man n1_edith n5_rembrandt_land n5_crau; do
  f=$(python3 -c "import json;print(json.load(open('tools/selecao.json'))['$k'])")
  for t in 1 2 3; do [ -f obras/hd/$k.jpg ] || python3 tools/wm_one.py "$f" obras/hd/$k.jpg 3840 1920; sleep 3; done
done
