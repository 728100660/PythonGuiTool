# -*- coding: utf-8 -*-
import json
import os
import requests
import sys
import time
import urllib.parse
from datetime import datetime
from itertools import groupby
from subprocess import Popen, PIPE, STDOUT

import numpy as np
import openpyxl as xl
import pandas as pd
from matplotlib import pyplot as plt
from tabulate import tabulate


class SimuData:

    def __init__(self, url, game_id, data=None, head=None, cookie=None, project_path=None):
        self.url = url
        self.game_id = game_id
        self.data = data
        self.headers = head
        self.cookie = cookie
        self.driver_path = r'C:\Users\admin\Desktop\模型\软件包\chromedriver-win64\chromedriver.exe'
        self.account = 'root'
        self.password = '123456'
        self.project_path = project_path
        self.csv_path = os.path.join(project_path, 'stage', 'server_csv')
        self.excel_path = os.path.join(project_path, 'stage')
        self.script_path = os.path.join(project_path, 'csvScript')

    def sent_csv_toweb(self, stop=True):
        file_path = self.csv_path
        self.tranForm_data()
        if stop:
            stop = self.url + 'SimulateLineGameController/stop?' + urllib.parse.urlencode({'gameId': self.game_id})
            stop_ret = requests.post(stop)
            time.sleep(1)
            if stop_ret.status_code != 200:
                print(stop_ret.text)
                sys.exit()
            else:
                time.sleep(10)
                print('stop sever success', '  ', 'Time: ', stop_ret.headers['Date'])

        post_url = self.url + 'csvConfig/upload'
        fileobj = {
            'type': (None, 'SERVER'),
            'name': (None, 'S' + time.strftime('%Y%m%d%H%M', time.localtime())),
        }
        # ret = self.get_new_cookie()[0]
        new_cookie = 'ds'  # ret.get('name') + '=' + ret.get('value')
        headers = {
            'Cookie': new_cookie,
        }
        menu_url = self.url + 'menu/get'
        print(os.path.basename(file_path))
        a = os.listdir(file_path)
        for i in a:
            if str(self.game_id) == [''.join(list(g)) for k, g in groupby(i, key=lambda x: x.isdigit())][0]:
                file_name = i
                print('find the file : {}'.format(file_name))
                break
        else:
            print('无法定位文件夹，输入文件夹的位置')
            file_name = input()
        file_path = os.path.join(file_path, file_name)
        print(file_path)
        file_list = os.listdir(file_path)
        for i, j in enumerate(file_list):
            # time.sleep(0.3)
            fileobj['file'] = (j, open(os.path.join(file_path, j), 'rb'))
            rests = requests.post(post_url, files=fileobj)
            if rests.status_code == 200:
                print(j, '----', 'upload success')
            elif rests.status_code == 500:
                print('\n', '__' * 20, 'renew cookie', '__' * 20)
                ret = self.get_new_cookie()[0]
                new_cookie = ret.get('name') + '=' + ret.get('value')
                print('\n', '__' * 20, 'new_cookie:', new_cookie, '__' * 20)
                headers['Cookie'] = new_cookie
                fileobj['file'] = (j, open(os.path.join(file_path, j), 'rb'))
                rests = requests.post(post_url, files=fileobj)
                if rests.status_code == 200:
                    print(j, '----', 'upload success')
                else:
                    print('__' * 20, 'upload success again', '__' * 20)
            else:
                print(rests.status_code, '----', 'upload fail', '  ', j)

                sys.exit()
        print('*' * 50, 'upload finished', '*' * 50)

    def sent_exl_toweb(self, stop=True):
        file_path = self.excel_path
        if stop:
            stop = self.url + 'SimulateLineGameController/stop?' + urllib.parse.urlencode({'gameId': self.game_id})
            stop_ret = requests.post(stop)
            time.sleep(1)
            if stop_ret.status_code != 200:
                print(stop_ret.text)
                sys.exit()
            else:
                time.sleep(10)
                print('stop sever success', '  ', 'Time: ', stop_ret.headers['Date'])

        post_url = self.url + 'excelConfig/uploadServer'
        fileobj = {
            'type': (None, 'SERVER'),
            'name': (None, 'S' + time.strftime('%Y%m%d%H%M', time.localtime())),
        }
        # ret = self.get_new_cookie()[0]
        new_cookie = 'ds'  # ret.get('name') + '=' + ret.get('value')
        headers = {
            'Cookie': new_cookie,
        }
        menu_url = self.url + 'menu/get'
        print(os.path.basename(file_path))
        a = os.listdir(file_path)
        for i in a:
            if str(self.game_id) == [''.join(list(g)) for k, g in groupby(i, key=lambda x: x.isdigit())][0]:
                file_name = i
                print('find the file : {}'.format(file_name))
                break
        else:
            print('无法定位文件夹，输入文件夹的位置')
            file_name = input()
        file_path = os.path.join(file_path, file_name)
        with open(file_path, "rb") as file:
            file_name = file_path.split(os.sep)[-1]
            fileobj['file'] = (file_name, file)
            rests = requests.post(post_url, files=fileobj)
            if rests.status_code == 200:
                print(file_name, '----', 'upload success')
            elif rests.status_code == 500:
                print('\n', '__' * 20, 'renew cookie', '__' * 20)
                ret = self.get_new_cookie()[0]
                new_cookie = ret.get('name') + '=' + ret.get('value')
                print('\n', '__' * 20, 'new_cookie:', new_cookie, '__' * 20)
                headers['Cookie'] = new_cookie
                fileobj['file'] = (file_name, open(os.path.join(file_path, file_name), 'rb'))
                rests = requests.post(post_url, files=fileobj)
                if rests.status_code == 200:
                    print(file_name, '----', 'upload success')
                else:
                    print('__' * 20, 'upload success again', '__' * 20)
            else:
                print(rests.status_code, '----', 'upload fail', '  ', file_name)

                sys.exit()
        print('*' * 50, 'upload finished', '*' * 50)

    def sent_csv_toweb_special(self, file_path='D:\slot\stage\server_csv', stop=True):
        self.tranForm_data()
        if stop:
            stop = self.url + 'SimulateLineGameController/stop?' + urllib.parse.urlencode({'gameId': self.game_id})
            stop_ret = requests.post(stop)
            time.sleep(1)
            if stop_ret.status_code != 200:
                print(stop_ret.text)
                sys.exit()
            else:
                print('stop sever success', '  ', 'Time: ', stop_ret.headers['Date'])

        post_url = self.url + 'csvConfig/upload'
        fileobj = {
            'type': (None, 'SERVER'),
            'name': (None, 'S' + time.strftime('%Y%m%d%H%M', time.localtime())),
        }
        # ret = self.get_new_cookie()[0]
        new_cookie = 'ds'  # ret.get('name') + '=' + ret.get('value')
        headers = {
            'Cookie': new_cookie,
        }
        menu_url = self.url + 'menu/get'
        print(os.path.basename(file_path))
        a = os.listdir(file_path)
        # for i in a:
        #     if str(self.game_id) == [''.join(list(g)) for k, g in groupby(i, key=lambda x: x.isdigit())][0]:
        #         file_name = i
        #         print('find the file : {}'.format(file_name))
        #         break
        # else:
        #     print('无法定位文件夹，输入文件夹的位置')
        #     file_name = input()
        # file_path = os.path.join(file_path, file_name)
        print(file_path)
        file_list = os.listdir(file_path)
        for i, j in enumerate(file_list):
            # time.sleep(0.3)
            fileobj['file'] = (j, open(os.path.join(file_path, j), 'rb'))
            rests = requests.post(post_url, files=fileobj)
            if rests.status_code == 200:
                print(j, '----', 'upload success')
            elif rests.status_code == 500:
                print('\n', '__' * 20, 'renew cookie', '__' * 20)
                ret = self.get_new_cookie()[0]
                new_cookie = ret.get('name') + '=' + ret.get('value')
                print('\n', '__' * 20, 'new_cookie:', new_cookie, '__' * 20)
                headers['Cookie'] = new_cookie
                fileobj['file'] = (j, open(os.path.join(file_path, j), 'rb'))
                rests = requests.post(post_url, files=fileobj)
                if rests.status_code == 200:
                    print(j, '----', 'upload success')
                else:
                    print('__' * 20, 'upload success again', '__' * 20)
            else:
                print(rests.status_code, '----', 'upload fail', '  ', j)

                sys.exit()
        print('*' * 50, 'upload finished', '*' * 50)

    def get_new_cookie(self):
        # options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        # service = Service(executable_path=self.driver_path)
        # driver = webdriver.Chrome(service=service, options=options)
        # driver.get(self.url)
        # try:
        #     time_sort_btn = WebDriverWait(driver, 3).until(
        #         EC.element_to_be_clickable(
        #             (By.XPATH, '//*[@id="account"]'))
        #     )
        #     time_sort_btn.send_keys(self.account)
        #     driver.find_element(By.XPATH,'//*[@id="password"]').send_keys(self.password)
        #     driver.find_element(By.XPATH,'//*[@id="login"]').click()
        #     ret = driver.get_cookies()
        # except TimeoutException:
        #     ret = driver.get_cookies()
        # print('\n', '__' * 20, 'get new cookie succeed', '__' * 20)
        # driver.quit()
        # print(ret)
        io = 'sd'
        return io

    def tranForm_data(self, type='stage'):
        return
        type_list = {'stage': 'server_transform-stage.bat', 'system': 'server_transform-system.bat'}
        fold_address = self.script_path
        bat_name = type_list[type]
        original_path = os.getcwd()
        os.chdir(fold_address)
        # os.environ['PYTHONIOENCODING'] = 'utf8'
        p = Popen("cmd.exe /c" + os.path.join(fold_address, bat_name), stdout=PIPE, stderr=STDOUT)
        curline = p.stdout.readline()
        print(curline.decode('utf8'))
        while 'pause' not in curline.decode('utf8'):
            curline = p.stdout.readline()
            print(curline.decode('utf8'))
        p.kill()
        os.chdir(original_path)
        print('*' * 50, 'Transform excel to csv success', '*' * 50)

    def simu_serverBet(self, need_request=None):
        if need_request:
            stop = self.url + 'SimulateLineGameController/stop?' + urllib.parse.urlencode({'gameId': self.game_id})
            stop_ret = requests.post(stop)
            time.sleep(1)
            if stop_ret.status_code != 200:
                print(stop_ret.text)
                sys.exit()
            else:
                time.sleep(10)
                print('stop sever success', '  ', 'Time: ', stop_ret.headers['Date'])

            clean = self.url + 'SimulateLineGameController/reset?' + urllib.parse.urlencode(
                {'gameId': self.game_id, 'type': 'NON'})
            clean_respones = requests.post(clean)
            time.sleep(1)
            if clean_respones.status_code != 200:
                print(clean_respones.text)
                sys.exit()
            else:
                print('clean data success', '  ', 'Time: ', clean_respones.headers['Date'])

            SimulateLineGameController = self.url + 'SimulateLineGameController/serverBet?'
            for i in self.data:
                if self.data[i]:
                    if i == 'times':
                        SimulateLineGameController += i + '=' + str(self.data[i])
                    else:
                        SimulateLineGameController += i + '=' + str(self.data[i]) + '&'
                else:
                    continue
            get_r = requests.post(SimulateLineGameController)
            if get_r.status_code != 200:
                print(get_r.text)
                sys.exit()
            else:
                print('request data success', '  ', 'Time: ', get_r.headers['Date'])

        time.sleep(1)
        getSimulateData = self.url + 'SimulateLineGameController/getStatistic?' + urllib.parse.urlencode(
            {'gameId': self.game_id})
        # for i in range(2):
        #     time.sleep(1.5)
        #     resp = requests.post(getSimulateData).json()
        #     print('totalTimes',resp['totalTimes'])
        final = requests.post(getSimulateData)
        # print(final.json())
        # print(json.dumps(final))
        return final.json()

    def simu_OldGame(self, need_request=None):

        if need_request:

            stop = self.url + 'GameDataRecordHandle/stop?' + urllib.parse.urlencode({'gameId': self.game_id})
            stop_ret = requests.get(stop)
            if stop_ret.status_code != 200:
                print(stop_ret.text)
                sys.exit()
            else:
                print('stop server success')
            time.sleep(1)

            clean = self.url + 'GameDataRecordHandle/clearGameRunData?' + urllib.parse.urlencode(
                {'gameId': self.game_id})
            clean_respones = requests.get(clean)
            if clean_respones.status_code != 200:
                print(clean_respones.text)
                sys.exit()
            else:
                print('clean data success')
            time.sleep(1)

            SimulateLineGameController = self.url + 'GameDataRecordHandle/betWithThread?' + urllib.parse.urlencode(
                self.data)
            get_r = requests.post(SimulateLineGameController)
            if get_r.status_code != 200:
                print(get_r.text)
                sys.exit()
            else:
                print('request success')

        time.sleep(1)
        getSimulateData = self.url + 'GameDataRecordHandle/getGameRunData?' + urllib.parse.urlencode(
            {'gameId': self.game_id})

        final = requests.get(getSimulateData)
        if final.status_code != 200:
            print(final.text)
            sys.exit()
        else:
            print('get data success', '  ', 'Time: ', final.headers['Date'])
        # print(final.json())
        return final.json()

    def simu_Bet(self, need_request=None):

        if need_request:

            stop = self.url + 'SimulateLineGameController/stop?' + urllib.parse.urlencode({'gameId': self.game_id})
            stop_ret = requests.post(stop)
            if stop_ret.status_code != 200:
                print(stop_ret.text)
                sys.exit()
            else:
                print('stop sever success', '  ', 'Time: ', stop_ret.headers['Date'])
            time.sleep(1)

            clean = self.url + 'SimulateLineGameController/reset?' + urllib.parse.urlencode(
                {'gameId': self.game_id, 'type': 'NON'})
            clean_respones = requests.post(clean)
            if clean_respones.status_code != 200:
                print(clean_respones.text)
                sys.exit()
            else:
                print('clean data success', '  ', 'Time: ', clean_respones.headers['Date'])
            time.sleep(1)
            SimulateLineGameController = self.url + 'SimulateLineGameController/bet?'
            for i in self.data:
                if self.data[i]:
                    if i == 'times':
                        SimulateLineGameController += i + '=' + str(self.data[i])
                    else:
                        SimulateLineGameController += i + '=' + str(self.data[i]) + '&'
                else:
                    continue
            get_r = requests.post(SimulateLineGameController)
            if get_r.status_code != 200:
                print(get_r.text)
                sys.exit()
            else:
                print('request data success', '  ', 'Time: ', get_r.headers['Date'])
        time.sleep(1)
        getSimulateData = self.url + 'SimulateLineGameController/getStatistic?' + urllib.parse.urlencode(
            {'gameId': self.game_id})
        final = requests.post(getSimulateData).json()
        return final

    def serverBet_Data_plot(self, type=None):
        info = self.simu_serverBet(type)
        ret_list = np.array([])
        for i in range(len(info)):
            ret_list = np.append(ret_list, info["LongLongType(m_Long1={}, m_Long2={})".format(i, 5)]['totalRtp'])
        if len(ret_list[ret_list >= 80]) / len(ret_list) >= 0.8:
            plt.figure(dpi=200)
            plt.scatter([i for i in range(30)], ret_list, label='simulated RTP', color='r')
            plt.plot([i for i in range(30)], [80 for i in range(30)], label='line: RTP = 80', color='b')
            plt.title('Satisfaction rate: {}%'.format(round(len(ret_list[ret_list >= 80]) / len(ret_list) * 100, 2)))
            plt.grid(axis='y')
            plt.legend()
            plt.show()

    def is_formated_bet_data(self, bet_data):
        if not isinstance(bet_data, dict):
            return False
        for key, data in bet_data.items():
            if not isinstance(data, dict):
                return False
        return True

    def serverBet_Data_print(self, type=None):
        server_bet_data = self.simu_serverBet(type)
        key = (f"SimulateBetKey(groupId={self.data.get('group', 0)}, betType={self.data['betType']}, "
               f"gameActive={self.data['gameActive']}, unlockFunction={'true' if self.data['unlockFunction'] else 'false'})")
        data = server_bet_data[key]
        # data = self.simu_serverBet(type)["LongLongType(m_Long1=0, m_Long2=1)"]
        # 如果服务器格式化了返回结果则使用服务器的，否则使用默认的格式化方式返回结果
        if self.is_formated_bet_data(bet_data=data):
            return data
        data_info = {
            'overall': {
                'totalTimes': data['totalTimes'],
                'totalRtp': data['totalRtp'],
                'normalRtp': data['normalRtp'],
                'mgBounsRtp': data.get('mgBounsRtp', 0),
                'fgBounsRtp': data.get('fgBounsRtp', 0),
                'freeRtp': data['freeRtp'],
                'jackpotRtp': data['jackpotRtp'],
                'bonusRtp': data['bonusRtp'],
                'FGZeroRate': sum(data['freeRateCountMap'].values()) / data['freeRateCountMap']['0'] if data[
                    'freeRateCountMap'].get('0', False) else 0,
                'Broken': data['broken'],
                'CoV': data['rvalue'],
            },
            # 'baseGame':{
            #     '3_Freq':data['totalTimes']/data['iconLineTotalWinMap']['3']['totalTimes'] if data['iconLineTotalWinMap']['3']['totalTimes'] else 0,
            #     '4_Freq':data['totalTimes']/data['iconLineTotalWinMap']['4']['totalTimes'] if data['iconLineTotalWinMap']['4']['totalTimes'] else 0,
            #     '5_Freq':data['totalTimes']/data['iconLineTotalWinMap']['5']['totalTimes'] if data['iconLineTotalWinMap']['5']['totalTimes'] else 0,
            # },
            'FG': {
                'freeRtp': data['freeRtp'],
                'fgBounsRtp': data.get('fgBounsRtp', 0),
                'fg_Freq': data['totalTimes'] / data['fgTimes'] if data['fgTimes'] else 0,
                'fg_times': data['fgTimes'],
                'totalTimes': data['totalTimes'],
            },
            # 'Jackpot':{
            #     'jackpotRtp': data['jackpotRtp'],
            #     'jackpot_Freq': data['totalTimes']/data['bonusWinMap']['1']['totalTimes'],
            #     'jackpot_times': data['jackpotWin']['totalTimes'],
            # },
            # 'Bonus':{
            #     'bonusRtp': data['bonusRtp'] - data['jackpotRtp'],
            #     'mgBounsRtp': data['mgBounsRtp'],
            #     'fgBounsRtp': data['fgBounsRtp'],
            #     'bonus_Freq': data['totalTimes']/data['bonusWinMap']['2']['totalTimes'],
            #     'bonus_times': data['bonusWin']['totalTimes'],
            # },
            # 'mgBounsRtp':data['mgBounsRtp'],
        }

        # self.print_lab(data_info)
        # if data['totalTimes'] == self.data['times']:
        #     self.printOut()
        return data_info

    def printOut(self):
        a = self.simu_serverBet()
        with open(os.path.join(os.getcwd(), '{}.json'.format(
                str(self.game_id) + '_' + str(self.data['gameActive']) + '_' + str(self.data['times']))), 'w+') as st:
            st.write(json.dumps(a))
        sys.exit()

    def OldGame_Data_print(self, type_w=None):

        data = self.simu_OldGame(type_w)
        print(data)
        data_s = json.loads(data['extraData'])
        out_put = {
            'overall': {
                'RTP': data['rtp'],
                'deductionCount': data['deductionCount'],
                'bet': data['bet'],
            },
            'normal': {
                # 'normalRtp': data_s['normalWin']/,
                'normalWin': data_s['normalWin'],
            },
            # 'FG': {
            #     # 'freeRtp':data_s['freeRtp'],
            #     'freeTrigger':int(data['deductionCount'])/int(data_s['freeCount']) if int(data_s['freeCount']) else 0,
            #     'freeWin':data_s['freeWin'],
            #     # 'fg_jackpot':data_s['fg_jackpot'],
            #     'freeCount':data_s['freeCount'],
            #     # 'freeRateCountMap':data_s['extraData']['freeRateCountMap'],
            # },
            # 'JP':{
            #     # 'jackpotRtp': data_s['jackpotRtp'],
            #     'jackpotCount': data_s['jackpotCount'],
            #     'jackpotWin': data_s['jackpotWin'],
            #     'mg_jackpot': data_s['mg_jackpot'],
            # },
            # 'normalRateCountMap':data_s['normalRateCountMap'],
            # 'freeRateCountMap': data_s['freeRateCountMap'],
        }
        # head = []
        # for i in out_put:
        #     head.append(str(i.keys()))
        self.print_lab(out_put)
        # return data

    def Task_simu(self, need_request=None, callback=None):

        if need_request:

            self.tranForm_data()

            stop = self.url + 'SimulateLineGameController/stop?' + urllib.parse.urlencode({'gameId': self.game_id})
            stop_ret = requests.post(stop)
            if stop_ret.status_code != 200:
                print(stop_ret.text)
                sys.exit()
            else:
                print('stop sever success', '  ', 'Time: ', stop_ret.headers['Date'])
            time.sleep(3)
            file_path = 'D:\slot\stage\server_csv\任务模拟配置表\simulate_quest.csv'

            clean_id = self.url + 'QuesetSimulateController/clearUserId'
            clean_id_respones = requests.get(clean_id)
            if clean_id_respones.status_code != 200:
                print(clean_id_respones.text)
                sys.exit()
            else:
                print('clean user id success', '  ', 'Time: ', clean_id_respones.headers['Date'])
            time.sleep(3)

            clean = self.url + 'SimulateLineGameController/reset?' + urllib.parse.urlencode(
                {'gameId': self.game_id, 'type': 'NON'})
            clean_respones = requests.post(clean)
            if clean_respones.status_code != 200:
                print(clean_respones.text)
                sys.exit()
            else:
                print('clean data success', '  ', 'Time: ', clean_respones.headers['Date'])
            time.sleep(3)

            post_url = self.url + 'csvConfig/upload'
            fileobj = {
                'type': (None, 'SERVER'),
                'name': (None, 'S' + time.strftime('%Y%m%d%H%M', time.localtime())),
                'file': ('simulate_quest.csv', open(file_path, 'rb'))
            }
            rests = requests.post(post_url, files=fileobj)
            if rests.status_code == 200 and rests.json()['success']:
                print('任务模拟配置表.xlsx', '----', 'upload success')
            else:
                print(rests.status_code, '----', 'upload fail', '  ', '任务模拟配置表.xlsx')
                sys.exit()
            print('upload finished')

            SimulateLineGameController = self.url + 'SimulateLineGameController/bet?' + urllib.parse.urlencode(
                self.data)
            get_r = requests.post(SimulateLineGameController)
            if get_r.status_code != 200:
                print(get_r.text)
                sys.exit()
            else:
                print('request data success', '  ', 'Time: ', get_r.headers['Date'])

        time.sleep(3)
        getSimulateData = self.url + 'QuesetSimulateController/getSimulateData'
        global g_run_forever
        for i in range(500):
            if not g_run_forever:
                break
            time.sleep(3)
            resp = requests.get(getSimulateData).text
            print(resp)
            if callback:
                callback(resp)
        set_thread_stop_flag(0)

    @staticmethod
    def print_lab(data):
        """
        输出版面的排版
        :param data: 输出的数据-字典格式，最多嵌套两层字典
        :return:
        """
        len_m, head, data_fame = [], [], []
        op = 0
        for i in data:
            len_m.append(len(data[i]))
            op += 1
        for k, i in enumerate(data):
            head.append(i)
            a = []
            for j in data[i]:
                if type(data[i][j]) != float:
                    a.append(str(j) + ":  " + str(data[i][j]))
                else:
                    a.append(str(j) + ": " + str(round(data[i][j], 4)))
            data_fame.append(a)
        we = []
        for i in range(max(len_m)):
            we.append([])
            for j in range(op):
                try:
                    we[i].append(data_fame[j][i])
                except IndexError:
                    we[i].append(" ")
        print(tabulate(we, headers=head, tablefmt='double_outline'))
        return tabulate(we, headers=head, tablefmt='double_outline')


def run(url, initial_info, callback=None, project_path=None):
    game_id = initial_info.get("gameId")
    if not game_id:
        print(f"!!!!!!!!!!!!!!错误的gameId{game_id}!!!!!!!!!!!")
        return
    axw = SimuData(url=url, game_id=game_id, data=initial_info, project_path=project_path)

    # axw.sent_csv_toweb()
    axw.sent_exl_toweb()
    # axw.sent_csv_toweb_special(file_path='D:\slot\stage\server_csv\关卡模式表', stop=True)
    # axw.simu_Bet(1)
    # for i in range(1000):
    #     print(axw.simu_Bet())

    # axw.Task_simu(1)
    #

    a = axw.simu_serverBet(1)
    global g_run_forever
    for i in range(5000):
        if not g_run_forever:
            break
        time.sleep(5)
        data = axw.serverBet_Data_print()
        if callback:
            callback(data)
    set_thread_stop_flag(0)

    # a = axw.simu_OldGame(1)
    # for i in range(5000):
    #     time.sleep(3)
    #     axw.OldGame_Data_print()

    # a = axw.simu_serverBet()
    # with open('156_1_10000000.json','w') as st:
    #     st.write(json.dumps(a))


def rtp_check():
    url = ('http://192.168.30.108:8098/')
    # url = 'http://192.168.30.81:8094/'
    file_path = r'D:\saga\stage'
    success_pass = "C:\\Users\\admin\\Desktop\\special_mode_simu_data\\pass_info\\"
    fail_pass = 'C:\\Users\\admin\\Desktop\\special_mode_simu_data\\fail_info\\'
    simu_times = 1000000
    game_mode = {
        1: '普通模式',
        4: '超级模式',
        5: '新手模式',
        6: 'Quest模式',
        7: '储值模式',
        8: '首充模式',
        9: '过剩模式',
    }

    check_stage_list = {
        # 70:[1,5],
        # 111:[1,5],
        #  1:[1],
        #  2:[1],
        #  55:[1],
        #  74:[1],
        #  75:[1],
        #  88:[1],
        #  106:[1],
        #  107:[1],
        #  109:[1],
        #  110:[1],

        111: [1],
        112: [1],
        119: [1],
        134: [1],

    }
    get_file_path = r'C:\Users\admin\Desktop\模拟结果'
    count_time = 1
    line_num = 1
    # lock_type = 'unlock'
    rtp_info = pd.DataFrame(columns=['Game_Id', 'RTP'])
    for i in range(1):
        lock_type = False if i == 0 else True
        for game_id in check_stage_list:
            for mode in check_stage_list[game_id]:

                initial_info = {
                    'betMoney': 1000000000,
                    'betType': 0,
                    'gameActive': mode,
                    'gameId': game_id,
                    'unlockFunction': lock_type,
                    'brokenInitialIndex': 60,
                    'ex': 0.9,
                    # 'group':30,
                    # 'chooseIndex':0,
                    'initLevel': 100,
                    'initMoney': 10000000000000000000,
                    'threadNum': 8,
                    'times': simu_times,
                }
                initial_info_1 = {
                    'betMoney': 10000,
                    'betTypeEnum': 'REGULAR',
                    'gameId': game_id,
                    'gameActive': mode,
                    'initMoney': 10000000000000,
                    'level': 200,
                    'parameter': 1 if game_id != 134 else 3,
                    'run': simu_times,
                    'writeLib': False,
                    'thread': 1,

                }

                a = os.listdir(file_path)
                for i in a:
                    if str(game_id) == [''.join(list(g)) for k, g in groupby(i, key=lambda x: x.isdigit())][0]:
                        file_name = i
                # excel_change(os.path.join(file_path,file_name),mode)
                axw = SimuData(url=url, game_id=game_id, data=initial_info_1)
                # if count_time == 1 :
                #     axw.sent_csv_toweb()
                # axw.sent_csv_toweb_special(file_path='D:\slot\stage\server_csv\关卡模式表',stop=True)
                axw.simu_OldGame(1)

                runTimes = 0
                while True:
                    time.sleep(3)
                    # data = axw.simu_serverBet()["SimulateBetKey(groupId=0, betType=0, gameActive={0}, unlockFunction={1})".format(mode,str.lower(str(lock_type)))]
                    data = axw.simu_OldGame(need_request=None)
                    # print('游戏ID：',game_id,'    Type：',lock_type,'    游戏名称：',file_name.split('.')[0],'    游戏模式：',game_mode[mode],'   模拟次数：',data['totalTimes'],'    总RTP：',data['totalRtp'])
                    print('游戏ID：', game_id, '    游戏名称：', file_name.split('.')[0], '   模拟次数：',
                          data['deductionCount'], '总RTP：', data['rtp'])
                    # print(data['totalRtp'])
                    # if data['totalTimes'] == initial_info['times']:

                    if (int(data['deductionCount']) == initial_info_1['run']) or (
                            (int(data['deductionCount']) == runTimes) and (
                            abs(initial_info_1['run'] - int(data['deductionCount'])) < initial_info_1['run'] * 0.05)):
                        now = datetime.now()
                        # timestamp = now.timestamp()
                        rtp_info.loc[line_num] = [game_id, data['rtp']]
                        line_num += 1
                        tital = 'https://api.day.app/bTx8KAeebQ2uuyXmRUU3L9/'
                        final = tital + 'GameId：{}/'.format(str(game_id)) + str(data['rtp']) + '  ' + str(
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        requests.get(final)
                        # with open(os.path.join(get_file_path, '{}.json'.format(str(game_id) +'_' + str(lock_type)+ '_' + str(game_mode[mode]) +'_' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))),'w+') as st:
                        #     a = data
                        #     st.write(json.dumps(a))
                        #     print('-'*50,'写入完成','-'*50)
                        break
                    runTimes = int(data['deductionCount'])
                    count_time += 1
    rtp_info.to_excel('total_info.xlsx', sheet_name='Sheet1')

    # while True:
    #     time.sleep(1)
    #     data = axw.OldGame_Data_print()['LongLongType(m_Long1=0, m_Long2={})'.format(mode)]
    #     print('游戏ID：',game_id,'    游戏名称：',file_name.split('.')[0],'    解锁状态：',lock_type,'    游戏模式：',game_mode[mode],'   模拟次数：',data['totalTimes'],'    总RTP：',data['totalRtp'])
    #     if int(data['totalTimes']) == simu_times:
    #         a = data
    #         with open(os.path.join(get_file_path, '{}.json'.format(
    #                 str(game_id) + '_' + str(mode) +'_' +lock_type+'_' + str(simu_times))),
    #                   'w+') as st:
    #             st.write(json.dumps(a))
    #         print('-'*50,'写入完成','-'*50)
    #         break
    # count_time += 1


def excel_change(path, mode_change):
    excel_list = 'ABCDEFGHIJK'
    name = ''
    data_1 = pd.read_excel(path, sheet_name=None)
    for i in list(data_1.keys()):
        if 'reel_pro' in i:
            name = i
    print(name)
    data = pd.read_excel(path, sheet_name=name, header=2)
    intial_list = np.array(data[data.game_active == 1].index) + 4
    change_list = np.array(data[data.game_active == mode_change].index) + 4
    game_active_col = data.columns.tolist().index('game_active')
    data = xl.load_workbook(path)
    data_write = data[name]
    for i in intial_list:
        data_write['{}'.format(excel_list[game_active_col] + str(i))] = mode_change
    for i in change_list:
        data_write['{}'.format(excel_list[game_active_col] + str(i))] = 1
    data.save(path)
    print('*' * 50, 'change game_active finish', '*' * 50)


def json_read():
    path = r'C:\Users\admin\Desktop\special_mode_simu_data\json_info'
    excel_path = r'C:\Users\admin\Desktop\special_mode_simu_data\total_info.xlsx'
    excel = xl.load_workbook(excel_path)
    dat = excel['info']
    count_time = 2
    for i in os.listdir(path):
        with open(os.path.join(path, i), 'r') as f:
            data = json.load(f)
            dat['A{}'.format(count_time)] = i.split('_')[1].split('.')[0]
            dat['B{}'.format(count_time)] = i.split('_')[0]
            dat['C{}'.format(count_time)] = data['rtp']
        count_time += 1

    excel.save(excel_path)


def task_run(url, task_info, callback=None, project_path="D:\\slot\\", need_request=1):

    game_id = task_info.get("gameId")
    axw = SimuData(url=url, game_id=game_id, data=task_info, project_path=project_path)
    # axw.sent_csv_toweb()
    axw.sent_exl_toweb()
    axw.Task_simu(need_request, callback)

    # a = axw.simu_serverBet()
    # with open('156_1_10000000.json','w') as st:
    #     st.write(json.dumps(a))


def old_game_check():
    url = 'http://192.168.30.108:8098/'
    file_path = r'D:\saga\stage'
    get_file_path = r'C:\Users\admin\Desktop\模拟结果'
    tital = 'https://api.day.app/bTx8KAeebQ2uuyXmRUU3L9/'
    check_stage_list = [1, 2]

    total_info = pd.DataFrame(columns=['Game_Id', 'Game_Name', 'Set_No', 'Set_Count', 'RTP'])
    line_num = 1
    for index, game_id in enumerate(check_stage_list):
        try:
            a = os.listdir(file_path)
            for i in a:
                if str(game_id) == [''.join(list(g)) for k, g in groupby(i, key=lambda x: x.isdigit())][0]:
                    file_name = i
            # os.close(file_path)
            game_name = file_name.split('.')[0]
            setNoNumber = url + 'GameDataRecordHandle/getSetNoByGameId?' + urllib.parse.urlencode({'gameId': game_id})
            set_count = requests.get(setNoNumber)
            time.sleep(1)
            if set_count.status_code != 200:
                print(set_count.text)
                sys.exit()
            else:
                set_info = set_count.json()
            for set_no in set_info[str(game_id)].keys():
                # if int(set_no) < 900:
                #     continue
                old_game = {
                    'betMoney': 10000,
                    'betTypeEnum': 'REGULAR',
                    'gameId': game_id,
                    'gameActive': 1,
                    'initMoney': 10000000000,
                    'level': 200,
                    'parameter': 1,
                    'setNo': set_no,
                    'run': 100000,
                    'thread': 1,
                    'writeLib': False,

                }
                axw = SimuData(url=url, game_id=game_id, data=old_game)
                # axw.sent_csv_toweb()
                axw.simu_OldGame(need_request=True)
                while True:
                    time.sleep(3)
                    data = axw.simu_OldGame(need_request=None)
                    print('游戏ID：', game_id, '    游戏名称：', game_name, '   模拟次数：', data['deductionCount'],
                          '   Set_No：', set_no, '    总RTP：', data['rtp'])
                    # print(data['totalRtp'])
                    if int(data['deductionCount']) == old_game['run']:
                        total_info.loc[line_num] = [game_id, game_name, set_no, set_info[str(game_id)][set_no],
                                                    float(data['rtp']) * 0.01]
                        line_num += 1
                        with open(os.path.join(get_file_path, '{}.json'.format(
                                str(game_id) + '_' + str(set_no) + '_' + str(old_game['run']))),
                                  'w+') as st:
                            a = data
                            st.write(json.dumps(a))
                            print('-' * 50, '写入完成', '-' * 50)
                        break
            info_to = tital + 'GameId：{}/'.format(str(game_id)) + str(
                (index + 1) / len(check_stage_list) * 100) + '%    ' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            requests.get(info_to)
        except Exception as e:
            final = tital + 'STOP IN ：{}/'.format(str(game_id)) + str(e)
            requests.get(final)
    total_info.to_excel('total_info.xlsx', sheet_name='Sheet1')


def stop_bet(url, game_id):
    stop = (url + 'SimulateLineGameController/stop?' +
            urllib.parse.urlencode({'gameId': game_id}))
    stop_ret = requests.post(stop)
    time.sleep(1)
    if stop_ret.status_code != 200:
        print(stop_ret.text)
        sys.exit()

def set_thread_stop_flag(flag=1):
    global g_run_forever
    if flag == 1:
        g_run_forever = 0
    else:
        g_run_forever = 1

g_run_forever = 1       # 程序是否一直循环

if __name__ == '__main__':
    g_game_id = 162
    g_task_info = {
        'betMoney': 2000000,
        'betType': 0,
        'gameActive': 1,
        'gameId': g_game_id,
        # 'group':30,
        # 'chooseIndex':0,
        'initLevel': 650,
        'initMoney': 10000000000000000000,
        'threadNum': 1,
        'times': 10000,
    }
    g_initial_info = {
        'betMoney': 1000000000,
        'betType': 0,
        'gameActive': 1,
        'gameId': g_game_id,
        'brokenInitialIndex': 60,
        'ex': 0.9,
        'unlockFunction': True,
        # 'group':30,
        # 'chooseIndex':0,
        'initVipLevel': 1,
        'initLevel': 100,
        'initMoney': 10000000000000000000,
        'threadNum': 8,
        'times': 50000000,
    }
    g_old_game = {
        'betMoney': 10000,
        'betTypeEnum': 'REGULAR',
        'gameId': g_game_id,
        'gameActive': 1,
        'initMoney': 10000000000,
        'level': 200,
        'parameter': 2,
        'run': 10000000,
        'thread': 1,

    }
    # url = 'http://192.168.30.13:8095/'
    # url = 'http://192.168.30.74:8094/'
    # g_url = 'http://192.168.30.68:8096/'
    g_url = 'http://192.168.30.121:8093/'
    run(g_url, g_task_info, g_initial_info, g_old_game,
        callback=None, project_path="D:\\slot\\")
    # old_game_check()
    # task_run(g_url, g_task_info)
    # rtp_check()
    # json_read()
    # excel_change(r'C:\Users\admin\Desktop\2恭喜发财配置.xlsx',7)
    # SimuData.tranForm_data()
