import re
import subprocess
from tkinter import *

# TO-DO LIST 
#####################################################################################
# What about up-times now? Try one with a mixed bunch of alerts; ups & downs
# Add secondary/tertiary contacts and their phone numbers 
# Evaluate PRTG alert formatter before starting Meraki alert formatter
#####################################################################################

# Create a new input.txt or clear an existing input.txt of its contents
with open("input.txt", "w"):
    pass

# Open input.txt in Notepad, allowing the user to paste in alert(s)
subprocess.run(["notepad.exe", "input.txt"])

# Read the contents of input.txt into file_text
file_text = ""
with open("input.txt", "r") as file:
    for line in file:
        file_text += line
    
    # Capture customer with regex and check that all alerts are for the same customer
    customer = list(set(re.findall(r"(?<=Customer: )(.+)", file_text)))
    if len(customer) > 1:
        print("Error: More than 1 customer was included in input.txt")
        exit()
    else:
        customer = customer[0]
        
    contact_person = re.search(r"(?<=Primary Contact - )(.+)", file_text) # what about secondary and tertiary?
    contact_number = re.search(r"(?<=  )(.+ )(?=\.+ Secondary Number:)", file_text) # same as above
    
    # Capture and sort lexicographically all unique locations in the alerts
    location_list = re.findall(r"(?<=Group: )(.+)", file_text)
    location_list = sorted(list(set(map(lambda x: x.strip(), location_list)))) # why does this one need the strip() method?
    
    # Capture and sort lexicographically all unique devices in the alerts
    device_list = re.findall(r"(?<=\=\=\=\=\=\= Device \=\=\=\=\=\=\n\n)(.+\))(?= \()", file_text)
    device_list = sorted(list(set(device_list)))
    

    ########### Working on it ###########
    # Left off not having actual down times; all set with down alerts and up times
    # Actual down times are at the very bottom; just need to capture the device they relate to
    # It then needs to be added to "alerts" and sorted
    # Should have four when done; down times, down alert times, up times, and combined alerts 
    # Move regex expressions to constants

    # Checking for up alerts 
    # This should be renamed somehow to reflect the section it's from; down alert time and up time are in this section
    alerts = re.findall(
        r"(?<= Device \=\=\=\=\=\=\n\n).+[\n]*.+[\n]*.*[\n]*.*[\n]*.*[\n]*.*[\n]*(?=\=\=\= Additional Customer Details \=\=\=)", 
        file_text, 
        re.MULTILINE
    )

    alerts_formatted = []
    down_alert_times_and_device_info = []
    up_alert_times_and_device_info = []
    # alert_received_time_and_device_info_list = []

    for alert in alerts:
        separate_lines = list(filter(lambda x: len(x) > 1, alert.split("\n")))

        device_and_ip = re.match(r"(.*)(?= \()", separate_lines[0]).group()
        alert_time = separate_lines[-1].split(": ")[1].split(" (")[0]
        alert_type = separate_lines[1]

        full_alert = (alert_time, alert_type, device_and_ip)
        alerts_formatted.append(full_alert)
        
        if alert_type == "Device Status: Down":
            down_alert_times_and_device_info.append(full_alert)
        elif "Device Status: Down ended (now: Up)" in alert_type:
            up_alert_times_and_device_info.append(full_alert)
        else:
            print("Unrecognized alert type")
            exit()
            
    print("Down alerts:")
    print(down_alert_times_and_device_info)
    print("Up times:")
    print(up_alert_times_and_device_info)
    print("All alerts:")
    print(alerts_formatted)
    
    down_times_and_device_info = []
    scan_info = re.findall(r"Last Scan\:.*\n\n.*\]", file_text)

    ############# New section #############   <---- this will still need to capture the device the actual down time relates to
    for entry in scan_info:
        # rewrite regex to capture something with device info in it
        separate_lines = entry.split("\n\n")
        last_scan_time = separate_lines[0].split(": ")[1]
        last_up_time = separate_lines[1].split(": ")[1]
        if last_scan_time != last_up_time:
            down_time = last_up_time
            event_type = "device down"
            # device_and_ip = ???
            # full_event = (down_time, event_type, device_and_ip)
            # down_times_and_device_info.append(full_event) 
   
    print(down_times_and_device_info)

    ############# Commented out from last night #############

    # scan_information = scan_info[0].split("\n\n") # have to iterate this, just doing one for now
    # last_scan_time = scan_information[0].split(": ")[1]
    # last_up_time = scan_information[1].split(": ")[1]
    # if last_scan_time != last_up_time:
    #     down_times_and_device_info.append(last_up_time)
   
    # print(down_times_and_device_info)

    ########################################################

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
    # for alert in alerts_formatted:
    #     combined_events.append(alert_received_time[0] + " - Alert received for " + alert_received_time[1])
    
    # for device_down_time in down_times_and_device_info_list:
    #     combined_events.append(device_down_time[0] + " - " + device_down_time[1] + " Down")
        
    # combined_events = sorted(combined_events, reverse=True)
    
    # for event in combined_events:
    #     file.write("\n\t" + event)





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