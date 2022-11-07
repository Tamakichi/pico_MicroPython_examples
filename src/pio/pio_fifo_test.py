"""
 Rasbery Pi pico PIO制御の練習(1)
 利用ボード： Seeed XIAO RP2040
 回路構成： GPIOにLED接続（アクティブLOW） ※通常版picoの場合ボード上LED(25)に置き換える
 
 TX FIFOからのデータを取り出し、取り出したデータが1の場合、GPIO16をLOWにしてLEDを点灯させる
 取り出したデータが0の場合、GPIO16をHIGHにしてLEDを消灯させる
 
 1)PIOは、送信FIFOからデータを取り出し待ちを行う
 2)メインCPUから送信FIFOから1バイトを書き込む(最下位1ビットのみ有効）
 3)PIOは、送信FIFOからデータを取り出す
 4)取り出したデータが1ならGPIO16ピンにLOWを出力して、LEDを点灯させる
 5)取り出したデータが0ならGPIO16ピンにHIGHを出力する
 
"""
import time
import rp2
from machine import Pin

@rp2.asm_pio(set_init=rp2.PIO.OUT_HIGH) # set指定の初期値としてGPIOにHIGHをセットする
def fifo_test():
    wrap_target()
    label("top")
    pull(block)             # OSR ←TX FIFO(TX FIFOからのデータ取り出し)
    mov(x,osr)              # X ← OSR 
    set(y,1)                # Y ← 1
    jmp(x_not_y,"led_off")  # X != Y なら "led_off" にジャンプ
    set(pins,0)             # pinsに0を出力
    label("led_off")        # "led_off":
    set(y,0)                # Y ← 0
    jmp(x_not_y,"top")      # X != Y なら "top" にジャンプ
    set(pins,1)             # pinsに1を出力
    wrap()                  # 先頭行にジャンプ


#PIO0を利用、pinsにGPIO16(LED_G)を指定
sm = rp2.StateMachine(0, fifo_test, freq=2000, set_base=Pin(16))
sm.active(1)                # PIOを稼働
for t in range(5):
    sm.put(1)               # TX FIFOに1を書き込む
    time.sleep_ms(500)
    sm.put(0)
    time.sleep_ms(500)      # TX FIFOに0を書き込む
sm.active(0)                # PIOを停止

