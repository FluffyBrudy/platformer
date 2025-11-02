# platformer
platformer game made  with python

## build excutable file
First install all dependencies with
```bash
	python3 -m pip install -r requirements.txt
```
*For linux virtual environment is required or harmful flag --break-site-packages or something similar flag*


```bash
python3 -m PyInstaller game.py --noconsole --add-data "assets:assets" --add-data "data:data"                                                                                                                                                                                 
```
**exe file for window/linux may be under dist/ if not check under game/**


