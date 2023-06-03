import datetime
import tkinter as tk
import requests
import json

from PIL import ImageTk, Image
import os
# Get the file path of the current Python file
file_path = os.path.abspath(__file__)

# Remove the file name from the file path
directory_path = os.path.dirname(file_path)


def update_time():
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    time_label.config(text=current_time)
    root.after(1000, update_time)
def update_date():
    current_date = datetime.datetime.now().strftime(r"%d-%B-%Y")
    date_label_2.config(text=current_date)
    next_update = datetime.datetime.now() + datetime.timedelta(hours=12)
    root.after(int((next_update - datetime.datetime.now()).total_seconds() * 1000), update_date)
def get_prayer_times():
    url = f"http://www.islamicfinder.us/index.php/api/prayer_times"
    parms = {
        'country':'US'
        ,'zipcode': '78501'
        ,'method':2
        ,'juristic':1
    }
    response = requests.get(url, params=parms)
    data = response.json()

    return(data)
def process_data(json_data):
    # Convert dictionary to JSON string
    json_string = json.dumps(json_data)

    # Parse the JSON string
    data = json.loads(json_string)

    # Access specific values
    p_t_1 = data['results']['Fajr'].replace('%','').upper()
    p_t_2 = data['results']['Dhuhr'].replace('%','').upper()
    p_t_3 = data['results']['Asr'].replace('%','').upper()
    p_t_4 = data['results']['Maghrib'].replace('%','').upper()
    p_t_5 = data['results']['Isha'].replace('%','').upper()

    prayer_times = {
        'Fajr':p_t_1
        , 'Dhuhr':p_t_2
        , 'Asr':p_t_3
        , 'Maghrib':p_t_4
        , 'Isha':p_t_5
    }
    return(prayer_times)
def get_hijiri_date():
    url = f"http://www.islamicfinder.us/index.php/api/calendar"
    islamic_months = {
        1 : 'Muḥarram',
        2 : 'Ṣafar',
        3 : 'Rabī‘ al-awwal',
        4 : 'Rabī‘ ath-thānī',
        5 : 'Jumādá al-ūlá',
        6 : 'Jumādá al-ākhirah',
        7 : 'Rajab',
        8 : 'Sha‘bān',
        9 : 'Ramaḍān',
        10 : 'Shawwāl',
        11 : 'Dhū al-Qa‘dah',
        12 : 'Dhū al-Ḥijjah'
    }
    #Get Date 
    date = datetime.datetime.now()
    year = date.year
    month = date.month
    day = date.day
    parms = {
        'day':day
        ,'month': month
        ,'year': year
    }
    response = requests.get(url, params=parms)
    data = response.json()['to']
    data = data.split('-')
    data = [int(x) for x in data]
    Hijri_1 = f'{data[2]}-{data[1]}-{data[0]}'
    Hijri_2 = f'{data[2]} {islamic_months[data[1]]} {data[0]}'
    date_label_1.config(text=Hijri_2)
    next_update = datetime.datetime.now() + datetime.timedelta(hours=12)
    root.after(int((next_update - datetime.datetime.now()).total_seconds() * 1000), get_hijiri_date)


#Get Prayer Times Data
data = get_prayer_times()
prayer_times = process_data(data)
Iqama_times = {'Fajr': '6:00 AM', 'Dhuhr': '2:00 PM', 'Asr': '6:30 PM', 'Maghrib': prayer_times['Maghrib'], 'Isha': '9:45 PM'}

# Create the main window
root = tk.Tk()
root.title("Digital Clock")

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the width and height for the widget
widget_width = screen_width
widget_height = screen_height

# Set the geometry of the window
root.geometry(f"{widget_width}x{widget_height}")

# Load the image
pic_name = "pic_2a.png"
pic_path = f'{directory_path}\{pic_name}'
image = Image.open(pic_path)
resized_image = image.resize((screen_width , screen_height), Image.ANTIALIAS)


background_image = ImageTk.PhotoImage(resized_image)
# Resize the image to fit the screen
#resized_image = image.subsample(screen_width // image.width(), screen_height // image.height())

#image = tk.PhotoImage(file="pic_2a.png")

# Create a label with the image as the background
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)


# Set the background color to white
root.configure(background="black")



# Create the text widget with the messages

##Create Mosque Name Widget
mosque_label = tk.Label(root, text = 'Masjid Umar AL - Farooq', fg="dark green", font=("Arial", 80), highlightbackground='gold', bg='black', highlightthickness=1)
mosque_label.grid(row=0, column=0,rowspan=1, columnspan=6, sticky="nsew", pady=.1)

##Create Time-Clock Widget
time_label = tk.Label(root, fg="dark green", font=("Arial", 90), highlightbackground='gold', bg='black', highlightthickness=1)
time_label.grid(row=1, column=3,rowspan=2, columnspan=3, sticky="nsew", pady=.1)

##Create ISLAMIC DATE Widget
date_label_1 = tk.Label(root, fg="white", font=("Arial", 50), highlightbackground='gold', bg='black', highlightthickness=1)
date_label_1.grid(row=3, column=3,rowspan=1, columnspan=3, sticky="nsew", pady=0)
##Create Regular DATE Widget 
date_label_2 = tk.Label(root, fg="white", font=("Arial", 50), highlightbackground='gold', bg='black', highlightthickness=1)
date_label_2.grid(row=4, column=3,rowspan=1, columnspan=3, pady=.1, sticky="nsew")

##Create Prayer / Iqama Widget 
prayer_label_3_0 = tk.Label(root, text = 'Starts', fg="white", font=("Arial", 40), highlightbackground='gold', bg='black', highlightthickness=1)
prayer_label_3_0.grid(row=1, column=1, padx=0,columnspan=1,rowspan=1,pady=.1, sticky="nsew")

prayer_label_4_0 = tk.Label(root, text = 'Iqamah', fg="white", font=("Arial", 40), highlightbackground='gold', bg='black', highlightthickness=1)
prayer_label_4_0.grid(row=1, column=2, padx=0,columnspan=1,rowspan=1,pady=.1, sticky="nsew")

prayer_label_4_0 = tk.Label(root, text = 'Jummah', fg="white", font=("Arial", 40), highlightbackground='gold', bg='black', highlightthickness=1)
prayer_label_4_0.grid(row=5, column=3, padx=0,columnspan=1,rowspan=1,pady=.1, sticky="nsew")
prayer_label_5_0 = tk.Label(root, text = '1:45 PM', fg="white", font=("Arial", 40), highlightbackground='gold', bg='black', highlightthickness=1)
prayer_label_5_0.grid(row=5, column=4, padx=0,columnspan=2,rowspan=1,pady=.1, sticky="nsew")


val = 0 
for key,value in prayer_times.items():
    #Create Text Widget
    start_num = 0
    prayer_name = tk.Label(root, fg="white", font=("Arial", 40), text = f'{key}', highlightbackground='gold'
                        , bg='black', highlightthickness=1)
    prayer_name.grid(row=val+1, column=start_num
                      ,columnspan=1
                      , padx=1, pady=0
                      , sticky="nsew")
    prayer_label = tk.Label(root, text = value,font=("Arial", 30),fg="white"
                            , highlightbackground='gold', bg='black', highlightthickness=1
                            )
    prayer_label.grid(row=val+1, column=start_num+1
                      ,columnspan=1
                      , padx=1, pady=0
                      , sticky="nsew")
    iqama_label = tk.Label(root, text = Iqama_times[key],font=("Arial", 30),fg="white"
                            , highlightbackground='gold', bg='black', highlightthickness=1
                            )
    iqama_label.grid(row=val+1, column=start_num+2
                      ,columnspan=1
                      , padx=1, pady=0
                      , sticky="nsew")
    val +=1
# Configure grid weights to adjust column width
root.grid_columnconfigure(0, weight=1,minsize=2)
root.grid_columnconfigure(1, weight=2,minsize=2)
root.grid_columnconfigure(2, weight=2,minsize=2)
root.grid_columnconfigure(3, weight=2,minsize=2)
root.grid_columnconfigure(4, weight=2,minsize=2)
root.grid_columnconfigure(5, weight=2,minsize=2)
root.grid_columnconfigure(6, weight=1,minsize=1)
root.grid_rowconfigure(0, weight=1, minsize=1)
root.grid_rowconfigure(1, weight=1, minsize=1)
root.grid_rowconfigure(2, weight=1, minsize=1)
root.grid_rowconfigure(3, weight=1, minsize=1)
root.grid_rowconfigure(4, weight=1, minsize=1)
root.grid_rowconfigure(5, weight=1, minsize=1)


# Call the update_time function to start updating the clock
update_time()
update_date()
get_hijiri_date()

# Start the Tkinter event loop
root.mainloop()
