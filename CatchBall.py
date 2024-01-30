import sensor, image, time,math,sys,gc,pyb
import json
from pyb import UART

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ball_threshold = (58,69,25,65,10,49) #球的顏色值( L最小, L最大, A最小, A最大, B最小, B最大)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

blue_goal_threshold = (33, 43, 8, 39, -79, -34) #藍色球門的顏色值
yellow_goal_threshold = (70, 76, 2, 35, 4, 61) #黃色球門的顏色值

otb_threshold = (163,187) #界線顏色值

#設置球的閾值，括號裡面的數值分別是L A B 的最大值和最小值（minL, maxL, minA,
# maxA, minB, maxB），LAB的值在圖像左側三個坐標圖中選取。如果是灰度圖，則只需
#設置（min, max）兩個數字即可。

BINARY_VISIBLE = True

sensor.reset() # 初始化攝像頭
sensor.set_pixformat(sensor.RGB565) # 格式為 RGB565.
sensor.set_framesize(sensor.QVGA) # QVGA = 畫質
sensor.skip_frames(time = 2000) # 跳過2000s，使新設置生效,並自動調節白平衡
sensor.set_auto_gain(False) # 關閉自動自動增益

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sensor.set_auto_whitebal(False, rgb_gain_db =(-4.760428, -6.02073, -2.319861)) # 固定白平衡
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

clock = time.clock() # 追踪幀率
uart = UART(3, 9600)

gx,gy,ga,gr = 0,0,0,0
bx,by,ba,br = 0,0,0,0
yx,yy,ya,yr = 0,0,0,0

while(True):

    try:

        clock.tick() # Track elapsed milliseconds between snapshots().
        img = sensor.snapshot()# 從鏡頭畫面獲得圖像
        gc.collect()

        blobs = img.find_blobs([ball_threshold])
        blue_blobs = img.find_blobs([blue_goal_threshold])
        yellow_blobs = img.find_blobs([yellow_goal_threshold])

        otb_blobs = img.find_blobs([otb_threshold])
        #find_blobs(thresholds, invert=False, roi=Auto),thresholds為顏色閾值，
        #是一個元組，需要用括號［ ］括起來。 invert=1,反轉顏色閾值，invert=False默認
        #不反轉。 roi設置顏色識別的視野區域，roi是一個元組， roi = (x, y, w, h)，代表
        #從左上頂點(x,y)開始的寬為w高為h的矩形區域，roi不設置的話默認為整個圖像視野。
        #這個函數返回一個列表，[0]代表識別到的目標顏色區域左上頂點的x坐標，［1］代表
        #左上頂點y坐標，［2］代表目標區域的寬，［3］代表目標區域的高，［4］代表目標
        #區域像素點的個數，［5］代表目標區域的中心點x坐標，［6］代表目標區域中心點y坐標，
        #［7］代表目標顏色區域的旋轉角度（是弧度值，浮點型，列表其他元素是整型），
        #［8］代表與此目標區域交叉的目標個數，［9］代表顏色的編號（它可以用來分辨這個
        #區域是用哪個顏色閾值threshold識別出來的）。

        if blobs:
        #如果找到了球的顏色
        #取最大色塊
            max_size=0
            for blob in blobs:
                if blob.pixels() > max_size:
                    max_blob=blob
                    max_size = blob.pixels()

            img.draw_rectangle(max_blob.rect())
            img.draw_cross(max_blob.cx(), max_blob.cy())

            gx = (max_blob.cx()) - 160
            if(gx == 0):
                gx = 0.0000001

            gy = ((max_blob.cy()) - 120)*-1

            gr = int(math.sqrt( math.pow(gx,2) + math.pow(gy,2) ))
            ga =int((math.atan2(gy,gx) * 180 / math.pi + 360)%360)

            print("球的座標   " + str(gx) + " , " + str( gy) + "\n"  )
            print("球的極座標  " + str(gr) + " , " + str(ga) + "\n")
            print(str(math.exp((float(gy) - 73.755)/16.78)*10))
            uart.write(str(gr) + " , " + str(ga) + "\n\n")

#---------------------------------------------------------------------------------------------

        if blue_blobs:
        #如果找到了藍色球門的顏色
            max_size=0
            for blob in blue_blobs:
                if blob.pixels() > max_size:
                    max_blob=blob
                    max_size = blob.pixels()

            img.draw_rectangle(max_blob.rect())
            img.draw_cross(max_blob.cx(), max_blob.cy())

            bx = (max_blob.cx()) - 160
            if(bx == 0):
                bx = 0.0000001

            by = ((max_blob.cy()) - 120)*-1

            br = int(math.sqrt( math.pow(bx,2) + math.pow(by,2) ))
            ba =int((math.atan2(by,bx) * 180 / math.pi + 360)%360)

            #print("藍色球門的座標   " + str(bx) + " , " + str( by) + "\n"  )
            #print("藍色球門的極座標  " + str(br) + " , " + str(ba) + "\n")
            uart.write(str(br) + " , " + str(ba) + "\n\n")

#---------------------------------------------------------------------------------------------

        if yellow_blobs:
        #如果找到了黃色球門的顏色
            max_size=0
            for blob in yellow_blobs:
                if blob.pixels() > max_size:
                    max_blob=blob
                    max_size = blob.pixels()

            img.draw_rectangle(max_blob.rect())
            img.draw_cross(max_blob.cx(), max_blob.cy())

            yx = (max_blob.cx()) - 160
            if(yx == 0):
                yx = 0.0000001

            yy = ((max_blob.cy()) - 120)*-1

            yr = int(math.sqrt( math.pow(yx,2) + math.pow(yy,2) ))
            ya =int((math.atan2(yy,yx) * 180 / math.pi + 360)%360)

           # print("黃色球門的座標   " + str(yx) + " , " + str( yy) + "\n"  )
            #print("黃色球門的極座標  " + str(yr) + " , " + str(ya) + "\n")
            uart.write(str(yr) + " , " + str(ya) + "\n\n")

#---------------------------------------------------------------------------------------------

    except:
        gc.collect()

    #函數返回回歸後的線段對象line，有x1(), y1(), x2(), y2(), length(), theta(), rho(), magnitude()參數。
    #x1 y1 x2 y2分別代表線段的兩個頂點坐標，length是線段長度，theta是線段的角度。
    #magnitude表示線性回歸的效果，它是（0，+∞）範圍內的一個數字，其中0代表一個圓。如果場景線性回歸的越好，這個值越大。

   # line = img.get_regression([(255,255) if BINARY_VISIBLE else otb_threshold])
   # if (line):
        #if (line): img.draw_line(line.line(), color = [120, 255, 255])


    #print(clock.fps()) # 注意: 你的OpenMV連到電腦後幀率大概為原來的一半
    #如果斷開電腦，幀率會增加
