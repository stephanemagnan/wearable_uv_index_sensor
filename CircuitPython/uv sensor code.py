from time import sleep
from analogio import AnalogIn
from digitalio import DigitalInOut
import board
import adafruit_74hc595

# board.A0 board.D1 (PA02)
# board.A1 board.D2 board.MISO board.SCL (PA09)
# board.A2 board.D0 board.SDA (PA08)
# board.A3 board.D3 board.RX board.SCK (PA07)
# board.A4 board.D4 board.MOSI board.TX (PA06)
# board.APA102_MOSI board.DOTSTAR_DATA (PA00)
# board.APA102_SCK board.DOTSTAR_CLOCK (PA01)
# board.D13 board.LED (PA10)

uv_sensor_pin = AnalogIn(board.A0)
osr_latch_pin = DigitalInOut(board.D0)
SHIFT_REGISTERS_NUM = 1
osr = adafruit_74hc595.ShiftRegister74HC595(
    board.SPI(), osr_latch_pin, SHIFT_REGISTERS_NUM
)
start_led = 1
led_count = 7
blink_time = 0.25


def get_uv_reading(read_pin):
    uv_reading = (read_pin.value * 3.3) / 65536
    print(f" Read {uv_reading}V")
    return uv_reading


def compute_uv_index(uv_reading):
    uv_index = uv_reading / 0.1
    print(f" UV Index is {round(uv_index)}")
    return round(uv_index)


def shutoff_leds(shift_reg):
    print(f"Turn off all LEDs")
    for led_id in range(8):
        this_led = shift_reg.get_pin(led_id)
        # print(f'Turn off led {led_id}')
        this_led.value = False  # turn off LED


def show_uv_index(uv_index, shift_reg):
    uv_index = min(uv_index, 11)
    # if the index is even, then blink the LED, if it is odd, then hold in positive.
    # repeat a total of 5 times before stopledg execution
    led_id = uv_index // 2 + 1
    blink_led = uv_index % 2

    if blink_led == 0:
        print(f" HOLD LED {led_id}")
        for toggle_led_id in range(start_led, start_led + led_count):
            toggle_led = shift_reg.get_pin(toggle_led_id) 
            if toggle_led_id == led_id:
                toggle_led.value = True
            else:
                toggle_led.value = False
            
        sleep(blink_time)
        
    else:
        print(f" HOLD LEDs {led_id} and {led_id+1}")
        for toggle_led_id in range(start_led, start_led + led_count):
            toggle_led = shift_reg.get_pin(toggle_led_id) 
            if (toggle_led_id == led_id) or (toggle_led_id == led_id + 1):
                toggle_led.value = True
            else:
                toggle_led.value = False
            
        sleep(blink_time)

def cycle_leds(shift_reg):
    for led_id in range(start_led, start_led + led_count):
        this_led = shift_reg.get_pin(led_id)
        print(f"Blink LED {led_id}")
        this_led.value = True  # turn on LED
        sleep(blink_time)
        this_led.value = False  # turn off LED
        sleep(blink_time/2)
    sleep(1)


# Main
shutoff_leds(osr)
cycle_leds(osr)
while True:
    print('Loop')
    this_reading = get_uv_reading(uv_sensor_pin)
    this_index = compute_uv_index(this_reading)
    show_uv_index(this_index, osr)


