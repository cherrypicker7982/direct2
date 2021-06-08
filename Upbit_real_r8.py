##https://www.youtube.com/watch?v=g0TVDyyVSGs 파이스탁 자동매매


# r2: 기본 코드에서 값 변경하기. 5분봉.  5 25 100 1440(5일선) 정배열일때 매수하는걸로.
# r3: 수익이랑 손절조건 추가해주기
# 4: price_buy 가격이 계속 바뀌어서 매도가 안나감.. 매도 익절 손절가가 계속바껴서. 수정함
# r5: git 업로드용임.    ip주소 211.196.254.138  (신림) ,15.164.229.188,172.31.38.8 (aws), 210.100.171.123 (이디야), 116.126.242.160(기숙사)
# ip주소 211.196.254.138,15.164.229.188,172.31.38.8,210.100.171.123,116.126.242.160

# r6: aws 업로드용 조건 단순화
# r7: 매도조건 오류에 대한 로직 수정중..
# r8: 주문 나가면 체결될때까지 기다리게되는데 취소하는 로직 추가 필요.



import threading
import queue
import time
import pyupbit
import datetime
from collections import deque


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
        hold_flag = False    # hold_flag = true 가 매수한 상태, flase가 매수안하고 비어잇는 상태
        wait_flag = False    # wait_flag = ? 하나의 1분봉에서 1번의 매수매도만하도록 제한하는것임.


    ########## upbit 텍스트파일 에서 key 읽어오는 코드 ##############

        # with open("upbit.txt", "r") as f:
        #     key0 = f.readline().strip()
        #     key1 = f.readline().strip()

    ###################################################################

        key0 = "nZcAVsx9IPqDCSOxoBzSXF7Sxz6HHw7Oxch942h0"
        key1 = "2jyUKlHOocISRaxAsW5vuWdR1RoHz4GAb6qVRG7Q"

        upbit = pyupbit.Upbit(key0, key1)
        print('upbit 접속 성공')

        cash = upbit.get_balance()
        print("보유현금", cash)


        i = 0

        while True:
            try:   # 데이터가 없을때 오류가 있을것이므로 try except 구문 넣어줌
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

                    wait_flag  = False   # 하나의 봉 완성되고 나서 다음번 데이터가 들어왔으니 이제 flase로 해주는것임.  하나의 봉 안에서 여러번의 매수매도 방지 기능

                price_curr = pyupbit.get_current_price(self.ticker)


                ## 에러 처리 코드 시작. 현재가 없을 경우##
                if price_curr == None:
                    continue
                ## 에러 처리 코드 끝. 현재가 없을 경우##








            ###############================= 매수 조건 확인 및 주문 시작 ================###################
                    #### hold_flag = flase 일때가 비어있는 상태임!!!  매수안한상태

                if hold_flag == False and wait_flag == False and \
                    price_curr >= curr_ma5 :
                    # 0.05%
                    #
                    # price_curr >= curr_ma5 and curr_ma5 >= curr_ma25 and curr_ma25 >= curr_ma100 and \
                    # price_curr <= curr_ma25 * 1.01 and price_curr <= curr_ma100 * 1.03:


                    cash_order = int( cash * 0.2 )   #잔고에서 주문할 금액 설정
                    buy_vol = int(cash_order / price_curr)

                    #ret = upbit.buy_market_order(self.ticker, cash_order)  # 시장가 매수
                    ret = upbit.buy_limit_order(self.ticker, price_buy, buy_vol)  #지정가 매수


                    print("매수 주문 ret:", ret)


                    ### 에러처리코드 시작. 주문이 이상할 경우 다시 처음으로 돌아감 ###
                    if ret == None or "error" in ret:
                        print("매수 주문 이상")
                        continue
                    ### 에러처리코드 끝. 주문이 이상할 경우 ###





                    #### 에러처리 시작. 주문한 매수 주문이 제대로 웹서버에서 처리 됐는지 확인. 에러일 경우 반복해서 주문 조회함 ####
                    while True:
                        #print( "133번줄 실행 ")
                        order = upbit.get_order(ret['uuid'])
                        print( '136줄 order 실행', order)
                        if order != None and len(order['trades']) > 0:
                            print("매수 주문 처리 완료", order)
                            break                                               #주문 처리가 제대로 됐으면 while 탈출함
                        else:
                            print("매수 주문 대기 중")
                            time.sleep(0.5)

                    while True:
                        volume = upbit.get_balance(self.ticker)
                        if volume != None:
                            break
                        time.sleep(0.5)

                    ### 매수 완료 되었으면 더이상 매수 안함.  hold flag= true 이면 매수 멈춤.
                    #### 중요 ###
                    price_buy_bal = price_buy    # price_buy_balance = 내가 매수한 평단가. 매수가격. 매수주문가가 5이평값으로 계속 바뀌기 때문임!!! 그래서 다시 정의필요
                    hold_flag = True

                    print('162줄 price_buy 값 출력: ', price_buy)
                    ### 매수 안하는 코드 완료


                    #### 에러처리 끝끝. 주문한 매수 주문이 제대로 웹서버에서 처리 됐는지 확인 ###
################ ================================ 매수 주문 및 체결 완료 ==============================#############################################

#
#
#
#
#
#
#
#
#
#
#
                ###############================= 매도 익절 조건 확인 및 주문 시작 ================###################
                #### hold_flag = flase 일때가 비어있는 상태임!!!  매도안한상태

                per_plus = 1.005
                per_minus = 0.995

                if hold_flag == True and wait_flag == False and \
                    price_curr >= (price_buy_bal * per_plus):
                    print("186줄 진입. 익절 주문 조건 만족중")
                    # 0.05%

                    price_sell = pyupbit.get_tick_size(price_buy_bal * per_plus)   # 현재가로 팔건데 틱사이즈에 맞게 수정


                    # ret = upbit.buy_market_order(self.ticker, cash_order)  # 시장가 매수
                    ret = upbit.sell_limit_order(self.ticker, price_sell, volume)  # 지정가 매도

                    print("매도 익절 주문 ret:", ret)

                    ### 에러처리코드 시작. 주문이 이상할 경우 다시 처음으로 돌아감 ###
                    if ret == None or "error" in ret:
                        print("매도 익절 주문 이상")
                        continue
                    ### 에러처리코드 끝. 주문이 이상할 경우 ###


                    #### 에러처리 시작. 주문한 매도 주문이 제대로 웹서버에서 처리 됐는지 확인. 에러일 경우 반복해서 주문 조회함 ####
                    while True:
                        # print( "133번줄 실행 ")
                        order = upbit.get_order(ret['uuid'])
                        print('210줄 order 실행', order)
                        if order != None and len(order['trades']) > 0:
                            print("매도 익절 주문 처리 완료", order)
                            break  # 주문 처리가 제대로 됐으면 while 탈출함
                        else:
                            print("매도 익절 주문 대기 중")
                            time.sleep(0.5)

                    while True:
                        volume = upbit.get_balance(self.ticker)

                        print("217줄 while문 도는중")
                        if volume < 1:   ### 매수랑 다름. 여기는 볼륨이 이 1보다 작을때는 없다고 봄.
                            break
                        time.sleep(0.5)

                    ### 매도 완료 되었으면 다시 매수할수있게설정.  hold flag= false 이면 매수함.
                    hold_flag = False

                    #### 에러처리 끝끝. 주문한 매수 주문이 제대로 웹서버에서 처리 됐는지 확인 ###
            ################ ================================ 매도 익절 주문 및 체결 완료 ==============================#############################################

#
#
#
#
#
#
#
#
#
#
#
                ###############================= 매도 손절 조건 확인 및 주문 시작 ================###################
                #### hold_flag = flase 일때가 비어있는 상태임!!!  매도안한상태

                if hold_flag == True and wait_flag == False and \
                    price_curr < (price_buy_bal * per_minus):
                    print("245줄 진입. 손절 주문 조건 만족중")
                    print("현재가, 손절기준가 출력", price_curr, price_buy_bal * per_minus)
                    # 0.05%

                    price_sell = pyupbit.get_tick_size( price_buy_bal * per_minus )  # 현재가로 팔건데 틱사이즈에 맞게 수정

                    # ret = upbit.buy_market_order(self.ticker, cash_order)  # 시장가 매수
                    ret = upbit.sell_limit_order(self.ticker, price_sell, volume)  # 지정가 매도

                    print("매도 손절 주문 ret:", ret)

                    ### 에러처리코드 시작. 주문이 이상할 경우 다시 처음으로 돌아감 ###
                    if ret == None or "error" in ret:
                        print("매도 손절 주문 이상")
                        continue
                    ### 에러처리코드 끝. 주문이 이상할 경우 ###

                    #### 에러처리 시작. 주문한 매도 주문이 제대로 웹서버에서 처리 됐는지 확인. 에러일 경우 반복해서 주문 조회함 ####
                    while True:
                        # print( "133번줄 실행 ")
                        order = upbit.get_order(ret['uuid'])
                        print('260줄 order 실행', order)
                        if order != None and len(order['trades']) > 0:
                            print("매도 손절 주문 처리 완료", order)
                            break  # 주문 처리가 제대로 됐으면 while 탈출함
                        else:
                            print("매도 손절 주문 대기 중")
                            time.sleep(0.5)

                    while True:
                        volume = upbit.get_balance(self.ticker)
                        print("거래량 출력 273줄", volume)
                        if volume < 1:  ### 매수랑 다름. 여기는 볼륨이 즉 잔고가 1보닺 작으면 없다고봄.
                            break
                        time.sleep(0.5)
                        print("276줄 while문 도는중")

                    ### 매도 완료 되었으면 다시 매수할수있게설정.  hold flag= false 이면 매수함.
                    hold_flag = False

                    #### 에러처리 끝끝. 주문한 매수 주문이 제대로 웹서버에서 처리 됐는지 확인 ###
            ################ ================================ 매도 주문 및 체결 완료 ==============================#############################################














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
                #
                #
                #     while True:
                #
                #         price_sell_plus = price_buy_bal * 1.02
                #         price_sell_minus = price_buy_bal * 0.98
                #
                #         if price_curr > price_sell_plus:
                #             price_sell = pyupbit.get_tick_size(price_sell_plus)
                #             ret = upbit.sell_limit_order(self.ticker, price_sell, volume)
                #
                #
                #         # price_sell = pyupbit.get_tick_size(price_sell)
                #         # ret = upbit.sell_limit_order(self.ticker, price_sell, volume)
                #             if ret == None or 'error' in ret:
                #                 print("매도 익절 주문 에러")
                #                 time.sleep(0.5)
                #             else:
                #                 print("매도 익절 주문 완료", ret)
                #                 hold_flag = True   # 매도 주문만 내고 체결되기 전까지는 flase 여야함.
                #                 break
                #
                #         if price_curr < price_sell_minus:
                #             price_sell = pyupbit.get_tick_size(price_sell_minus)
                #             ret = upbit.sell_limit_order(self.ticker, price_sell, volume)
                #
                #             if ret == None or 'error' in ret:
                #                 print("매도 손절 주문 에러")
                #                 time.sleep(0.5)
                #             else:
                #                 print("매도 손절 주문 완료", ret)
                #                 hold_flag = True
                #                 break
                #
                # #print("현재가, 5이평, 25이평, 100이평, 1440이평", price_curr, curr_ma5, curr_ma25, curr_ma100, curr_ma1440)
                #
                #
                #
                # #### 매도 주문 완료 되었는지 확인 코드 시작 #######
                # if hold_flag == True:
                #     uncomp = upbit.get_order(self.ticker)
                #     if uncomp != None and len(uncomp) == 0:
                #         cash = upbit.get_balance()    # 현금 잔고 확인 코드
                #         if cash == None:
                #             continue
                #
                #         print("매도완료", cash)
                #         hold_flag = False
                #         wait_flag = True
                # #### 매도 주문 완료 되었는지 확인 코드 끝#######





                # 일정기간마다 minutes 중간중간 현상황 프린팅해주기
                if i == (5 * 60 * 1):
                    print(f"[{datetime.datetime.now()}] 현재가 {price_curr}, 매수 목표가 {price_buy}, 이평값 ma5: {curr_ma5:.2f}, ma25: {curr_ma25:.2f}, ma100: {curr_ma100:.2f}, ma1440: {curr_ma1440:.2f}, hold_flag {hold_flag}, wait_flag {wait_flag}")
                    i = 0


                    #### ======== 주문 길어지면 취소하는 로직 시작 ##########################
                    try:
                        if ret['uuid'] != None:
                            cancel_order = upbit.cancel_order(ret['uuid'])  # 주문 대기가 너무 길어지면 취소하기.
                            print("383줄 주문 취소 완료: ", cancel_order)
                    except:
                        pass


                    ####3 ======= 주문 길어지면 취소하는 로직 끝 ######################

                i += 1
            except:
                print("379줄 데이터 없음 error")

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




############ ====  참고 조코딩 우분투 aws 명령어 모음 ###############################

#https://github.com/youtube-jocoding/pyupbit-autotrade
# Ubuntu 서버 명령어
# (*추가)한국 기준으로 서버 시간 설정: sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
# 현재 경로 상세 출력: ls -al
# 경로 이동: cd 경로
# vim 에디터로 파일 열기: vim bitcoinAutoTrade.py
# vim 에디터 입력: i
# vim 에디터 저장: :wq!
# 패키지 목록 업데이트: sudo apt update
# pip3 설치: sudo apt install python3-pip
# pip3로 pyupbit 설치: pip3 install pyupbit
# 백그라운드 실행: nohup python3 bitcoinAutoTrade.py > output.log &
# 실행되고 있는지 확인: ps ax | grep .py
# 프로세스 종료(PID는 ps ax | grep .py를 했을때 확인 가능): kill -9 PID