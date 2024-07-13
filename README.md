![Logo](https://i.imgur.com/6zM7JBq.png)


# Scraping


This project was created specifically for the collection and analysis of data on the requested technologies for the developer's Python.

## 👩‍💻 _Installation & Run_
### 🧠 Set up the environment 

### 📝 Set enviroment variable
- Copy and rename the **.env.sample** file to **.env** 
- Open the .env file and edit the environment variables (Email and password for Djinni)
- Save the .env file securely 
- Make sure the .env file is in .gitignore

 On Windows:
```python
python -m venv venv 
venv\Scripts\activate
 ```

 On UNIX or macOS:
```python
python3 -m venv venv 
source venv/bin/activate
 ```

### 🗃️ Install requirements 
```python
pip install -r requirements.txt
```

### 🚀 Start scraping 
```python
python scraper/scraper.py
```


### 🚀 Start analyzing
Set date in file to analyze data for existing day in scraped_data
```python
python analyzer/data_visualization.py
```

## 📝 Contributing
If you want to contribute to the project, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make the necessary changes and commit them.
4. Submit a pull request.

## 😋 _Enjoy it!_