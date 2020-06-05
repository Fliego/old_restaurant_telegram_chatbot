# 🍖 Restaurant telegram chatbot

This is a source code of Telegram restaurant chat-bot we built in 2016

Old spagetti-code, but still good to start with. In order to save user position in menu finite state machine notion used (in code represented by variable _step_)  


- Set bot token in *config.py* and webhook at the end of *bot.py*

- Change regular for your country code in is_correct_phone function in *utils.py*

- /broadcast for admins only to send notification for all of the bot users. handle_broadcast func - put your id here in *bot.py*

- I've translated some text for you in _messages_ table, but not all and everything. Be noticed, there are still dependencies on button names in source code
_buttons_ - table menu + first layer of categories
_comments_ - users reviews
_menu_ - for sending a photo of items in category
_messages_ - messages sent by bot
_orders_ - orders created by users
_products_ - items in final categories which are stated in _type_ column
_requrests_ - items which were put in baskets of users
_users_

- Description, price of item will not appear untill you will add _image_id_ in *products*

- Created order sends to admins (_users_ table set your telegra_id in your users row in _admin_ column) check _final_ function

Please, feel free to write me or create pull requests. More code later