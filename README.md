# Scrape the Australian Open results
---- 
We are after the results from the official [AO web site][1]. The site is all dynamic so we use [Selenium][2].
**Note** that sometimes the site behaves unusually: when you choose the type of competition such as, for example, *Women’s Singles* and then a competition day, you may see some results completely unrelated to the chosen type. This is because if there are no matches of the right type on a particular day, the page starts showing *All Events* by default.

[1]:	http://www.ausopen.com
[2]:	http://selenium-python.readthedocs.io/index.html