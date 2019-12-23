import urllib.request
import urllib.parse
import json
import time
import random
from lxml import html
import chardet
from urllib.request import ProxyHandler, build_opener

def getIpProxys():
    with open('../data/IPpool.json', 'r') as f:
        content = json.loads(f.read())
    IPs = []
    for x in content['data']:
        IPs.append(x['ip']+':'+str(x['port']))
    return IPs

def getUrlData(url):
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
    IPs = getIpProxys()
    
    req = urllib.request.Request(url=url, headers=header, method='GET')
    proxy_handler = ProxyHandler({
        'http': random.choice(IPs),
    })
    opener = build_opener(proxy_handler)
    htmlcode = opener.open(req)
    content = htmlcode.read().decode('utf-8')
    return content

def getCharInfo(char):
    ''' base_url '''
    base_url = 'https://hanyu.baidu.com/s?wd=' + urllib.parse.quote(char) + '&ptype=zici'
    
    ''' all xpaths '''
    pron_xpath = '//*[@id="pinyin"]/span'
    basicInfo_xpath = '//*[@id="basicmean-wrapper"]/div[1]/dl/dd/p'
    detailInfo_xpath = '//*[@id="detailmean-wrapper"]/div[1]/dl/dd'
    external_xpath = '//*[@id="baike-wrapper"]/div[2]/p'
    translation_xpath = '//*[@id="fanyi-wrapper"]/div/dl/dt'
    puzzle_xpath = '//*[@id="miyu-wrapper"]/div[1]/p'
    trad_xpath = '//*[@id="traditional"]/span'
    radical_xpath = '//*[@id="radical"]/span'

    ''' download data '''
    
    content = getUrlData(base_url)
    # content = urllib.request.urlopen(base_url).read().decode('utf-8')
    selector = html.fromstring(content)
    
    ''' fill result '''
    result = {}
    result['character'] = char
    
    '''get pron'''
    multipron = False
    data = selector.xpath(pron_xpath)
    if len(data) > 0:
        if len(data) == 1:
            multipron = False
            result['pronounciation'] = selector.xpath(pron_xpath)[0].xpath('b/text()')[0]
        else:
            multipron = True
            result = [{} for i in range(len(data))]
            for i in range(len(data)):
                result[i]['character'] = char
                result[i]['pronounciation'] = selector.xpath(pron_xpath)[i].xpath('b/text()')[0]
    
    '''get explanation '''
    if multipron == False:
        data = selector.xpath(basicInfo_xpath)
        result['explanation'] = []
        if len(data) > 0:
            for x in data:
                if len(x.xpath('text()')) > 0:
                    if '.' in x.xpath('text()')[0]:
                        explane = x.xpath('text()')[0].split('.')[1]
                    else:
                        explane = x.xpath('text()')[0]
                else:
                    explane = ''
                if len(x.xpath('span/text()')) > 0:
                    example = x.xpath('span/text()')[0].replace('～', '~').split('。')
                else:
                    example = []
                result['explanation'].append((explane, example))
    else:
        data = selector.xpath('//*[@id="basicmean-wrapper"]/div[1]/dl')
        for x in result:
            x['explanation'] = []
        if len(data) > 0:
            for x in data:
                x_pron = x.xpath('dt/text()')[0].strip(' []')
                for i in range(len(result)):
                    if result[i]['pronounciation'] == x_pron:
                        break
                x_data = x.xpath('dd/p')
                for y in x_data:
                    if len(y.xpath('text()')) > 0:
                        if '.' in y.xpath('text()')[0]:
                            explane = y.xpath('text()')[0].split('.')[1]
                        else:
                            explane = y.xpath('text()')[0]
                    else:
                        explane = ''
                    if len(y.xpath('span/text()')) > 0:
                        example = y.xpath('span/text()')[0].replace('～', '~').split('。')
                    else:
                        example = []
                    result[i]['explanation'].append((explane, example))
    
    ''' get detailed explanation '''
    if multipron == False:
        data = selector.xpath(detailInfo_xpath)
        result['detailed'] = {}
        if len(data) > 0:
            if len(data[0].xpath('p')) > 0:
                length = len(data[0].xpath('p'))
                for i in range(length):
                    feature = data[0].xpath('p')[i].xpath('strong/text()')[0].strip('〈〉')
                    result['detailed'][feature] = []
                    feature_data = data[0].xpath('ol')[i].xpath('li')
                    for x in feature_data:
                        mean = x.xpath('p')[0].xpath('text()')[0]
                        l = []
                        for y in x.xpath('p')[1:]:
                            y_text = y.xpath('text()')[0]
                            if '——' in y_text:
                                y_split = y_text.split('——')
                                l.append((y_split[1], y_split[0].replace(char, '~')))
                            else:
                                l.append((None, y_text.replace(char, '~')))
                        result['detailed'][feature].append((mean, l))
    else:
        data = selector.xpath('//*[@id="detailmean-wrapper"]/div[1]/dl')
        for x in result:
            x['detailed'] = {}
        if len(data) > 0:
            for z in data:
                x_pron = z.xpath('dt/a/text()')[0].split('[')[1].strip(' []')
                for j in range(len(result)):
                    if result[j]['pronounciation'] == x_pron:
                        break
                x_data = z.xpath('dd')
                if len(x_data[0].xpath('p')) > 0:
                    length = len(x_data[0].xpath('p'))
                    for i in range(length):
                        feature = x_data[0].xpath('p')[i].xpath('strong/text()')[0].strip('〈〉')
                        result[j]['detailed'][feature] = []
                        feature_data = x_data[0].xpath('ol')[i].xpath('li')
                        for x in feature_data:
                            mean = x.xpath('p')[0].xpath('text()')[0]
                            l = []
                            for y in x.xpath('p')[1:]:
                                y_text = y.xpath('text()')[0]
                                if '——' in y_text:
                                    y_split = y_text.split('——')
                                    l.append((y_split[1], y_split[0].replace(char, '~')))
                                else:
                                    l.append((None, y_text.replace(char, '~')))
                            result[j]['detailed'][feature].append((mean, l))
    
    ''' get external '''
    if multipron == False:
        data = selector.xpath(external_xpath)
        result['external'] = []
        if len(data) > 0:
            result['external'].append((data[0].xpath('text()')[0].strip(' \n'), []))
    else:
        data = selector.xpath(external_xpath)
        for j in range(len(result)):
            result[j]['external'] = []
        for j in range(len(result)):
            if len(data) > 0:
                result[j]['external'].append((data[0].xpath('text()')[0].strip(' \n'), []))
    
    ''' get translation '''
    if multipron == False:
        data = selector.xpath(translation_xpath)
        result['translation'] = []
        if len(data) > 0:
            result['translation'] = data[0].xpath('text()')[0].split('; ')[:]
    else:
        data = selector.xpath(translation_xpath)
        for j in range(len(result)):
            result[j]['translation'] = []
        for j in range(len(result)):
            if len(data) > 0:
                result[j]['translation'] = data[0].xpath('text()')[0].split('; ')[:]

    ''' get radical '''
    if multipron == False:
        data = selector.xpath(radical_xpath)
        result['radical'] = ''
        if len(data) > 0:
            result['radical'] = data[0].xpath('text()')[0]
    else:
        data = selector.xpath(radical_xpath)
        for j in range(len(result)):
            result[j]['radical'] = ''
        for j in range(len(result)):
            if len(data) > 0:
                result[j]['radical'] = data[0].xpath('text()')[0]

    ''' get traditional '''
    if multipron == False:
        data = selector.xpath(trad_xpath)
        result['traditional'] = ''
        if len(data) > 0:
            result['traditional'] = data[0].xpath('text()')[0]
    else:
        data = selector.xpath(trad_xpath)
        for j in range(len(result)):
            result[j]['traditional'] = ''
        for j in range(len(result)):
            if len(data) > 0:
                result[j]['traditional'] = data[0].xpath('text()')[0]
    

    ''' get encoding '''
    if multipron == False:
        result['encoding'] = 'utf-8'
    else:
        for j in range(len(result)):
            result[j]['encoding'] = 'utf-8'

    ''' get puzzles '''
    if multipron == False:
        data = selector.xpath(puzzle_xpath)
        result['puzzles'] = []
        if len(data) > 0:
            for x in data:
                if '.' in x.xpath('text()')[0]:
                    result['puzzles'].append(x.xpath('text()')[0].split('.')[1])
                else:
                    result['puzzles'].append(x.xpath('text()')[0])
    else:
        data = selector.xpath(puzzle_xpath)
        for j in range(len(result)):
            result[j]['puzzles'] = []
        for j in range(len(result)):
            if len(data) > 0:
                for x in data:
                    if '.' in x.xpath('text()')[0]:
                        result[j]['puzzles'].append(x.xpath('text()')[0].split('.')[1])
                    else:
                        result[j]['puzzles'].append(x.xpath('text()')[0])
        
    ''' return a python dict object '''
    return multipron, result


if __name__ == "__main__":
    start_uni = ord('\u4e00')
    end_uni = ord('\u9fa5')
    start_pos = int(input("start char:\n"))
    end_pos = int(input("end char:\n"))
    
    filename = '../data/char-data/char-' + str(start_pos) + '-to-' + str(end_pos) + '.txt'

    with open(filename, 'w') as f:
        for i in range(start_pos, end_pos):
            if start_uni + i > end_uni:
                break
            try :
                multipron, result = getCharInfo(chr(start_uni+i))
            except IndexError:
                print(i, end=': get Index error\n')
            except UnicodeDecodeError:
                print(i, end=': get Decode error\n')
            else:
                if multipron == False:
                    f.write(str(result)+'\n')
                else:
                    for x in result:
                        f.write(str(x)+'\n')
            print(i)
            time.sleep(random.uniform(0.1, 0.2))
