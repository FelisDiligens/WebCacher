# WebCacher
A http server that caches every requested resource from the internet for offline use.

![Screenshot](https://github.com/FelisDiligens/WebCacher/raw/master/screenshots/index.jpg)
> Screenshot showing the startpage.

<br><br>

![Screenshot](https://github.com/FelisDiligens/WebCacher/raw/master/screenshots/wiki.jpg)
> Screenshot showing cached Wikipedia.

## How does it work?
When you access a site through the cacher, it downloads the resource from the internet and saves it locally.
Then it will serve it from disk. (Queries are hashed, so search requests will be saved, too)

It will always prefer the cached resource, so you'll be able to access whole sites offline and save a lot of traffic.

## Deploy
### Prerequirements
You'll need this:
1. Python 3 interpreter
2. Python librarys: "requests", "Flask", "lxml"

### Install and run
It's really simple.
Just clone it and run "main.py".
That's it.

### Scripts
#### Windows
Install Python 3 and git first and then run in a Command Prompt:
```batch
pip install requests Flask lxml
git clone https://github.com/FelisDiligens/WebCacher.git
cd WebCacher
python main.py
```

#### Ubuntu
```bash
sudo apt install python3 git -y
pip install requests Flask lxml
git clone https://github.com/FelisDiligens/WebCacher.git
cd WebCacher
python3 main.py
```

## Remarks
The code is really not clean and optimized. I'm a newbie.

Some pages aren't rendered properly, but most do.
Also, there is no support for form requests (yet).

It's a bare-bones cacher and hopefully it serves your purpose. :)

### Motivation behind this
I'm frequently using public wifi and it's painfully slow.
So I wanted to save resources offline to save traffic and access them offline.
It works out pretty well, especially if the site reuses the same files across pages.
Google search request can be accessed offline, too.
