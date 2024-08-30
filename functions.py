import os
import datetime as dt
from cryptography.fernet import Fernet
from cProfile import label
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from O365 import Account, MSGraphProtocol
import pickle
import requests
import zipfile
class Subject:
    def __init__(self, name, grade, aimGrade):
        self.name = name
        self.grade = grade
        self.aimGrade = aimGrade
    def __str__(self):
        return f"Subject: {self.name}|Grade: {self.grade}|Target Grade: {self.aimGrade}"
#Function to read a specifc line from "data.txt"
def readspecific(lineNumber):
    f = open("data.txt", 'r')
    for currentLineNumber, line in enumerate(f, start=1):
         if currentLineNumber == lineNumber:
             return line.strip()
def createFile(path):
    f = open(path, "x")
    f.close()
def writespecific(lineNum, data):
    if checkFileExistence("data.txt"):
        with open("data.txt", "rt") as f:
            lines = f.readlines()
        while len(lines) < lineNum:
            lines.append("\n")
        linesAppend = lines[lineNum - 1 :]
        lines[lineNum - 1] = data + "\n"
        for i in range(len(linesAppend)):
            lines.append(linesAppend[i])
        with open("data.txt", "wt") as f:
            f.writelines(lines)
    else:
        createFile("data.txt")
        writespecific(lineNum, data)
def writefilepaths(data):
    if checkFileExistence("filepaths.txt"):
        with open("filepaths.txt", 'r') as f:
            lines = f.readlines()
        lines.append(data)
        with open("filepaths.txt", 'w') as f:
            f.writelines(lines)
    else:
        f = open("filepaths.txt","x")
        f.close()
        with open("filepaths.txt", 'r') as f:
            lines = f.readlines()
        lines.append(data)
        with open("filepaths.txt", 'w') as f:
            f.writelines(lines)
#Checks the existence of a file
def checkFileExistence(path):
    if os.path.exists(path):
        return True
    else:
      return False
#checks if the user has reset their info
def startCheck():
    if readspecific(1) == "1":
        pass
    else:
        setup()
#Checks what the time of day is and returns corresponding data
def timeOfDay():
    currentTime = dt.datetime.now().time()  # Get the current time
    if currentTime < dt.datetime.strptime("12:00", "%H:%M").time():
        return "Morning"
    elif currentTime < dt.datetime.strptime("20:00", "%H:%M").time():
        return "Afternoon"
    else:
        return "Evening"
#Pulls any events within the next day from your Outlook calendar
def calenderEvents():
   presenceFlag = False
   CLIENT_ID = 'a9b76c49-e4c0-4f48-971f-6b508fde7592'
   SECRET_ID = '-3k8Q~OPiKl4cQkkvWu5Zaub5.UXIxw9DMVHxbP1'
   credentials = (CLIENT_ID, SECRET_ID)
   protocol = MSGraphProtocol()
   scopes = ['Calendars.Read']
   account = Account(credentials, protocol=protocol)
   if account.authenticate(scopes=scopes):
      print('Authenticated!')
   else:
       print("Error: Could not authenticate")
       appcheck()
   schedule = account.schedule()
   calendar = schedule.get_default_calendar()
   start_time = dt.datetime.now().replace(hour=0, minute=0, second=0)
   end_time = start_time + dt.timedelta(days=1)
   q = calendar.new_query('start').greater_equal(start_time)
   q.chain('and').on_attribute('end').less_equal(end_time)
   events = calendar.get_events(query=q)
   for event in events:
      if events:
          print(f"Title: {event.subject}")
          print(f"Start: {str(event.start)[:-6]}")
          print(f"End: {str(event.end)[:-6]}\n")
          presenceFlag = True
   if not presenceFlag:
       print("No events for today")
   appcheck()
#Gets Latitude and Longitude for OpenWeather API
def getCoords(city):
    apiKey = '1cc64fee075fbef9166e23f47dbe40f7'
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={apiKey}"
    response = requests.get(geocode_url)
    data = response.json()
    if response.status_code == 200:
        lat = data[0]['lat']
        lon = data[0]['lon']
        return lat, lon
    else:
        print(f"Failed to retrieve geocoding data for {city}.")
        return None, None
#Runs the 'Home' app
def home():
    print(f"Good {timeOfDay()}, {readspecific(2)}")
    print(f"The date is {dt.datetime.now():%Y %m %d}\nThe time is {dt.datetime.now().strftime("%H:%M:%S")}")
#weather app
def weather():
    apiKey = '1cc64fee075fbef9166e23f47dbe40f7'
    cityName = readspecific(4)
    apiEndpoint = 'https://api.openweathermap.org/data/2.5/weather'
    choice = input("Current or Forecast\n").lower()
    if choice == "current":
        queryParams = {'q': cityName, 'appid': apiKey, 'units': 'metric'}
        response = requests.get(apiEndpoint, params=queryParams)
        if response.status_code == 200:
            data = response.json()
            weather = data['weather'][0]
            print(f"Weather: {weather["main"]}\nDescription: {weather['description'].capitalize()}\nTemprature: {data['main']['temp']}\nFeels Like: {data['main']['feels_like']}")
        else:
            print(f'Error: {response.status_code} - {response.text}')
    elif choice == "detail current":
        queryParams = {'q': cityName, 'appid': apiKey, 'units': 'metric'}
        response = requests.get(apiEndpoint, params=queryParams)
        if response.status_code == 200:
            data = response.json()
            weather = data['weather'][0]
            print(f"Weather: {weather["main"]}\nDescription: {weather['description'].capitalize()}\n")
            print(f"Temprature: {data['main']['temp']}\nFeels Like: {data['main']['feels_like']}")
            print(f"Pressure: {data['main']['pressure']} hPa\nHumidity: {data['main']['humidity']}%")
            print(f"Ground Level: {data['main']['grnd_level']} m\nSea Level: {data['main']['sea_level']} m")
            print(f"Visibility: {data['visibility']/1000}km\nWind Speed: {data['wind']['speed']}\nWind Direction (Degrees): {data['wind']['deg']}")
        else:
            print(f'Error: {response.status_code} - {response.text}')
    elif choice == "forecast":
        choice = input("Today or 8-day\n").lower()
        lat, lon = getCoords(readspecific(4))
        if choice == "today":
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,daily,alerts&appid={apiKey}&units=metric"
            response = requests.get(url)
            data = response.json()
            if response.status_code == 200:
                hourly_forecasts = data['hourly']
                now = dt.datetime.now()
                today_end = dt.datetime(now.year, now.month, now.day, 23, 59)
                print(f"Forecast for today:")
                for forecast in hourly_forecasts:
                    forecast_time = dt.datetime.fromtimestamp(forecast['dt'])
                    if now <= forecast_time <= today_end:
                        temp = forecast['temp']
                        description = forecast['weather'][0]['description'].capitalize()
                        print(f"{forecast_time.strftime('%H:%M:%S')}: {temp:.2f}°C, {description}")
        elif choice == "8-day":
            lat, lon = getCoords(readspecific(4))
            url = f"http://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={apiKey}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                dailyForecast = data['daily']
                print("8-Day Weather Forecast:")
                for day in dailyForecast[:8]:
                    date = dt.datetime.fromtimestamp(day['dt']).strftime('%d/%m')
                    temp = day['temp']['day']
                    description = day['weather'][0]['description'].capitalize()
                    print(f"Date: {date} Temperature: {temp}°C Weather: {description}")
            else:
                print(f"Error: {response.status_code})")
    appcheck()

def deletespecific(line_number):
    with open("filepaths.txt", 'r') as file:
        lines = file.readlines()
    lines.pop(line_number - 1)
    with open("filepaths.txt", 'w') as file:
        file.writelines(lines)
def locker():
    password = input("Please enter your password: ")
    while password != readspecific(3):
        password = input("Incorrect, please re-enter: ")
    choice = input("Storage or Packages?\n").lower()
    if choice == "storage":
        choice = input("View or Add?\n").lower()
        if choice == "view":
            with open("fernetkey.key","rb") as fk:
                key=fk.read()
            fernet = Fernet(key)
            if os.path.exists("filepaths.txt"):
                fp = open("filepaths.txt", "rt")
                lines = fp.readlines()
            else:
                fp = open("filepaths.txt","wt")
                fp.close()
                with open("filepaths.txt", "rt") as fp:
                    lines = fp.readlines()
            for i in range(len(lines)):
                print(f"{i}: {lines[i]}")
            viewNum = int(input("Enter the amount of files to be decrypted: "))
            for i in range(viewNum):
                choice = int(input("Enter the number of the file you want to decrypt: "))
                with open(lines[choice], "rb") as ef:
                    encrypted = ef.read()
                decrypted = fernet.decrypt(encrypted)
                with open(lines[choice], "wb") as df:
                    df.write(decrypted)
                print("Decrypted")
                deletespecific(choice)
        elif choice == "add":
            addNum = int(input("Enter the number of files to encrypt: "))
            for i in range(addNum):
                filePath = input(f"Please enter the file path of file {i+1} to be encrypted:\n")
                with open("fernetkey.key", "rb") as fk:
                    key = fk.read()
                fernet = Fernet(key)
                with open(filePath, "rb") as f:
                    original = f.read()
                encrypted = fernet.encrypt(original)
                with open(filePath, "wb") as ef:
                    ef.write(encrypted)
                print("File Encrypted")
                writefilepaths(filePath)
    elif choice == "packages":
        choice = input("Encrypt or Decrypt?\n").lower()
        if choice == "encrypt":
            filePath = input("Where is the file located: ")
            aesKey = os.urandom(32)
            nonce = os.urandom(16)
            if os.path.isdir(filePath):
                zipFilePath = filePath + '.zip'
                with zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk(filePath):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, filePath)
                            zf.write(file_path, arcname)
                            filePath = zipFilePath
            with open(filePath, "rb") as f:
                fileData = f.read()
            cipher = Cipher(
                algorithms.AES(aesKey),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(fileData) + encryptor.finalize()
            tag = encryptor.tag
            encryptedFile = nonce + ciphertext + tag
            keyPath = input("Where is the public key located?\n")
            with open(keyPath, 'rb') as kf:
                publicKey = serialization.load_pem_public_key(
                    kf.read(),
                    backend=default_backend()
                )
            encryptedAesKey = publicKey.encrypt(
                aesKey,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=SHA256()),
                    algorithm=SHA256(),
                    label=None
                )
            )
            fileExtension = os.path.splitext(filePath)[1]
            with zipfile.ZipFile("package.zip", 'w') as zipf:
                zipf.writestr("pack.enc", encryptedFile)
                zipf.writestr("key.bin", encryptedAesKey)
                zipf.writestr('fileExtension.txt', fileExtension)
        elif choice == "decrypt":
            packPath = input("Enter the path of the package: ")
            exLoc = os.path.dirname(packPath)
            with zipfile.ZipFile(packPath, 'r') as z:
                z.extractall(exLoc)
            with open("privateKey.pem", "rb") as kf:
                privateKey = serialization.load_pem_private_key(
                    kf.read(),
                    password=None,
                    backend=default_backend()
                )
            with open(os.path.join(exLoc, "key.bin"), "rb") as ekf:
                ek = ekf.read()
            aesKey = privateKey.decrypt(
                ek,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=SHA256()),
                    algorithm=SHA256(),
                    label=None
                )
            )
            with open(os.path.join(exLoc, "pack.enc"), "rb") as ef:
                efc = ef.read()
                nonce = efc[:16]
                ciphertext = efc[16:-16]
                tag = efc[-16:]
            with open(os.path.join(exLoc, "fileExtension.txt"), "rt") as fe:
                fileExtension = fe.read()
            cipher = Cipher(
                algorithms.AES(aesKey),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decryptedData = decryptor.update(ciphertext) + decryptor.finalize()
            if fileExtension == ".zip":
                decryptedZipPath = 'decrypted_content.zip'
                with open(decryptedZipPath, 'wb') as df:
                    df.write(decryptedData)
                with zipfile.ZipFile(decryptedZipPath, 'r') as zf:
                    zf.extractall()
                os.remove(decryptedZipPath)
            else:
                with open(os.path.join("processedPackage"+fileExtension), "wb") as of:
                    of.write(decryptedData)
            os.remove(os.path.join(exLoc, "key.bin"))
            os.remove(os.path.join(exLoc, "pack.enc"))
            os.remove(os.path.join(exLoc, "fileExtension.txt"))
            print("Data decrypted")
    appcheck()
def reset():
    writespecific(1,str(0))
    setup()
def setup():
    data = "1"
    writespecific(1,data)
    data = input("What is your name?\n")
    writespecific(2, data)
    password = input("Enter your password for the Safe APP (WARNING: NOT SECURELY STORED): ")
    writespecific(3,password)
    data = input("What city do you live in?\n")
    writespecific(4,data)
    subjects = []
    subNum = int(input("Enter Number of Subjects: "))
    for i in range(subNum):
        name = input(f"Enter subject name: ")
        grade = input(f"Enter {name}'s Grade: ")
        aimGrade = input(f"Enter {name}'s target grade: ")
        subject = Subject(name, grade, aimGrade)
        subjects.append(subject)
    with open("subjects.pickle", "wb") as f:
        pickle.dump(subjects, f)
    key = Fernet.generate_key()
    with open("fernetkey.key", "wb") as f:
        f.write(key)
    privateKey = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    publicKey = privateKey.public_key()
    with open("privateKey.pem", "wb") as key_file:
        key_file.write(
            privateKey.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
    with open("publicKey.pem", "wb") as key_file:
        key_file.write(
            publicKey.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
    print("Fernet and RSA keys created")
    main()
def movieReccomender():
    apiKey = "c1dd25ae29f68062bb75c73fb81ce0c7"
    title = input("Enter the name of the film you enjoyed: ")
    url = f"https://api.themoviedb.org/3/search/movie?api_key={apiKey}&query={title}"
    response = requests.get(url)
    data = response.json()
    movieID = data['results'][0]['id']
    url = f"https://api.themoviedb.org/3/movie/{movieID}?api_key={apiKey}"
    response = requests.get(url)
    data = response.json()
    genres = data["genres"]
    genres1 =  [genre['name'] for genre in genres]
    print(f"Genres: {", ".join(genres1)}")
    url = f"https://api.themoviedb.org/3/movie/{movieID}/recommendations?api_key={apiKey}"
    response = requests.get(url)
    data = response.json()
    recommendations = [movie['title'] for movie in data['results']]
    for movie in recommendations:
        print(movie)
    appcheck()
def subjects():
    choice = input("Display or Change?\n").lower()
    f = open(f'subjects.pickle', 'rb')
    subjectsNew = pickle.load(f)
    f.close()
    count = 0
    if choice == "display":
        for subject in subjectsNew:
            count += int(subject.grade)
            print(subject)
        print(f"Average Grade: {round(count / len(subjectsNew))}")
    elif choice == "change":
        choice = input("Add or Modify?\n").lower()
        if choice == "modify":
            subjectIndex = int(input("Enter number of subject to modify"))
            toModify = input("Enter what you want to modify").lower()
            match toModify:
                case "name":
                    subjectsNew[subjectIndex-1].name = input("Enter new name ")
                case "grade":
                    subjectsNew[subjectIndex-1].grade = int(input("Enter new grade "))
                case "target grade":
                    subjectsNew[subjectIndex-1].aimGrade = int(input("Enter new target grade "))
            with open(f'subjects.pickle', 'wb') as file:
                pickle.dump(subjectsNew, file)
            print("Moddified")
        elif choice == "add":
            subNum = int(input("Enter number of subjects to add: "))
            if subNum > 50 or subNum < 0:
                while subNum > 50 or subNum < 0:
                    print("Unreasonable number of subjects")
                    subNum = int(input("Please Re-enter: "))
            for i in range(subNum):
                name = input(f"Enter subject name")
                grade = input(f"Enter {name}'s Grade")
                aimGrade = input(f"Enter {name}'s target grade")
                subject = Subject(name, grade, aimGrade)
                subjectsNew.append(subject)
            with open(f'subjects.pickle', 'wb') as file:
                pickle.dump(subjectsNew, file)
            print("Added")
    appcheck()
def userHelp():
    print(f"Apps:\nWeather\nCalender\nSubjects\nMovie Recommender\nLocker\n Reset")
    appcheck()
#Asks User which App to launch
def appcheck():
    appChoice = input("Please enter app you want to launch: (Type 'help' for a list) (Press q to quit)\n").lower()
    match appChoice:
        case "calender":
            calenderEvents()
        case "weather":
            weather()
        case "help":
            userHelp()
        case "subjects":
            subjects()
        case "movie recommender":
            movieReccomender()
        case "locker":
            locker()
        case "q":
            quit()
        case "reset":
            reset()
        case _:
            print("Please Try Again")
            appcheck()
def main():
    startCheck()
    home()
    appcheck()
