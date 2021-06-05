##https://www.youtube.com/watch?v=g0TVDyyVSGs 파이스탁 자동매매


# r2: 기본 코드에서 값 변경하기. 5분봉.  5 25 100 1440(5일선) 정배열일때 매수하는걸로.
# r3: 수익이랑 손절조건 추가해주기
# 4: price_buy 가격이 계속 바뀌어서 매도가 안나감.. 매도 익절 손절가가 계속바껴서. 수정함
# r5: git 업로드용임.    ip주소 211.196.254.138  (신림) ,15.164.229.188,172.31.38.8 (aws)

import threading
import queue
import time
import pyupbit
import datetime
from collections import deque

#
# ### 접속 확인하기 ############
#
# access_key = "QyVvZAHpcXLRLq0Iv9xoYHUr3ixXjao6T01u8AWq"
# secret_key = "ONyn77Fm7eQeNraxMbtLfscsxxFqBaVc1QRDeKeo"
# upbit = pyupbit.Upbit(access_key, secret_key)
#
#
#         # 잔고 조회
# balances = upbit.get_balances()
# print(" 잔고조회 ")
# print(balances)
#
# for balance in balances:
#     print(balance)
#
# for i in range(0, 34):
#     print(i, balances[i]['currency'], balances[i]['balance'])
#
#         # 원화 잔고 조회
#     print("보유 KRW : {}".format(upbit.get_balance(ticker="KRW")))  # 보유 KRW
#     print("총매수금액 : {}".format(upbit.get_amount('ALL')))  # 총매수금액
#     print("비트수량 : {}".format(upbit.get_balance(ticker="KRW-BTC")))  # 비트코인 보유수량
#     print("리플 수량 : {}".format(upbit.get_balance(ticker="KRW-XRP")))  # 리플 보유수량
#     print("\n")
#     print(upbit.get_chance('KRW-BTC'))  # 마켓별 주문 가능 정보를 확인
#     print("\n")
#     print(upbit.get_order('KRW-XRP'))  # 주문 내역 조회

        ################






class Consumer(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q
        #self.ticker = "KRW-XRP"
        self.ticker = "KRW-DOGE"

        self.ma5 = deque(maxlen=5)
        self.ma25 = deque(maxlen=25)
        self.ma100 = deque(maxlen=100)
        self.ma1440 = deque(maxlen=1440)

        df = pyupbit.get_ohlcv(self.ticker, interval="minute5")

        self.ma5.extend(df['close'])
        self.ma25.extend(df['close'])
        self.ma100.extend(df['close'])
        self.ma1440.extend(df['close'])

        print(len(self.ma5), len(self.ma25), len(self.ma100), len(self.ma1440))


    def run(self):
        price_curr = None
        hold_flag = False
        wait_flag = False


    ########## upbit 텍스트파일 에서 key 읽어오는 코드 ##############

        # with open("upbit.txt", "r") as f:
        #     key0 = f.readline().strip()
        #     key1 = f.readline().strip()

    ###################################################################

        key0 = "0zMnYeOuZyxPEjboxr9pJDDOSPc4WpXbvJx2oYvx"
        key1 = "IwFKvpX9GzTX9SkwMooSDPSIoV5tML6C7luc6X8d"

        upbit = pyupbit.Upbit(key0, key1)
        print('upbit 접속 성공')

        cash = upbit.get_balance()
        print("보유현금", cash)


        i = 0

        while True:
            try:
                if not self.q.empty():
                    if price_curr != None:
                        self.ma5.append(price_curr)
                        self.ma25.append(price_curr)
                        self.ma100.append(price_curr)
                        self.ma1440.append(price_curr)

                    curr_ma5 = sum(self.ma5) / len(self.ma5)
                    curr_ma25 = sum(self.ma25) / len(self.ma25)
                    curr_ma100 = sum(self.ma100) / len(self.ma100)
                    curr_ma1440 = sum(self.ma1440) / len(self.ma1440)

                    curr_ma5_tick = pyupbit.get_tick_size( curr_ma5 )   # 주문할때 5이평 가까운 틱값을 정의해주기

                    price_open = self.q.get()
                    if hold_flag == False:
                        price_buy  = curr_ma5_tick



                    wait_flag  = False

                price_curr = pyupbit.get_current_price(self.ticker)
                if price_curr == None:
                    continue

                if hold_flag == False and wait_flag == False and \
                    price_curr >= curr_ma5 and curr_ma5 >= curr_ma25 and curr_ma25 >= curr_ma100 and \
                    price_curr <= curr_ma25 * 1.01 and price_curr <= curr_ma100 * 1.03:
                    # 0.05%

                    cash_order = int( cash * 0.2 )   #잔고에서 주문할 금액 설정
                    buy_vol = int(cash_order / price_curr)

                    #ret = upbit.buy_market_order(self.ticker, cash_order)  # 시장가 매수
                    ret = upbit.buy_limit_order(self.ticker, price_buy, buy_vol)  #지정가 매수

                    #### 중요 ###
                    price_buy_bal = price_buy    # price_buy_balance = 내가 매수한 평단가. 매수가격. 매수주문가가 5이평값으로 계속 바뀌기 때문임!!! 그래서 다시 정의필요

                    print("매수 주문 ret:", ret)
                    if ret == None or "error" in ret:
                        print("매수 주문 이상")
                        continue
                    #print("131번줄 실행 ")

                    while True:
                        #print( "133번줄 실행 ")
                        order = upbit.get_order(ret['uuid'])
                        print( '136줄 order 실행', order)
                        if order != None and len(order['trades']) > 0:
                            print("매수 주문 처리 완료", order)
                            break
                        else:
                            print("매수 주문 대기 중")
                            time.sleep(0.5)

                    while True:
                        volume = upbit.get_balance(self.ticker)
                        if volume != None:
                            break
                        time.sleep(0.5)


  ##    매도주문 바로 실행하는 코드 ## 오리지널코드
                    # while True:
                    #     price_sell = pyupbit.get_tick_size(price_sell)
                    #     ret = upbit.sell_limit_order(self.ticker, price_sell, volume)
                    #     if ret == None or 'error' in ret:
                    #         print("매도 주문 에러")
                    #         time.sleep(0.5)
                    #     else:
                    #         print("매도주문", ret)
                    #         hold_flag = True
                    #         break
                    #

    #### 매도주문 조건에 따라 수익 손실 주문하는 코드 ########


                    while True:

                        price_sell_plus = price_buy_bal * 1.02
                        price_sell_minus = price_buy_bal * 0.98

                        if price_curr > price_sell_plus:
                            price_sell = pyupbit.get_tick_size(price_sell_plus)
                            ret = upbit.sell_limit_order(self.ticker, price_sell, volume)


                        # price_sell = pyupbit.get_tick_size(price_sell)
                        # ret = upbit.sell_limit_order(self.ticker, price_sell, volume)
                            if ret == None or 'error' in ret:
                                print("매도 익절 주문 에러")
                                time.sleep(0.5)
                            else:
                                print("매도 익절 주문 완료", ret)
                                hold_flag = True
                                break

                        if price_curr < price_sell_minus:
                            price_sell = pyupbit.get_tick_size(price_sell_minus)
                            ret = upbit.sell_limit_order(self.ticker, price_sell, volume)

                            if ret == None or 'error' in ret:
                                print("매도 손절 주문 에러")
                                time.sleep(0.5)
                            else:
                                print("매도 손절 주문 완료", ret)
                                hold_flag = True
                                break

                #print("현재가, 5이평, 25이평, 100이평, 1440이평", price_curr, curr_ma5, curr_ma25, curr_ma100, curr_ma1440)

                if hold_flag == True:
                    uncomp = upbit.get_order(self.ticker)
                    if uncomp != None and len(uncomp) == 0:
                        cash = upbit.get_balance()
                        if cash == None:
                            continue

                        print("매도완료", cash)
                        hold_flag = False
                        wait_flag = True

                # 3 minutes 중간중간 현상황 프린팅해주기
                if i == (5 * 60 * 1):
                    print(f"[{datetime.datetime.now()}] 현재가 {price_curr}, 매수 목표가 {price_buy}, 이평값 ma5: {curr_ma5:.2f}, ma25: {curr_ma25:.2f}, ma100: {curr_ma100:.2f}, ma1440: {curr_ma1440:.2f}, hold_flag {hold_flag}, wait_flag {wait_flag}")
                    i = 0
                i += 1
            except:
                print("error")

            time.sleep(0.2)

class Producer(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q

    def run(self):
        while True:
            #price = pyupbit.get_current_price("KRW-XRP")
            price = pyupbit.get_current_price("KRW-DOGE")
            self.q.put(price)
            time.sleep(60)

q = queue.Queue()
Producer(q).start()
Consumer(q).start()
