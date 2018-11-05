import requests
import json
import time
import random


base_url = 'http://m.shmetro.com/interface/metromap/metromap.aspx?func=fltime&line='
station_info_url = 'http://m.shmetro.com/interface/metromap/metromap.aspx?func=stationInfo&stat_id='
station_timesheet_url = 'http://m.shmetro.com/interface/metromap/metromap.aspx?func=fltime&stat_id='

line_num_arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17]
station_file = 'station.json'


def read_json(filename):
    with open(filename, 'r', encoding='utf8') as f:
        return json.load(f);


def write_json(filename, data):
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)
        f.close()


def carwler_station_info():
    # keys = read_json('key.json')
    json_str = '[{"华夏中路":"1622"},{"周浦东":"1624"},{"鹤沙航城":"1625"},{"航头东":"1626"},{"新场":"1627"},{"野生动物园":"1628"},{"惠南":"1629"},{"惠南东":"1630"},{"书院":"1631"},{"临港大道":"1632"},{"滴水湖":"1633"}]'
    keys = json.loads(json_str, encoding='utf8')
    result = []
    for key in keys:
        station_name = list(key.keys())[0]
        station_id = key[station_name]
        # url = station_info_url + station_id
        url = station_timesheet_url + station_id
        station_info = make_request(url)
        result = result + station_info
    write_json('timesheet_append.json', result)


def format_timesheet():
    # timesheets = read_json('timesheet_append.json')
    station_infos = read_json('stationinfo_append.json')
    data = {}
    # for timesheet in timesheets:
    for station_info in station_infos:
        # stat_id = timesheet['stat_id']
        stat_id = station_info['stat_id']
        if not stat_id in data:
            data[stat_id] = [station_info]
        else:
            data[stat_id].append(station_info)
    write_json('stationInfo_append1.json', data)


def crawler(filename):
    result = []
    for line_num in line_num_arr:
        print('request for line ' + str(line_num))
        # request result json by line_num
        result = result + make_request(base_url + str(line_num))
    print('request finished!')
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(result, f, ensure_ascii=False)


def make_request(url):
    r = requests.get(url)
    return r.json()


def format_station_info():
    timesheets = read_json('timesheet2.json')
    station_infos = read_json('stationInfo1.json')
    data = {}
    for stat_id in timesheets:
        timesheet = timesheets[stat_id]
        station_info = station_infos[stat_id]
        data[stat_id] = {
            'timesheet': timesheet,
            'toiletPosition': station_info['toiletPosition'],
            'elevator': station_info['elevator'],
            'entranceInfo': station_info['entranceInfo']
        }
    print(data)
    write_json('stationInfo2.json', data)


def find_value_vy_key(arr, key):
    for ele in arr:
        if key.strip() == list(ele.keys())[0]:
            return ele[key.strip()]
    return None


def add_stat_id():
    keys = read_json('key.json')
    # stations = read_json('stations.json')
    transfers = read_json('transfers.json')
    data = []
    # for station in stations:
    for transfer in transfers:
        # station_name = station['id']
        transfer_name = transfer['data-id']
        stat_id = find_value_vy_key(keys, transfer_name)
        if stat_id is not None:
            transfer['statid'] = stat_id
        else:
            print('has not find stat_id for ' + transfer_name)
        data.append(transfer)
    write_json('transfers.json', data)


def delete_dict_by_names(dic, names):
    for name in names:
        if dict is not None and name in dic:
            del dic[name]
    return dic


def format_timesheet_json():
    # key is stat_id
    result = {}
    timesheet = read_json('timesheet.json')
    for ele in timesheet:
        stat_id = ele['stat_id']
        ele = delete_dict_by_names(ele, ["station_code", "direction"])
        if stat_id in result:
            result[stat_id]['timesheet'].append(ele)
        else:
            result[stat_id] = {}
            result[stat_id]['timesheet'] = [ele]
    write_json('timesheet.json', result)
    return result, list(dict.keys(result))


def crawl_stat_info_by_id(timesheet, stat_ids):
    for stat_id in stat_ids:
        url = station_info_url + stat_id
        station_info = make_request(url)[0]
        timesheet[stat_id]['elevator'] = station_info['elevator']
        timesheet[stat_id]['entranceInfo'] = station_info['entrance_info']
        timesheet[stat_id]['toiletPosition'] = station_info['toilet_position']
        time.sleep(random.random())
    write_json('timesheet1.json', timesheet)



if __name__ == '__main__':
    filename = 'timesheet.json'
    # crawl for line information, only for timesheet
    # generate timesheet.json
    crawler(filename)
    # format the timesheet json
    # result[stat_id]['timeshhet']
    timesheet, stat_ids = format_timesheet_json()
    crawl_stat_info_by_id(timesheet, stat_ids)
    # carwler_station_info()
    # format_station_info()
    # add_stat_id()
    # format_timesheet()