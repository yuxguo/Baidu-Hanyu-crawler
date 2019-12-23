import urllib.request
import urllib.parse
import json
import time
import random
from lxml import html
from urllib.request import ProxyHandler, build_opener
import urllib.error


def getIpProxys():
    with open('../data/IPpool.json', 'r') as f:
        content = json.loads(f.read())
    IPs = []
    for x in content['data']:
        IPs.append(x['ip']+':'+str(x['port']))
    return IPs


def getUrlData(url, IPs):
    USER_AGENTS = [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5"
    ]
    header = {'User-Agent': random.choice(USER_AGENTS)}
    
    req = urllib.request.Request(url=url, headers=header, method='GET')
    proxy_handler = ProxyHandler({
        'http': random.choice(IPs),
    })
    opener = build_opener(proxy_handler)
    htmlcode = opener.open(req)
    content = htmlcode.read().decode('utf-8')
    return content


def getWordList(char, IPs, one_page=True):
    ''' Multi page data need to change one_page=False '''
    ''' first to get all words of the char '''
    words_url = 'https://hanyu.baidu.com/hanyu/ajax/search_list?wd=' + urllib.parse.quote(char+'组词') + '&cf=zuci&ptype=term&pn='
    page = 1
    results = []
    while True:
        content = getUrlData(words_url+str(page), IPs)
        if content == -1:
            continue
        data = json.loads(content)
        if data['ret_num'] == 0:
            break
        for x in data['ret_array']:
            d = {}
            d['word'] = x['name'][0]
            d['pronounciation'] = x['pinyin'][0]
            results.append(d)
        page +=1

        if one_page:
            break
        # time.sleep(random.uniform(0.1, 0.2))
    print('words number:', end='')
    print(len(results))
    return results


def getWordInfo(r_word, IPs):
    ''' visit every word '''
    result = {}
    result['word'] = r_word['word']
    result['pronounciation'] = r_word['pronounciation']
    ''' xpaths '''
    basicInfo_xpath = '//*[@id="basicmean-wrapper"]/div[1]/dl/dd/p'
    detailInfo_xpath = '//*[@id="detailmean-wrapper"]/div[1]/dl/dd/ol/li' 
    external_xpath = '//*[@id="baike-wrapper"]/div[2]/p'
    translation_xpath = '//*[@id="fanyi-wrapper"]/div/dl/dt'


    ''' get every word '''
    base_url = 'https://hanyu.baidu.com/s?wd=' + urllib.parse.quote(result['word'])+'&ptype=zici'
    content = getUrlData(base_url, IPs)
    selector = html.fromstring(content)

    ''' get basic info '''
    data = selector.xpath(basicInfo_xpath)
    result['explanation'] = []
    if len(data) > 0:
        for x in data:
            if len(x.xpath('text()')) > 0:
                text = x.xpath('text()')[0].strip(' \n')
                if '.' in x.xpath('text()')[0]:
                    text = text.split('.')[1]
                if '：' in text:
                    t = text.split('：')
                    explane = t[0]
                    example = [y for y in t[1].replace('～', '~').split('。') if y != '']
                else:
                    explane = text
                    example = []
            else:
                explane = ''
                example = []
            result['explanation'].append((explane, example))

    ''' get detail info '''
    data = selector.xpath(detailInfo_xpath)
    result['detailed'] = []
    if len(data) > 0:
        for x in data:
            if len(x.xpath('p')) == 2:
                ''' Have example '''
                mean = x.xpath('p')[0].xpath('text()')[0]
                example = []
                e_text = x.xpath('p')[1].xpath('text()')[0].replace(result['word'], '~').replace('～', '~')
                e_data = [y for y in e_text.split('”') if y != '']
                for y in e_data:
                    if '：“' in y:
                        ''' Have author '''
                        example.append((y.split('：“')[0], y.split('：“')[1]))
                    else:
                        ''' No author '''
                        example.append((None, y))
                result['detailed'].append((mean, example))
            elif len(x.xpath('p')) == 1:
                ''' No example '''
                mean = x.xpath('p')[0].xpath('text()')[0]
                result['detailed'].append((mean, []))
            else:
                pass

    ''' get external info '''
    data = selector.xpath(external_xpath)
    result['external'] = []
    if len(data) > 0:
        result['external'].append((data[0].xpath('text()')[0].strip(' \n'), []))
        
    ''' get translation info '''
    data = selector.xpath(translation_xpath)
    result['translation'] = []
    if len(data) > 0:
        result['translation'] = data[0].xpath('text()')[0].split('; ')[:]

    return result


if __name__ == "__main__":

    start_uni = ord('\u4e00')
    end_uni = ord('\u9fa5')
    start_pos = int(input("start char:\n"))
    end_pos = int(input("end char:\n"))
    filename = '../data/word-data/word-' + str(start_pos) + '-to-' + str(end_pos) + '.txt'
    IPs = getIpProxys()
    with open(filename, 'w') as f:
        for i in range(start_pos, end_pos):
            if start_uni + i > end_uni:
                break
            for k in range(5):
                try:
                    rs = getWordList(chr(start_uni+i), IPs)
                except ConnectionResetError:
                    if k == 4:
                        print('ConnectionResetError')
                        exit(0)
                    print('retry '+str(k)+' times')
                    time.sleep(random.uniform(1, 2))
                except urllib.error.URLError:
                    if k == 4:
                        print('urllib.error')
                        exit(0)
                    print('retry '+str(k)+' times')
                    time.sleep(random.uniform(1, 2))
                except KeyError:
                    print('retry '+str(k)+' times')
                    time.sleep(random.uniform(1, 2))
                else:
                    break
            
            for j in range(len(rs)):
                for k in range(5):
                    try:
                        result = getWordInfo(rs[j], IPs)
                    except ConnectionResetError:
                        if k == 4:
                            print('ConnectionResetError')
                            exit(0)
                        print('retry '+str(k)+' times')
                        time.sleep(random.uniform(1, 2))
                    except urllib.error.URLError:
                        if k == 4:
                            print('urllib.error')
                            exit(0)
                        print('retry '+str(k)+' times')
                        time.sleep(random.uniform(1, 2))
                    else:
                        f.write(str(result)+'\n')
                        break
            print(i, end='\n\n')
            