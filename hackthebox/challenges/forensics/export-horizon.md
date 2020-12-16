
The info of the challenge is the next: *Our CEO's computer was compromised in a phishing attack. The attackers took care to clear the PowerShell logs, so we don't know what they executed. Can you help us?*

We're given a folder with event log files, I'll use Windows for this challenge

![image1](/images/htb-event-horizon/eventhorizon1.png)

Using the Event Viewer tool we can see information about the files, the ones that are 68kb haven't info, but the files that have more have information, with the information given I'll look for powershell logs that are more than 68 kb, I find the `Microsoft-Windows-Security-Mitigations%4KernelMode` that in the first warning there's the flag:

![image2](/images/htb-event-horizon/eventhorizon2.png)
