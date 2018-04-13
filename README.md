# heart_rate_databases_starter
Backend built on MongoDB and Flask. Flask handles web requests and connects to the database. The backend allows patients and their heart rates to be stored in a database and can serve various measurements to the user (e.g. average heart rate).

To get started, first start MongoDB by running:
```
docker run -v $PWD/db:/data/db -p 27017:27017 mongo
```
on the virtual machine with Docker. Once the database is running, activate the `virtualenv` and install all the necessary dependencies using `pip install -r requirements.txt` Then run the web service by running:
```
python main.py
```
