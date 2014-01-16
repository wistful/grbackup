[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/wistful/grbackup/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

# grbackup readme
grbackup is a Python library for backup Google Reader items from your profile.

Licensed under the MIT license: [http://www.opensource.org/licenses/mit-license.php](http://www.opensource.org/licenses/mit-license.php)


## Usage

list subscriptions: `grbackup -e email@gmail.com -p password -ls`  
list topics: `grbackup -e email@gmail.com -p password -lt http://feed.com`  
list starred: `grbackup -e email@gmail.com -p password -lx`  
list all items: `grbackup -e email@gmail.com -p password -la`  


backup subscriptions: `grbackup -e email@gmail.com -p password -bs -o json:/tmp/subscriptions.json`  
backup topics: `grbackup -e email@gmail.com -p password -bt http://myfeed.com -o json:/tmp/myfeed.json`  
backup starred into MongoDB: `grbackup -e email@gmail.com -p password -bx -o mongodb://localhost:27017`  
backup all items into Redis: `grbackup -e email@gmail.com -p password -ba -o redis://localhost:6379/3`  

## Installation

grbackup on pypi at [http://pypi.python.org/pypi/grbackup/](http://pypi.python.org/pypi/grbackup/)

    $ pip install grbackup

or 

    $ easy_install grbackup
