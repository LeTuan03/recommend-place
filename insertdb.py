import pymysql
import numpy as np
import pandas as pd

# Kết nối tới cơ sở dữ liệu
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Letuan191003+',
                             database='traveldb')

# Tạo đối tượng cursor
cursor = connection.cursor()

# Tạo dữ liệu mẫu cho bảng user_data
user_data = pd.DataFrame({
    "user_id": np.arange(1000),
    "user_name": [f"user_{i}" for i in range(1000)],
    "full_name": [f"Fullname_{i}" for i in range(1000)],
    "password": ["123456"] * 1000,
    "age": np.random.randint(18, 65, size=1000),
    "gender": np.random.choice(["Male", "Female"], size=1000),
})

# Tạo dữ liệu mẫu cho bảng location_data
location_data = pd.DataFrame({
    "location_id": [i for i in range(1000)],
    "location_name": [f"Location_{i}" for i in range(1000)],
    "category": np.random.choice(["Restaurant", "Cafe", "Bar", "Park"], size=1000),
    "description": ["Readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English."] * 1000,
    "image": np.random.choice(["https://i.pinimg.com/236x/ff/02/0f/ff020f5460556b671a0101abae76772c.jpg", "https://i.pinimg.com/236x/4e/c4/6a/4ec46aebf1bc57915874133d3a945188.jpg", "https://i.pinimg.com/236x/f5/34/5f/f5345f208d2b65b007ae012e697e3ab6.jpg"], size=1000),
})

# Tạo dữ liệu mẫu cho bảng ratings
ratings = pd.DataFrame({
    "user_id": np.random.choice(user_data["user_id"], size=5000),
    "location_id": np.random.choice(location_data["location_id"], size=5000),
    "rating": np.random.randint(1, 6, size=5000)
})

# Chèn dữ liệu vào bảng user_data
for index, row in user_data.iterrows():
    cursor.execute("INSERT INTO user_data (user_id, user_name, full_name, password, age, gender) VALUES (%s, %s, %s, %s, %s, %s)",
                   (row['user_id'], row['user_name'], row['full_name'], row['password'], row['age'], row['gender']))

# Chèn dữ liệu vào bảng location_data
for index, row in location_data.iterrows():
    cursor.execute("INSERT INTO location_data (location_id, location_name, category, description, image) VALUES (%s, %s, %s, %s, %s)",
                   (row['location_id'], row['location_name'], row['category'], row['description'], row['image']))

# Chèn dữ liệu vào bảng ratings
for index, row in ratings.iterrows():
    cursor.execute("INSERT INTO ratings (user_id, location_id, rating) VALUES (%s, %s, %s)",
                   (row['user_id'], row['location_id'], row['rating']))

# Lưu các thay đổi vào cơ sở dữ liệu
connection.commit()

# Đóng cursor và kết nối
cursor.close()
connection.close()
