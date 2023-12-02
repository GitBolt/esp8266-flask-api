import urequests
import utime
from machine import Pin, PWM

api_url = "http://46.250.226.112:5000/api/medications"

led = Pin(2, Pin.OUT)
buzzer = PWM(Pin(4))

def fetch_data():
    try:
        response = urequests.get(api_url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Error:", e)
    return None

def blink_led():
    end_time = utime.time() + 10
    while utime.time() < end_time:
        led.value(1)
        utime.sleep(0.1)
        led.value(0)
        utime.sleep(0.1)

def play_funky_sound():
    for frequency in range(100, 2500, 200):
        buzzer.freq(frequency)
        buzzer.duty(512)
        utime.sleep(0.1)
    buzzer.duty(0)

def parse_time(iso_time_str):
    year, month, day, hour, minute = map(int, iso_time_str.replace('T', '-').replace(':', '-').split('-'))
    return utime.mktime((year, month, day, hour, minute, 0, 0, 0))

def main():
    while True:
        data = fetch_data()
        if data and len(data) > 0:
            medication = data[0]
            current_time = utime.time()
            for med_time_str in medication["times"]:
                med_time = parse_time(med_time_str)
                if abs(current_time - med_time) <= 20:
                    blink_led()
                    play_funky_sound()
        utime.sleep(10)

if __name__ == "__main__":
    main()
