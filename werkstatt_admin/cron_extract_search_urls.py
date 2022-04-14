import re
from datetime import date

with open('/var/log/nginx/access.log.1') as f:
    lines = f.readlines()
    
search_urls = list()

for l in lines:
    if 'GET ' in l:
        r = re.search(r'GET (\S+)', l)
        if 'search' in r.group(1):
            search_urls.append(r.group(1))
            
with open('/home/ubuntu/search_analysis/urls_{}.txt'.format(date.weekday(date.today())), mode="w") as f:
    f.write('\n'.join(search_urls))
