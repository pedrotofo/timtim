import json,sys
p=json.load(open('tools/prompts.json'))
print(json.dumps([{'model':'nano-banana-2','mode':'text2image','params':{'aspectRatio':p[k]['ar'],'resolution':'1K','prompt':p[k]['prompt']}} for k in sys.argv[1:]],ensure_ascii=False))
