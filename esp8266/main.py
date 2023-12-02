import urequests
import utime
from machine import Pin, PWM
import os
from ntptime import settime

api_url = "http://46.250.226.112:5000/api/medications"
led = Pin(2, Pin.OUT)
buzzer = PWM(Pin(4))
touch = Pin(5)

def boot_signal():
    start_freq = 400
    end_freq = 1000
    freq_step = 5
    for freq in range(start_freq, end_freq, freq_step):
        buzzer.freq(freq)
        buzzer.duty(512)
        utime.sleep(0.02)
        buzzer.duty(0)
    led.value(1)
    utime.sleep(1)
    led.value(0)
        
boot_signal()
print(os.listdir())

def ist():
    (year, month, mday, hour, minute, second, weekday, yearday) = utime.localtime()
    hour += 5
    minute += 30
    if minute >= 60:
        minute -= 60
        hour += 1
    if hour >= 24:
        hour -= 24
        mday += 1
    return utime.localtime(utime.mktime((year, month, mday, hour, minute, second, weekday, yearday)))

def ist_timestamp():
    utc_timestamp = utime.time()
    ist_offset = 5 * 3600 + 30 * 60
    ist_timestamp = utc_timestamp + ist_offset
    return ist_timestamp


def fetch_data():
    print("Fetching data from API...")
    try:
        response = urequests.get(api_url)
        print("Response received. Status code:", response.status_code)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data. Status code:", response.status_code)
    except Exception as e:
        print("Error during fetching data:", e)
    return None

def blink_led_and_play_sound():
    print("Blinking LED and playing sound...")
    log_event("Blinking LED and playing sound")
    end_time = utime.time() + 10
    while utime.time() < end_time:
        led.value(1)
        buzzer.freq(1000)
        buzzer.duty(512)
        utime.sleep(0.1)
        led.value(0)
        buzzer.duty(0)
        utime.sleep(0.1)

def update_counter(medication):
    print("Updating counter for medication:", medication['name'])
    medication["counter"] += 1
    response = urequests.put(api_url, json=medication)
    print("Response Status code:", response.status_code)
    if response.status_code == 200:
        updated_medication = response.json()
        print("Res: ", updated_medication)
        return updated_medication
    else:
        print("Failed to update medication. Status code:", response.status_code)
    return None

def parse_time(iso_time_str):
    year, month, day, hour, minute = map(int, iso_time_str.replace('T', '-').replace(':', '-').split('-')[:5])
    return utime.mktime((year, month, day, hour, minute, 0, 0, 0))

def log_event(event):
    with open("medication_log.txt", "a") as log_file:
        timestamp = ist()#utime.localtime() 
        log_file.write("{}/{}/{} {}:{}:{} - {}\n".format(timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5], event))
    log_file.close()
    
def main():
    print("Starting main loop...")
    while True:
        buzzer.freq(2000)
        buzzer.duty(200)
        utime.sleep(0.03)
        buzzer.duty(0)
        data = fetch_data()
        
        if data == None or len(data) == 0:
            utime.sleep(1)
            continue
    
        val = touch.value()
        print("Touch Reading: ", val)

        if val == 1:
            update_counter(data[0])
            log_event("Medication counter updated for " + data[0]['name'])
        log_event(f"Next Iteration...Medication Times: {data[0]["times"]}")
        
        if data and len(data) > 0:
            for medication in data:
                current_time = ist_timestamp() #utime.time()
                print("Current time:", current_time)
                for med_time_str in medication["times"]:
                    med_time = parse_time(med_time_str)
                    print("Medication/Current time:", med_time, current_time)
                    if 0 <= (current_time - med_time) <= 10:
                        print("Time match found. Executing actions...")
                        blink_led_and_play_sound()
        else:
            print("No data found or empty response.")
        print("Waiting for next iteration...\n")
        utime.sleep(1)

if __name__ == "__main__":
    main()



