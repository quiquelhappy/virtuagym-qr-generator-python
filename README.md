# Disclaimer
(hypothetical scenario - this is just for security hardening purposes) I wanted to enter the gym with just my Apple Watch without having to carry my phone. Before building the entire app, I created this to test at the gym and seeing if it does work.

# How to run
Login into your gym's website using the virtuagym software, in my case, https://<your gym slug>.virtuagym.com/
You can likely find this URL by looking for a login option inside your gym landing page or password recovery in-app.

Then, login, and get the following cookies:
- ``virtuagym_u``
- ``virtuagym_pref_club``

then, run the script with:
```
python gen.py --vg_member_id your_virtuagym_u --superclub_id your_virtuagym_pref_club
```

if this doesn't work, try
```
python gen.py --vg_member_id your_virtuagym_u --superclub_id your_virtuagym_pref_club --club_member_id your_club_member_id
```
I'm not sure on where to get ``your_club_member_id``, it might show up at ``https://<your gym slug>.virtuagym.com/user/<your account slug>/settings/sportschool``