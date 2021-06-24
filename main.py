# _*_ coding:utf-8 _*_
# author: liuyunfz
import re
import threading
import os
import time

import requests
from urllib.parse import quote, unquote
from lxml import etree


def out_error(msg: str):
    with open("error.txt", "a+") as f:
        f.write(msg + "\n")


class DealThread(threading.Thread):
    def __init__(self, url):
        super(DealThread, self).__init__()
        self.url = url

    def run(self) -> None:
        rsp_t = None
        try:
            rsp_t = requests.get(url=self.url)
        except Exception as e:
            out_error(str(e) + "\n" + self.url)
            print(e)
        rsp_HTML_t = etree.HTML(rsp_t.text)
        file_list_t = rsp_HTML_t.xpath("//a[@class='list-group-item list-group-item-action']")
        print(self.url, threading.currentThread().getName(), rsp_t.status_code, len(file_list_t))
        for item_t in file_list_t[1:]:
            if item_t.xpath("./i/@class")[0] == "icon ion-ios-folder":
                thread_t = DealThread(url=item_t.xpath("./@href")[0])
                thread_t.start()
                thread_t.join()
            else:
                try:
                    rsp_f = requests.get(requests.get(url=item_t.xpath("./@href")[0]).url.replace("pdf/?file=/paperdownload/", ""))
                    # file_name = re.findall("(?<=dir/).*(?=/)", rsp_f.url)[0].replace("%7C", "/").replace("%20", " ")
                    file_name = unquote(re.findall("(?<=dir/).*(?=/)", rsp_f.url)[0]).replace("|", "/")
                    print(file_name)

                    try:
                        dirs = "pdf floder/"
                        dir_path = unquote(rsp_f.url.split("/dir/%7C")[1]).replace("|", "/")
                        if os.path.exists(dirs + dir_path[:-1]):
                            time.sleep(0.5)
                            continue
                        dir_path_list = dir_path.split("/")[:-2]
                        print(dir_path_list)
                        for i in dir_path_list:
                            dirs = dirs + i + "/"
                            try:
                                os.mkdir(dirs)
                            except FileExistsError:
                                continue
                    except Exception as e:
                        out_error("Error:%s\nFile_name:%s\n dir_path:%s" % (e, file_name, dir_path))

                        print(e)

                    with open("pdf floder%s" % file_name, "wb") as f:
                        f.write(rsp_f.content)
                        time.sleep(0.2)
                except Exception as e:
                    out_error("Error:%s" % e)
                    print(e)
                    # print(re.findall("(?<=filename\\*=utf-8'')\\S*[.][a-zA-Z]+", rsp_f.headers.get('Content-Disposition'))[0])


if __name__ == '__main__':
    if not os.path.exists("pdf floder"):
        os.mkdir("pdf floder")
    url = "https://easypaper.zqwei-tech.cn/paperdownload/show/"
    rsp = requests.get(url=url)
    rsp_HTML = etree.HTML(rsp.text)
    file_list = rsp_HTML.xpath("//a[@class='list-group-item list-group-item-action']")
    print(len(file_list))
    threadPool = []
    for item in file_list:
        if item.xpath("./i/@class")[0] == "icon ion-ios-folder":
            url = item.xpath("./@href")[0]
            threadPool.append(DealThread(url=url))

        else:
            print(item.xpath("./@href")[0])
    for threadItem in threadPool:
        threadItem.start()
    for threadItem in threadPool:
        threadItem.join()
