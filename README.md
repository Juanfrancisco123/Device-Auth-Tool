# Device Auth Tool

A device auths generator tool which allows you to choose the client and the grant type

---

##### Configuration

* You can choose if you want to save the data individually or in `device_auths.json` file.
For that just change `output_type` in config.json
**1**: device_auths.json
**0**: individually (filename will be the account email)

*Important note:*
Not all clients supports all grant types, you may get an error saying the client is unauthorized. In that case try using another grant type

---

##### Supported Clients

* SwitchGameClient
* IOSGameClient
* AndroidGameClient

##### Supported Grants

* Authorization Code
* Device Code

---
You can use the code **BayGamerJJ** in the item shop if you want to support me! **#EpicPartner**