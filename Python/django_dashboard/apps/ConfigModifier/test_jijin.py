import concurrent.futures
# print("dddd")
import json
import time


list_dic ={'ddd':1,'kkkkk':2}
list = []
test_string = '{"Nikhil" : 1, "Akshat" : 2, "Akash" : 3}'
res = json.loads(test_string)
print(list_dic)
timestr = time.strftime("%Y%m%d-%H%M%S")
# f = open("C:\\Users\\mzhao\\Downloads\\myfile_"+timestr +".txt", "x")
# f.write(json.dumps(sorted(list_dic.items(), key=lambda item: item[1])))
# f.write(json.dumps(list_dic))
# f.close()


def find_unused_cases_runnable(url):
    print("re " + str(url))
    return url


with open('C:\\Users\\mzhao\\Downloads\\data.txt', 'r') as file:
    data = file.read()
    res = json.loads(data)
    for value,url in  res.items():
        print(value + " : " + str(url))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    future_to_url = {executor.submit(find_unused_cases_runnable, url): url for value,url in  list_dic.items()}
    for future in concurrent.futures.as_completed(future_to_url):
        suite_map = future_to_url[future]
        try:
            total_cases_temp, project_list_temp = future.result()
        except Exception as exc:
            print('') 
        else:
            print('')        