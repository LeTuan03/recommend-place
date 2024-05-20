-- Create a new database
CREATE DATABASE traveldb;

-- Switch to the newly created database
USE traveldb;

-- Create user_data table
CREATE TABLE user_data (
    user_id INT PRIMARY KEY,
    user_name VARCHAR(255),
    full_name VARCHAR(255),
    password VARCHAR(255),
    age INT,
    gender VARCHAR(10)
);

-- Create location_data table
CREATE TABLE location_data (
    location_id INT PRIMARY KEY,
    location_name VARCHAR(255),
    category VARCHAR(50),
    description longtext,
    image longtext
);

-- Create ratings table
CREATE TABLE ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    location_id INT,
    rating INT,
    FOREIGN KEY (user_id) REFERENCES user_data(user_id),
    FOREIGN KEY (location_id) REFERENCES location_data(location_id)
);
