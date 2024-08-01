import re
import subprocess
from tkinter import *

# TO-DO LIST 
#####################################################################################
# What about up-times now? Try one with a mixed bunch of alerts; ups & downs
# Add secondary/tertiary contacts and their phone numbers 
# Evaluate PRTG alert formatter before starting Meraki alert formatter
#####################################################################################


with open("input.txt", "w"):
    pass

subprocess.run(["notepad.exe", "input.txt"])

file_text = ""
with open("input.txt", "r") as file:
    for line in file:
        file_text += line
    
    # Look-ahead insertions are used (?<=) but do not appear as part of the resulting match
    customer = list(set(re.findall(r"(?<=Customer: )(.+)", file_text)))
    if len(customer) > 1:
        print("Error: More than 1 customer was included in the input")
    else:
        customer = customer[0]
        
    contact_person = re.search(r"(?<=Primary Contact - )(.+)", file_text) # what about secondary and tertiary?
    contact_number = re.search(r"(?<=  )(.+ )(?=\.+ Secondary Number:)", file_text) # same as above
    
    location_list = re.findall(r"(?<=Group: )(.+)", file_text)
    location_list = sorted(list(set(map(lambda x: x.strip(), location_list))))
    
    device_list = re.findall(r"(?<=\=\=\=\=\=\= Device \=\=\=\=\=\=\n\n)(.+\))(?= \()", file_text)
    device_list = sorted(list(set(device_list)))
    
    
    # Checking for up alerts 
    all_alerts = re.findall(
        r"(?<= Device \=\=\=\=\=\=\n\n).+[\n]*.+[\n]*.*[\n]*.*[\n]*.*[\n]*.*[\n]*(?=\=\=\= Additional Customer Details \=\=\=)", 
        file_text, 
        re.MULTILINE
    )

    all_alerts_formatted = []
    down_alert_times_and_device_info = []
    up_times_and_device_info_list = []
    # alert_received_time_and_device_info_list = []

    for notification in all_alerts:
        separate_lines = list(filter(lambda x: len(x) > 1, notification.split("\n")))
        device_and_ip = re.match(r"(.*)(?= \()", separate_lines[0]).group()
        notification_type = separate_lines[1]
        notification_time = separate_lines[-1].split(": ")[1].split(" (")[0]
        full_notification = (notification_time, notification_type, device_and_ip)
        all_alerts_formatted.append(full_notification)
        
        if notification_type == "Device Status: Down":
            down_alert_times_and_device_info.append(full_notification)
        elif "Device Status: Down ended (now: Up)" in notification_type:
            up_times_and_device_info_list.append(full_notification)
        else:
            print("Unrecognized alert type")
            exit()
            
    print("Down alerts:")
    print(down_alert_times_and_device_info)
    # print("\n\n\n")
    print("Up times:")
    print(up_times_and_device_info_list)
    
    print("All alerts:")
    print(all_alerts_formatted)
    
    device_down_actual_times = []
    scan_information_list = re.findall(r"Last Scan\:.*\n\n.*\]", file_text)
    scan_information = scan_information_list[0].split("\n\n") # have to iterate this, just doing one for now
    last_scan = scan_information[0].split(": ")[1]
    last_up = scan_information[1].split(": ")[1]
    if last_scan != last_up:
        device_down_actual_times.append(last_up)
   
    print(device_down_actual_times)
    exit()
    
    
    # alert_received_time_list = re.findall(r"(?<=^Device: ).+[\n]+.+(?= \()", file_text, re.MULTILINE)
    # alert_received_time_and_device_info_list = []
    # for alert in alert_received_time_list:
    #     print(alert)
    #     separate_values = alert.split("\n")
    #     device_and_ip = separate_values[0]
    #     alert_received_time = separate_values[1].split(": ")[1]
    #     alert_received_time_and_device_info_list.append((alert_received_time, device_and_ip))
    # alert_received_time_and_device_info_list = sorted(alert_received_time_and_device_info_list, key=lambda x: x[0])
    
    # print(alert_received_time_and_device_info_list)
    # exit()

    # device_down_time_list = re.findall(r"([A-Za-z0-9\-]+ \([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\).+)(?=\[)", file_text)
    # down_times_and_device_info_list = []
    # for device_down_time in device_down_time_list:
    #     separate_words = device_down_time.split(" ")
    #     device_and_ip = separate_words[0] + " " + separate_words[1]
    #     down_time = separate_words[7] + " " + separate_words[8] + " " + separate_words[9]
    #     down_times_and_device_info_list.append((down_time, device_and_ip))
    # down_times_and_device_info_list = sorted(down_times_and_device_info_list, key=lambda x: x[0])
    
    

with open("output.txt", "w") as file:
    file.write("Support has received the following alerts.\n\nEdnetics Case: [[CAS]]\n\n")
    file.write("Customer: " + customer)
    file.write("\nPoC: " + contact_person.group()) # currently only takes the primary
    file.write("\nContact Number: " + contact_number.group()) 
    
    file.write("\n\nLocation(s):")
    if len(location_list) > 1:
        for location in location_list:
            file.write("\n\t" + location)
    else: 
        file.write(" " + location_list[0])
            
    file.write("\nDevice Name (IP/MAC):")
    if len(device_list) > 1:
        for device in device_list:
            file.write("\n\t" + device)
    else:
        file.write(" " + device_list[0])
        
    file.write("\n\nAlert Date/Time:")
    if len(down_alert_times_and_device_info) > 1:
        for alert in down_alert_times_and_device_info:
            file.write("\n\t" + alert[0] + " - " + alert[1])
    else:
        file.write(" " + down_alert_times_and_device_info[0][0])
    
    file.write("\nUp Date/Time: TBD")
    file.write("\n\nNext Steps/RFO: Investigating")
    file.write("\n-----------------------------------------------------------------------------------------")
    file.write("\nTime Line (Pacific):")

    # combined_events = []
    # for alert_received_time in alert_received_time_and_device_info_list:
    #     combined_events.append(alert_received_time[0] + " - Alert received for " + alert_received_time[1])
    
    # for device_down_time in down_times_and_device_info_list:
    #     combined_events.append(device_down_time[0] + " - " + device_down_time[1] + " Down")
        
    # combined_events = sorted(combined_events, reverse=True)
    
    # for event in combined_events:
    #     file.write("\n\t" + event)

subprocess.run(["notepad.exe", "output.txt"])


# window = Tk()
# window.title("Alert Formatter")
# window.geometry('300x300')

# customer_label = Label(window, text="Customer:").grid(row=0, column=0, padx=10, pady=10)
# customer_entry = Entry(window).grid(row=0, column=1)

# window.mainloop()