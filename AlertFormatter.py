import math
import re
import subprocess
from tkinter import *

# TO-DO LIST 
#####################################################################################
# Move regex expressions to constants
# Add filters for all other types of phone number
# What about formatting numbers for viewing? Some aren't formatted the same when scraped
# Have to handle Health Probe type alerts
# What about Summaries?
# Start the one for Meraki alerts
# Clean up, document everything
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
    customer = list(set(re.findall(r"(?<=Customer: )(.+)(?=\n)", file_text)))
    print("customer:", customer)
    if len(customer) > 1:
        print("Error: More than 1 customer was included in input.txt")
        exit()
    else:
        customer = customer[0]
    
    
    def collect_contact_information(regex):
        contact_query = re.search(regex, file_text)
        if contact_query is not None:
            contact = contact_query.group()
            contact_lines = contact.split("\n")
            contact_lines = list(map(lambda x: x.strip(), contact_lines))
            
            contact_person = contact_lines[0]
            
            # Phone number formats covered: (???) ???-????, ???-???-????
            contact_numbers = re.findall(r"(\([0-9]{3}\)\s[0-9]{3}\-[0-9]{4}|[0-9]{3}\-[0-9]{3}\-[0-9]{4})", contact_lines[1])
            # print("contacts:", contact_numbers)
            contact_primary_number = contact_numbers[0] if 0 < len(contact_numbers) else "           "
            contact_secondary_number = contact_numbers[1] if 1 < len(contact_numbers) else "           "
            
            contact_emails = re.findall(r"([A-Za-z0-9\_\.]*@[A-Za-z0-9\_\.]*\.[A-Za-z]{3})", contact_lines[2])
            # print("emails:", contact_emails)
            contact_primary_email = contact_emails[0] if 0 < len(contact_emails) else "           "
            contact_secondary_email = contact_emails[1] if 1 < len(contact_emails) else "           "
            
            # print("Email:", contact_primary_email)
            # print("Email 2:", contact_secondary_email)
            return {
                "person": contact_person,
                "primary_number": contact_primary_number,
                "secondary_number": contact_secondary_number,
                "primary_email": contact_primary_email,
                "secondary_email": contact_secondary_email,
                "person_padding": "\t",
                "primary_email_padding": "\t",
                "secondary_email_padding": "\t"
            }
        else:
            return None
		
    # Capture contact information
    primary_contact = collect_contact_information(r"(?<=Primary Contact - )(.*[\n]+.*[\n].*)")
    secondary_contact = collect_contact_information(r"(?<=Secondary Contact - )(.*[\n]+.*[\n].*)") 
    tertiary_contact = collect_contact_information(r"(?<=Tertiary Contact - )(.*[\n]+.*[\n].*)") 
    
    longest_name_length = len(primary_contact["person"])
    longest_primary_email = len(primary_contact["primary_email"])
    longest_secondary_email = len(primary_contact["secondary_email"])
    
    if secondary_contact is not None:
        if len(secondary_contact["person"]) > longest_name_length:
            longest_name_length = len(secondary_contact["person"])
        if len(secondary_contact["primary_email"]) > longest_primary_email:
            longest_primary_email = len(secondary_contact["primary_email"])
        if len(secondary_contact["secondary_email"]) > longest_secondary_email:
            longest_secondary_email = len(secondary_contact["secondary_email"])
            
    if tertiary_contact is not None:
        if len(tertiary_contact["person"]) > longest_name_length:
            longest_name_length = len(tertiary_contact["person"])
        if len(tertiary_contact["primary_email"]) > longest_primary_email:
            longest_primary_email = len(tertiary_contact["primary_email"])
        if len(tertiary_contact["secondary_email"]) > longest_secondary_email:
            longest_secondary_email = len(tertiary_contact["secondary_email"])
            
    # print("longest primary email:", longest_primary_email)
    
    primary_contact["person_padding"] = math.ceil((longest_name_length - len(primary_contact["person"]))) * " " + "\t"
    primary_contact["primary_email_padding"] = math.ceil((longest_primary_email - len(primary_contact["primary_email"]))) * " " + "\t"
    primary_contact["secondary_email_padding"] = math.ceil((longest_secondary_email - len(primary_contact["secondary_email"]))) * " " + "\t"
    if secondary_contact is not None:
        secondary_contact["person_padding"] = math.ceil((longest_name_length - len(secondary_contact["person"]))) * " " + "\t"
        secondary_contact["primary_email_padding"] = math.ceil((longest_primary_email - len(secondary_contact["primary_email"]))) * " " + "\t"
        secondary_contact["secondary_email_padding"] = math.ceil((longest_secondary_email - len(secondary_contact["secondary_email"]))) * " " + "\t"
    if tertiary_contact is not None:
        tertiary_contact["person_padding"] = math.ceil((longest_name_length - len(tertiary_contact["person"]))) * " " + "\t"
        tertiary_contact["primary_email_padding"] = math.ceil((longest_primary_email - len(tertiary_contact["primary_email"]))) * " " + "\t"
        tertiary_contact["secondary_email_padding"] = math.ceil((longest_secondary_email - len(tertiary_contact["secondary_email"]))) * " " + "\t"
    
    # Capture and sort lexicographically all unique locations in the alerts
    location_list = re.findall(r"(?<=Group: )(.+)", file_text)
    location_list = sorted(list(set(map(lambda x: x.strip(), location_list)))) # why does this one need the strip() method?
    
    # # Capture and sort lexicographically all unique devices in the alerts
    # device_list = re.findall(r"(?<= Device \=\=\=\=\=\=\n\n)(.*\([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\))", file_text)
    # device_list = sorted(list(set(device_list)))

    alerts = re.findall(
        r"(?<= Device \=\=\=\=\=\=\n\n).+[\n]*.+[\n]*.*[\n]*.*[\n]*.*[\n]*.*[\n]*(?=\=\=\= Additional Customer Details \=\=\=)", 
        file_text, 
        re.MULTILINE
    )

    alerts_formatted = []
    down_alert_times_and_device_info = []
    up_alert_times_and_device_info = []
    down_escalations_and_device_info = []
    
    # Capture and sort lexicographically all unique devices in the alerts
    device_list = []
    

    for alert in alerts:
        separate_lines = list(filter(lambda x: len(x) > 1, alert.split("\n\n")))
        device_and_ip = re.match(r"(.*)(?= \()", separate_lines[0]).group()
        device_list.append(device_and_ip)
        link_alert = False
        
        if "sensor" in separate_lines[1]:
            # print(separate_lines[1])
            link = re.search(r"(?<=Sensor Type: )(.*)(?= Traffic \()", separate_lines[1]).group()
            device_and_ip = device_and_ip + " " + link
            link_alert = True
        
        alert_time = separate_lines[-1].split(": ")[1].split(" (")[0]
        
        alert_type = ""
        for i in range(len(separate_lines)):
            if "Device Status:" in separate_lines[i]:
                alert_type = separate_lines[i].split("\n")[0]
                # print(alert_type)
            
        full_alert = (alert_time, alert_type, device_and_ip, link_alert)
        # print("full_alert:", full_alert)
        alerts_formatted.append(full_alert)
        
        if "Device Status: Down" in alert_type:
            down_alert_times_and_device_info.append(full_alert)
        elif "Device Status: Down ended (now: Up)" in alert_type:
            up_alert_times_and_device_info.append(full_alert)
        elif "Down ESCALATION" in alert_type:
            down_escalations_and_device_info.append(full_alert)
        else:
            print("Unrecognized alert type")
            exit()
            
    device_list = sorted(list(set(device_list)))
    down_alert_times_and_device_info = sorted(down_alert_times_and_device_info, reverse=True)
                    
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
            # print("this thing:", re.search(r"indicating a link", file_text))
            link_alert = True if re.search(r"indicating a link", file_text) is not None else False
            print("link_alert:", link_alert)
            separate_words = case_subject_info.split(" ")
            device_info = ""
            for i in range(len(separate_words)):
                if re.search(r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", separate_words[i]) is not None:
                    device = separate_words[i - 1]
                    ip = separate_words[i]
                    device_info = device + " " + ip
                    down_times_and_device_info.append((down_time, event_type, device_info, link_alert))
            
            
            # print("Actual Down Times:", down_times_and_device_info)
    
# add padding to the length of each email, name, alert, etc.
# Format this section for visual simplicity
with open("output.txt", "w") as file:
    file.write("=" * 165 + "\n")
    file.write("Primary Contact: \t" + primary_contact["person"] + primary_contact["person_padding"] + primary_contact["primary_number"] + 
               ("\t" if primary_contact["primary_email"] else "") + primary_contact["primary_email"] + " " + primary_contact["primary_email_padding"] + "|   " + primary_contact["secondary_number"] + 
               ("\t" if primary_contact["secondary_email"] else "") + primary_contact["secondary_email"] + "\n")
    
    if secondary_contact is not None:
        file.write("Secondary Contact: \t" + secondary_contact["person"] + secondary_contact["person_padding"] + secondary_contact["primary_number"] + 
                ("\t" if secondary_contact["primary_email"] else "") + secondary_contact["primary_email"] + " " + secondary_contact["primary_email_padding"] + "|   " + secondary_contact["secondary_number"] + 
                ("\t" if secondary_contact["secondary_email"] else "") + secondary_contact["secondary_email"] + "\n")
    if tertiary_contact is not None:
        file.write("Tertiary Contact: \t" + tertiary_contact["person"] + tertiary_contact["person_padding"] + tertiary_contact["primary_number"] + 
                ("\t" if tertiary_contact["primary_email"] else "") + tertiary_contact["primary_email"] + " " + tertiary_contact["primary_email_padding"] + "|   " + tertiary_contact["secondary_number"] + 
                ("\t" if tertiary_contact["secondary_email"] else "") + tertiary_contact["secondary_email"] + "\n")

    
    file.write("=" * 165 + "\n\n")
    
    
    file.write("Support has received the following alerts.\n\nEdnetics Case: [[CAS]]\n\n")
    file.write("Customer: " + customer)
    file.write("\nPoC: " + primary_contact["person"])
    file.write("\nContact Number: " + primary_contact["primary_number"]) 
    
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
            file.write("\n\t" + alert[0] + " - " + alert[2])
    else:
        # print("boom:", down_alert_times_and_device_info)
        file.write(" " + down_alert_times_and_device_info[0][0])
    
    file.write("\n\nUp Date/Time: TBD")
    file.write("\n\nNext Steps/RFO: Investigating")
    file.write("\n" + "-" * 165)
    file.write("\nTime Line (Pacific):")

    print("downtimes:", down_times_and_device_info)
    combined_events = alerts_formatted + down_times_and_device_info
    combined_events = sorted(combined_events, reverse=True)
    print("combined:", combined_events)
    
    for event in combined_events:
        if event[1].strip() == "Device Status: Down":
            event_message = "Down alert       \t" if event[3] == False else "Link alert       \t"
        elif event[1] == "Actual Down Time":
            event_message = "Device down      \t" if event[3] == False else "Link down        \t"
        elif "Device Status: Down ended (now: Up)" in event[1]:
            event_message = "Device up        \t" if event[3] == False else "Link up          \t"
        elif "Down ESCALATION" in event[1]:
            event_message = "Escalation alert \t"
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