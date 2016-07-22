# -*- coding: utf-8 -*-
import datetime
#import tarfile
import os
import serial
#import time
import spidev
import array
#import numpy
import binascii
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)#режим роботи з GPIO
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)#підтяжка 17 піна до 3.3 В
#GPIO.setup(27, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, True)
GPIO.setup(18, GPIO.IN)

port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=0.1)#ініціалізація параметрів для роботи з COM-портом

#ініціалізація параметрів для роботи по SPI
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=(23000000)
count1 = long(0)
count2 = long(0)

while True:
#  print GPIO.input(27)
  try:#перевірка на переривання
    GPIO.wait_for_edge(17, GPIO.FALLING)
    GPIO.setup(27, True)#налаштування піна для підтвердження (GPIO 27 0-->1)
    print "interrupt was detected!!!"

    #запит у мікроконтролера розміру фото        
    port.write("?")

    #відповідь мікроконтролера (XXXX байт)
    rcv = port.read(6)
    data =  rcv.strip()

    if len(data) > 0:

        data_int = int(data)
        print data_int
    
        resp = spi.readbytes(data_int)#зчитуємо фото
    
        result = binascii.hexlify(bytearray(resp))
        print resp  

        resp = array.array('B', resp).tostring()#перевести отриманий файл у бінарний формат
 
   #перевірка з яких дверей прийшло фото
        if GPIO.input(18) == 1:
            date = datetime.datetime.now().strftime("%d-%m-%y_%H:%M:%S:%f")
            os.makedirs('/home/pi/cams/')
            file = open('/home/pi/cams/'+'1'+date+'_'str(count1)+'.jpg','wb')
            file.write(resp)
            file.close()
            count1 += 1
            #tar = tarfile.open('/home/pi/dor1'+'_'+date+'.tar.gz', 'w:gz')
            print "...file 1 saved"
            print result
        else:
            date = datetime.datetime.now().strftime("%d-%m-%y_%H:%M:%S:%f")
            os.makedirs('/home/pi/cams/')
            file = open('/home/pi/cams/'+'2'date +'_' str(count2)+".jpg","wb")
            file.write(resp)
            file.close()
            count2 += 1
            print "...file 2 saved"
            print result	

    GPIO.setup(27, False)#підтвердження отримання даних (GPIO 27 1-->0)

  except KeyboardInterrupt: 
      spi.close()  
