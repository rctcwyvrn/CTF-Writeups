CTF: tamuCTF
===
## Info
* Category: Misc
* Challenge: Onboarding Checklist
* Solved by: Howard Lin
* Writeup by: Howard Lin
## Solution
This problem was fairly straightforward, we needed to send an email to tamuCTF with our personal email in the body and a spoofed email address in the from. This was so that the "business" would think that the owner of the spoofed email had hired us and would send us their info.

So the challenge was to send an email with a spoofed email sender address. To do this I used sendemail and gmail's SMTP server (which surprsingly worked). The only thing you need to is to get a device password (because it won't let you authenticate with your normal one) for your google account and you're good to go.


So with sendemail you would just need to use something like this:

sendemail -o tls=yes -t buisness-destination@gmail.com -f spoofed-email-here@gmail.com -s smtp.gmail.com:587 -xu your-email-here@gmail.com -xp your-device-password -u "whatever subject you want" -m "your-email-here@gmail.com"

Note: This worked for the challenge, but the email still has your personal email in the sender box, along with the spoofed email, so it doesn't work for actual phishing (yet).

Thanks for reading!

