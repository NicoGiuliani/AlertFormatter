import re
import subprocess
from tkinter import *

# TO-DO LIST 
#####################################################################################
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
    device_list = re.findall(r"(?<= Device \=\=\=\=\=\=\n\n)(.+)(?<=\))", file_text)
    # device_list = re.findall(r"(?<=\=\=\=\=\=\= Device \=\=\=\=\=\=\n\n)(.+\))(?= \()", file_text)
    device_list = sorted(list(set(device_list)))
    # print(device_list)
    # exit()

    # Move regex expressions to constants

    alerts = re.findall(
        r"(?<= Device \=\=\=\=\=\=\n\n).+[\n]*.+[\n]*.*[\n]*.*[\n]*.*[\n]*.*[\n]*(?=\=\=\= Additional Customer Details \=\=\=)", 
        file_text, 
        re.MULTILINE
    )

    alerts_formatted = []
    down_alert_times_and_device_info = []
    up_alert_times_and_device_info = []
    down_escalations_and_device_info = []

    for alert in alerts:
        separate_lines = list(filter(lambda x: len(x) > 1, alert.split("\n")))

        device_and_ip = re.match(r"(.*)(?= \()", separate_lines[0]).group()
        alert_time = separate_lines[-1].split(": ")[1].split(" (")[0]
        alert_type = separate_lines[1]

        full_alert = (alert_time, alert_type, device_and_ip)
        alerts_formatted.append(full_alert)
        # print(alert_type)
        
        if alert_type.strip() == "Device Status: Down":
            down_alert_times_and_device_info.append(full_alert)
        elif "Device Status: Down ended (now: Up)" in alert_type:
            up_alert_times_and_device_info.append(full_alert)
        elif "Down ESCALATION" in alert_type:
            down_escalations_and_device_info.append(full_alert)
        else:
            print("Unrecognized alert type")
            exit()
            
    down_alert_times_and_device_info = sorted(down_alert_times_and_device_info, reverse=True)
            
    # print("Down alerts:", down_alert_times_and_device_info)
    # print("Up times:", up_alert_times_and_device_info)
    # print("All alerts:", alerts_formatted)
        
    down_times_and_device_info = []
    scan_info = re.findall(r"Last Scan\:.*\n\n.*\]", file_text)
    for entry in scan_info:
        separate_lines = entry.split("\n\n")
        last_scan_time = separate_lines[0].split(": ")[1]
        last_up_time = separate_lines[1].split(": ")[1]
        if last_scan_time != last_up_time:
            down_time = last_up_time.split(" [")[0]
            event_type = "Actual Down Time"

            case_subject_info = re.search(r"(?<= indicating )" + r".*" + re.escape(down_time) + r".*" + r"(?= \[)", file_text).group()
            separate_words = case_subject_info.split(" ")
            device_info = ""
            for i in range(len(separate_words)):
                if re.search(r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", separate_words[i]) is not None:
                    device = separate_words[i - 1]
                    ip = separate_words[i]
                    device_info = device + " " + ip
                    down_times_and_device_info.append((down_time, event_type, device_info))
            
            
            print("Actual Down Times:", down_times_and_device_info)
    
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
    if len(down_alert_times_and_device_info) == 0:
        pass
    elif len(down_alert_times_and_device_info) > 1:
        for alert in down_alert_times_and_device_info:
            file.write("\n\t" + alert[0] + " - " + alert[1] + "\t" + alert[2])
    else:
        file.write(" " + down_alert_times_and_device_info[0][0])
    
    file.write("\nUp Date/Time: TBD")
    file.write("\n\nNext Steps/RFO: Investigating")
    file.write("\n-----------------------------------------------------------------------------------------")
    file.write("\nTime Line (Pacific):")


    combined_events = alerts_formatted + down_times_and_device_info
    combined_events = sorted(combined_events, reverse=True)
    event_message = ""
    for event in combined_events:
        # print("event:", event)
        if event[1].strip() == "Device Status: Down":
            event_message = "Down alert\t"
        elif event[1] == "Actual Down Time":
            event_message = "Device down\t"
        elif "Device Status: Down ended (now: Up)" in event[1]:
            event_message = "Device up\t"
        elif "Down ESCALATION" in event[1]:
            event_message = "Escalation alert\t"
        else:
            print("Who even knows, I'm as lost as you.")
            exit()
        file.write("\n\t" + event[0] + " - " + event_message + " " + event[2])


subprocess.run(["notepad.exe", "output.txt"])


# window = Tk()
# window.title("Alert Formatter")
# window.geometry('300x300')

# customer_label = Label(window, text="Customer:").grid(row=0, column=0, padx=10, pady=10)
# customer_entry = Entry(window).grid(row=0, column=1)

# window.mainloop()